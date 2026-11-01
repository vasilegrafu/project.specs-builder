#!/usr/bin/env python3
"""Say what there is to build from, before anything else is read: the scout's report.

    python scripts/scout.py --plan <material> [<material> ...] [--into evidence/scout.md]
    python scripts/material_plan.py --selftest

A material is a folder or a file of code, documents or screenshots, the
folder of a site already captured, or the address of a live site. For each
it says what it is and what it holds -- the languages of its code, its
routes and sets of states, an API description and its endpoints, its
documents, its pictures, a site's views -- and then, part by part of the
specification, what can be built from all of it together: in full, in
part, or not at all, from what, and what material would make it whole.
Then the agents the reading would take, wave by wave, and how big it is.

It is the gate of the reverse-engineer mode: the user reads it and
chooses what to build before anything else is read. What no material
holds -- why the product exists, its goals, its priorities -- is never
built from material, and the report says so on every row it touches.

It reads the surface only: names, kinds and sizes of files, the routes and
states a parser finds, the endpoints of a description, and for a live site
the views `crawl.py --list` finds where Playwright is installed. It never
opens a file of data. With --into, the report is written as Markdown, as
every file of the evidence is. Standard library only.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_spec  # noqa: E402
import textfile  # noqa: E402
import scan_code  # noqa: E402
import scout  # noqa: E402

UI_SUFFIXES = {".jsx", ".tsx", ".vue", ".svelte", ".html", ".htm", ".cshtml", ".razor", ".jinja", ".j2", ".liquid"}
# A file that says a folder is a part of the code standing apart: a front end, a back end, a service.
PART_MARKERS = {"package.json", "pyproject.toml", "setup.py", "requirements.txt", "go.mod", "pom.xml", "build.gradle",
                "Cargo.toml", "Gemfile", "composer.json"}
LANGUAGE_OF = {".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".jsx": "JSX",
               ".ts": "TypeScript", ".tsx": "TSX", ".cs": "C#", ".java": "Java", ".kt": "Kotlin", ".go": "Go",
               ".rb": "Ruby", ".php": "PHP", ".rs": "Rust", ".swift": "Swift", ".vue": "Vue", ".svelte": "Svelte",
               ".sql": "SQL", ".sh": "shell", ".ps1": "PowerShell", ".html": "HTML", ".cshtml": "Razor",
               ".razor": "Razor", ".css": "CSS", ".scss": "SCSS"}
PARTS = ("Evidence", "Requirements", "Flows", "Design System", "Screens", "Prototype", "Open")


@dataclass
class Material:
    """One piece of material, and what its surface holds."""
    said: str                                    # as the user gave it
    kind: str                                    # code, documents, pictures, a site's captures, a live site
    files: int = 0
    languages: dict[str, int] = field(default_factory=dict)
    routes: int = 0
    states: int = 0
    endpoints: int = 0
    tests: int = 0
    descriptions: list[str] = field(default_factory=list)
    documents: int = 0
    pictures: int = 0
    data: int = 0
    styles: int = 0
    ui_files: int = 0
    views: int = 0
    parts: list[str] = field(default_factory=list)
    note: str = ""


def read_folder(path: Path) -> Material:
    """What a folder or a file holds, by its surface."""
    entries, _ = scout.scan(path, syntax=False)
    found = Material(path.as_posix(), "")
    found.files = len(entries)
    for entry in entries:
        suffix = Path(entry.path).suffix.lower()
        if entry.kind in ("code", "markup", "style") and suffix in LANGUAGE_OF:
            found.languages[LANGUAGE_OF[suffix]] = found.languages.get(LANGUAGE_OF[suffix], 0) + 1
        found.documents += entry.kind == "document"
        found.pictures += entry.kind == "image"
        found.data += entry.kind == "data"
        found.styles += entry.kind == "style"
        found.ui_files += suffix in UI_SUFFIXES
    root = path if path.is_dir() else path.parent
    if path.is_dir() and scout.site_inventory(path) is not None:
        found.kind = "a site's captures"
        found.views = sum(1 for e in entries if e.kind == "capture")
        found.pictures = sum(1 for p in path.rglob("*") if scout.kind_of(p) == "image")
        return found
    if sum(found.languages.values()):
        scanned = scan_code.scan(path, scan_code.Engine())
        found.routes = sum(1 for f in scanned.facts if f.name == "action.route")
        found.states = sum(1 for f in scanned.facts if f.name == "data.enum")
        found.tests = scanned.tests
        if path.is_dir():
            found.parts = parts_of(root, entries)
    endpoints, _ = api_spec.scan(path)
    found.endpoints = len(endpoints)
    found.descriptions = sorted({e.file for e in endpoints})
    found.kind = ("code" if sum(found.languages.values()) else "documents" if found.documents >= found.pictures
                  else "pictures" if found.pictures else "other files")
    return found


def parts_of(root: Path, entries: list) -> list[str]:
    """The parts of the code that stand apart, each with how many files of code it holds: the folders a project
    file marks -- a package.json, a pyproject.toml -- or, where those name fewer than two, the folders at the top
    that hold code, tests left out."""
    code = [e.path for e in entries if e.kind in ("code", "markup", "style")]
    marked = sorted({p.parent.relative_to(root).as_posix() or "." for p in root.rglob("*")
                     if p.name in PART_MARKERS and not scout.LEFT_OUT & set(p.relative_to(root).parts)})
    if len(marked) < 2:
        tops: dict[str, int] = {}
        for name in code:
            top = name.split("/", 1)[0] if "/" in name else "."
            tops[top] = tops.get(top, 0) + 1
        marked = sorted(top for top, count in tops.items()
                        if count >= 5 and top != "." and not re.search(r"(^|_)tests?$|^__", top))
    counts = {part: sum(1 for n in code if n.startswith(part + "/") or part == ".") for part in marked}
    return [f"{part} ({count} file{'' if count == 1 else 's'})" for part, count in counts.items()]


def read_site(address: str) -> Material:
    """A live site: its views in scope, counted by crawl.py where Playwright is there."""
    found = Material(address, "a live site")
    try:
        import crawl  # noqa: PLC0415
        import playwright.sync_api  # noqa: F401, PLC0415  # pyright: ignore[reportMissingImports]
    except ImportError:
        found.note = "its views are counted by the walk: Playwright for Python is not installed for crawl.py --list"
        return found
    views = crawl.walk(address, None, crawl.hosts_of(address, ""), crawl.MOST, crawl.PACE, False,
                       crawl.robots_for(address))
    found.views = sum(1 for v in views if not v.why_not)
    found.note = f"{len(views) - found.views} more not to be entered: stop points, or refused by robots.txt" \
        if len(views) > found.views else ""
    return found


def holds(m: Material) -> str:
    """What a material holds, in a line."""
    said = []
    if m.languages:
        said.append(", ".join(f"{lang} {count}" for lang, count in sorted(m.languages.items(), key=lambda i: -i[1])))
    if m.routes or m.states:
        said.append(f"{m.routes} route(s) and {m.states} set(s) of states a parser finds")
    if m.tests:
        said.append(f"{m.tests} file(s) of tests")
    if m.endpoints:
        said.append(f"an API description ({', '.join(m.descriptions)}) with {m.endpoints} endpoint(s)")
    if m.parts and len(m.parts) > 1:
        said.append(f"{len(m.parts)} parts that stand apart: {', '.join(m.parts)}")
    if m.documents:
        said.append(f"{m.documents} document(s)")
    if m.pictures:
        said.append(f"{m.pictures} picture(s)")
    if m.views:
        said.append(f"{m.views} view(s)")
    if m.data:
        said.append(f"{m.data} file(s) of data, never opened")
    if m.note:
        said.append(m.note)
    return "; ".join(said) or "nothing a scout can read"


def buildable(materials: list[Material]) -> list[list[str]]:
    """Each part of the specification: whether it can be built, from what, and what would make it whole."""
    code = [m for m in materials if m.kind == "code"]
    site = [m for m in materials if m.kind in ("a live site", "a site's captures")]
    pictures = [m for m in materials if m.pictures and m.kind != "a site's captures"]
    documents = [m for m in materials if m.documents]
    ui_code = [m for m in code if m.ui_files]
    styles = [m for m in code if m.styles]
    why = "the why -- the problem, the goals and their numbers, the priorities -- is asked of the user, always"

    def row(part: str, level: str, source: list[str], whole: str) -> list[str]:
        return [part, level, "; ".join(source) or "-", whole]

    out = [row("Evidence", "full" if materials else "none", ["every material, each with what was read of it"], "-")]
    from_req = (["code: what it does, its rules, limits and words" for _ in code[:1]]
                + ["the site: what a user meets" for _ in site[:1]]
                + ["documents: what was asked for" for _ in documents[:1]]
                + ["pictures: what a screen shows" for _ in pictures[:1]])
    level = "full" if code or site or documents else "part" if pictures else "none"
    out.append(row("Requirements", level, from_req, why if level == "full" else
                   "code, a running site or documents, for the rules behind what a screen shows; and " + why))
    flows_from = (["the site: each journey walked"] if site else []) + \
                 (["the code: routes and screens"] if ui_code else []) + (["documents: workflows"] if documents else [])
    level = "full" if site or ui_code else "part" if documents or pictures else "none"
    out.append(row("Flows", level, flows_from + (["their stories, from the users and the goals"] if flows_from else []),
                   ("" if level == "full" else "a running site, or the code of the interface, to see each step and "
                    "branch; ") + "who the users are and the goals each flow serves, from the user"))
    look = (["the site's captured styles"] if site else []) + (["the code's style sheets"] if styles else []) + \
           (["the pictures, by eye; no value is taken from a picture"] if pictures else [])
    level = "full" if site or styles else "part" if pictures else "none"
    out.append(row("Design System", level, look, "-" if level == "full" else
                   "a running site or the style sheets, for the values; a look nobody gave is asked, not invented"))
    screens = (["the site's views and states"] if site else []) + (["the code of the interface"] if ui_code else []) \
        + (["the pictures: one state of each"] if pictures else [])
    level = "full" if site or ui_code else "part" if pictures else "none"
    out.append(row("Screens", level, screens, "-" if level == "full" else
                   "a running site, to reach each state; until then each unseen state is likely, with how to find it"))
    level = "alike" if site or pictures else "grey" if ui_code else "none"
    out.append(row("Prototype", level, (["made alike to the screenshots, width by width"] if site or pictures else
                                        ["grey: the structure and words, no look"] if ui_code else []),
                   "-" if level == "alike" else "screenshots or a running site, to make it look as the product does"))
    out.append(row("Open", "full", ["everything not settled, not read or not accounted for"], "-"))
    return out


def agents(materials: list[Material]) -> list[list[str]]:
    """The agents the reading would take, wave by wave: one collector per kind of material the scope holds, the
    two synthesisers on what they merge, and the three that check (references/archaeologists.md)."""
    out = []
    for m in materials:
        if m.kind == "code":
            parts = m.parts if len(m.parts) > 1 else ["the whole"]
            out += [["Collect", "code archaeologist", f"{m.said}: {part}"] for part in parts]
            out.append(["Collect", "data archaeologist", f"{m.said}: its models, migrations, enums and seeds"])
            out.append(["Collect", "test archaeologist", f"{m.said}: its tests, fixtures and mocks"
                        + (f", {m.tests} file(s)" if m.tests else "")])
            if m.endpoints or m.routes:
                out.append(["Collect", "API archaeologist", f"{m.said}: its routes"
                            + (f" and {', '.join(m.descriptions)}" if m.descriptions else "")])
            if m.styles or m.pictures:
                out.append(["Collect", "visual archaeologist", f"{m.said}: its style sheets and assets"])
        elif m.kind == "documents":
            out.append(["Collect", "documentation archaeologist", m.said])
        elif m.kind in ("a live site", "a site's captures"):
            if m.kind == "a live site":
                out.append(["Capture", "web archaeologist, after crawl.py", m.said])
            out.append(["Collect", "visual archaeologist", f"the captures of {m.said}"])
        elif m.kind == "pictures":
            out.append(["Collect", "visual archaeologist", m.said])
        if m.kind == "code" and m.documents:
            out.append(["Collect", "documentation archaeologist", f"the documents in {m.said}"])
    screens = any(m.kind in ("a live site", "a site's captures", "pictures") or m.ui_files for m in materials)
    if screens:
        out.append(["Synthesise", "usage archaeologist", "the merged findings, the captures, the screenshots"])
    if materials:
        out.append(["Synthesise", "meaning archaeologist", "the merged findings, and the usage analysis"])
    out += [["Reconcile", "reconciler", "the disagreements the merge kept"],
            ["Investigate", "investigator", "what `spec.py open` says to investigate"],
            ["Critique", "critic", "the whole, and nothing of what was meant"]]
    return out


def table(head: list[str], rows: list[list[str]]) -> list[str]:
    cell = (lambda said: " ".join(str(said).split()).replace("|", "\\|"))
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head),
            *("| " + " | ".join(cell(c) for c in row) + " |" for row in rows)]


def depths(crew: list[list[str]]) -> list[list[str]]:
    """The three depths the user chooses between at the gate, each with the agents it starts and when it stops
    (references/archaeologists.md, The depths)."""
    collect = sum(1 for row in crew if row[0] in ("Capture", "Collect"))
    synthesise = sum(1 for row in crew if row[0] == "Synthesise")
    check = sum(1 for row in crew if row[0] in ("Reconcile", "Investigate", "Critique"))
    rounds = sum(1 for row in crew if row[0] in ("Investigate", "Critique"))
    return [["quick", f"{collect + synthesise}", "the collectors and the synthesisers; no reconciler, investigator "
                                                "or critic", "the document is written; what is not settled is listed, "
                                                             "not chased"],
            ["standard", f"{collect + synthesise + check}", "all, the investigator and the critic once",
             "the gaps above the line are settled or reported, the critic's objections answered once"],
            ["full", f"{collect + synthesise + check} to {collect + synthesise + check + 2 * rounds}",
             "all, the investigator and the critic up to three times",
             "`spec.py open` holds only what is for people, or three rounds are done"]]


def sources_of(spec: Path) -> tuple[dict[str, dict], object]:
    """The specification's sources, each with its place and its coverage, read through the application's own
    loader: what it read before."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
    import evidence                             # noqa: PLC0415
    import load as loading                      # noqa: PLC0415
    done = loading.load(spec)
    return ({i: {"where": n.fields.get("where", ""), "coverage": n.fields.get("coverage") or []}
             for i, n in done.nodes.items() if n.kind == "source"}, evidence)


def changed_since(spec: Path, materials: list[Material]) -> list[list[str]]:
    """The parts of the material that changed since the specification read them, by the print each line of a
    source's coverage carries, with the agent to start again on each: a second reading starts only those."""
    if not (spec / textfile.DOCUMENT).is_file():
        return []
    sources, evidence = sources_of(spec)
    kinds = {m.said: m.kind for m in materials}
    out = []
    for moved in evidence.moved(spec, sources):
        there = evidence.source_place(spec, sources[moved["source"]]["where"])
        kind = next((k for said, k in kinds.items() if there is not None and Path(said).resolve() == there.resolve()), "")
        agent = {"code": "the code, data and test archaeologists", "documents": "the documentation archaeologist",
                 "pictures": "the visual archaeologist", "a site's captures": "the web and visual archaeologists",
                 "a live site": "the web and visual archaeologists"}.get(kind, "the archaeologist of its kind")
        out.append([moved["source"], moved["part"].strip().strip("`"), agent])
    return out


def plan(materials: list[Material], when: str | None = None, spec: Path | None = None) -> str:
    """The scout's report: what there is, what can be built from it, what reading it would take at each depth, and,
    where the specification has read this material before, what changed since."""
    when = when or datetime.now().strftime("%Y-%m-%d")
    crew = agents(materials)
    changed = changed_since(spec, materials) if spec is not None else []
    routes = sum(m.routes for m in materials)
    views = sum(m.views for m in materials)
    endpoints = sum(m.endpoints for m in materials)
    tests = sum(m.tests for m in materials)
    documents = sum(m.documents for m in materials)
    out = ["# What there is to build from", "",
           "The scout's report: what each material holds, what of the specification can be built from all of it, "
           "and what reading it would take. Choose what to build before anything else is read.", "",
           f"- **Scouted:** {when}",
           f"- **Material:** {', '.join(m.said for m in materials)}", "",
           "## Material", "",
           *table(["Material", "Kind", "Files", "What it holds"],
                  [[m.said, m.kind, str(m.files) if m.files else "-", holds(m)] for m in materials]), "",
           "## What can be built", "",
           "Each part of the specification, and whether the material can build it: `full`, `part`, `none`; for the "
           "prototype `alike` -- made alike to how the product looks -- or `grey`.", "",
           *table(["Part", "Can be built", "From", "What would make it whole"], buildable(materials)), "",
           "## What it would take", "",
           *table(["Wave", "Agent", "Reads"], crew), "",
           f"About {routes} route(s), {endpoints} endpoint(s), {views} view(s), {tests} file(s) of tests and "
           f"{documents} document(s) to account for; {len(crew)} agent(s) in all, at most six at a time, one at a "
           f"time in the browser.", "",
           "## The depths", "",
           "How far the reading goes, chosen at the gate: the agents each depth starts, and when it stops.", "",
           *table(["Depth", "Agents", "Who runs", "Stops when"], depths(crew)), ""]
    if changed:
        out += ["## What changed since", "",
                "This specification has read this material before: the parts whose hash no longer matches what the "
                "evidence holds, and the agents to start again on each. A second reading starts only these.", "",
                *table(["Source", "Part", "Start again"], changed), ""]
    elif spec is not None and (spec / textfile.DOCUMENT).is_file():
        out += ["## What changed since", "",
                "This specification has read this material before, and no part it hashed has changed since.", ""]
    out += ["## To choose", "",
            "- What the material is to the product: `rebuild`, `extend`, `example`, `intent` or `evidence`.",
            "- Which parts of the specification to build, from the table above.",
            "- What of the material is in scope: what is left out that a reader would expect becomes a non-goal.",
            "- The depth: `quick`, `standard` or `full`, from the table above.",
            *([f"- Whether the API description -- {', '.join(sorted({d for m in materials for d in m.descriptions}))} "
               f"-- is generated by the server from its code, and so read as the product itself (`seen`), or written "
               f"by hand, a document about it (`said`)."] if any(m.descriptions for m in materials) else []),
            "- Why: what the work is for, what should be better afterwards and by what number, and who uses it.", ""]
    return "\n".join(out)


def read_all(said: list[str]) -> list[Material]:
    out = []
    for item in said:
        if item.startswith(("http://", "https://")) or item.startswith("localhost"):
            out.append(read_site(item if "://" in item else "http://" + item))
        elif Path(item).exists():
            out.append(read_folder(Path(item)))
        else:
            out.append(Material(item, "not found", note="not on this machine, and not an address"))
    return out


def run_selftest() -> int:
    bad: list[str] = []

    def expect(label: str, got: object, wanted: object) -> None:
        print(f"{'ok' if got == wanted else 'FAILED'}  {label}")
        if got != wanted:
            bad.append(f"{label}: got {got!r}, wanted {wanted!r}")

    with tempfile.TemporaryDirectory(prefix="specs-builder-plan-") as tmp:
        root = Path(tmp)
        (root / "shop/api").mkdir(parents=True)
        (root / "shop/web/src").mkdir(parents=True)
        (root / "shop/api/requirements.txt").write_text("fastapi\n", encoding="utf-8")
        (root / "shop/api/app.py").write_text('@app.get("/items/{id}")\ndef item(id: int):\n    return {}\n',
                                              encoding="utf-8")
        (root / "shop/web/package.json").write_text("{}\n", encoding="utf-8")
        (root / "shop/web/src/Page.tsx").write_text("export const Page = () => <h1>Items</h1>;\n", encoding="utf-8")
        (root / "shop/web/src/page.css").write_text(".a { color: #123456; }\n", encoding="utf-8")
        (root / "shop/customers.csv").write_text("name\nAnn\n", encoding="utf-8")
        (root / "notes").mkdir()
        (root / "notes/interviews.md").write_text("# Interviews\n", encoding="utf-8")
        (root / "shots").mkdir()
        (root / "shots/home.png").write_bytes(b"")
        shop, notes, shots = read_all([str(root / "shop"), str(root / "notes"), str(root / "shots")])
        expect("code is code", shop.kind, "code")
        expect("its parts stand apart", shop.parts, ["api (1 file)", "web (2 files)"])
        expect("its route is counted", shop.routes, 1)
        expect("its data is counted, never opened", shop.data, 1)
        expect("documents are documents", notes.kind, "documents")
        expect("pictures are pictures", shots.kind, "pictures")
        rows = {row[0]: row[1] for row in buildable([shop, notes, shots])}
        expect("from code, documents and pictures", rows, {"Evidence": "full", "Requirements": "full", "Flows": "full",
                                                           "Design System": "full",
                                                           "Screens": "full", "Prototype": "alike", "Open": "full"})
        alone = {row[0]: row[1] for row in buildable([shots])}
        expect("from pictures alone", (alone["Requirements"], alone["Design System"], alone["Prototype"]),
               ("part", "part", "alike"))
        crew = [row[1] for row in agents([shop, notes])]
        expect("a code archaeologist per part, and the API's", crew.count("code archaeologist"), 2)
        expect("the API archaeologist", "API archaeologist" in crew, True)
        expect("the data and test archaeologists, for code", ("data archaeologist" in crew, "test archaeologist" in crew),
               (True, True))
        expect("the usage archaeologist with the code's interface, and the meaning archaeologist always",
               ("usage archaeologist" in crew, "meaning archaeologist" in crew), (True, True))
        expect("no usage archaeologist for documents alone, but the meaning archaeologist",
               [row[1] for row in agents([notes]) if row[0] == "Synthesise"], ["meaning archaeologist"])
        said = plan([shop, notes, shots], "2026-10-09")
        expect("the report has its parts", all(f"## {h}" in said for h in ("Material", "What can be built",
                                                                           "What it would take", "The depths",
                                                                           "To choose")), True)
        expect("the why is asked, always", "asked of the user, always" in said, True)
        sized = {row[0]: row[1] for row in depths(agents([shop, notes, shots]))}
        collectors = sum(1 for row in agents([shop, notes, shots]) if row[0] == "Collect")
        expect("quick is the collectors and the synthesisers, standard three more, full up to four more",
               (sized["quick"], sized["standard"], sized["full"]),
               (str(collectors + 2), str(collectors + 5), f"{collectors + 5} to {collectors + 9}"))
        # a specification that read this material before: a part that changed is said, with the agent to start
        spec = root / "spec"
        (spec / "data/sources").mkdir(parents=True)
        (spec / textfile.DOCUMENT).write_text("---\nname: x\n---\n\nA shop.\n", encoding="utf-8")
        _, evidence = sources_of(spec)
        digest = evidence.print_of(root / "shop", "api/app.py")
        (spec / "data/sources/S1.md").write_text(
            f"---\nid: S1\nname: the shop's code\nwhere: {(root / 'shop').as_posix()}\n---\n\n## Coverage\n\n"
            "| Part | Read | Note | Print |\n|---|---|---|---|\n"
            f"| api/app.py | full | | {digest} |\n| web/ | full | | 000000000000 |\n| customers.csv | not read | data | |\n",
            encoding="utf-8")
        again = plan([shop], "2026-10-09", spec=spec)
        expect("the part that changed is said, and the one that did not is not",
               ("| S1 | web/ | the code, data and test archaeologists |" in again, "| S1 | api/app.py |" in again),
               (True, False))
    for message in bad:
        print("ERROR " + message)
    print(f"{'FAILED' if bad else 'PASSED'} -- {len(bad)} problem(s)")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Say what there is to build from: the scout's report.")
    parser.add_argument("material", nargs="*", help="folders, files, a site's captures, or a site's address")
    parser.add_argument("--into", type=Path, help="write the report here: evidence/scout.md of the specification")
    parser.add_argument("--selftest", action="store_true", help="check this script against material it makes")
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.material:
        parser.error("at least one material is needed unless --selftest is given")
    # the specification the report is written into, where --into names a place in one: what it read before
    spec = textfile.spec_of(args.into.resolve()) if args.into else None
    said = plan(read_all(args.material), spec=spec)
    if args.into:
        args.into.parent.mkdir(parents=True, exist_ok=True)
        args.into.write_text(said, encoding="utf-8", newline="\n")
        print(f"{args.into}: written")
    else:
        print(said, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
