"""What an agent found, merged into the specification: its staging file, `evidence/staging/<role>.md`, judged whole
and made into operations applied as one change -- or refused, every reason said, and nothing changed.

    python app/spec.py merge evidence/staging/web.md --check    the agent's own check, before it answers: nothing written
    python app/spec.py merge evidence/staging/web.md            the main agent's merge, once the agent has answered

A staging file is refused while a facet of its role has no row, or a row says other than found, none or n/a; while
a finding names a source there is not, a lens or a word of Seen there is not, says nothing of what was found, or
carries no quote though it was seen, run or said; while a quote is not in the file its Where names, or that file is
a file of data; while a finding is one the specification holds already. A source the agent declares, for material
no source covered, is added with the next free ID, and the rows naming it follow. Each finding becomes a node,
each Coverage row a line of its source's coverage with a print of what the part is now, a version the source lacks
is written; what the agent said of its work -- its facets, its disagreements, its report -- is kept in
`evidence/reports/<file>.md`, its disagreements gathered in `evidence/staging/disagreements.md` for the reconciler,
and the staging file goes.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import evidence
import load as loading
import logic
import nodefile

AGENTS = Path(__file__).resolve().parent / "agents.json"
FACET_WORDS = ("found", "none", "n/a")


@dataclass
class Staged:
    """A staging file, read: its header lines, its tables, its free parts."""
    name: str
    title: str = ""
    lines: dict[str, str] = field(default_factory=dict)
    new_sources: list[tuple[str, str, str]] = field(default_factory=list)
    tables: dict[str, list[list[str]]] = field(default_factory=dict)
    parts: dict[str, str] = field(default_factory=dict)


def read(path: Path) -> Staged:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    staged = Staged(path.stem)
    heading = ""
    body: dict[str, list[str]] = {"": []}
    for line in text.split("\n"):
        if line.startswith("# ") and not staged.title:
            staged.title = line[2:].strip()
            continue
        if line.startswith("## "):
            heading = line[3:].strip()
            body[heading] = []
            continue
        body.setdefault(heading, []).append(line)
        key = re.match(r"^- \*\*([\w ]+):\*\*\s*(.*)$", line)
        if key and not heading:
            if key.group(1).lower() == "new source":
                parts = [p.strip() for p in key.group(2).split("|")]
                if parts and re.fullmatch(r"S\d+", parts[0]):
                    staged.new_sources.append((parts[0], parts[1] if len(parts) > 1 else "",
                                               parts[2] if len(parts) > 2 else ""))
            else:
                staged.lines[key.group(1).lower()] = key.group(2).strip()
    for heading, lines in body.items():
        staged.parts[heading] = "\n".join(lines).strip()
        rows = [l.strip() for l in lines if l.strip().startswith("|")]
        if len(rows) >= 2:
            staged.tables[heading] = [nodefile.cells(r) for r in rows[2:]]
    return staged


def facets_of(role: str) -> list[str] | None:
    held = json.loads(AGENTS.read_text(encoding="utf-8"))["facets"]
    return held.get(role)


def data_files() -> tuple[str, ...]:
    return tuple(json.loads(AGENTS.read_text(encoding="utf-8"))["data files"])


@dataclass
class Judged:
    problems: list[str]
    operations: list[list[str]]
    findings: int
    staged: Staged


def judge(root: Path, path: Path) -> Judged:
    """What merging the file would do, and why it may not."""
    g = loading.grammar()
    done = loading.load(root)
    staged = read(path)
    problems: list[str] = []
    operations: list[list[str]] = []
    if done.problems:
        return Judged([f"the specification does not load ({len(done.problems)} problem(s)): `spec.py check`"], [], 0,
                      staged)
    role = staged.lines.get("role", "").strip("` ").lower()
    wanted = facets_of(role)
    if wanted is None:
        problems.append(f"Role: `{role or 'none given'}` is no agent's; they are "
                        f"{', '.join(json.loads(AGENTS.read_text(encoding='utf-8'))['facets'])}")
        wanted = []
    facets = {r[0].strip("` ").lower(): (r + ["", "", ""])[:4] for r in staged.tables.get("Facets", []) if r and r[0]}
    for facet in wanted:
        if facet not in facets:
            problems.append(f"facet {facet}: no row under ## Facets -- found, none or n/a")
            continue
        _, word, named, looked = facets[facet]
        word = word.strip("` ").lower()
        if word not in FACET_WORDS:
            problems.append(f"facet {facet}: `{word}` is none of {', '.join(FACET_WORDS)}")
        elif word != "found" and not (looked.strip() or named.strip()):
            problems.append(f"facet {facet}: {word}, and it does not say where it looked or why")
    sources = {i: n for i, n in done.nodes.items() if n.kind == "source"}
    places: dict[str, Path | None] = {i: evidence.source_place(root, n.fields.get("where", "")) for i, n in sources.items()}
    named_as: dict[str, str] = {i: i for i in sources}
    for ref, where, what in staged.new_sources:      # material no source covered: added first, named by `$n`
        if ref in sources:
            problems.append(f"New source {ref}: there is a source {ref} already; declare the next free one")
            continue
        operations.append(["add", "source", what or where, f"where={where}"])
        named_as[ref] = f"${len(operations)}"
        places[ref] = evidence.source_place(root, where)
    held: dict[tuple, list[tuple[int | None, str]]] = {}
    for n in done.nodes.values():
        if n.kind == "finding" and n.fields.get("quote"):
            src = next((e.dst for e in done.edges if e.src == n.id and e.rel == "from"), "")
            key = (src, evidence.place_of(n.fields.get("where", "")).lower(), n.fields.get("lens"),
                   evidence.squeeze(n.fields["quote"].strip("`")), n.fields.get("seen"))
            held.setdefault(key, []).append((evidence.line_of(n.fields.get("where", "")), n.id))
    lenses, seen_words = g["choices"]["lens"], g["choices"]["seen"]
    count = 0
    for at, row in enumerate(staged.tables.get("Findings", []), 1):
        source, where, lens, found, quote, seen, _became, limits = (row + [""] * 8)[:8]
        bare = quote.strip().strip("`").strip()
        said = f"finding {at} ({where or 'no Where'})"
        if source not in named_as:
            problems.append(f"{said}: `{source}` is no source; they are {', '.join(sorted(named_as)) or 'none'}")
            continue
        if lens not in lenses:
            problems.append(f"{said}: `{lens}` is no lens; they are {', '.join(lenses)}")
        if seen not in seen_words:
            problems.append(f"{said}: `{seen}` is none of {', '.join(seen_words)}")
        if not found.strip():
            problems.append(f"{said}: it does not say what was found")
        if seen != "inferred" and not bare:
            problems.append(f"{said}: it was {seen or 'seen'} and carries no quote")
        there = places.get(source)
        if bare and there is not None:
            file = evidence.file_of(there, where)
            if file is None:
                problems.append(f"{said}: `{evidence.place_of(where)}` is not a file of {source}")
            elif file.suffix.lower() in data_files():
                problems.append(f"{said}: it quotes a file of data, {file.name}, which is never opened")
            elif evidence.squeeze(bare) not in evidence.squeeze(file.read_text(encoding="utf-8", errors="replace")):
                problems.append(f"{said}: the quote is not in {file.name}")
        if bare:
            key = (source, evidence.place_of(where).lower(), lens, evidence.squeeze(bare), seen)
            line = evidence.line_of(where)
            twin = next((ident for l, ident in held.get(key, []) if l is None or line is None or l == line), None)
            if twin:
                problems.append(f"{said}: the same place and quote as {twin}")
            held.setdefault(key, []).append((line, f"finding {at}"))
        words = ["add", "finding", found, f"source={named_as[source]}", f"where={where}", f"lens={lens}",
                 f"seen={seen}"]
        words += [f"quote={bare}"] if bare else []
        words += [f"limits={limits}"] if limits.strip() else []
        operations.append(words)
        count += 1
    for row in staged.tables.get("Coverage", []):
        source, part, read_word, note = (row + [""] * 4)[:4]
        if source not in named_as:
            problems.append(f"coverage of `{part}`: `{source}` is no source")
            continue
        if read_word not in g["choices"]["read"]:
            problems.append(f"coverage of `{part}`: `{read_word}` is none of {', '.join(g['choices']['read'])}")
            continue
        there = places.get(source)
        printed = evidence.print_of(there, part) if there is not None and read_word != "not read" else ""
        if source in sources:
            rows = sources[source].fields.get("coverage") or []
            if any(evidence.part_named(r.get("part", "")) == evidence.part_named(part) for r in rows):
                operations.append(["remove-line", source, "coverage", next(
                    r["part"] for r in rows if evidence.part_named(r.get("part", "")) == evidence.part_named(part))])
        operations.append(["add-line", named_as[source], "coverage", part, f"read={read_word}", f"note={note}",
                           f"print={printed}"])
    version = staged.lines.get("version", "")
    if version:
        for ref in sorted({(r + [""])[0] for r in staged.tables.get("Findings", [])} & set(sources)):
            if not sources[ref].fields.get("version"):
                operations.append(["set", ref, "version", version])
    return Judged(problems, operations, count, staged)


def check(root: Path, path: Path) -> tuple[bool, list[str]]:
    """The agent's own check: what the merge would refuse, with nothing written. The change is tried as the logic
    would make it, so that a fault only the whole would show is told too."""
    if not path.is_file():
        return False, [f"{path}: not found"]
    judged = judge(root, path)
    said = [f"{path.name}: {p}" for p in judged.problems]
    if not judged.problems:
        try:
            result = logic.apply(root, judged.operations, who=judged.staged.lines.get("role", "agent"), dry=True)
            said += [f"{path.name}: {file}:{line}: {message}" for file, line, message in result.problems]
        except logic.Refused as why:
            said.append(f"{path.name}: {why}")
    ok = not said
    said.append(f"{path.name}: {judged.findings} finding(s) would be merged" if ok else
                f"{path.name}: correct each line above, then check again -- nothing is merged while one stands")
    return ok, said


def merge(root: Path, path: Path) -> tuple[bool, list[str]]:
    """The merge of one staging file: all of it, or nothing."""
    ok, said = check(root, path)
    if not ok:
        return False, said
    judged = judge(root, path)
    staged = judged.staged
    result = logic.apply(root, judged.operations, who=f"{staged.lines.get('role', 'an')} agent",
                         because=f"merged from {path.name}")
    if result.problems:
        return False, [f"{path.name}: {f}:{l}: {m}" for f, l, m in result.problems]
    made = [line.rsplit("->", 1)[1].strip() for line in result.applied if line.startswith("add finding")]
    keep_report(root, staged, made)
    disagreements = staged.parts.get("Disagreements", "").strip()
    if disagreements:
        kept = root / evidence.DISAGREEMENTS
        held = kept.read_text(encoding="utf-8").rstrip("\n") if kept.is_file() else (
            "# What the agents found to disagree: each that holds becomes a contradiction; then this file goes")
        kept.write_text(f"{held}\n\n## {staged.name}\n\n{disagreements}\n", encoding="utf-8", newline="\n")
    path.unlink()
    span = f"{made[0]} to {made[-1]}" if len(made) > 1 else made[0] if made else "no finding"
    return True, [f"{path.name}: merged -- {len(made)} finding(s), {span}; its report kept in "
                  f"{evidence.REPORTS}/{staged.name}.md" + ("; its disagreements kept for the reconciler"
                                                            if disagreements else "")]


def keep_report(root: Path, staged: Staged, made: list[str]) -> None:
    """What the agent said of its work, kept: what it looked at and found nothing in stays on record."""
    path = root / evidence.REPORTS / f"{staged.name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    span = (f"{made[0]} to {made[-1]}, {len(made)} findings" if len(made) > 1 else
            f"{made[0]}, 1 finding" if made else "no finding")
    if path.is_file():
        held = path.read_text(encoding="utf-8").rstrip("\n")
        path.write_text(f"{held}\n\n## Merged again\n\n- **Merged:** {span}\n", encoding="utf-8", newline="\n")
        return
    out = [f"# {staged.title or staged.name}", "",
           *(f"- **{key.capitalize()}:** {staged.lines[key]}" for key in ("role", "read", "version")
             if staged.lines.get(key)), f"- **Merged:** {span}"]
    for heading in ("Facets", "Disagreements", "Report"):
        if staged.parts.get(heading):
            out += ["", f"## {heading}", "", staged.parts[heading]]
    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def staged_files(root: Path) -> list[Path]:
    place = root / evidence.STAGING
    return sorted(p for p in place.glob("*.md") if p.name != Path(evidence.DISAGREEMENTS).name) if place.is_dir() else []
