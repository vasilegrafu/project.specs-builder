"""How the application stands up to a large specification: not part of the selftest, for it takes minutes.

    python tests/scale.py                       50,000 nodes and about 200,000 links, written to a new temporary folder
    python tests/scale.py --screens 500         a smaller one
    python tests/scale.py --keep                keep the folder, and say where it is

It writes a real specification, as files, loads and builds it as the server does, then times each question the Matrix
asks through the server's own `answer`, and the questions that hold the whole specification, so that what stands in the
way of a larger one is measured and not guessed. Nothing is written outside the temporary folder.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "app"))
import load as loading  # noqa: E402
import serve  # noqa: E402

ELEMENTS = 8                          # to a screen
CRITERIA = 4                          # to a requirement
SHOWS = 4                             # the requirements each element shows
AIM = 200                             # ms: what a click on the Matrix should take
HEAD = "| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |\n" \
       "|---|---|---|---|---|---|---|---|---|---|---|\n"


def write(root: Path, screens: int) -> None:
    requirements = max(10, screens // 3)
    data = root / "data"
    for folder in ("goals", "requirements", "screens", "flows"):
        (data / folder).mkdir(parents=True)
    (root / "prototypes" / "screens").mkdir(parents=True)
    (root / "prototypes" / "page.html").write_text("<!doctype html><title>{{title}}</title><body>{{body}}</body>\n", encoding="utf-8")
    (data / "document.md").write_text("---\nid: document\nname: A large specification\nkind: product\nstatus: draft\n---\n\n"
                                      "Written by tests/scale.py, to measure.\n", encoding="utf-8")
    (data / "goals" / "G1.md").write_text("---\nid: G1\nname: The application stands up to size\nmeasured by: a click\n"
                                          "today: none\ntarget: 200 ms\n---\n", encoding="utf-8")
    for r in range(1, requirements + 1):
        rows = "\n".join(f"- R{r}.{c} Given a thing, when it happens, then the product does it, case {c}." for c in range(1, CRITERIA + 1))
        (data / "requirements" / f"R{r}.md").write_text(
            f"---\nid: R{r}\nname: Requirement {r}\npriority: must\nserves: G1\n---\n\n"
            f"The product shall do thing {r}, as asked.\n\n## Accepted when\n\n{rows}\n", encoding="utf-8")
    for s in range(1, screens + 1):
        cells = []
        for e in range(1, ELEMENTS + 1):
            shows = ", ".join(f"R{(s * 7 + e * 11 + i * 13) % requirements + 1}" for i in range(SHOWS))
            cells.append(f"| {e} | Element {e} | region | What element {e} of screen {s} shows. |  |  |  | {shows} |  |  |  |")
        (data / "screens" / f"SC{s}.md").write_text(
            f"---\nid: SC{s}\nname: Screen {s}\nkind: page\naddress: /{s}\nwho: anyone\nreached by: a link\n---\n\n"
            f"A visitor sees screen {s}.\n\n## Elements\n\n{HEAD}" + "\n".join(cells) + "\n", encoding="utf-8")
        drawn = "".join(f'<div data-el="{e}">Element {e}</div>' for e in range(1, ELEMENTS + 1))
        (root / "prototypes" / "screens" / f"SC{s}.html").write_text(f"<h1>Screen {s}</h1>\n{drawn}\n", encoding="utf-8")
    for f in range(1, screens // 10 + 2):
        passes = ", ".join(f"SC{(f * 3 + i) % screens + 1}" for i in range(5))
        (data / "flows" / f"F{f}.md").write_text(
            f"---\nid: F{f}\nname: Flow {f}\nuser: a visitor\nserves: G1\npasses: {passes}\n---\n\nA visitor goes through flow {f}.\n",
            encoding="utf-8")


def timed(word: str, did) -> float:
    began = time.perf_counter()
    found = did()
    took = (time.perf_counter() - began) * 1000
    size = len(json.dumps(found, ensure_ascii=False)) // 1024 if found is not None else 0
    print(f"  {took:9.1f} ms  {size:7d} KB  {word}", flush=True)
    return took


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--screens", type=int, default=5000, help="screens, each with 8 elements; a third as many requirements")
    parser.add_argument("--keep", action="store_true", help="keep the folder")
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="specs-scale-"))
    try:
        began = time.perf_counter()
        write(root, args.screens)
        print(f"written in {time.perf_counter() - began:.1f} s", flush=True)
        began = time.perf_counter()
        done = loading.load(root)
        print(f"loaded in {time.perf_counter() - began:.1f} s: {len(done.nodes)} nodes, {len(done.edges)} links, "
              f"{len(done.problems)} problem(s)", flush=True)
        for file, line, message in done.problems[:8]:
            print(f"  {file}:{line} {message}")
        if done.problems:
            return 1
        began = time.perf_counter()
        spec = serve.Spec(root)
        print(f"the server started in {time.perf_counter() - began:.1f} s: it loads, builds and stamps", flush=True)
        ask = lambda path, **query: serve.answer(spec, path, {k: [str(v)] for k, v in query.items()})[1]    # noqa: E731
        print("the Matrix, each question once the server has glanced at the files:", flush=True)
        last = args.screens // 2
        small = [
            timed("the grid, first asked", lambda: ask("/api/matrix")),
            timed("the grid, held", lambda: ask("/api/matrix")),
            timed("a kind's first page", lambda: ask("/api/matrix/tree", kind="screen")),
            timed("a kind's page deep down", lambda: ask("/api/matrix/tree", kind="screen", offset=last)),
            timed("the page a node is on", lambda: ask("/api/matrix/tree", kind="screen", at=f"SC{last}")),
            timed("a node's rows", lambda: ask("/api/matrix/tree", parent="SC1")),
            timed("a node's links", lambda: ask("/api/matrix/links/SC1")),
            timed("a much linked node's links", lambda: ask("/api/matrix/links/R1")),
            timed("more of one sort", lambda: ask("/api/matrix/links/R1", way="back", rel="shows", offset=50, limit=200)),
            timed("a link", lambda: ask("/api/matrix/link", src="F1", rel="passes", dst=f"SC{3 % args.screens + 1}")),
            timed("a cell", lambda: ask("/api/matrix/cell", **{"from": "screen", "to": "requirement"})),
            timed("a cell deep down", lambda: ask("/api/matrix/cell", **{"from": "screen", "to": "requirement"}, offset=args.screens * 16)),
            timed("find", lambda: ask("/api/matrix/find", q="screen 2500")),
            timed("find, one word", lambda: ask("/api/matrix/find", q="element")),
            timed("a much linked node's links, by kind", lambda: ask("/api/matrix/links/R1", by="kind")),
            timed("a much linked node's links, narrowed", lambda: ask("/api/matrix/links/R1", q="element 3")),
            timed("a cell, narrowed", lambda: ask("/api/matrix/cell", q="element 3", **{"from": "screen", "to": "requirement"})),
            timed("a problem filter's page", lambda: ask("/api/matrix/tree", kind="requirement", problem="open")),
            timed("a path, first asked", lambda: ask("/api/matrix/path", **{"from": "F1", "to": "R1"})),
            timed("a path, the joins held", lambda: ask("/api/matrix/path", **{"from": "F1", "to": "R2"})),
            timed("a path with none", lambda: ask("/api/matrix/path", **{"from": "G1", "to": "document"})),
            timed("the Graph's map, folded", lambda: ask("/api/map")),
            timed("the Graph's map, every kind open", lambda: ask("/api/map", open="goal:60,requirement:60,screen:60,flow:60")),
            timed("focus on a much linked node", lambda: ask("/api/map/around", id="R1")),
            timed("a step of impact", lambda: ask("/api/map/stands", id="R1")),
            timed("the layers of a much linked node", lambda: ask("/api/map/layers", id="R1")),
            timed("the layers of the most linked node", lambda: ask("/api/map/layers", id="G1", steps=1)),
            timed("a card", lambda: ask("/api/card/R1")),
            timed("a kind walked far down", lambda: ask("/api/map", open="screen:24@3000")),
        ]
        print(f"  the slowest of these: {max(small):.1f} ms, against an aim of {AIM} ms", flush=True)
        print("what looks at every file, or holds the whole specification:", flush=True)
        timed("any other question: every file looked at", spec.files)
        timed("the search above the bar", lambda: ask("/api/search", q="screen 2500"))
        timed("every name", lambda: ask("/api/names"))
        timed("the summary", lambda: ask("/api/summary"))
        timed("the menu", lambda: ask("/api/menu"))
        timed("the Graph's whole graph", lambda: ask("/api/graph"))
        return 0
    finally:
        if args.keep:
            print(f"kept: {root}")
        else:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
