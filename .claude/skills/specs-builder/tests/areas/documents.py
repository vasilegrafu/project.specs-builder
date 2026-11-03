"""The documents: every command the manual and the tutorial write runs, and every number they tell is true."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from support import loading, SKILL


def spec_overview(root: Path) -> str:
    """How many nodes a specification holds, as the check says it."""
    return subprocess.run([sys.executable, "-B", "app/spec.py", "check"], cwd=root, capture_output=True, text=True, encoding="utf-8", check=False).stdout.replace(" node(s)", " nodes")


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """README.md, SETUP.md and the pages of user-manual/ held to what is true: the manual's worked example run, command by
    command, on a new specification; every command and operation they name a real one; every link in them leading somewhere."""
    import html
    import shlex
    import subprocess

    checks = []

    def bare(markup: str) -> str:
        return html.unescape(re.sub(r"<[^>]+>", "", markup))

    def blocks(mark: str) -> list[str]:
        return [bare(b) for b in re.findall(rf"<!-- {re.escape(mark)} -->\s*<pre[^>]*>(.*?)</pre>", pages, re.S)]

    held = {f"user-manual/{p.name}": p.read_text(encoding="utf-8") for p in sorted((SKILL / "user-manual").glob("*.html"))}
    pages = "\n".join(held.values())
    manual = bare(pages)
    said = {**{n: (SKILL / n).read_text(encoding="utf-8") for n in ("README.md", "SETUP.md")}, **{n: bare(p) for n, p in held.items()}}
    root = tmp / "first-spec"
    made = subprocess.run([sys.executable, str(SKILL / "scripts/new_spec.py"), str(root), "--name", "Invoices", "--kind",
                           "application", "--summary", "Customers take an invoice out of the portal as a PDF."],
                          capture_output=True, text=True, check=False)
    (root / "first.txt").write_text(blocks("first.txt")[0], encoding="utf-8")
    steps = [line for block in blocks("walkthrough") for line in block.strip().splitlines()]
    failed = [] if made.returncode == 0 else [f"new_spec: {made.stderr[-200:]}"]
    last = ""
    for step in steps:
        words, _, note = step.partition("  # ")
        if "<print>" in words:                              # the print the step before showed beside the node
            ident = shlex.split(words)[shlex.split(words).index("confirm") + 1]
            found = re.search(rf"do confirm {re.escape(ident)} ([0-9a-f]+)", last)
            words = words.replace("<print>", found.group(1) if found else "none")
        done = subprocess.run([sys.executable, *shlex.split(words)[1:]], cwd=root, capture_output=True, text=True, check=False)
        last = done.stdout
        if done.returncode != (1 if note.startswith("exits 1") else 0):
            failed.append(f"{step}: {(done.stdout + done.stderr).strip()[-160:]}")
    checks.append((f"the manual's worked example works, every command as it is written{': ' + '; '.join(failed) if failed else ''}",
                   len(steps) >= 12 and not failed and (root / "export/invoices.html").is_file()))
    helped = subprocess.run([sys.executable, str(SKILL / "app/spec.py"), "--help"], capture_output=True, text=True, check=False).stdout
    known = set(re.search(r"\{([a-z,]+)\}", helped).group(1).split(","))
    named = {w for text in said.values() for w in re.findall(r"app/spec\.py ([a-z]+)", text)}
    first_cells = lambda part: set(re.findall(r"<tr>\s*<td><code>([a-z-]+)", part))  # noqa: E731
    named |= first_cells(re.search(r'id="checking-and-reading"(.*?)id="changing-with-do"', pages, re.S).group(1))
    ways = first_cells(re.search(r'id="changing-with-do"(.*?)id="reading-material"', pages, re.S).group(1))
    logic_text = (SKILL / "app/logic.py").read_text(encoding="utf-8") + (SKILL / "app/edit.py").read_text(encoding="utf-8")
    checks.append((f"every command the documents name is one the command line has{': ' + ', '.join(sorted((named - known) - {'do'})) if (named - known) - {'do'} else ''}",
                   len(named) >= 12 and not (named - known) - {"do"}))
    # the running story of the manual, on a copy of Voltline: every command as it is written, and every number it tells
    six = tmp / "five-to-six"
    shutil.copytree(clean, six)
    (six / "six.txt").write_text(blocks("six.txt")[0], encoding="utf-8")

    def spec(*said_words: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", "app/spec.py", *said_words], cwd=six, capture_output=True, text=True, encoding="utf-8", check=False)

    counts, wrong = [], []
    for step in [line for block in blocks("change") for line in block.strip().splitlines()]:
        line, _, note = step.partition("  # ")
        done = subprocess.run([sys.executable, "-B", *shlex.split(line)[1:]], cwd=six, capture_output=True, text=True, encoding="utf-8", check=False)
        if done.returncode != (1 if note.startswith("exits 1") else 0):
            wrong.append(f"{line[:60]}: {(done.stdout + done.stderr).strip()[-120:]}")
        counts += [int(n) for n in re.findall(r"(\d+) node\(s\) stale", done.stdout) + re.findall(r"stale at once if it changes \((\d+)\)", done.stdout)]
    owed = spec("stale").stdout
    counts.append(int(re.search(r"(\d+) node\(s\) stale", owed).group(1)))
    for ident, shown in sorted(set(re.findall(r"do confirm (\S+) ([0-9a-f]+)", owed))):
        spec("do", "confirm", ident, shown)
    drawn = re.search(r"prototypes to look at[^:]*: (.+)", spec("ready").stdout)
    looked = drawn.group(1).split(", ") if drawn else []
    for name in ("SC3", "SC5"):
        path = six / f"prototypes/screens/{name}.html"
        path.write_text(path.read_text(encoding="utf-8").replace('max="5"', 'max="6"'), encoding="utf-8", newline="\n")
    for ident in sorted(set(looked) - {"SC3", "SC5"}):
        spec("do", "confirm-drawn", ident)
    agreed = spec("do", "set", "document", "status", "agreed", "--because", "Six of a product, read through")
    wrong += [agreed.stderr.strip()[:400]] if agreed.returncode else []
    checks.append((f"the manual's change from five to six goes as it says: 8, then 15, then 27 stale, six prototypes, and agreed again{': ' + '; '.join(wrong) if wrong else ''}",
                   not wrong and counts == [8, 8, 15, 27] and len(looked) == 6 and {"SC3", "SC5"} <= set(looked) and agreed.returncode == 0))
    # the tutorial's story, on a copy of the bakery: what it says comes back
    baked = tmp / "two-to-three"
    shutil.copytree(SKILL / "examples/bakery/specs", baked)

    def bake(*said_words: str) -> str:
        done = subprocess.run([sys.executable, "-B", "app/spec.py", *said_words], cwd=baked, capture_output=True, text=True, encoding="utf-8", check=False)
        return done.stdout + done.stderr

    bake("do", "set", "document", "status", "draft")
    kept = bake("do", "remove", "R6")
    reach = bake("impact", "B1")
    bake("do", "set", "B1", "says", "An order's pick-up day is at least three days after the day the order is placed.")
    one = bake("stale")
    bake("do", "set", "R5", "statement", "The website shall accept a pick-up day only if the bakery is open on it and it is at least three days after the order is placed.")
    two = bake("stale")
    tutorial = "".join(p.read_text(encoding="utf-8") for p in (SKILL / "tutorial").glob("*.html"))
    checks.append(("the tutorial's bakery goes as it says: R6 is kept, B1 reaches four, then four and six go stale, and its numbers are the example's",
                   "refused: R6 is linked from" in kept and "stale at once if it changes (4)" in reach and "4 node(s) stale" in one and "6 node(s) stale" in two
                   and "186 nodes" in spec_overview(SKILL / "examples/bakery/specs") and all(w in tutorial for w in ("186", "466", "157 values"))))
    every = [c for c in known if c not in ("build",) and f"<code>{c}" not in pages and f"spec.py {c}" not in manual]
    checks.append((f"the manual says every command there is{': ' + ', '.join(sorted(every)) if every else ''}", not every))
    checks.append(("every operation the manual lists is one the logic takes",
                   len(ways) >= 10 and all(f'"{w}"' in logic_text for w in ways)))
    gone = []

    def leads(name: str, doc: str, anchor: str, here: Path, text: str) -> None:
        """A link in `name`, from the folder `here`, to `doc` -- the page itself, if none -- and an anchor in it."""
        path = (here / doc).resolve() if doc else None
        if path and not path.is_file():
            gone.append(f"{name}: {doc}")
        if not anchor or (path and not path.is_file()):
            return
        heads = path.read_text(encoding="utf-8") if path else text
        if anchor not in set(re.findall(r'\bid="([^"]+)"', heads)) | {
                re.sub(r"[^a-z0-9 -]", "", h.lower()).strip().replace(" ", "-") for h in re.findall(r"^#+ (.+)$", heads, re.M)}:
            gone.append(f"{name}: {doc}#{anchor}")

    for name in ("README.md", "SETUP.md"):
        for doc, anchor in re.findall(r"\]\(([^)#:]*)(?:#([a-z0-9-]+))?\)", said[name]):
            leads(name, doc, anchor, SKILL, said[name])
    entered = (*(f"tutorial/{p.name}" for p in (SKILL / "tutorial").glob("*.html")), "USER-MANUAL.html", "TUTORIAL.html")
    for name, page in {**held, **{n: (SKILL / n).read_text(encoding="utf-8") for n in entered}}.items():
        for doc, anchor in re.findall(r'(?:href|src)="([^"#:]*)(?:#([^"]*))?"', page):
            leads(name, doc, anchor, (SKILL / name).parent, page)
    checks.append((f"every link in the documents leads somewhere{': ' + ', '.join(gone) if gone else ''}", not gone))
    checks.append(("the documents are told in the application's words: the bar's buttons and the words of the ladder are there",
                   all(w in manual for w in ("Export", "What is built", "What is open", "On this page", "Every screen drawn", "Around", "Impact", "Layers", "Matrix"))
                   and all(f"<code>{w}</code>" in pages for w in loading.grammar()["choices"]["confidence"])))
    return checks
