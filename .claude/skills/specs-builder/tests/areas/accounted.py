"""What a specification says, held to what it must say: each shortfall planted and told, none of them refusing a change, all of them
holding an agreement; the gaps a review reads; shared pieces; what moved since it was agreed; what it lets people do; its README."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from support import SKILL, add, edit, loading, remove

SC3, P3, A1, F1, R4 = "data/screens/SC3.md", "prototypes/screens/SC3.html", "data/endpoints/A1.md", "data/flows/F1.md", "data/requirements/R4.md"
MAIN = '<main data-prototype="SC3">'
FOOTER = "prototypes/shared/C13.html"
M, S = re.MULTILINE, re.DOTALL
EXAMPLES = ("bakery", "cart", "clinic", "parcels", "shop", "stock-sync", "vat")

# Each seed: what it plants, the file, what to find, what to put in its place, the flags, and words of what must be told.
SEEDS = [
    ("a state its kind likely has, left out", SC3, r"^\| Loading \|.*\n", "", M, "likely has the state `loading`"),
    ("a behaviour left out", SC3, r"^\| Hover \|.*\n", "", M, "has no `hover` line"),
    ("observed, and seen in nothing", SC3, r"(\| Few-left \| observed \|[^|]*\|) E16 \|", r"\1  |", 0, "is observed and names nothing"),
    ("likely, with no way to find out", SC3, r"(\| Error \| likely \|  \|  \|) [^|]*\|", r"\1  |", 0, "is likely and does not say how"),
    ("n/a, with no reason", SC3, r"\| Unauthorized \| n/a \| [^|]*\|", "| Unauthorized | n/a |  |", 0, "is n/a and does not say why"),
    ("a status that is no status", SC3, r"\| Few-left \| observed", "| Few-left | glimpsed", 0, "one of observed"),
    ("a state that says nothing of what it shows", SC3, r"(\| Few-left \| observed \|) [^|]*\|", r"\1  |", 0, "says nothing of what it shows"),
    ("a screenshot that is not there", SC3, r"(\| Few-left \| observed \|) ", r"\1 Seen in evidence/captures/site/shots/nothing.jpg. ", 0, "names the screenshot"),
    ("a screen of no kind", SC3, r"^kind: detail\n", "", M, "says no kind"),
    ("a screen with no transitions", SC3, r"## Transitions.*?(?=## Variants)", "", S, "has no Transitions"),
    ("a transition from no state", SC3, r"\| normal \| Add to cart is selected \|", "| nowhere | Add to cart is selected |", 0, "goes from `nowhere`"),
    ("a transition to no state", SC3, r"\| The stock runs out \| out-of-stock \|", "| The stock runs out | elsewhere |", 0, "goes to `elsewhere`"),
    ("a transition with no event", SC3, r"\| normal \| Add to cart is selected \|", "| normal |  |", 0, "says no event"),
    ("a transition standing on nothing", SC3, r"\| SC5 \| SC5 \| R4 \| E14 \|", "| SC5 | SC5 |  |  |", 0, "names neither the requirement"),
    ("a layout fixed by nothing", SC3, r"Quantity first \| E13 \|", "Quantity first | by eye |", 0, "what fixes"),
    ("a layout row short of a cell", SC3, r"on one line, Quantity first", "", 0, "needs all three"),
    ("a surface said twice", "data/endpoints/A2.md", r"^surface: .*$", "surface: GET /api/v1/products", M, "has the surface of A1"),
    ("an endpoint that does not say who may call it", A1, r"## Who may call.*?(?=## )", "", S, "who may call it"),
    ("an endpoint that does not say what it answers", A1, r"## Answers.*?(?=## )", "", S, "what it answers"),
    ("an endpoint standing on no requirement", A1, r"^shows: .*\n", "", M, "stands on no requirement"),
    ("a target with no number", "data/goals/G1.md", r"^target: .*$", "target: fewer than now", M, "target has no number"),
    ("a today with no number", "data/goals/G1.md", r"^today: .*$", "today: some", M, "today has no number"),
    ("a wont with no reason", "data/requirements/R15.md", r"## Why.*?(?=## |\Z)", "", S, "is a wont and does not say why"),
    ("a criterion that is no scenario", R4, r"- R4\.1 Given .*", "- R4.1 It works", 0, "a criterion is"),
    ("a decision with nothing turned down", "data/decisions/D1.md", r"## Instead of.*?(?=## |\Z)", "", S, "does not say `## Instead of`"),
    ("a rule that governs nothing", "data/rules/B1.md", r"^applies to: .*\n", "", M, "governs no entity"),
    ("a flow with no steps", F1, r"## Steps.*?(?=## |\Z)", "", S, "has no steps"),
    ("a document with no problem", "data/document.md", r"## Problem.*?(?=## )", "", S, "under `## Problem`"),
    ("a tag left open", P3, MAIN, MAIN + "<div>", 0, "is still open"),
    ("an id used twice", P3, MAIN, MAIN + '<span id="q"></span>', 0, "is used twice"),
    ("an image with nothing said of it", P3, MAIN, MAIN + '<img src="x.png" data-el="10">', 0, "image without alt"),
    ("styles of its own", P3, MAIN, MAIN + '<p style="color:red" data-el="10">x</p>', 0, "carries styles of its own"),
    ("a script of its own", P3, MAIN, MAIN + "<script>1</script>", 0, "a script written in the prototype"),
    ("a handler of its own", P3, MAIN, MAIN + '<button data-el="10" onclick="x()">x</button>', 0, "onclick attribute"),
    ("a bare ampersand", P3, MAIN, MAIN + '<p data-el="10">a & b</p>', 0, "a bare &"),
    ("something shown with no anchor", P3, MAIN, MAIN + "<p>A line nobody numbered</p>", 0, "with no anchor"),
    ("a state drawn that is not listed", P3, MAIN, MAIN + '<p data-el="10" data-when="sold">x</p>', 0, "shows the state `sold`"),
    ("a link the row does not say", P3, MAIN, MAIN + '<a href="SC9.html" data-el="10">x</a>', 0, "leads to SC9 in the prototype"),
    ("a link to no screen", P3, MAIN, MAIN + '<a href="SC99.html" data-el="10">x</a>', 0, "no screen has that ID"),
    ("a prototype that names another screen", P3, MAIN, '<main data-prototype="SC4">', 0, "whose prototype it is"),
    ("reached by a screen that is not there", SC3, r"on SC1, SC2 and SC4", "on SC1, SC2 and SC99", 0, "is reached by SC99"),
]


def plant(root: Path, rel: str, pattern: str, new: str, flags: int) -> str:
    """The file with one thing changed; what it held comes back to put it right."""
    path = root / rel
    held = path.read_text(encoding="utf-8")
    if pattern == MAIN:
        changed = held.replace(MAIN, new, 1)
    else:
        changed = re.sub(pattern, new, held, count=1, flags=flags)
    if changed == held:
        raise AssertionError(f"the seed for {rel} finds no {pattern!r}")
    path.write_text(changed, encoding="utf-8", newline="\n")
    return held


def spec(root: Path, *words: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SKILL / "app/spec.py"), *words, "--spec", str(root)], capture_output=True, text=True, encoding="utf-8")


def ids_of(items: list[dict]) -> list[str]:
    return [n["id"] for n in items]


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    import api
    import content
    import export as exporting
    import finish
    import logic
    import review
    import shared

    g = loading.grammar()
    root = tmp / "accounted"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")

    def faults() -> list[str]:
        return [f["says"] for f in content.faults(g, loading.load(root))]

    checks = [("the example falls short of nothing", not faults())]
    missed = []
    for title, rel, pattern, new, flags, words in SEEDS:
        held = plant(root, rel, pattern, new, flags)
        done = loading.load(root)
        if done.problems or not any(words in said for said in faults()):
            missed.append(f"{title}: {done.problems[:1] or faults()[:2]}")
        (root / rel).write_text(held, encoding="utf-8", newline="\n")
    checks.append((f"each shortfall planted is told, and none stops the data loading: {missed or len(SEEDS)}", not missed))
    checks.append(("taken out again, nothing is told", not faults()))
    checks.append(("a component's drawing shows a link that leads nowhere; a screen's may not",
                   not content.strict('<a class="x">y</a>', links=False) and bool(content.strict('<a class="x">y</a>'))))
    held = plant(root, P3, MAIN, MAIN + '<svg aria-hidden="true"></svg>', 0)
    checks.append(("what no reader meets needs no anchor", not faults()))
    (root / P3).write_text(held, encoding="utf-8", newline="\n")

    # what is short of the content holds an agreement, and refuses nothing else
    held = plant(root, "data/goals/G1.md", r"^target: .*$", "target: fewer than now", M)
    reasons = finish.ready(g, loading.load(root), review.held(root))
    checks.append(("ready says where the content falls short", any("falls short" in r and "G1" in r for r in reasons)))
    logic.apply(root, [["set", "G1", "name", "Orders on the site, not by phone"]], who="selftest")
    refused = ""
    try:
        logic.apply(root, [["set", "document", "status", "agreed"]], who="selftest")
    except logic.Refused as wrong:
        refused = str(wrong)
    checks.append(("a change goes through while the content falls short, and an agreement does not", "falls short" in refused))
    told = finish.opened(g, loading.load(root), review.held(root))
    checks.append(("open holds the faults and the gaps", any(f["id"] == "G1" for f in told["faults"])
                   and {"rules unenforced", "in no story", "read in part"} <= set(told["gaps"])))

    # what is added through the logic, and so what is listed that nothing had said
    second = tmp / "added"
    shutil.copytree(clean, second)
    edit(second, "data/document.md", "status: agreed", "status: draft")
    logic.apply(second, [["add-row", "SC3", "name=A note", "is=text", "does=Says a thing"],
                         ["add", "requirement", "Keep a wish list", "priority=must", "serves=G2", "from=S2, the cart",
                          "statement=When a customer selects Save, the shop shall keep the product in their wish list."],
                         ["add-row", "$2", "says=Given a signed-in customer on a product, when Save is selected, then it is kept."],
                         ["add", "rule", "Never on a Sunday", "says=Nothing is sent on a Sunday.", "applies to=N2"],
                         ["add", "question", "Who knows", "question=Who knows?", "answers=investigate"],
                         ["tie", "SC3.10", "leads to", "SC9"]], who="selftest")
    done = loading.load(second)
    said = [f["says"] for f in content.faults(g, done)]
    gaps = content.gaps(done)
    wish = next(n.id for n in done.nodes.values() if n.fields.get("name") == "Keep a wish list")
    rule = next(n.id for n in done.nodes.values() if n.fields.get("name") == "Never on a Sunday")
    checks.append(("an element with nothing under it, and one left to be drawn", any("stands on nothing" in s for s in said) and any("to be drawn" in s for s in said)))
    checks.append(("a requirement from material that no finding became", any(s.startswith(f"{wish} is taken from material") for s in said)))
    checks.append(("a rule in a specification read from material that nothing backs", any(s.startswith(f"{rule} stands on no finding") for s in said)))
    checks.append(("a question for the skill that does not say how", any("does not say how: `investigate" in s for s in said)))
    checks.append(("a row's link the prototype does not draw", any("SC3.10 leads to SC9 by its row" in s for s in said)))
    checks.append(("the gaps: a rule enforced by nothing, a must nothing shows and tied to nothing, a requirement in no story",
                   rule in ids_of(gaps["rules unenforced"]) and wish in ids_of(gaps["musts unshown"])
                   and wish in ids_of(gaps["musts tied to nothing"]) and wish in ids_of(gaps["in no story"])))
    plant(second, A1, r"## Fails.*?(?=## |\Z)", "", S)
    checks.append(("an endpoint that does not say how it fails is a gap; material read in part and views not captured are listed",
                   "A1" in ids_of(content.gaps(loading.load(second))["endpoints with no fails"]) and bool(gaps["read in part"]) and bool(gaps["not captured"])))
    checks.append(("no gap holds an agreement: the example has them, and is agreed",
                   any(content.gaps(loading.load(clean)).values()) and not finish.ready(g, loading.load(clean), review.held(clean))))

    # a piece the screens share
    third = tmp / "pieces"
    shutil.copytree(clean, third)
    pieces = lambda: [f["says"] for f in shared.faults(loading.load(third))]  # noqa: E731
    checks.append(("every prototype holds the shared piece as it stands", not pieces()))
    edit(third, P3, "Electronics, picked and known", "Other words")
    checks.append(("a copy changed by hand is told", any("is not its shared piece" in s for s in pieces())))
    checks.append(("stamping puts that one prototype right", shared.stamp(third) == [P3] and not pieces()))
    edit(third, FOOTER, "Electronics, picked and known", "Picked, and known")
    moved = shared.stamp(third)
    hosts = sum("data-stamp" in p.read_text(encoding="utf-8") for p in (third / "prototypes/screens").glob("*.html"))
    checks.append(("a piece changed once reaches every screen that holds it", len(moved) == hosts == 18
                   and "Picked, and known" in (third / P3).read_text(encoding="utf-8")))
    stamped = spec(third, "stamp")
    checks.append(("the command says when nothing moved", stamped.returncode == 0 and "as they stand" in stamped.stdout))
    add(third, "prototypes/shared/C99.html", "<p>x</p>\n")
    remove(third, FOOTER)
    told = pieces()
    checks.append(("a host with no piece, and a piece of no component", any("is not there" in s for s in told) and any("of no component" in s for s in told)))

    # what moved since it was agreed
    fourth = tmp / "moved"
    shutil.copytree(clean, fourth)
    since = lambda at: review.since_agreed(g, loading.load(at))  # noqa: E731
    checks.append(("as agreed, nothing has moved", since(fourth) is not None and since(fourth)["changes"] == []))
    shown = spec(fourth, "changes")
    checks.append(("the command says so", shown.returncode == 0 and "0 node(s) moved" in shown.stdout))
    logic.apply(fourth, [["set", "document", "status", "draft"]], who="selftest")
    logic.apply(fourth, [["set", "R4", "priority", "should"]], who="selftest")
    checks.append(("a change since is told, against what was agreed",
                   any(c["id"] == "R4" and c["fields"]["priority"] == ["must", "should"] for c in since(fourth)["changes"])))
    shown = spec(fourth, "changes")
    checks.append(("and the command tells it", "R4" in shown.stdout and "must" in shown.stdout))
    logic.apply(fourth, [["set", "R4", "priority", "must"]], who="selftest")
    logic.apply(fourth, [["set", "document", "status", "agreed"]], who="selftest", dry=True)
    checks.append(("a dry run keeps no agreement", (fourth / review.AGREED).read_text(encoding="utf-8") == (clean / review.AGREED).read_text(encoding="utf-8")))
    fifth = tmp / "by-hand"
    shutil.copytree(clean, fifth)
    plant(fifth, R4, r"^name: .*$", "name: Put a product in the cart", M)
    checks.append(("a hand edit while it is agreed is told by ready", any("changed since it was agreed" in r and "R4" in r for r in finish.ready(g, loading.load(fifth), review.held(fifth)))))
    remove(fifth, review.AGREED)
    checks.append(("agreed before agreements were kept, there is nothing to compare with", since(fifth) is None))
    plant(fifth, R4, r"^name: .*$", "name: Add a product to the cart", M)
    logic.apply(fifth, [["set", "document", "status", "draft"]], who="selftest")
    logic.apply(fifth, [["set", "document", "status", "agreed"]], who="selftest")
    checks.append(("agreeing keeps what was agreed", since(fifth) is not None and since(fifth)["changes"] == []))

    # what it lets people do
    able = finish.capabilities(g, loading.load(clean))
    first = next(c for c in able if c["flow"] == "F1")
    checks.append(("a row for each flow: who may take it, the rules it meets, what it carries, what it goes through",
                   len([c for c in able if c["flow"]]) == sum(n.kind == "flow" for n in loading.load(clean).nodes.values())
                   and bool(first["who"]) and bool(first["rules"]) and bool(first["requirements"]) and "SC1" in first["through"]))
    checks.append(("and a last row for what no flow carries", able[-1]["outcome"] == "Carried by no flow" and bool(able[-1]["requirements"])))
    checks.append(("the application and the command line say the same", api.capabilities(clean) == able))
    said = spec(clean, "overview", "--budget", "0")
    checks.append(("the overview says it", "What it lets people do" in said.stdout and "Carried by no flow" in said.stdout))
    written = exporting.export(clean, tmp / "whole.html")
    checks.append(("and the export", 'id="capabilities"' in written.read_text(encoding="utf-8")))

    # the folder's README
    sys.path.insert(0, str(SKILL / "scripts"))
    import folder
    made = tmp / "readme"
    shutil.copytree(clean, made)
    (made / "README.md").unlink(missing_ok=True)
    folder.write_readme(made)
    text = (made / "README.md").read_text(encoding="utf-8")
    checks.append(("the README names the product and how to read and build from it", "Voltline: the product specification" in text
                   and "index.cmd" in text and "AGENTS.md" in text))
    (made / "README.md").write_text(text + "\nOur own notes.\n", encoding="utf-8")
    edit(made, "data/document.md", "name: Voltline", "name: Voltage")
    folder.write_readme(made)
    text = (made / "README.md").read_text(encoding="utf-8")
    checks.append(("written again, what is the skill's is new and what is not stays", "Voltage: the product specification" in text
                   and "Our own notes." in text and text.count("README:") == 1))
    checks.append(("every specification carries one", all((SKILL / "examples" / e / "specs/README.md").is_file() for e in EXAMPLES)))

    # the words the checks hold are the words the reference gives
    guide = (SKILL / "references/ux.md").read_text(encoding="utf-8")
    words = g["words"]

    def rows(heading: str) -> list[list[str]]:
        part = re.search(rf"^### {heading}\n(.*?)(?=^#{{2,3}} |\Z)", guide, re.M | re.S)
        return [[c.strip() for c in line.strip("| \n").split("|")] for line in part.group(1).splitlines() if line.startswith("| `")]

    kinds = {r[0].strip("`"): [s.strip() for s in r[2].split(",") if s.strip() and s.strip() != "none"] for r in rows("Screen kinds")}
    checks.append(("the kinds' states, the behaviours and the states that are one are the guide's",
                   kinds == words["screen states"] and [r[0].strip("`") for r in rows("Behaviours")] == words["behaviours"]
                   and {r[0].strip("`"): [content.slug(w) for w in r[1].split(",")] for r in rows("States that are one")} == words["states that are one"]))

    # every example stands up to all of it, and carries its agreement
    short = []
    for name in EXAMPLES:
        at = SKILL / "examples" / name / "specs"
        done = loading.load(at)
        moved = review.since_agreed(g, done)
        short += [f"{name}: {x}" for x in (*(f["says"] for f in content.faults(g, done)), *finish.ready(g, done, review.held(at)),
                                           *([] if review.status_of(done) == "agreed" else ["it is not agreed"]),
                                           *(["it holds no agreement"] if moved is None else [c["id"] for c in moved["changes"]]))]
    checks.append((f"every example is agreed, falls short of nothing and has not moved since{': ' + '; '.join(short[:4]) if short else ''}", not short))

    # what the importer used to drop: no specification of the first form is left, so a piece of one stands in
    import import_site

    class Earlier:
        """Just enough of a specification of the first form for what no example of it is left to show."""
        PAGE = ("# A1 · Read\n\nLeft out: nobody asked for it.\n\n## Example\n\n<!-- a note -->\n\n```http\nGET /x\n```\n")

        def page(self, at: str) -> str:
            return self.PAGE

        def json(self, name: str) -> dict:
            return {}

        def kind(self, folder: str) -> list[dict]:
            return [{"id": "A1", "name": "Read", "purpose": "It reads.", "surface": "GET /x", "at": "a.html", "out": {}}] if folder == "endpoints" else []

    earlier_form = import_site.Importer(Earlier(), tmp / "from-pages")
    earlier_form.endpoints()
    written = (tmp / "from-pages/data/endpoints/A1.md").read_text(encoding="utf-8")
    checks.append(("an import keeps an endpoint's Example, without its notes, and why a wont is left out, and a screenshot's place",
                   "## Example" in written and "```http" in written and "a note" not in written and earlier_form.left_out({"at": "a.html"}) == "nobody asked for it."
                   and earlier_form.shot("../evidence/captures/site/shots/V6.jpg") == "evidence/captures/site/shots/V6.jpg"))

    # an endpoint's Example, and a script that finds its elements by old names
    told = spec(clean, "unit", "A1", "--budget", "0")
    checks.append(("whoever builds is given an endpoint's Example", "```http" in told.stdout and "Example:" in told.stdout))
    shops = sum(bool(n.fields.get("example")) for n in loading.load(clean).nodes.values())
    checks.append(("the examples hold the Examples they came with", shops == 3
                   and sum(bool(n.fields.get("example")) for name in EXAMPLES for n in loading.load(SKILL / "examples" / name / "specs").nodes.values()) == 28))
    fenced = tmp / "fenced"
    shutil.copytree(clean, fenced)
    edit(fenced, "data/document.md", "status: agreed", "status: draft")
    block = "```sh\n# a comment, no heading\n\n## nor this\nrun it\n```"
    logic.apply(fenced, [["set", "A1", "example", block]], who="selftest")
    logic.apply(fenced, [["set", "A1", "purpose", "What a category page calls, said again."]], who="selftest")
    done = loading.load(fenced)
    checks.append(("a `#` in a fenced block is no heading, read and written", not done.problems and done.nodes["A1"].fields.get("example") == block))
    sixth = tmp / "script"
    shutil.copytree(clean, sixth)
    add(sixth, "prototypes/assets/js/prototype.js", "main.querySelector('[data-spec-element=\"1\"]');\n")
    checks.append(("a script that finds its elements by their old names is told",
                   any("it stops on every screen" in f["says"] for f in content.faults(g, loading.load(sixth)))))
    return checks
