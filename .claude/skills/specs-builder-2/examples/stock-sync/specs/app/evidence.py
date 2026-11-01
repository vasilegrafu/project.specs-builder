"""The evidence beside the data: where each source is, what a part of it was when it was read, and the files the
agents and the scripts keep in `evidence/` -- captures of what cannot be opened where it lives, each agent's report,
the analyses, the scout's report, and the staging files waiting to be merged.

A source's `where` is a path, from the specification's folder or absolute -- `../dev/`, `evidence/captures/site/`
-- or words saying the material is not in reach. A finding's `where` is the file within it, and the line or the
detail after it: `api/cart.py:42`, `V3-the-checkout.md, after leaving Amount empty`. A part's print is twelve hex
digits of what it was when it was read -- a file's bytes; a folder's or a pattern's every file, by path and bytes --
so that a part changed since is told, and the findings resting on it read again.
"""
from __future__ import annotations

import fnmatch
import hashlib
import os
import re
from pathlib import Path

EVIDENCE = "evidence"
CAPTURES = f"{EVIDENCE}/captures"
REPORTS = f"{EVIDENCE}/reports"
ANALYSIS = f"{EVIDENCE}/analysis"
STAGING = f"{EVIDENCE}/staging"
DISAGREEMENTS = f"{STAGING}/disagreements.md"
SCOUT = f"{EVIDENCE}/scout.md"
ELSEWHERE = ("not in this folder", "not in reach", "elsewhere", "http://", "https://")


def part_named(part: str) -> str:
    """A part as a path: without the backticks it may be written in, or a closing slash."""
    return part.strip().strip("`").strip().rstrip("/")


def place_of(where: str) -> str:
    """The file a finding's `where` names, without the line or the detail after it."""
    return re.split(r":\d|,", where, maxsplit=1)[0].strip() or where


def line_of(where: str) -> int | None:
    found = re.search(r":(\d+)", where)
    return int(found.group(1)) if found else None


def source_place(root: Path, where: str) -> Path | None:
    """Where a source is on disk, or nothing where it is not in reach."""
    said = where.strip()
    if not said or said.lower().startswith(ELSEWHERE):
        return None
    there = Path(said) if Path(said).is_absolute() else root / said
    return there if there.exists() else None


def file_of(there: Path, where: str) -> Path | None:
    """The file a finding names, within its source."""
    if there.is_file():
        return there
    target = there / place_of(where)
    return target if target.is_file() else None


def print_of(there: Path, part: str) -> str:
    """What a part of a source is now, in twelve hex digits; nothing where it is not there to be printed."""
    root = there if there.is_dir() else there.parent
    files: list[Path] = []
    for named in dict.fromkeys((part_named(part), place_of(part_named(part)))):
        target = there if there.is_file() and named in ("", there.name) else root / named
        if target.is_file():
            files = [target]
        elif target.is_dir():
            files = sorted(p for p in target.rglob("*") if p.is_file())
        else:
            files = sorted(p for p in root.rglob("*") if p.is_file()
                           and fnmatch.fnmatch(p.relative_to(root).as_posix(), named))
        if files:
            break
    if not files:
        return ""
    digest = hashlib.sha256()
    for file in files:
        digest.update(file.relative_to(root).as_posix().encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(file.read_bytes()).digest())
    return digest.hexdigest()[:12]


def squeeze(text: str) -> str:
    """Text with its spacing made one, so that a quote is found however the lines of its file are broken."""
    return " ".join(text.split())


def files(root: Path) -> list[str]:
    """Every file of the evidence, by its path from the specification's folder, staging aside."""
    place = root / EVIDENCE
    if not place.is_dir():
        return []
    natural = lambda s: [int(x) if x.isdigit() else x for x in re.findall(r"\d+|\D+", s)]   # noqa: E731
    return sorted((p.relative_to(root).as_posix() for p in place.rglob("*")
                   if p.is_file() and STAGING not in p.relative_to(root).as_posix()), key=natural)


def moved(root: Path, sources: dict[str, dict]) -> list[dict]:
    """Each part read whose print is not what it is now: `sources` maps each source's ID to its `where` and its
    Coverage rows."""
    out = []
    for ident, said in sources.items():
        there = source_place(root, said.get("where", ""))
        if there is None:
            continue
        for row in said.get("coverage", []):
            held = row.get("print", "")
            if not held or row.get("read") == "not read":
                continue
            now = print_of(there, row.get("part", ""))
            if now != held:
                out.append({"source": ident, "part": row.get("part", ""), "was": held, "now": now or "gone"})
    return out


# A live site's captures, `evidence/captures/<site>/`: its inventory names every view, each view's capture stands
# beside it and says where and when it was taken and its screenshots; an address the captured views link to on the
# site's own host that no view of the inventory is, is not walked yet.
INVENTORY = "inventory.md"
SITE_SAYS = ("Address", "Scope", "Walked", "Browser")
CAPTURE_SAYS = ("Address", "Captured", "Screenshots", "Redacted")
NOT_CAPTURED = "not captured:"
LINK_RE = re.compile(r"^link: .*? \u2192 (/[^\s?]*)", re.MULTILINE)


def line_value(text: str, key: str) -> str:
    found = re.search(rf"^- \*\*{re.escape(key)}:\*\* *(.*)$", text, re.MULTILINE)
    return found.group(1).strip() if found else ""


def table_rows(text: str, heading: str) -> list[tuple[int, list[str]]]:
    lines = text.split("\n")
    out, inside, seen = [], False, 0
    for n, line in enumerate(lines, start=1):
        if line.startswith("## "):
            inside = line[3:].strip() == heading
            seen = 0
            continue
        if inside and line.strip().startswith("|"):
            seen += 1
            if seen > 2:
                cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
                out.append((n, cells))
    return out


def address_pattern(address: str) -> re.Pattern[str]:
    """An address of the inventory as a pattern of paths: a part in braces, after a colon, or a star is any one."""
    path = re.sub(r"^[a-z]+://[^/]+", "", address.split(",", 1)[0].strip(), flags=re.IGNORECASE)
    path = path.split("?", 1)[0].rstrip("/") or "/"
    parts = [r"[^/]+" if re.fullmatch(r"\{[^}]*\}|:\w+|\*|<[^>]*>", part) else re.escape(part)
             for part in path.split("/")]
    return re.compile("/".join(parts) if path != "/" else "/")


def sites(root: Path) -> list[dict]:
    """Each fault and note of the captured sites: {"file", "line", "says", "note"} -- a note where the walk has
    not reached somewhere yet, a fault where a capture or the inventory is not whole."""
    out: list[dict] = []
    captures = root / CAPTURES
    if not captures.is_dir():
        return out
    for inventory in sorted(captures.glob(f"*/{INVENTORY}")):
        site = inventory.parent
        name = inventory.relative_to(root).as_posix()
        text = inventory.read_text(encoding="utf-8", errors="replace")
        say = lambda file, line, words, note=False: out.append({"file": file, "line": line, "says": words,  # noqa: E731
                                                                "note": note})
        for key in SITE_SAYS:
            if not line_value(text, key):
                say(name, 0, f"the inventory does not say its {key}: a `- **{key}:**` line")
        rows = table_rows(text, "Views")
        if not rows:
            say(name, 0, "the inventory has no table under `## Views`: every view of the site in scope, a row each")
        listed: set[str] = set()
        linked: dict[str, str] = {}
        for line, row in rows:
            ref, address, _reached, capture = (row + [""] * 4)[:4]
            if not re.fullmatch(r"V\d+", ref):
                say(name, line, f"a view's ID is V and a number; this one is `{ref}`")
                continue
            if capture.lower().startswith(NOT_CAPTURED):
                if not capture[len(NOT_CAPTURED):].strip():
                    say(name, line, f"{ref} is not captured and does not say why")
                continue
            if not capture or not (site / capture).is_file():
                say(name, line, f"{ref}: its capture `{capture}` is not there: name the file, or write "
                                f"`{NOT_CAPTURED}` and why")
                continue
            listed.add(capture)
            held = (site / capture).read_text(encoding="utf-8", errors="replace")
            for target in LINK_RE.findall(held):
                linked.setdefault(target.rstrip("/") or "/", ref)
        walked = [line_value(text, "Address")] + [row[1] for _, row in rows if len(row) > 1]
        patterns = [address_pattern(a) for a in walked if a]
        for target, ref in sorted(linked.items()):
            if not any(pattern.fullmatch(target) for pattern in patterns):
                say(name, 0, f"{target}, linked from {ref}, is no view of the inventory: walk it, or list it as a "
                             f"view `{NOT_CAPTURED}` and why", True)
        for path in sorted(site.glob("V*.md")):
            file = path.relative_to(root).as_posix()
            if path.name not in listed:
                say(file, 0, "it is not in the inventory: a capture is the capture of one view of its table")
            held = path.read_text(encoding="utf-8", errors="replace")
            for key in CAPTURE_SAYS:
                if not line_value(held, key):
                    say(file, 0, f"the capture does not say its {key}: a `- **{key}:**` line")
            shots = line_value(held, "Screenshots")
            if shots and not shots.lower().startswith("none"):
                for shot in (x.strip() for x in shots.split(",")):
                    if shot and not (path.parent / shot).is_file():
                        say(file, 0, f"the screenshot `{shot}` is not there")
            if not re.search(r"^## On the page\n+\S", held, re.MULTILINE):
                say(file, 0, "the capture holds no text under `## On the page`: the view's words, one to a line")
    return out


def unaccounted(root: Path, sources: dict[str, dict]) -> list[dict]:
    """Each file of a source in reach that no line of any source's coverage covers -- by the file, a folder above it,
    or a pattern -- so that sources lying one inside another account for each other's files: what nobody says was
    read, or why not. A capture's screenshots are the capture's own."""
    rules: list[tuple[str, str]] = []                   # (a folder, as an absolute path with a closing slash; a part)
    places: dict[str, Path] = {}
    for ident, said in sources.items():
        there = source_place(root, said.get("where", ""))
        if there is None:
            continue
        places[ident] = there
        base = os.path.abspath(there if there.is_dir() else there.parent)
        rules += [(base.replace("\\", "/").rstrip("/") + "/", part_named(r.get("part", "")))
                  for r in said.get("coverage", [])]

    def covered(file: str) -> bool:
        for base, part in rules:
            if not file.startswith(base):
                continue
            rel = file[len(base):]
            if part in ("", ".") or rel == part or rel.startswith(part + "/") or fnmatch.fnmatch(rel, part):
                return True
        return False

    out, seen = [], set()
    for ident, there in places.items():
        base = os.path.abspath(there if there.is_dir() else there.parent).replace("\\", "/").rstrip("/") + "/"
        for file in [there] if there.is_file() else sorted(p for p in there.rglob("*") if p.is_file()):
            where = os.path.abspath(file).replace("\\", "/")
            if where in seen:
                continue
            seen.add(where)
            shot = file.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif") and CAPTURES in where
            if shot or STAGING in where or covered(where):
                continue
            out.append({"source": ident, "file": where[len(base):] if where.startswith(base) else file.name})
    return out
