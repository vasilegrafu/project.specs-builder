"""What a builder asks of a specification: where to start, in what order to build, all one thing needs, its tests,
whether the specification may be built from now -- and, once code is built, what it was built from and what moved
since.

Snapshots are kept in the code, not in the specification: `<code>/.snapshots/specs-builder/spec_<stamp>.json`,
committed with it, the newest three kept. One holds every node by what it means and what it links to, a print of every
file of the prototypes -- markup, styles, scripts, images, tokens -- and what those prototypes draw, element by element,
so that what changed since is told whole: each node new, gone or changed with its fields before and after, each file,
each element, style, token and sample value, the slices, requirements, screens and endpoints to build again, the tests
to run again, and the tests to take out.

What of the specification the code carries is read from the code: a test names the criterion it proves, `R4.2` or
`R4_2`, and code may name its requirement. Only files of a language of code are opened, the specification's own folder
left out should it lie inside. A snapshot leaves where the code is in `stamps/target.json`, so that it need not be said
again.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import api
import redrawn
import inbox
import load as loading
from load import natural
import logic
import review
from model import Model

SNAPSHOTS = ".snapshots/specs-builder"
TARGET = "stamps/target.json"
KEEP = 3
# what reading the code takes as code, leaves out as not the product's, and takes as a test; and how it names an ID
CODE_SUFFIXES = {".py", ".cs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".java", ".kt", ".go", ".rb", ".php", ".swift",
                 ".rs", ".feature", ".ps1", ".sh"}
NOT_THE_PRODUCTS = {"node_modules", ".git", ".venv", "venv", "vendor", "bin", "obj", "dist", "build", "__pycache__",
                    ".cache", ".pytest_cache", ".next", ".snapshots"}
TEST_PLACE_RE = re.compile(r"(^|/)(tests?|specs?|__tests__|e2e)/|(^|/)(test|spec)s?[_.-]|[_.-](test|spec)s?(\.[a-z0-9]+$|/)",
                           re.IGNORECASE)
TEST_NAME_RE = re.compile(r"(Tests?|Specs?)(\.[a-z0-9]+$|/)")   # CartTests.cs, Shop.Tests/, where case tells it
NAMED_RE = re.compile(r"(?<![A-Za-z0-9])R(\d+)(?:[._](\d+))?(?![0-9A-Za-z])")


def loaded(root: Path) -> loading.Load:
    done = loading.held(root)
    if done.problems:
        raise ValueError(f"{len(done.problems)} problem(s) in the data: `spec.py check` says them; nothing is built "
                         f"from a specification that does not load")
    return done


def stale_of(root: Path, done: loading.Load) -> list[dict]:
    return loading.remembered(done, "stale", lambda: review.stale(loading.grammar(), done, review.held(root)))


def label(g: dict, node: loading.Node) -> str:
    return api.label(g, node.kind, node.fields)


def overview(root: Path) -> dict:
    g = loading.grammar()
    done = loaded(root)
    counts: dict[str, int] = {}
    for n in done.nodes.values():
        counts[n.kind] = counts.get(n.kind, 0) + 1
    doc = done.nodes.get("document")
    stale = review.stale(g, done, review.held(root))
    return {"name": doc.fields.get("name") if doc else api.title(root), "kind": doc.fields.get("kind") if doc else "",
            "status": doc.fields.get("status") if doc else "", "summary": doc.fields.get("summary", "") if doc else "",
            "counts": dict(sorted(counts.items())), "links": len(done.edges),
            "open questions": sorted((i for i, n in done.nodes.items() if n.kind == "question"), key=natural),
            "stale": sorted({s["node"] for s in stale}, key=natural)}


def plan(root: Path) -> list[dict]:
    """The order to build in: the slices, from the foundation everything stands on to the last flow."""
    return Model(root, loaded(root)).slices()


def unit(root: Path, ident: str, done: loading.Load | None = None) -> dict:
    """All one node needs to be built: itself, its rows, each link both ways with what the node at its end says,
    the questions about it, and what it owes a review."""
    g = loading.grammar()
    done = done or loaded(root)
    node = done.nodes.get(ident)
    if node is None:
        raise KeyError(f"{ident}: no node has that ID")

    def said(other: str) -> dict:
        n = done.nodes[other]
        texts = [d.get("as") for d in g["kinds"][n.kind].get("sections", {}).values() if d["type"] == "text"]
        main = next((n.fields[t] for t in texts if n.fields.get(t)), n.fields.get("says") or n.fields.get("does") or "")
        return {"id": other, "kind": n.kind, "name": label(g, n), "says": " ".join(str(main).split())}

    rows = [said(e.dst) | {"fields": done.nodes[e.dst].fields} for e in done.edges if e.src == ident and e.rel == "has"]
    links = [{"rel": e.rel} | said(e.dst) for e in done.edges if e.src == ident and e.rel != "has"]
    back = [{"rel": g["relations"][e.rel].get("back", e.rel)} | said(e.src) for e in done.edges
            if e.dst == ident and e.rel != "has"]
    for row in [r["id"] for r in rows]:                 # what its rows link to belongs to it too
        links += [{"rel": e.rel, "from": row} | said(e.dst) for e in done.edges if e.src == row and e.rel != "has"]
    questions = sorted({l["id"] for l in links + back if l["kind"] == "question"}, key=natural)
    stale = [s for s in stale_of(root, done) if s["node"] in {ident, *(r["id"] for r in rows)}]
    return {"id": ident, "kind": node.kind, "name": label(g, node), "file": node.file, "fields": node.fields,
            "rows": sorted(rows, key=lambda r: natural(r["id"])), "links": links, "back": back,
            "questions": [said(q) for q in questions], "stale": stale}


def tests(root: Path, ident: str | None = None) -> list[dict]:
    """The acceptance criteria, as tests: of one requirement, or of all of them, in the order of the plan."""
    done = loaded(root)
    wanted = [ident] if ident and ident != "all" else Model(root, done).order()
    if ident and ident != "all" and (ident not in done.nodes or done.nodes[ident].kind != "requirement"):
        raise KeyError(f"{ident}: no requirement has that ID")
    out = []
    for req in wanted:
        for n in sorted((n for n in done.nodes.values() if n.parent == req and n.kind == "criterion"),
                        key=lambda n: natural(n.id)):
            out.append({"id": n.id, "requirement": req, "says": n.fields.get("says", "")})
    return out


def gherkin(test: dict) -> str:
    """A criterion as a scenario: Given, When, Then, split where it says them."""
    says = " ".join(test["says"].split())
    parts = re.split(r",?\s+(?=(?:when|then|and)\b)", says, flags=re.I)
    lines = [f"Scenario: {test['id']}"]
    for part in parts:
        word, _, rest = part.partition(" ")
        lines.append(f"  {word.capitalize()} {rest}" if word.lower() in ("given", "when", "then", "and") else f"  {part}")
    return "\n".join(lines)


def verify(root: Path) -> tuple[bool, list[str]]:
    """Whether the specification may be built from now: it loads clean and nothing in it is stale. Open questions
    are said; they do not stop a build, but whoever builds names them."""
    done = loading.held(root)
    said = [f"{f}:{n}: {m}" if n else f"{f}: {m}" for f, n, m in done.problems]
    if done.problems:
        return False, said + [f"{len(done.problems)} problem(s): fix them before building"]
    stale = stale_of(root, done)
    for s in stale:
        said.append(f"stale: {s['node']} stands on {s['on']}, which changed since ({s['link']})")
    for a in inbox.read(root):
        said.append(f"asked, waiting for the keeper: #{a['no']} about {', '.join(a['about']) or 'nothing named'} -- "
                    f"build what does not depend on it")
    questions = [i for i, n in done.nodes.items() if n.kind == "question"]
    if questions:
        said.append(f"open: {', '.join(sorted(questions, key=natural))} -- name them where what you build stands on them")
    ok = not stale
    said.append("ready to build from" if ok else f"{len({s['node'] for s in stale})} node(s) stale: they are "
                                                 f"confirmed, or changed, before building")
    return ok, said


def prints_of(root: Path) -> dict[str, str]:
    """A print of every file of the prototypes: what the nodes do not hold, told file by file."""
    place = root / "prototypes"
    if not place.is_dir():
        return {}
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            for p in sorted(place.rglob("*")) if p.is_file()}


def snapshot(root: Path, target: Path, keep: int = KEEP) -> Path:
    """What the code in `target` is built from, written into it: every node, every prototype file."""
    g = loading.grammar()
    done = loaded(root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")[:-4] + "Z"
    place = target / SNAPSHOTS
    place.mkdir(parents=True, exist_ok=True)
    held = {"taken": stamp, "spec": api.title(root), "nodes": logic.summary_of(g, done), "files": prints_of(root),
            "drawn": redrawn.drawn_of(Model(root, done))}
    path = place / f"spec_{stamp}.json"
    path.write_text(json.dumps(held, ensure_ascii=False, indent=0, sort_keys=True) + "\n", encoding="utf-8",
                    newline="\n")
    if keep > 0:
        for old in snapshots(target)[:-keep]:
            old.unlink()
    remember(root, target)
    return path


def remember(root: Path, target: Path) -> None:
    """Where the code is, from the specification's folder where a path reaches it from there."""
    try:
        where = os.path.relpath(target.resolve(), root.resolve())
    except ValueError:                                  # another drive
        where = str(target.resolve())
    (root / TARGET).parent.mkdir(exist_ok=True)
    (root / TARGET).write_text(json.dumps({"target": Path(where).as_posix()}, indent=1) + "\n", encoding="utf-8",
                               newline="\n")


def built_in(root: Path, target: Path | None = None) -> Path:
    """The folder of the code built from the specification: the one given, or the one the last snapshot left."""
    if target is None:
        try:
            target = root / json.loads((root / TARGET).read_text(encoding="utf-8"))["target"]
        except (OSError, ValueError, KeyError):
            raise FileNotFoundError("no code is known to be built from it: say --target <code>, or take a snapshot, "
                                    "`spec.py snapshot --target <code>`, and it is remembered") from None
    if not target.is_dir():
        raise FileNotFoundError(f"{target}: there is no such folder of code")
    if target.resolve() == root.resolve():
        raise FileNotFoundError(f"{target} is the specification itself: --target is the folder of the code built from it")
    return target.resolve()


def is_test(relative: str) -> bool:
    return (relative.endswith(".feature") or TEST_PLACE_RE.search(relative) is not None
            or TEST_NAME_RE.search(relative) is not None)


def names_in(root: Path, where: Path) -> dict:
    """Each ID the code under `where` names, with the files of its tests and of the rest that name it, and how many of
    each were read. A criterion named names its requirement too."""
    out = {"tests": {}, "code": {}, "tests read": 0, "code read": 0}
    spec = root.resolve()
    for folder, below, files in os.walk(where):
        below[:] = sorted(d for d in below if d not in NOT_THE_PRODUCTS and Path(folder, d).resolve() != spec)
        for name in sorted(files):
            path = Path(folder, name)
            if path.suffix.lower() not in CODE_SUFFIXES:
                continue
            relative = path.relative_to(where).as_posix()
            place = "tests" if is_test(relative) else "code"
            out[f"{place} read"] += 1
            for requirement, case in NAMED_RE.findall(path.read_text(encoding="utf-8", errors="replace")):
                for ident in (f"R{requirement}", f"R{requirement}.{case}" if case else ""):
                    held = out[place].setdefault(ident, []) if ident else []
                    if relative not in held:
                        held.append(relative)
    return out


def named(root: Path, ident: str, target: Path | None = None) -> dict | None:
    """The files of the code that name one requirement or criterion: nothing where no code is known."""
    try:
        read = names_in(root, built_in(root, target))
    except FileNotFoundError:
        if target is not None:
            raise
        return None
    return {"tests": read["tests"].get(ident, []), "code": read["code"].get(ident, [])}


def coverage(root: Path, target: Path | None = None) -> dict:
    """What of the specification the code carries: each requirement with its criteria, the tests that name each, and
    the rest of the code that names it; the criteria no test names; and the IDs the code names that the specification
    has not. Whole when a test names every criterion of every `must` and `should`."""
    where = built_in(root, target)
    done = loaded(root)
    read = names_in(root, where)
    tests, code = read["tests"], read["code"]
    rows = []
    for node in sorted((n for n in done.nodes.values() if n.kind == "requirement"), key=lambda n: natural(n.id)):
        criteria = sorted((n.id for n in done.nodes.values() if n.parent == node.id and n.kind == "criterion"), key=natural)
        rows.append({"id": node.id, "name": node.fields.get("name", ""), "priority": node.fields.get("priority", ""),
                     "criteria": [{"id": c, "tests": tests.get(c, [])} for c in criteria],
                     "untested": [c for c in criteria if c not in tests],
                     "tests": tests.get(node.id, []), "code": code.get(node.id, [])})
    counted = [r for r in rows if r["priority"] != "wont"]
    return {"target": where.as_posix(), "tests read": read["tests read"], "code read": read["code read"],
            "requirements": rows,
            "no test": [r["id"] for r in counted if not r["tests"]],
            "untested": [c for r in counted for c in r["untested"]],
            "unknown": [{"id": i, "files": tests.get(i, []) + code.get(i, [])}
                        for i in sorted((set(tests) | set(code)) - set(done.nodes), key=natural)],
            "whole": not any(r["untested"] for r in counted if r["priority"] in ("must", "should"))}


def built(root: Path) -> dict:
    """What the application shows of the code: its coverage, or why there is none to show."""
    try:
        return coverage(root)
    except FileNotFoundError as none:
        return {"none": str(none)}


def snapshots(target: Path) -> list[Path]:
    place = target / SNAPSHOTS
    return sorted(place.glob("spec_*.json")) if place.is_dir() else []


def told(change: dict) -> str:
    """One node's change, in a line or a few."""
    head = f"  {change['id']} {change['change']}"
    out = [head]
    for key, (was, now) in (change.get("fields") or {}).items() if change["change"] == "changed" else []:
        if isinstance(was, list) or isinstance(now, list):      # a table: the lines it lost and gained
            line = lambda r: " | ".join(str(v) for v in r.values()) if isinstance(r, dict) else str(r)  # noqa: E731
            before, after = [line(r) for r in was or []], [line(r) for r in now or []]
            out.append(f"      {key}:")
            out += [f"        - {r}" for r in before if r not in after]
            out += [f"        + {r}" for r in after if r not in before]
            continue
        out.append(f"      {key}: {review.moved(was, now)}")
    for word in ("tied", "untied"):
        if change.get(word):
            out.append(f"      {word}: {', '.join(change[word])}")
    return "\n".join(out)


def kept(target: Path, name: str | None = None) -> tuple[Path, dict]:
    """A snapshot by what its name holds, or the newest: its file and what it holds."""
    taken = snapshots(target)
    if name:
        taken = [p for p in taken if name in p.name]
    if not taken:
        raise FileNotFoundError(f"{target}: no snapshot" + (f" names {name}" if name else "") +
                                " -- `spec.py snapshot --target` records what the code is built from")
    return taken[-1], json.loads(taken[-1].read_text(encoding="utf-8"))


def changed(root: Path, target: Path, since: str | None = None, until: str | None = None) -> dict:
    """What moved since a snapshot -- the newest, or the one `since` names -- beside the specification now, or beside a
    later snapshot `until` names, and what to build and test again."""
    if until:
        later, then = kept(target, until)
        earlier = [p for p in snapshots(target) if p.name < later.name and (not since or since in p.name)]
        if not earlier:
            raise FileNotFoundError(f"{target}: no snapshot before {until}" + (f" names {since}" if since else ""))
        was = json.loads(earlier[-1].read_text(encoding="utf-8"))
    else:
        then, was = None, kept(target, since)[1]
    g = loading.grammar()
    done = loaded(root)
    model = Model(root, done)
    now_nodes = then["nodes"] if then else logic.summary_of(g, done)
    changes = logic.compare(was["nodes"], now_nodes)
    now_files, was_files = then.get("files", {}) if then else prints_of(root), was.get("files", {})
    files = {"new": sorted(set(now_files) - set(was_files)), "gone": sorted(set(was_files) - set(now_files)),
             "changed": sorted(k for k in set(now_files) & set(was_files) if now_files[k] != was_files[k])}
    kind_of = {i: n["kind"] for i, n in {**was["nodes"], **now_nodes}.items()}
    parent = lambda i: i.rsplit(".", 1)[0] if "." in i and kind_of.get(i) in ("criterion", "element", "part", "state") else i  # noqa: E731
    touched = {c["id"] for c in changes}
    again = {"requirements": set(), "screens": set(), "endpoints": set(), "components": set()}
    for ident in touched:
        top = parent(ident)
        kind = kind_of.get(top)
        if kind == "requirement" and top in now_nodes:
            again["requirements"].add(top)
        elif kind == "screen" and top in now_nodes:
            again["screens"].add(top)
        elif kind == "endpoint" and top in now_nodes:
            again["endpoints"].add(top)
        elif kind == "component" and top in now_nodes:
            again["components"].add(top)
    for path in files["new"] + files["changed"]:
        found = re.search(r"prototypes/(screens|components)/((?:SC|C)\d+)\.html$", path)
        if found:
            again["screens" if found.group(1) == "screens" else "components"].add(found.group(2))
    for c in changes:                                   # a requirement changed reaches what shows it
        if kind_of.get(c["id"]) == "requirement" and c["id"] in now_nodes:
            for e in done.edges:
                if e.rel == "shows" and e.dst == c["id"]:
                    top = parent(e.src)
                    again[{"screen": "screens", "endpoint": "endpoints", "component": "components"}.get(
                        kind_of.get(top), "screens")].add(top)
    run = sorted((c["id"] for c in changes if kind_of.get(c["id"]) == "criterion" and c["change"] in ("added", "changed")),
                 key=natural)
    remove = sorted((c["id"] for c in changes if kind_of.get(c["id"]) == "criterion" and c["change"] == "removed"),
                    key=natural)
    now_drawn = (then.get("drawn") if then else redrawn.drawn_of(model))
    moved = redrawn.compare(was["drawn"], now_drawn) if "drawn" in was and now_drawn is not None else None
    if moved:
        again["screens"] |= set(moved["screens"]) & set(now_nodes)
    reached = redrawn.reached_by(moved, now_drawn) if moved else []
    build_again = {k: sorted(v, key=natural) for k, v in again.items() if v}
    named_again = {*touched, *(i for v in again.values() for i in v), *(parent(i) for i in touched)}
    return {"since": was["taken"], "until": then["taken"] if then else "now", "changes": changes, "files": files,
            "build again": build_again, "tests to run again": run, "tests to remove": remove, "drawn": moved,
            "slices": [p["id"] for p in model.slices() if named_again & {*p["nodes"], *p["requirements"]}],
            "ui tests": build_again.get("screens", []), "screens reached": [s for s in reached if s not in build_again.get("screens", [])]}
