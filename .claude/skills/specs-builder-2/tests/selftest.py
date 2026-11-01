"""specs-builder-2's selftest: the shop example loads clean, and each fault planted in a copy of it is told at its
file and line -- or, for the database, refused there.

    python .claude/skills/specs-builder-2/tests/selftest.py
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 14):
    raise SystemExit(f"specs-builder-2 needs Python 3.14 or later; this is {sys.version.split()[0]}")

import re
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "app"))
import load as loading  # noqa: E402

EXAMPLE = SKILL / "examples" / "shop" / "specs"


def natural(ident: str) -> list:
    import re
    return [int(x) if x.isdigit() else x for x in re.findall(r"\d+|\D+", ident)]


def edit(root: Path, name: str, old: str, new: str) -> None:
    path = root / name
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise AssertionError(f"the seed for {name} expects one {old!r}, and finds {text.count(old)}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


def remove(root: Path, name: str) -> None:
    (root / name).unlink()


def add(root: Path, name: str, text: str) -> None:
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(text, encoding="utf-8", newline="\n")


# Each seed: what it plants, the change, and the problem expected -- its file, where in it (a line's number, 0 for
# none, or words on the line, found in the file as planted), and words in the problem.
R4, B1, SC3, C1 = "data/requirements/R4.md", "data/rules/B1.md", "data/screens/SC3.md", "data/components/C1.md"
SEEDS = [
    ("an unknown key in a header",
     lambda r: edit(r, R4, "priority: must\n", "priority: must\nowner: U1\n"), (R4, "owner: U1", "`owner:` is no field of a requirement")),
    ("a misspelled link key, read as nothing in the old form",
     lambda r: edit(r, R4, "serves: G2, G3", "serve: G2, G3"), (R4, "serve: G2", "`serve:` is no field")),
    ("a link to an ID that is not there",
     lambda r: edit(r, R4, "enforces: B1, B5", "enforces: B1, B99"), (R4, "enforces:", "B99 is not defined")),
    ("a link to a node of the wrong kind",
     lambda r: edit(r, R4, "serves: G2, G3", "serves: G2, R3"), (R4, "serves:", "and R3 is a requirement")),
    ("a link that is not an ID",
     lambda r: edit(r, R4, "serves: G2, G3", "serves: G2, the conversion goal"), (R4, "serves:", "is not an ID")),
    ("a link said twice",
     lambda r: edit(r, R4, "serves: G2, G3", "serves: G2, G2"), (R4, "serves:", "is said twice")),
    ("a requirement that serves no goal",
     lambda r: edit(r, R4, "serves: G2, G3\n", ""), (R4, "id: R4", "R4 serves nothing")),
    ("a requirement with no criterion",
     lambda r: edit(r, R4, "## Accepted when", "## Except"), (R4, "id: R4", "R4 has nothing")),
    ("a line in a list section that is no item",
     lambda r: edit(r, R4, "- R4.1 ", "R4.1 "), (R4, "R4.1 Given", "holds only its list")),
    ("a criterion under the wrong requirement",
     lambda r: edit(r, R4, "- R4.3 ", "- R5.3 "), (R4, "- R5.3", "R5.3 is not R4's")),
    ("a criterion defined twice",
     lambda r: edit(r, R4, "- R4.3 ", "- R4.2 "), (R4, "R4.2 Given a product out of stock", "R4.2 is defined twice")),
    ("a value outside its choices",
     lambda r: edit(r, R4, "priority: must", "priority: urgent"), (R4, "priority: urgent", "`priority: urgent` is not one of")),
    ("a required field missing",
     lambda r: edit(r, R4, "name: Add a product to the cart\n", ""), (R4, "id: R4", "R4 has no `name:`")),
    ("a statement that says nothing the product shall do",
     lambda r: edit(r, R4, "the shop shall add", "the shop adds"), (R4, "the shop adds", "says what the product `shall` do")),
    ("a section the kind does not have",
     lambda r: edit(r, R4, "## Accepted when", "## Notes\n\nsee R5\n\n## Accepted when"),
     (R4, "## Notes", "`## Notes` is no section of a requirement")),
    ("a `# ` heading in place of the name",
     lambda r: edit(r, B1, "A cart holds at most five", "# Up to five\n\nA cart holds at most five"),
     (B1, "# Up to five", "not a `# ` heading")),
    ("a key said twice",
     lambda r: edit(r, B1, "name: Up to five of a product\n", "name: Up to five of a product\nname: Five at most\n"),
     (B1, "name: Five at most", "`name` is said twice")),
    ("a header never closed",
     lambda r: add(r, "data/goals/G9.md", "---\nid: G9\nname: Open-ended\n"), ("data/goals/G9.md", 1, "the header is never closed")),
    ("an ID that does not match its file",
     lambda r: edit(r, "data/goals/G3.md", "id: G3", "id: G7"), ("data/goals/G3.md", "id: G7", "the file of G7 is named G7.md")),
    ("an ID of the wrong kind for its folder",
     lambda r: edit(r, "data/goals/G3.md", "id: G3", "id: R3"), ("data/goals/G3.md", "id: R3", "`R3` is no goal's ID")),
    ("a file where no node belongs",
     lambda r: add(r, "data/notes/todo.md", "---\nid: X1\n---\n"), ("data/notes/todo.md", 0, "not a node's file")),
    ("a self-link",
     lambda r: edit(r, "data/requirements/R5.md", "serves:", "depends on: R5\nserves:"),
     ("data/requirements/R5.md", "depends on: R5", "R5 depends on itself")),
    ("a cycle across two requirements",
     lambda r: (edit(r, "data/requirements/R5.md", "serves:", "depends on: R6\nserves:"),
                edit(r, "data/requirements/R6.md", "serves:", "depends on: R5\nserves:")),
     ("data/requirements/R5.md", "depends on: R6", "R5 depends on R6 depends on R5: a cycle")),
    ("an action that is not `yes`, `no` or `?`",
     lambda r: edit(r, "data/roles/U1.md", "- yes: R1 browse", "- maybe: R1 browse"),
     ("data/roles/U1.md", "- maybe: R1", "each action is `- yes: R1")),
    ("an action about a goal",
     lambda r: edit(r, "data/roles/U1.md", "- yes: R1 browse", "- yes: G1 browse"), ("data/roles/U1.md", "- yes: G1", "and G1 is a goal")),
    # tables, and rows that are nodes of their own
    ("a row a cell short",
     lambda r: edit(r, SC3, "| 8 | The SKU | text |", "| 8 | The SKU |"), (SC3, "| 8 | The SKU", "this row has 10 cells")),
    ("a table with columns its kind does not have",
     lambda r: edit(r, SC3, "| Asks | Leads to |\n", "| Asks | Goes to |\n"), (SC3, "| # | Element", "has the columns")),
    ("an element that shows a goal",
     lambda r: edit(r, SC3, "| C4 | R2 |", "| C4 | G1 |"), (SC3, "| 9 | The price", "and G1 is a goal")),
    ("an element that is two components",
     lambda r: edit(r, SC3, "| C4 | R2 |", "| C4, C5 | R2 |"), (SC3, "| 9 | The price", "no more than 1")),
    ("a line in a table's section that is not the table",
     lambda r: edit(r, C1, "a product out of stock |\n", "a product out of stock |\nand more\n"), (C1, "and more", "holds only its table")),
    # the prototypes, held to the data both ways
    ("an anchor in the markup with no row",
     lambda r: edit(r, "prototypes/screens/SC3.html", 'data-el="9"', 'data-el="99"'),
     ("prototypes/screens/SC3.html", 'data-el="99"', '`data-el="99"` has no row')),
    ("a row drawn nowhere in the markup",
     lambda r: edit(r, "prototypes/screens/SC3.html", ' data-el="9"', ""), (SC3, "| 9 | The price", "SC3.9 is drawn nowhere")),
    ("a link written in the markup, as it was before",
     lambda r: edit(r, "prototypes/screens/SC3.html", 'data-el="9"', 'data-el="9" data-spec-req="R2"'),
     ("prototypes/screens/SC3.html", "data-spec-req", "`data-spec-req` in the markup")),
    ("a part the markup names that no component has",
     lambda r: edit(r, "prototypes/screens/SC3.html", 'data-part="C9.1"', 'data-part="C9.99"'),
     ("prototypes/screens/SC3.html", 'data-part="C9.99"', "names no part")),
    ("a variant drawn nowhere",
     lambda r: edit(r, "prototypes/components/C1.html", 'data-variant="disabled"', 'data-variant="off"'),
     (C1, "| disabled |", "variant `disabled` is drawn nowhere")),
    ("a screen with no prototype",
     lambda r: remove(r, "prototypes/screens/SC17.html"), ("data/screens/SC17.md", "id: SC17", "SC17 has no prototype")),
    ("a prototype of no screen",
     lambda r: add(r, "prototypes/screens/SC99.html", "<main></main>\n"), ("prototypes/screens/SC99.html", 0, "a prototype of no screen")),
    ("a page shell without its body's place",
     lambda r: edit(r, "prototypes/page.html", "{{body}}", ""), ("prototypes/page.html", 0, "holds {{body}} 0 times")),
    # the kinds the earlier form held, now nodes of their own
    ("an endpoint with no surface",
     lambda r: edit(r, "data/endpoints/A1.md", "surface: GET /api/v1/products\n", ""),
     ("data/endpoints/A1.md", "id: A1", "A1 has no `surface:`")),
    ("a finding read in no source there is",
     lambda r: edit(r, "data/findings/E1.md", "source: S1", "source: S9"), ("data/findings/E1.md", "source: S9", "S9 is not defined")),
    ("a state that moves to one its entity does not have",
     lambda r: edit(r, "data/entities/N2.md", "| empty |  | N2.open |", "| empty |  | N2.gone |"),
     ("data/entities/N2.md", "| empty |  | N2.gone", "N2.gone is not defined")),
    ("a document that says nothing",
     lambda r: edit(r, "data/document.md", "Voltline is a small electronics shop", "## More\n\nVoltline is a small electronics shop"),
     ("data/document.md", 1, "says nothing in its text")),
]


WISH = ('add requirement "Keep a wish list" priority=should serves=G2 statement="When a customer selects Save, '
        'the shop shall keep the product in their wish list."')
WISH_TEST = 'add-row $1 says="Given a signed-in customer on a product, when Save is selected, then it is kept."'


def operations(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """The operations on a copy of the example, each kept or refused as it should be."""
    import hashlib
    import json

    import logic

    root = tmp / "operated"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")    # changed: an agreed one takes none

    def files() -> dict[str, str]:
        return {q.relative_to(root).as_posix(): hashlib.sha256(q.read_bytes()).hexdigest()
                for q in root.rglob("*") if q.is_file() and ".cache" not in q.parts}

    def last() -> dict:
        lines = (root / logic.CHANGES).read_text(encoding="utf-8").splitlines()
        return json.loads(lines[-1])

    checks = []
    loading.build(loading.load(root))
    logic.notice(root, loading.load(root))
    before = files()
    result = logic.apply(root, [logic.parse(WISH)])          # a requirement with no criterion: refused whole
    checks.append(("a change that would not load clean is refused, and every file stays as it was, byte for byte",
                   bool(result.problems) and files() == before))
    result = logic.apply(root, [logic.parse(WISH), logic.parse(WISH_TEST),
                                logic.parse("tie SC3.13 shows $1")], who="selftest", because="Q9")
    done = loading.load(root)
    checks.append(("a change set is applied whole, `$1` naming what its first operation made",
                   not result.problems and "R17.1" in done.nodes
                   and any(e.src == "SC3.13" and e.rel == "shows" and e.dst == "R17" for e in done.edges)))
    entry = last()
    checks.append(("the change is logged with who, why, its operations as applied and each node's change",
                   entry["who"] == "selftest" and entry["because"] == "Q9" and "add-row R17 says=" in entry["operations"][1]
                   and {c["id"] for c in entry["changes"]} == {"R17", "R17.1", "SC3.13"}))
    r4 = (root / "data/requirements/R4.md").read_text(encoding="utf-8").splitlines()
    logic.apply(root, [logic.parse("set R4 priority should")])
    r4_now = (root / "data/requirements/R4.md").read_text(encoding="utf-8").splitlines()
    checks.append(("a field set changes that one line of the file and nothing else",
                   len(r4) == len(r4_now) and [i for i, (a, b) in enumerate(zip(r4, r4_now)) if a != b] == [3]))
    checks.append(("a field set is logged before and after", last()["changes"][0]["fields"] == {"priority": ["must", "should"]}))
    try:
        logic.apply(root, [logic.parse("remove R17")])
        checks.append(("a node linked from elsewhere is not removed without --untie", False))
    except logic.Refused as refused:
        checks.append(("a node linked from elsewhere is not removed without --untie", "SC3.13 shows R17" in str(refused)))
    logic.apply(root, [logic.parse("remove R17 --untie")])
    ids = json.loads((root / logic.IDS).read_text(encoding="utf-8"))
    checks.append(("removed with --untie: its links taken out, it and its rows retired",
                   "R17" not in loading.load(root).nodes and {"R17", "R17.1"} <= set(ids["retired"])))
    result = logic.apply(root, [logic.parse(WISH), logic.parse(WISH_TEST)])
    checks.append(("a removed ID is never given again: the next is R18", "R18" in loading.load(root).nodes))
    add(root, "data/requirements/R17.md", "---\nid: R17\nname: Back again\npriority: wont\n---\n\nThe shop shall not.\n")
    checks.append(("a retired ID written again by hand is refused",
                   any("R17 was removed on" in m for _, _, m in loading.load(root).problems)))
    remove(root, "data/requirements/R17.md")
    result = logic.apply(root, [logic.parse('add-row SC3 name="Save, C2" is=button component=C2 shows=R18')])
    markup = (root / "prototypes/screens/SC3.html").read_text(encoding="utf-8")
    checks.append(("an element added to a screen gets a placeholder in its markup, its anchor where all see it",
                   not result.problems and 'data-el="26" class="spec-new"' in markup))
    edit(root, "data/rules/B2.md", "name: Delivery is free from fifty euros", "name: Delivery is free from sixty euros")
    noticed = logic.notice(root, loading.load(root))
    checks.append(("an edit by hand is noticed and logged as one", last()["who"] == "by hand"
                   and noticed and noticed[0]["id"] == "B2"))
    held, logic.LOCK_WAIT = logic.LOCK_WAIT, 0.4
    (root / logic.LOCK).write_text("{}", encoding="utf-8")
    try:
        logic.apply(root, [logic.parse("set R4 priority must")])
        checks.append(("while another change is being written, a second waits, then is refused", False))
    except logic.Refused:
        checks.append(("while another change is being written, a second waits, then is refused", True))
    finally:
        (root / logic.LOCK).unlink(missing_ok=True)
        logic.LOCK_WAIT = held
    return checks


def procedures(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """What the procedures stand on: answering, additions, tables, agreeing, what is open, impact and trace, and a
    new specification -- each on a copy of the example."""
    import json
    import subprocess

    import api
    import finish
    import logic
    import review

    root = tmp / "procedures"
    shutil.copytree(clean, root)
    loading.build(loading.load(root))
    logic.notice(root, loading.load(root))
    g = loading.grammar()
    checks = []

    def refused(operations: list[str]) -> str:
        try:
            result = logic.apply(root, [logic.parse(o) for o in operations])
            return "" if not result.problems else "; ".join(m for _, _, m in result.problems)
        except logic.Refused as why:
            return str(why)

    def opened() -> dict:
        done = loading.load(root)
        return finish.opened(g, done, review.held(root))

    # an agreed specification takes no change but going back to draft
    why = refused(["set R4 priority should"])
    checks.append(("an agreed specification refuses a change, naming what it would change, until it is draft",
                   "agreed" in why and "R4" in why and "draft" in why))
    # a question is answered only once no text names it; then it becomes a decision, its links moved
    answer = 'answer Q1 "A visitor\'s cart is kept for 30 days" because="as the old shop" instead="the session only"'
    why = refused(["set document status draft", answer])
    checks.append(("an answer is refused while a text still names the question, each place said",
                   "data/risks/K1.md" in why and "data/screens/SC5.md" in why))
    result = logic.apply(root, [logic.parse(o) for o in [
        "set document status draft",
        'set K1 mitigation "The new platform keeps a visitor\'s cart for 30 days, as the old shop does"',
        'set SC5 who "anyone: a visitor\'s cart is kept for 30 days, a customer\'s under the account"', answer]])
    done = loading.load(root)
    decision = result.applied[-1].rsplit(" ", 1)[1]
    links = {(e.src, e.rel, e.dst) for e in done.edges}
    ids = json.loads((root / logic.IDS).read_text(encoding="utf-8"))
    checks.append(("an answer makes a decision about what the question was about, and the question is retired",
                   done.nodes[decision].kind == "decision" and "Q1" not in done.nodes and "Q1" in ids["retired"]
                   and {(decision, "about", "K1"), (decision, "about", "R4")} <= links))
    checks.append(("every link to the question moves to the decision; a row that asked it is now about it",
                   ("K1", "about", decision) in links and ("SC3.13", "about", decision) in links
                   and not any(e.dst == "Q1" for e in done.edges)))
    # an addition: open, in the way of agreeing, confirmed with its rows
    result = logic.apply(root, [logic.parse(o) for o in [
        'add addition "Merging carts" says="Two carts are merged at sign-in, the larger quantity kept" added_to=R4',
        'add-row R4 says="Given 2 in a visitor\'s cart and 3 in the account\'s, when they sign in, then it holds 3"',
        "tie $1 adds to $2"]])
    addition = result.applied[0].rsplit(" ", 1)[1]
    o = opened()
    checks.append(("an addition is open, with what it was added to, a row too",
                   [a["id"] for a in o["additions"]] == [addition] and o["additions"][0]["added to"] == ["R4", "R4.5"]))
    loading.build(loading.load(root))
    unsettled = api.node(root, "R4")["unsettled"]
    checks.append(("a node says what is unsettled about it -- each addition once, with what it is on",
                   [(u["id"], u["on"]) for u in unsettled] == [(addition, ["R4", "R4.5"])]))
    why = refused(["set document status agreed"])
    checks.append(("agreeing is refused while anything stands in the way, every reason said",
                   "not ready to be agreed" in why and addition in why and "stale" in why))
    logic.apply(root, [logic.parse("confirm-added R4")])
    gone = json.loads((root / logic.IDS).read_text(encoding="utf-8"))["retired"]
    checks.append(("confirm-added on a requirement confirms what was added to it and to its rows",
                   addition not in loading.load(root).nodes and addition in gone))
    # what is stale, confirmed; then it may be agreed, and nothing missing
    for s_ in sorted({s["node"] for s in review.stale(g, loading.load(root), review.held(root))}, key=natural):
        logic.apply(root, [logic.parse(f"confirm {s_}")])
    checks.append(("once nothing stands in the way, it may be agreed", not refused(["set document status agreed"])))
    checks.append(("agreed again, it refuses a change again", "agreed" in refused(["set R4 priority should"])))
    logic.apply(root, [logic.parse("set document status draft")])
    # tables that are not rows: a line added and taken out, a variant drawn as a placeholder, a state by its word
    result = logic.apply(root, [logic.parse(o) for o in [
        'add-line SC5 states offline status=likely "what it shows"="the cart as last seen" investigation="the network off"',
        "remove-line SC5 states loading", 'add-line C1 variants pressed when="while it is pressed"',
        'add-row N2 state=held means="kept for a visitor who left"']])
    states = [r["state"] for r in loading.load(root).nodes["SC5"].fields["states"]]
    drawings = (root / "prototypes/components/C1.html").read_text(encoding="utf-8")
    checks.append(("a table's line is added and taken out by its first cell, the rest of the table kept",
                   not result.problems and "offline" in states and "Loading" not in states and "Empty" in states))
    checks.append(("a variant added is drawn as a placeholder until someone draws it",
                   'data-variant="pressed"' in drawings and "spec-new" in drawings))
    checks.append(("an entity's state is added by its word", "N2.held" in loading.load(root).nodes))
    why = refused(["remove-line SC5 states nothing"])
    checks.append(("a line nobody can find is refused, the lines there named", "Empty" in why and "offline" in why))
    # retarget: every link moved, a link said twice made once
    logic.apply(root, [logic.parse(WISH), logic.parse(WISH_TEST), logic.parse("tie SC3.13 shows $1")])
    logic.apply(root, [logic.parse("retarget R17 R4")])
    done = loading.load(root)
    shown = [e.dst for e in done.edges if e.src == "SC3.13" and e.rel == "shows"]
    checks.append(("retarget moves every link to the new node, a link it doubles said once",
                   shown == ["R4"] and not any(e.dst == "R17" for e in done.edges)))
    # what is open, ranked; the words a review reads for, as notes
    edit(root, "data/requirements/R5.md", "the shop shall", "the shop shall quickly")
    o = opened()
    checks.append(("a vague word in a requirement is a note for a review, never a fault",
                   any(w["id"] == "R5" and w["note"] == "vague" and "quickly" in w["words"] for w in o["words"])
                   and not loading.load(root).problems))
    done = loading.load(root)
    held_now = review.held(root)
    told = finish.stories(g, done)
    checks.append(("the menu's short ways say what the long ways say: stories told together, what is open from the stale list held, ready from what is open",
                   bool(told) and told == [finish.story(g, done, s["id"]) for s in told]
                   and finish.opened(g, done, held_now, review.stale(g, done, held_now)) == finish.opened(g, done, held_now)
                   and finish.ready(g, done, held_now, finish.opened(g, done, held_now)) == finish.ready(g, done, held_now)))
    impact = finish.impact(g, done, review.held(root), "R4.1")
    checks.append(("impact of a criterion reaches what stands on its requirement",
                   {"SC3.13", "U1"} <= {n["id"] for n in impact["stale at once"]}))
    trace = finish.trace(g, done, "R4")
    checks.append(("trace says what a requirement stands on, the findings it came from, what shows it and on which flow",
                   {"G2", "B1", "N2"} <= {n["id"] for n in trace["stands on"]}
                   and any(c["id"] == "E14" and c["quote"] for c in trace["came from"])
                   and any(n["id"] == "SC3.13" and "F1" in n["flows"] for n in trace["shown by"])))
    # before a change is saved: what it would turn stale, said by a dry run that writes nothing
    held_r4 = (root / "data/requirements/R4.md").read_bytes()
    tried = logic.apply(root, [["set", "document", "status", "draft"], ["set", "R4", "priority", "should"]], dry=True)
    plain = logic.apply(root, [["set", "document", "status", "draft"], ["set", "F1", "diagram", "flowchart TD\n  a --> b"]],
                        dry=True)
    checks.append(("a dry run says what a change would turn stale -- what stands on R4 -- and a change that means "
                   "nothing turns nothing stale; neither writes a thing",
                   {"SC3.13", "U1"} <= {s["node"] for s in tried.stale} and {s["on"] for s in tried.stale} == {"R4"}
                   and not plain.stale and (root / "data/requirements/R4.md").read_bytes() == held_r4))
    # how well a requirement stands is worked out from what is behind it, never written
    def stands(*found, unsettled="", addition=False, on="R1"):
        out = loading.Load(root)
        out.nodes.update({"R1": loading.Node("R1", "requirement", "", 0),
                          "R1.1": loading.Node("R1.1", "criterion", "", 0, parent="R1")})
        for number, (seen, source) in enumerate(found, 1):
            out.nodes[f"E{number}"] = loading.Node(f"E{number}", "finding", "", 0, {"seen": seen})
            out.nodes.setdefault(source, loading.Node(source, "source", "", 0))
            out.edges += [loading.Edge(f"E{number}", "became", on, "", 0), loading.Edge(f"E{number}", "from", source, "", 0)]
        if unsettled != "":
            out.nodes["X1"] = loading.Node("X1", "contradiction", "", 0, {"settled": unsettled})
            out.edges.append(loading.Edge("X1", "between", "E1", "", 0))
        if addition:
            out.nodes["AD1"] = loading.Node("AD1", "addition", "", 0)
            out.edges.append(loading.Edge("AD1", "adds to", "R1", "", 0))
        loading.standing(loading.grammar(), out)
        return out.nodes["R1"].fields["confidence"]
    checks.append(("the ladder holds at every rung, from the findings behind a requirement or a row of it, and a "
                   "settled contradiction disputes nothing",
                   stands(("seen", "S1"), ("said", "S2"), unsettled="no") == "disputed"
                   and stands(("seen", "S1"), ("said", "S2"), unsettled="yes") == "corroborated"
                   and stands(("run", "S1"), ("said", "S2"), on="R1.1") == "corroborated"
                   and stands(("seen", "S1"), ("inferred", "S2")) == "seen"
                   and stands(("said", "S1"), ("said", "S2")) == "documented"
                   and stands(("inferred", "S1")) == "inferred"
                   and stands(addition=True) == "added" and stands() == "stated"))
    before = loading.load(root).nodes["R4"].fields["confidence"]
    written = (root / "data/requirements/R4.md").read_bytes()
    (root / "data/requirements/R4.md").write_bytes(written.replace(b"\nname:", b"\nconfidence: seen\nname:", 1))
    typed = loading.load(root)
    (root / "data/requirements/R4.md").write_bytes(written)
    checks.append(("how well a requirement stands is never typed: a file that says it is refused, and What is open "
                   "lists what only documents stand behind",
                   before in loading.grammar()["choices"]["confidence"]
                   and any("confidence" in p[2] and p[0].endswith("R4.md") for p in typed.problems)
                   and all(isinstance(finish.opened(g_, loading.load(root), review.held(root))["documented"], list)
                           for g_ in [loading.grammar()])))
    # whoever builds asks back: the question waits in the inbox, never in the data, until the keeper takes it in
    import inbox
    data_before = sorted(p.name for p in (root / "data" / "questions").iterdir())
    first = inbox.ask(root, "Does the limit of five count lines added from another device?", ["R4"], "the builder")
    second = inbox.ask(root, "Is the cart's | count shown on a phone?", ["R4", "SC3"], "a coding agent")
    try:
        inbox.ask(root, "What of R99?", ["R99"], "the builder")
        unknown_refused = False
    except ValueError:
        unknown_refused = True
    waiting = inbox.read(root)
    held = finish.ready(g, loading.load(root), review.held(root))
    checks.append(("a builder's question waits in the inbox -- never in the data -- what it is about held to the "
                   "specification, and holds it from being agreed",
                   [e["no"] for e in waiting] == [first["no"], second["no"]] and waiting[1]["question"].count("|") == 1
                   and unknown_refused and sorted(p.name for p in (root / "data" / "questions").iterdir()) == data_before
                   and any("waiting in the inbox" in r for r in held)))
    logic.apply(root, [["set", "document", "status", "draft"]])
    made = inbox.raise_(root, first["no"], "the product side")
    inbox.take(root, second["no"])
    third = inbox.ask(root, "Another?", ["R4"], "the builder")
    raised = loading.load(root).nodes.get(made)
    checks.append(("the keeper makes a builder's question an open question, tied to what it is about, or closes it; "
                   "a number is never given twice",
                   raised is not None and raised.kind == "question" and not [e for e in inbox.read(root) if e["no"] < third["no"]]
                   and third["no"] == second["no"] + 1
                   and any(e.src == made and e.rel == "about" and e.dst == "R4" for e in loading.load(root).edges)))
    inbox.take(root, third["no"])
    # a flow as a user story, and what it carries
    told = finish.story(g, done, "F1")
    checks.append(("a flow is told as a user story -- as its user, I want to do what it is named, so that the goals "
                   "it serves -- with the requirements its steps name, in their order, priority, backing and criteria",
                   told["story"].startswith("As the visitor") and "I want to buy a product, so that" in told["story"]
                   and [r["id"] for r in told["requirements"]][:3] == ["R1", "R3", "R2"]
                   and all(r["priority"] and r["backed"] and r["criteria"] for r in told["requirements"])
                   and told["criteria"] == sum(len(r["criteria"]) for r in told["requirements"]) and not told["untold"]))
    job = loading.load(SKILL / "examples" / "stock-sync" / "specs")
    checks.append(("a flow no user drives is told as a job, started by its trigger",
                   finish.story(g, job, "F1")["story"].startswith("Started by the timer")))
    bare = loading.load(root)
    bare.edges = [e for e in bare.edges if not (e.src == "F2" and e.rel == "serves")]
    checks.append(("a flow whose story cannot be told holds the specification from being agreed",
                   any("story cannot be told" in r and "F2 (serves no goal)" in r
                       for r in finish.ready(g, bare, review.held(root)))))
    said = subprocess.run([sys.executable, str(root / "app" / "spec.py"), "story", "F1", "--json"],
                          capture_output=True, text=True, encoding="utf-8")
    checks.append(("spec.py story says a flow's story, as JSON for an agent",
                   said.returncode == 0 and json.loads(said.stdout)["id"] == "F1"))
    # a new specification: a folder that loads clean; one that exists is refused
    fresh = tmp / "fresh"
    script = SKILL / "scripts" / "new_spec.py"
    made = subprocess.run([sys.executable, str(script), str(fresh), "--name", "Invoices", "--kind", "application",
                           "--summary", "Customers take an invoice as a PDF."], capture_output=True, text=True)
    again = subprocess.run([sys.executable, str(script), str(fresh), "--name", "X", "--kind", "api",
                            "--summary", "X."], capture_output=True, text=True)
    new = loading.load(fresh)
    checks.append(("a new specification loads clean, its app and launchers beside it; one there is not written over",
                   made.returncode == 0 and not new.problems and (fresh / "app/spec.py").is_file()
                   and (fresh / "index.cmd").is_file() and again.returncode != 0))
    checks.append(("a new specification is not ready: every quality is still to be said",
                   any("speed" in r for r in finish.ready(g, new, review.held(fresh)))))
    return checks


def staging(root: Path, fault: str = "") -> Path:
    """An agent's staging file, as rules.md shapes it, with one fault planted where `fault` names it."""
    import json

    facets = json.loads((SKILL / "app/agents.json").read_text(encoding="utf-8"))["facets"]["web"]
    facets = facets[1:] if fault == "facet" else facets
    quote = "link: Cart 9 → /cart.html" if fault == "quote" else "link: Cart 2 → /cart.html"
    where = "x.csv" if fault == "data" else "V21-the-cart.md"
    lens = "touch" if fault == "lens" else "action"
    twin = "| S2 | V5-aero-14-a-product-with-a-deal.md | rule | Five at most | `field: Quantity (number, min 1, max 5)` | run | | |\n" \
        if fault == "twin" else ""
    rows = "\n".join(f"| {f} | none | | the cart's views |" for f in facets)
    text = f"""# Web: the cart, walked again

- **Role:** web
- **Read:** S2, the cart's views
- **Version:** 2026-10-26
- **New source:** S9 | evidence/captures/the-brief.md | the brief, read again as its own source

## Findings

| Source | Where | Lens | Found | Quote | Seen | Became | Limits |
|---|---|---|---|---|---|---|---|
| S2 | {where} | {lens} | The header's cart link says how many lines the cart holds | `{quote}` | run | | seen as Ana only |
| S9 | the-brief.md | need | The shop must behave as it does today | `the shop must behave on the new one as it does today` | said | | |
{twin}
## Coverage

| Source | Part | Read | Note |
|---|---|---|---|
| S2 | V21-the-cart.md | full | |
| S9 | the-brief.md | full | |

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
{rows}

## Disagreements

- V21 says Cart 2 while the cart lists three lines.

## Report

Walked the cart again.
"""
    path = root / "evidence/staging/web.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def reading(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """Reading material: an agent's staging file judged and merged, all or nothing; what was read held to what it
    is now; the captured sites held whole; the evidence served, and nothing beside it."""
    import threading
    import urllib.error
    import urllib.request

    import evidence
    import finish
    import load as fresh
    import logic
    import merge
    import review
    import serve

    root = tmp / "reading"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")
    (root / "evidence/captures/site/x.csv").write_text("name,email\nAna,ana@example.com\n", encoding="utf-8")
    edit(root, "data/sources/S2.md", "| inventory.md | full |", "| x.csv | not read | private rows |  |\n| inventory.md | full |")
    loading.build(loading.load(root))
    logic.notice(root, loading.load(root))
    checks = []
    said = lambda fault: " ".join(merge.check(root, staging(root, fault))[1])   # noqa: E731
    checks.append(("a staging file with a facet of its role unanswered is refused, the facet named",
                   "facet views: no row" in said("facet")))
    checks.append(("a quote not in the file its Where names is refused", "the quote is not in V21-the-cart.md" in said("quote")))
    checks.append(("a lens that is none of the grammar's is refused", "`touch` is no lens" in said("lens")))
    checks.append(("a quote from a file of data is refused, the file never opened", "file of data" in said("data")))
    checks.append(("a finding the specification holds already is refused, naming it", "the same place and quote as E14" in said("twin")))
    before = sorted(p.name for p in (root / "data/findings").glob("*.md"))
    ok, _ = merge.merge(root, staging(root, "quote"))
    checks.append(("a refused staging file merges nothing and stays", not ok and (root / "evidence/staging/web.md").is_file()
                   and sorted(p.name for p in (root / "data/findings").glob("*.md")) == before))
    ok, told = merge.merge(root, staging(root))
    done = fresh.load(root)
    made = [n for n in done.nodes.values() if n.kind == "finding" and n.id not in {b[:-3] for b in before}]
    source = next((n for n in done.nodes.values() if n.kind == "source" and n.fields.get("where") == "evidence/captures/the-brief.md"), None)
    s2 = done.nodes["S2"].fields.get("coverage") or []
    checks.append(("a good staging file merges whole: each finding a node, a declared source added with the next free ID",
                   ok and len(made) == 2 and source is not None and source.id == "S4"
                   and any(e.src == made[1].id and e.rel == "from" and e.dst == "S4" for e in done.edges)))
    checks.append(("each part read is a line of its source's coverage, with the print of what it is now",
                   any(r["part"] == "V21-the-cart.md" and r["print"] == evidence.print_of(root / "evidence/captures/site",
                                                                                          "V21-the-cart.md") for r in s2)
                   and sum(1 for r in s2 if r["part"] == "V21-the-cart.md") == 1))
    checks.append(("the agent's report is kept, its disagreements gathered, its staging file gone",
                   (root / "evidence/reports/web.md").is_file() and (root / evidence.DISAGREEMENTS).is_file()
                   and not (root / "evidence/staging/web.md").exists()))
    g = loading.grammar()
    o = finish.opened(g, done, review.held(root))
    checks.append(("disagreements not reconciled keep the specification from being agreed",
                   any("disagreements" in r for r in finish.ready(g, done, review.held(root))) and o["disagreements"]))
    # what was read, held to what it is now
    edit(root, "evidence/captures/site/V22-checkout.md", "# V22", "# V22 ")
    (root / "evidence/captures/site/V99-a-new-view.md").write_text("# V99 · A new view\n", encoding="utf-8")
    (root / "evidence/captures/site/shots/V1-375.jpg").unlink()
    done = fresh.load(root)
    o = finish.opened(g, done, review.held(root))
    checks.append(("a part changed since it was read is told, and to be investigated with the findings resting on it",
                   any(m["part"] == "V22-checkout.md" for m in o["material moved"])
                   and any(r["what"] == "material changed since it was read" and r["says"] == "V22-checkout.md"
                           for r in o["to investigate"])))
    checks.append(("a file of a source no line of coverage accounts for is told",
                   any(u["file"] == "site/V99-a-new-view.md" or u["file"].endswith("V99-a-new-view.md") for u in o["unaccounted"])))
    checks.append(("a capture not in the inventory, and a screenshot gone, are faults of the site",
                   any("V99" in x["file"] and "not in the inventory" in x["says"] for x in o["sites"])
                   and any("V1-375.jpg" in x["says"] for x in o["sites"])))
    checks.append(("what is to investigate is ranked, the heaviest first",
                   [r["weight"] for r in o["to investigate"]] == sorted((r["weight"] for r in o["to investigate"]), reverse=True)
                   and any(r["what"] == "state" for r in o["to investigate"])))
    # the evidence served, and nothing beside it
    httpd = serve.server(root, 0)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/evidence/captures/site/V21-the-cart.md") as answer:
            served = answer.status == 200 and answer.headers["Content-Type"].startswith("text/plain") \
                and b"V21" in answer.read()
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/evidence/..%2Fdata%2Fdocument.md")
            outside = False
        except urllib.error.HTTPError as wrong:
            outside = wrong.code == 404
        checks.append(("the evidence is served as text, and nothing outside it", served and outside))
        try:
            serve.server(root, port)
            checks.append(("a port another server holds is refused, not shared", False))
        except OSError:
            checks.append(("a port another server holds is refused, not shared", True))
    finally:
        httpd.shutdown()
    return checks


def documents(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """README.md, SETUP.md and USER-MANUAL.md held to what is true: the manual's worked example run, command by command,
    on a new specification; every command and operation they name a real one; every link in them leading somewhere."""
    import shlex
    import subprocess

    checks = []
    said = {n: (SKILL / n).read_text(encoding="utf-8") for n in ("README.md", "SETUP.md", "USER-MANUAL.md")}
    manual = said["USER-MANUAL.md"]
    root = tmp / "first-spec"
    made = subprocess.run([sys.executable, str(SKILL / "scripts/new_spec.py"), str(root), "--name", "Invoices", "--kind",
                           "application", "--summary", "Customers take an invoice out of the portal as a PDF."],
                          capture_output=True, text=True, check=False)
    (root / "first.txt").write_text(re.search(r"<!-- first\.txt -->\n```\n(.*?)```", manual, re.S).group(1), encoding="utf-8")
    steps = [line for block in re.findall(r"<!-- walkthrough -->\n```\n(.*?)```", manual, re.S)
             for line in block.strip().splitlines()]
    failed = [] if made.returncode == 0 else [f"new_spec: {made.stderr[-200:]}"]
    for step in steps:
        words, _, note = step.partition("  # ")
        done = subprocess.run([sys.executable, *shlex.split(words)[1:]], cwd=root, capture_output=True, text=True, check=False)
        if done.returncode != (1 if note.startswith("exits 1") else 0):
            failed.append(f"{step}: {(done.stdout + done.stderr).strip()[-160:]}")
    checks.append((f"the manual's worked example works, every command as it is written{': ' + '; '.join(failed) if failed else ''}",
                   len(steps) >= 12 and not failed and (root / "export/invoices.html").is_file()))
    helped = subprocess.run([sys.executable, str(SKILL / "app/spec.py"), "--help"], capture_output=True, text=True, check=False).stdout
    known = set(re.search(r"\{([a-z,]+)\}", helped).group(1).split(","))
    named = {w for text in said.values() for w in re.findall(r"app/spec\.py ([a-z]+)", text)}
    table = re.search(r"\*\*Checking and reading\*\*(.*?)\*\*Changing, with", manual, re.S).group(1)
    named |= set(re.findall(r"^\| `([a-z]+)", table, re.M))
    ways = set(re.findall(r"^\| `([a-z-]+)", re.search(r"\*\*Changing, with `do`\*\*(.*?)`do --file", manual, re.S).group(1), re.M))
    logic_text = (SKILL / "app/logic.py").read_text(encoding="utf-8") + (SKILL / "app/edit.py").read_text(encoding="utf-8")
    checks.append((f"every command the documents name is one the command line has{': ' + ', '.join(sorted((named - known) - {'do'})) if (named - known) - {'do'} else ''}",
                   len(named) >= 12 and not (named - known) - {"do"}))
    every = [c for c in known if c not in ("build",) and f"`{c}" not in manual and f"{c} " not in manual]
    checks.append((f"the manual says every command there is{': ' + ', '.join(sorted(every)) if every else ''}", not every))
    checks.append(("every operation the manual lists is one the logic takes",
                   len(ways) >= 10 and all(f'"{w}"' in logic_text for w in ways)))
    gone = []
    for name, text in said.items():
        for target in re.findall(r"\]\(([^)#:]+\.md)(?:#[^)]*)?\)", text):
            if not (SKILL / target).is_file():
                gone.append(f"{name}: {target}")
        for doc, anchor in re.findall(r"\]\(([^)#:]*)#([a-z0-9-]+)\)", text):
            heads = (SKILL / doc).read_text(encoding="utf-8") if doc else text
            slugs = {re.sub(r"[^a-z0-9 -]", "", h.lower()).strip().replace(" ", "-") for h in re.findall(r"^#+ (.+)$", heads, re.M)}
            if anchor not in slugs:
                gone.append(f"{name}: #{anchor}")
    checks.append((f"every link in the documents leads somewhere{': ' + ', '.join(gone) if gone else ''}", not gone))
    checks.append(("the documents are told in the application's words: the bar's buttons and the words of the ladder are there",
                   all(w in manual for w in ("Export", "What is built", "What is open", "On this page", "Every screen drawn", "### The graph", "### The matrix"))
                   and all(f"`{w}`" in manual for w in loading.grammar()["choices"]["confidence"])))
    return checks


def contrast_faults(css: str) -> list:
    """Each text colour of the stylesheet -- the text in its three steps, the accent, a colour for each part and the
    signals -- against the page and a panel, in the light and the dark appearance: those under 4.5:1."""
    def tokens(block):
        return dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", block))
    light = tokens(css[css.index(":root {"):css.index(":root[data-theme=\"dark\"]")])
    dark = {**light, **tokens(css[css.index(":root[data-theme=\"dark\"]"):css.index("/* a kind's colour is its part's")])}

    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
        return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]

    def ratio(a, b):
        a, b = lum(a), lum(b)
        return (max(a, b) + .05) / (min(a, b) + .05)
    texts = ["ink", "ink-2", "ink-3", "accent", "p-evidence", "p-decisions", "p-requirements", "p-domain", "p-api",
             "p-ux", "s-open", "s-bad", "warn-ink"]
    out = []
    for name, t in (("light", light), ("dark", dark)):
        for fg in texts:
            for bg in ("bg", "panel"):
                if fg in t and bg in t and ratio(t[fg], t[bg]) < 4.5:
                    out.append(f"{name} {fg} on {bg} {ratio(t[fg], t[bg]):.1f}")
    return out


def guarded(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """What a change is held to, and the export: what a kind holds, a change refused when what it was made against moved
    since, and one file that holds the whole specification."""
    import json
    import re

    import api
    import export
    import logic

    root = tmp / "editing"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")
    loading.build(loading.load(root))
    logic.notice(root, loading.load(root))
    g = loading.grammar()
    checks = []
    requirement, screen = api.form(g, "requirement"), api.form(g, "screen")
    checks.append(("a form says what a kind holds: a requirement needs its goal and a first criterion; a screen is tied "
                   "only by what is written as a whole, not in its tables' cells",
                   any(r["rel"] == "serves" and r.get("least") == 1 for r in requirement["relations"])
                   and requirement["rows"]["least"] == 1 and requirement["rows"]["list"]
                   and {r["rel"] for r in screen["relations"]} == {"shows", "about", "displays"}))
    try:
        logic.apply(root, [logic.parse("tie SC3 leads to SC4")])
        checks.append(("a link written only in a table's cell is refused when tied to the node as a whole", False))
    except logic.Refused as why:
        checks.append(("a link written only in a table's cell is refused when tied to the node as a whole",
                       "cell of a table" in str(why)))
    held = loading.version(g, loading.load(root), "R4")
    loading.build(loading.load(root))
    checks.append(("a node's version is the same read from the database as from the files",
                   api.node(root, "R4")["version"] == held))
    result = logic.apply(root, [logic.parse("set R4 priority should")], expect={"R4": held})
    try:
        logic.apply(root, [logic.parse("set R4 priority must")], expect={"R4": held})
        refused = ""
    except logic.Refused as why:
        refused = str(why)
    checks.append(("a change made against a node that moved since is refused, and the first one kept",
                   not result.problems and "changed since you opened it" in refused
                   and "priority: should" in (root / "data/requirements/R4.md").read_text(encoding="utf-8")))
    try:
        logic.apply(root, [logic.parse("set R99 priority must")], expect={"R99": "0"})
        gone = ""
    except logic.Refused as why:
        gone = str(why)
    checks.append(("a change made against a node gone since is refused", "gone since you opened it" in gone))
    print_of = lambda: loading.fingerprint(g, loading.load(root).nodes["R3"])    # noqa: E731
    first_print = print_of()
    logic.apply(root, [logic.parse('set R3 why "Shoppers leave when they cannot find a product."')], who="selftest")
    why_print = print_of()
    logic.apply(root, [logic.parse('set R3 details "It covers names, not descriptions."')], who="selftest")
    told_fields = loading.load(root).nodes["R3"].fields
    written = (root / "data/requirements/R3.md").read_text(encoding="utf-8")
    checks.append(("a requirement's Why and Details stand between its statement and its criteria: a Why turns nothing stale, Details does",
                   why_print == first_print and print_of() != first_print and not loading.load(root).problems
                   and told_fields["why"].startswith("Shoppers") and told_fields["details"].startswith("It covers")
                   and written.index("## Why") < written.index("## Details") < written.index("## Accepted when")))
    edit(root, "data/requirements/R5.md", "the shop shall", "the shop <script>alert(1)</script> shall")
    out = export.export(root, tmp / "export.html")
    text = out.read_text(encoding="utf-8")
    ids = set(re.findall(r' id="([^"]+)"', text))
    hrefs = set(re.findall(r'href="#([^"]+)"', text))
    tops = {i for i, n in loading.load(root).nodes.items() if n.parent is None}
    checks.append(("the export holds every node, each where a link to it lands, and every link lands",
                   tops <= ids and not (hrefs - ids)))
    checks.append(("the export tells each flow as a user story, with what it carries",
                   text.count('<p class="story">') == sum(1 for n in loading.load(root).nodes.values() if n.kind == "flow")
                   and "I want to buy a product" in text))
    checks.append(("the export draws each screen's prototype in a sandboxed frame, needing nothing beside it",
                   text.count('<iframe class="proto" sandbox="allow-scripts"') == sum(
                       1 for n in loading.load(root).nodes.values() if n.kind == "screen")
                   and 'src="assets/' not in text.split("srcdoc=")[1][:200_000]))
    held = loading.load(root).nodes
    flows = sum(1 for n in held.values() if n.kind == "flow")
    blocks = re.findall(r"<script>(.*?)</script>", text, re.S)
    cards = json.loads(re.search(r"window\.cards = (\{.*?\});\nwindow\.flows", text, re.S).group(1))
    checks.append(("the export holds every ID's card, by the application's own card.js: a right click opens it and it needs "
                   "no server",
                   set(cards) == set(held) and all(cards[i] for i in cards) and cards["R4"]["kind"] == "requirement"
                   and any("function openCard" in b and "inExport" in b for b in blocks) and "id-card" in text))
    checks.append(("the export gives each flow its diagram above its steps, by the application's own flowmap.js, in "
                   "place of the diagram's bare text",
                   text.count('class="flow-slot"') == flows and any("function flowMap" in b for b in blocks)
                   and "<code>flowchart" not in text and "language-mermaid" not in text
                   and text.index('data-flow="F1"') < text.index("<h4>Steps</h4>", text.index('id="F1"'))))
    checks.append(("the bar has an Export button beside the printer, which asks the server for the whole file",
                   'id="export-button"' in (SKILL / "app/web/index.html").read_text(encoding="utf-8")
                   and '"/api/export"' in (SKILL / "app/web/aids.js").read_text(encoding="utf-8")
                   and "export: [" in (SKILL / "app/web/menu.js").read_text(encoding="utf-8")))
    checks.append(("the export is on A4 on paper, and keeps its dark appearance off it",
                   "size: A4" in text and "beforeprint" in text and ".id-card { display" not in text.split("@media print")[0]))
    checks.append(("the export escapes what the data says: no markup of it runs",
                   "<script>alert(1)</script>" not in text and "&lt;script&gt;alert(1)&lt;/script&gt;" in text))
    web = (SKILL / "app/web/index.html").read_text(encoding="utf-8")
    checks.append(("the page loads the request, the menu and the help before the engine, and has no way to edit",
                   web.index("request.js") < web.index("menu.js") < web.index("help.js") < web.index("engine.js")
                   and "edit" not in web and not (SKILL / "app/web/edit.js").exists()))
    checks.append(("the bar has two rows: the name, search, help and the appearance above; the parts below",
                   web.index('class="bar-top"') < web.index('id="search"') < web.index('id="help-link"')
                   < web.index('id="theme"') < web.index('<nav id="nav"')
                   and "open-link" not in web and "brand-kicker" not in web))
    menu = (SKILL / "app/web/menu.js").read_text(encoding="utf-8")
    card = (SKILL / "app/web/card.js").read_text(encoding="utf-8")
    g = json.loads((SKILL / "app/grammar.json").read_text(encoding="utf-8"))
    named = []                                       # what a kind's card names that the kind does not hold
    for kind, spec in g["kinds"].items():
        held = (set(spec.get("fields") or {}) | set(spec.get("worked out") or ())
                | {d.get("as") for d in (spec.get("sections") or {}).values()})
        held |= {c.get("as") for c in spec.get("columns", [])}
        shape = spec.get("card")
        if shape is None:
            named.append(f"{kind}: no card")
            continue
        named += [f"{kind}: {w}" for w in shape.get("facts", []) if ("field" in w and w["field"] not in held)
                  or ("text" in w and w["text"] not in held) or ("rows" in w and w["rows"] not in (spec.get("sections") or {}))
                  or any(k in w and w[k] not in g["relations"] for k in ("link", "back"))]
        named += [f"{kind}: said {shape['said']}"] if shape.get("said") and shape["said"] not in held else []
    checks.append((f"every kind has a card, naming only what the kind holds{': ' + ', '.join(named) if named else ''}",
                   not named))
    side = (SKILL / "app/web/side.js").read_text(encoding="utf-8")
    css = (SKILL / "app/web/style.css").read_text(encoding="utf-8")
    faint = contrast_faults(css)
    checks.append((f"every text colour reads at 4.5:1 or more on the surfaces it stands on, light and dark"
                   f"{': ' + ', '.join(faint) if faint else ''}", not faint))
    checks.append(("a part's pages have its tree down the left -- its kinds folding to their nodes, the part's own page at "
                   "its head -- a button under 1024px, and none in the preview",
                   web.index("side.js") < web.index("engine.js") and "has-side" in side and "partView" in side
                   and '"peeked"' in side and 'id="side"' in web and "side-grip" in side and "SIDE_WIDTHS" in side
                   and "side-folded" in side and "side-tip" in side and "drawSide(" in (SKILL / "app/web/engine.js").read_text(encoding="utf-8")
                   and "max-width: 1023px" in (SKILL / "app/web/style.css").read_text(encoding="utf-8")))
    flowmap = (SKILL / "app/web/flowmap.js").read_text(encoding="utf-8")
    grammar = json.loads((SKILL / "app/grammar.json").read_text(encoding="utf-8"))
    checks.append(("a flow's page draws its diagram with Mermaid, fetched at one exact version and kept out of the "
                   "repository -- the one its Diagram section holds, else one made from its steps",
                   web.index("flowmap.js") < web.index("engine.js") and "function flowMap" in flowmap
                   and "function made" in flowmap and "cdn.jsdelivr.net/npm/mermaid@11.9.0/" in flowmap
                   and not (SKILL / "app/web/vendor").exists()
                   and "Diagram" in grammar["kinds"]["flow"]["sections"]
                   and "flowMap(n)" in (SKILL / "app/web/engine.js").read_text(encoding="utf-8")))
    engine_js = (SKILL / "app/web/engine.js").read_text(encoding="utf-8")
    graphmap = (SKILL / "app/web/graphmap.js").read_text(encoding="utf-8")
    menu_js = (SKILL / "app/web/menu.js").read_text(encoding="utf-8")
    style = (SKILL / "app/web/style.css").read_text(encoding="utf-8")
    checks.append(("the Graph page draws the whole specification with D3, fetched at one exact version and kept out of the "
                   "repository, loaded before the engine and after the file it keeps its folds with; it says so without a "
                   "connection; the graph around one node is still there",
                   web.index("side.js") < web.index("graphmap.js") < web.index("engine.js")
                   and "cdn.jsdelivr.net/npm/d3@7.9.0/" in graphmap and "The graph is not drawn" in graphmap
                   and "if (!id) return await wholeGraph();" in graphmap and "await graphPage(decoded)" in engine_js))
    checks.append(("the Graph is in the bar, straight to its page, and fills the window under it",
                   'Graph: "#/graph"' in menu_js and '"Graph"].filter(Boolean)' in menu_js
                   and 'where === "matrix" || where === "graph"' in engine_js and 'if (active === "graph") return "Graph";' in menu_js))
    checks.append(("a kind folds to a bubble and opens to a box, what shows is what is joined, a node is an ID's link with its "
                   "card, and the picture prints flat in SVG",
                   "function mapBubble" in graphmap and "function mapBox" in graphmap and "function mapLinks" in graphmap
                   and 'class: `ref map-node' in graphmap and "href: mapHref(n.id)" in graphmap and "<canvas" not in graphmap
                   and "function focusGraph" in graphmap and "function impactGraph" in graphmap and "function layersGraph" in graphmap
                   and 'get("graph")' not in graphmap and "function mapMore" in graphmap
                   and 'svg("a", { class: `ref map-tag' in graphmap and 'class: `mx-tool${on ? " on" : ""}`' in graphmap
                   and graphmap.count(".wheelDelta(mapWheel)") == 2 and 'id.startsWith("layers:")' in graphmap and "map-band" in graphmap
                   and "function mapPick" in graphmap and "&steps=${mapState.steps}" in graphmap and '"graph-scope"' in graphmap
                   and "onwheel: wheel" in graphmap and "MAP_LAYER_HIDDEN" in graphmap
                   and "if (SHEET)" in graphmap and ".graph-map.flat" in style and "MAP_OPEN" in graphmap))
    matrix_js = (SKILL / "app/web/matrix.js").read_text(encoding="utf-8")
    loader = (SKILL / "app/load.py").read_text(encoding="utf-8")
    checks.append(("a node's ways into the Graph stand under its title, not at the foot of its page",
                   engine_js.index('class: "actions-row node-ways"') < engine_js.index("if (n.stale && n.stale.length)")
                   and "waysOf([...pictureWays(n.id)," in engine_js and 'waysOf([["prototype", "Prototype: open it"' in engine_js
                   and 'scrolling: whole ? "no" : null' in engine_js
                   and "waysOf(pictureWays(" in (SKILL / "app/web/matrix.js").read_text(encoding="utf-8")
                   and ".node-ways .live-seg" in style))
    checks.append(("a view is built whole before anything on the page moves, and one overtaken by another is never shown",
                   engine_js.index("content = await overview()") < engine_js.index("if (turn !== routed) return;\n    nav(active);") < engine_js.index("view.replaceChildren(...withAids(")
                   and "if (turn !== routed) return;" in engine_js))
    checks.append(("the Matrix is in the bar before the Graph, straight to its page, fills the window, and stays on the page as "
                   "it is walked, asking only for what the address changed",
                   'Matrix: "#/matrix"' in menu_js and '"Matrix", "Graph"].filter(Boolean)' in menu_js
                   and 'if (active === "matrix") return "Matrix";' in menu_js and 'where === "prototype" || where === "matrix"' in engine_js
                   and 'where === "matrix" && matrixShowing()' in engine_js
                   and web.index("side.js") < web.index("matrix.js") < web.index("engine.js")))
    checks.append(("the Matrix never holds the whole specification: the tree draws the rows in view and fetches a page as it is "
                   "scrolled to, a node's links come a few at a time, and it asks for no library and no whole graph",
                   "function mxAsk" in matrix_js and "mxDraw" in matrix_js and "MX_SPARE" in matrix_js and "matrix/tree?" in matrix_js
                   and "Show more" in matrix_js and "loadD3" not in matrix_js and 'get("graph")' not in matrix_js
                   and "https://" not in matrix_js and "CREATE TABLE crossings" in loader and "nodes_of_kind" in loader))
    checks.append(("the Matrix's tree reads as the other trees do: names cut by the same words(), the menu's icons and letters, a "
                   "row measured for a name that wraps, and its width dragged at the same edge and kept with theirs; the grid is "
                   "drawn whole, and the pane scrolls",
                   "words(n.name" in matrix_js and "lettersOf(row.kind)" in matrix_js and "PARTS[row.name].icon" in matrix_js
                   and "function mxRowAt" in matrix_js and 'wireGrip(mx.root.querySelector(".mx-left"), "Matrix")' in matrix_js
                   and "sideState.widths.Matrix" in matrix_js and 'wireTips(mx.root.querySelector(".mx-left"))' in matrix_js
                   and "var(--side-w, 288px)" in style and ".mx-grid-frame { width: max-content;" in style
                   and "var(--mx-far-w, 340px)" in style and "{ set: mxFarWide," in matrix_js))
    checks.append(("every label in the Matrix's tree shows something in the middle, and only a chevron folds; nothing in the middle "
                   "is cut: it wraps",
                   "function mxPartView" in matrix_js and "function mxKindView" in matrix_js and "place: `kind:${kind}`" in matrix_js
                   and "onclick: mxCollapse" in matrix_js and "function mxRemember" in matrix_js and "mxTravel(-1)" in matrix_js and "mxTravel(1)" in matrix_js
                   and "function mxFilter" in matrix_js and "function mxNarrow" in matrix_js and "function mxPathView" in matrix_js
                   and "mxKindHref(k.kind)" in matrix_js and "mx-owed" in style
                   and "onclick: fold, title:" in matrix_js and ".mx-link-main .mx-name { flex: 1; overflow: visible; white-space: normal;" in style))
    checks.append(("the Matrix prints what is in view, the whole grid on A4; on a phone its sides are tabs",
                   "if (SHEET) return matrixSheet" in matrix_js and "html.sheet .mx-grid" in style and '.mx-panes[data-pane="told"]' in style))
    checks.append(("the prototype folds the bars away, the screen nearly full height, and shows them again from a strip",
                   "proto-folded" in engine_js and "live-strip" in engine_js and "PROTO_FOLDED" in engine_js
                   and "html.proto-folded .bar" in (SKILL / "app/web/style.css").read_text(encoding="utf-8")))
    aids = (SKILL / "app/web/aids.js").read_text(encoding="utf-8")
    theme_js = (SKILL / "app/web/theme.js").read_text(encoding="utf-8")
    on_paper = css[css.index("@media print {\n  .bar"):css.index("/* what the code carries")]
    checks.append(("a page has its outline and the nodes beside it, and neither a preview, the prototype nor a sheet has them",
                   web.index("side.js") < web.index("aids.js") < web.index("engine.js")
                   and "withAids(view, where, decoded, content)" in engine_js and "function outline" in aids
                   and "function pager" in aids and "peeked" in aids and 'where === "prototype"' in aids
                   and "if (SHEET) return onSheet(content)" in aids))
    checks.append(("a node's page has small links to the nodes beside it at its top and its foot, an icon and an ID on "
                   "each, its name on a pause, and none on paper",
                   "crumbs.append(above)" in aids and 'h("footer", { class: "page-foot" }, pager(arg))' in aids
                   and 'icon("chevron")' in aids and "title: said" in aids and ".pager," in on_paper))
    checks.append(("the printer in the bar opens the page alone on a sheet of A4 in a tab of its own, shown first, light "
                   "and not to be edited, a prototype in the state it is shown in",
                   'id="print-link"' in web and 'target="_blank"' in web[web.index('id="print-link"'):web.index('id="help-link"')]
                   and "print: [" in (SKILL / "app/web/menu.js").read_text(encoding="utf-8") and "/?print=1" in aids
                   and 'classList.add("peeked", "sheet")' in theme_js and 'sheet ? "light"' in theme_js
                   and "width: 210mm" in css and "tool.shown = query()" in engine_js
                   and "screenOnSheet(decoded)" in engine_js and "window.print()" in aids
                   and "window.print()" not in aids[aids.index("function withAids"):]))
    checks.append(("on paper a page is A4 with margins of its own and a foot saying what it is, with no frame, ink on white "
                   "in either theme, a diagram whole and in its colours, and no row kept whole at the cost of half a sheet",
                   "size: A4" in css and "@bottom-left" in aids and "counter(pages)" in aids
                   and all(part in on_paper for part in (".bar", ".side", ".outline", ".sheet-bar", ".filter", ".flow-diagram, .card"))
                   and ".label-container" in on_paper and not re.search(r"(^|[\s,])tr[\s,].*break-inside", on_paper, re.M)
                   and "beforeprint" in aids and "afterprint" in aids and '"data-theme", "light"' in aids))
    checks.append(("a screen on paper fills the width of A4, whatever the window, and runs on from sheet to sheet: one frame "
                   "to a sheet in a box no taller than it, the page moved and not scrolled, no cut through what it holds",
                   "SHEET_WIDE / wide" in aids and "clientWidth / wide" not in aids and "SHEET_TALL / tall" not in aids
                   and ".sheet-part { width: 174mm; overflow: hidden; }" in css and ".sheet-part { break-inside: avoid; }" in on_paper
                   and "translateY(" in aids and "scrollTo" not in aids and "cutAt(held, at, room)" in aids
                   and ".frame-box, " not in on_paper))
    views = set(re.findall(r'where === "\w+"\) content = await (?:\(SHEET \? (\w+)\(\w+\) : )?(\w+)\(', engine_js)) | set()
    called = {name for pair in views for name in pair if name}
    written = "".join(p.read_text(encoding="utf-8") for p in (SKILL / "app/web").glob("*.js"))
    missing = sorted(name for name in called if f"function {name}(" not in written)
    checks.append((f"every view a route opens is written{': ' + ', '.join(missing) if missing else ''}",
                   len(called) >= 10 and not missing and "function gallery(" in written))
    request_js = (SKILL / "app/web/request.js").read_text(encoding="utf-8")
    card_js = (SKILL / "app/web/card.js").read_text(encoding="utf-8")
    checks.append(("a node's page and its card ask for a change, and only the inbox hears it: no page posts a change to the data",
                   "requestChange(n.id, n.name)" in engine_js and "requestChange(c.id, c.name)" in card_js
                   and '"/api/inbox"' in request_js and "editing." not in written and "/api/changes" not in written))
    story = (SKILL / "app/web/story.js").read_text(encoding="utf-8")
    checks.append(("a flow's page begins with its story and a table of the requirements its steps name, told by the "
                   "server",
                   web.index("story.js") < web.index("engine.js") and "function flowStory" in story
                   and "story/" in story and "flowStory(n)" in (SKILL / "app/web/engine.js").read_text(encoding="utf-8")))
    foundations = (SKILL / "app/web/foundations.js").read_text(encoding="utf-8")
    checks.append(("a foundation's page draws what each row of its tables looks like, from the row's own values",
                   web.index("foundations.js") < web.index("engine.js") and "function foundationBody" in foundations
                   and "Looks like" in foundations and "foundationBody(f[key])" in (SKILL / "app/web/engine.js").read_text(encoding="utf-8")))
    checks.append(("the menu of a part holds its kinds and its own pages; a click on the part opens its page",
                   "Everything in" not in (SKILL / "app/web/menu.js").read_text(encoding="utf-8")))
    tips = card[card.index("function wireTips"):card.index("function wireCards")]
    cards_alone = card.replace(tips, "")
    told = (SKILL / "TUTORIAL.md").read_text(encoding="utf-8")
    pictures = re.findall(r"\]\((tutorial/[^)]+)\)", told)
    checks.append(("the tutorial and the manual come as pages too, and every picture the tutorial names is there",
                   (SKILL / "TUTORIAL.html").is_file() and (SKILL / "USER-MANUAL.html").is_file() and len(pictures) >= 8
                   and all((SKILL / p).is_file() for p in pictures)))
    bar_js = (SKILL / "app/web/menu.js").read_text(encoding="utf-8")
    checks.append(("a part's word opens its page and a small arrow its menu, and nothing opens on a hover",
                   'href: partPage(key)' in bar_js and 'class: "nav-arrow"' in bar_js and "mouseenter" not in bar_js and "mouseleave" not in bar_js
                   and ".nav-arrow {" in style))
    checks.append(("a pause on an ID only says what it is: the tip opens no card and closes none",
                   "openCard" not in tips and "closeCard" not in tips and "shutCard" not in tips and "function idKind" in card))
    checks.append(("a right click on an ID opens its card, and nothing else does, whose Preview shows the node in a popup without the bar",
                   web.index("card.js") < web.index("engine.js") and "/?peek=1" in card
                   and "peeked" in (SKILL / "app/web/theme.js").read_text(encoding="utf-8")
                   and 'target: "_blank"' in card and 'icon("preview")' in card and 'icon("newtab")' in card
                   and '"contextmenu"' in card and '"mouseover"' not in cards_alone and '"focusin"' not in cards_alone and "[data-card]" in card
                   and "function pinCard" in card and "function shutCard" in card and "function flashCard" in card
                   and '"pointerdown"' in card and ".id-card-head { cursor: move;" in style
                   and "id-card-graph" in card and "mapHref(`impact:${id}`)" in card and "mapHref(`layers:${id}`)" in card and "mxNode(top)" in card
                   and 'class: "mx-tool away"' in card and "ways.map((way) => wayAway(...way))" in card and ".mx-tool.away .icon:last-child" in style
                   and "const beside = sideOf(at);" in card and "function wireTips" in card and ".id-tip { position: fixed;" in style and graphmap.count("mapOpen(") == 3 and "MAP_TWICE" in graphmap and "ondblclick: twice" in graphmap and "CARD_PRESS" in card and 'e.pointerType === "mouse"' in card and "if (!press.done) openCard(link)" in card
                   and "-webkit-touch-callout: none" in style and ".map-tag.selected rect, .map-tag.centre rect { fill: var(--accent);" in style and ".live-bar.graph-bar { min-height: 38px;" in style and '"live-bar graph-bar"' in graphmap
                   and 'link.closest("#view, .id-card")' in card and "CARD_MOST" in card and '"scroll"' not in cards_alone))
    engine = (SKILL / "app/web/engine.js").read_text(encoding="utf-8")
    runtime = (SKILL / "app/web/runtime/live.js").read_text(encoding="utf-8")
    checks.append(("a part opens a plain menu of its kinds with their counts, and the prototype is a link straight to it",
                   'Prototype: "#/prototype"' in menu and "href: DIRECT[key]" in menu and "drop-count" in menu and "mega" not in menu + web
                   and "mega" not in (SKILL / "app/web/style.css").read_text(encoding="utf-8")))
    checks.append(("the prototype is a tool: a toolbar, the screen full size, an inspector fed by the runtime's messages",
                   all(w in engine for w in ('class: "live-bar"', 'class: "live-inspector"', "postMessage", 'what.live === "pick"'))
                   and "function history(" not in engine))           # a function of that name hides window.history
    checks.append(("the runtime reads data-el and data-part as handles, and marks nothing unless asked",
                   '[data-el], [data-part]' in runtime and 'params.get("marks") === "hover" ? "hover" : "off"' in runtime))
    head, css = web.split("</head>")[0], (SKILL / "app/web/style.css").read_text(encoding="utf-8")
    checks.append(("the appearance is set in the head before the page paints, and dark is the reader's choice",
                   '<script src="theme.js"></script>' in head and "defer" not in head
                   and ':root[data-theme="dark"]' in css and "prefers-color-scheme" not in css))
    checks.append(("the export lets its reader choose the appearance, and is dark without a script where the system is",
                   'data-look="dark"' in text and ':root[data-theme="dark"]' in text and ":root:not([data-theme])" in text))
    order = [text.find(f'<h2 id="{a}"') for a in ("the-document", "evidence", "decisions-and-what-is-open",
                                                  "requirements", "domain", "what-programs-call",
                                                  "how-it-is-used-and-how-it-looks", "prototype")]
    checks.append(("the export follows the menu's order, the prototype a part of its own, each screen drawn once in it",
                   -1 not in order and order == sorted(order)
                   and text.find('<iframe class="proto"') > order[-1] and 'href="#prototype-SC7"' in text))
    return checks


def builder(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """What a builder asks, answered from a copy of the example; a snapshot taken, the data changed, and told."""
    import build
    import logic

    root = tmp / "built-from"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")    # changed: an agreed one takes none
    code = tmp / "the-code"
    checks = []
    o = build.overview(root)
    checks.append(("the overview names the product and counts what it holds",
                   o["name"] == "Voltline" and o["counts"].get("requirement") == 16 and o["open questions"] == ["Q1"]))
    checks.append(("a specification with nothing stale may be built from", build.verify(root)[0]))
    logic.apply(root, [logic.parse("tie R1 depends on R16")])
    order = [s["slice"] for s in build.plan(root)]
    built = sorted((i for i, n in loading.load(root).nodes.items()
                    if n.kind == "requirement" and n.fields.get("priority") != "wont"), key=natural)
    checks.append(("the plan starts with the foundation and builds a requirement after what it depends on, "
                   "and none it will not",
                   order[0] == "foundation" and order.index("R16") < order.index("R1")
                   and sorted(order[1:], key=natural) == built and len(built) == 15))
    u = build.unit(root, "R4")
    checks.append(("a unit holds its criteria, what it enforces with what that says, what shows it, its questions",
                   [r["id"] for r in u["rows"]] == ["R4.1", "R4.2", "R4.3", "R4.4"]
                   and any(l["id"] == "B1" and "five" in l["says"] for l in u["links"])
                   and any(l["id"] == "SC3.13" and l["rel"] == "shown by" for l in u["back"])
                   and [q["id"] for q in u["questions"]] == ["Q1"]))
    found = build.tests(root, "R4")
    scenario = build.gherkin(found[0])
    checks.append(("a requirement's criteria are its tests, and read as scenarios",
                   [t["id"] for t in found] == ["R4.1", "R4.2", "R4.3", "R4.4"]
                   and scenario.startswith("Scenario: R4.1\n  Given ") and "\n  When " in scenario and "\n  Then " in scenario))
    # what the code carries: read from the names in it, criterion by criterion
    try:
        build.coverage(root)
        checks.append(("coverage with no code known says so", False))
    except FileNotFoundError as wrong:
        checks.append(("coverage with no code known says so", "no code is known" in str(wrong)))
    for name, text in (("tests/test_cart.py", "def test_R4_1_adds(): pass\ndef test_R4_2(): pass\ndef test_R99(): pass\n"
                                              "def test_R5_only_the_requirement(): pass\n"),
                       ("src/Shop.Tests/Browse.cs", "// R1.1\n"), ("src/app/CartTests.cs", "// R6.1\n"),
                       ("src/app/latest.py", "# carries R2\nname = 'R2D2 R7x'\n"), ("node_modules/lib/test.js", "// R8.1\n"),
                       ("features/search.feature", scenario.replace("R4.1", "R3.1"))):
        (code / name).parent.mkdir(parents=True, exist_ok=True)
        (code / name).write_text(text, encoding="utf-8")
    cover = build.coverage(root, code)
    held = {r["id"]: r for r in cover["requirements"]}
    inside = shutil.copytree(root, code / "the-spec", ignore=shutil.ignore_patterns(".cache", "__pycache__"))
    (inside / "tests").mkdir()
    (inside / "tests" / "test_own.py").write_text("# R10.1\n", encoding="utf-8")
    of_inside = build.coverage(inside, code)
    shutil.rmtree(inside)
    checks.append(("coverage counts a requirement by the criteria its tests name, not by being named, and tells tests "
                   "by their place and their name",
                   [c["id"] for c in held["R4"]["criteria"] if c["tests"]] == ["R4.1", "R4.2"]
                   and held["R4"]["untested"] == ["R4.3", "R4.4"] and held["R5"]["tests"] == ["tests/test_cart.py"]
                   and len(held["R5"]["untested"]) == len(held["R5"]["criteria"])
                   and held["R1"]["tests"] == ["src/Shop.Tests/Browse.cs"] and held["R6"]["tests"] == ["src/app/CartTests.cs"]
                   and held["R2"]["code"] == ["src/app/latest.py"] and not held["R2"]["tests"]
                   and held["R3"]["tests"] == ["features/search.feature"] and "R5" not in cover["no test"]
                   and "R2" in cover["no test"]))
    checks.append(("coverage leaves out what is not the product's, and the specification's own folder, says what the "
                   "code names that the specification has not, and is not whole while a must has a criterion untested",
                   not held["R8"]["tests"] and "R7" not in {r for r, h in held.items() if h["code"]}
                   and [u["id"] for u in cover["unknown"]] == ["R99"] and not cover["whole"] and "R15" not in cover["no test"]
                   and "the-spec" not in str(of_inside["requirements"]) and of_inside["code read"] == cover["code read"]))
    checks.append(("the application says so where no code is known", "none" in build.built(root)))
    try:
        build.coverage(root, root)
        checks.append(("coverage refuses the specification's own folder as its code", False))
    except FileNotFoundError as wrong:
        checks.append(("coverage refuses the specification's own folder as its code", "is the specification itself" in str(wrong)))
    try:
        build.changed(root, code)
        checks.append(("changed with no snapshot says so", False))
    except FileNotFoundError as wrong:
        checks.append(("changed with no snapshot says so", "no snapshot" in str(wrong)))
    build.snapshot(root, code)
    checks.append(("a snapshot leaves where the code is, for coverage and the application to need no telling",
                   build.coverage(root)["requirements"][3]["tests"] == ["tests/test_cart.py"]
                   and build.named(root, "R4.1")["tests"] == ["tests/test_cart.py"] and "none" not in build.built(root)))
    logic.apply(root, [logic.parse('set R4 statement "When a visitor selects Add to cart on a product in stock, the '
                                   'shop shall add it to their cart, one to six."'), logic.parse("remove R4.4")])
    (root / "prototypes/assets/img/new-badge.svg").write_text("<svg/>", encoding="utf-8")
    c = build.changed(root, code)
    ids = {x["id"]: x["change"] for x in c["changes"]}
    checks.append(("changed tells each node new, gone or changed since the snapshot",
                   ids.get("R4") == "changed" and ids.get("R4.4") == "removed"))
    checks.append(("changed tells every file of the prototypes, an image too",
                   "prototypes/assets/img/new-badge.svg" in c["files"]["new"]))
    checks.append(("changed says what to build again and the tests to take out",
                   "R4" in c["build again"].get("requirements", []) and "SC3" in c["build again"].get("screens", [])
                   and c["tests to remove"] == ["R4.4"]))
    checks.append(("a change makes the specification not ready to build from until it is reviewed",
                   not build.verify(root)[0]))
    for _ in range(3):
        build.snapshot(root, code)
    checks.append(("snapshots kept in the code, the newest three", len(build.snapshots(code)) == 3))
    return checks


def staleness(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """What each node was reviewed against, kept and told as it should be."""
    import logic
    import review

    root = tmp / "reviewed"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")    # changed: an agreed one takes none
    (root / review.REVIEWED).unlink(missing_ok=True)
    g = loading.grammar()

    def owed() -> list[dict]:
        return review.stale(g, loading.load(root), review.held(root))

    def nodes() -> set[str]:
        return {s["node"] for s in owed()}

    checks = []
    logic.notice(root, loading.load(root))
    checks.append(("the first stamping takes every link as reviewed: nothing is stale",
                   (root / review.REVIEWED).is_file() and not owed()))
    logic.apply(root, [logic.parse('set R4 statement "When a visitor selects Add to cart on a product in stock, the '
                                   'shop shall add it to their cart, one to six."')])
    told = [s for s in owed() if s["node"] == "SC3.13" and s["on"] == "R4"]
    checks.append(("a change reaches every node that stands on it, with what it meant then and now",
                   {"SC3.12", "SC3.13", "C3.5", "U1"} <= nodes() and told
                   and "one to five" in told[0]["was"]["statement"] and "one to six" in told[0]["now"]["statement"]))
    checks.append(("a rule is not stale because a requirement that enforces it changed", "B1" not in nodes()))
    logic.apply(root, [logic.parse("confirm SC3.13")])
    checks.append(("confirmed, a node is stale no more, and the others still are",
                   "SC3.13" not in nodes() and "SC3.12" in nodes()))
    logic.apply(root, [logic.parse("untie SC3.12 shows R4"), logic.parse("tie SC3.12 shows R4")])
    checks.append(("untying and tying again does not clear what is owed", "SC3.12" in nodes()))
    for ident in sorted(nodes()):
        logic.apply(root, [logic.parse(f"confirm {ident}")])
    checks.append(("every node confirmed: nothing is stale", not owed()))
    logic.apply(root, [logic.parse('set R4.2 says "Given the product is in the cart with quantity 5, when one more is '
                                   'added, then the shop refuses it."')])
    checks.append(("a criterion changed reaches what stands on its requirement", {"SC3.13", "U1"} <= nodes()))
    for ident in sorted(nodes()):
        logic.apply(root, [logic.parse(f"confirm {ident}")])
    logic.apply(root, [logic.parse('set SC3.9 name "The price and the deal, C4"')])
    checks.append(("an element changed does not make stale the screens that lead to its screen",
                   not any(s["on"] == "SC3" for s in owed())))
    logic.apply(root, [logic.parse("remove U3 --untie")])        # findings say what became of it
    checks.append(("a node removed takes its stamps with it",
                   not any("U3" in k for k in review.held(root)["links"])))
    (root / review.REVIEWED).write_text("<<<<<<< HEAD\n{}", encoding="utf-8")
    try:
        logic.apply(root, [logic.parse("set R4 priority should")])
        checks.append(("a stamps file that cannot be read stops a change, and is never taken as empty", False))
    except logic.Refused as refused:
        checks.append(("a stamps file that cannot be read stops a change, and is never taken as empty",
                       "cannot be read" in str(refused)))
    return checks


def served(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """The server started on a copy of the example, every question the engine asks put to it, and a hand edit made
    while it runs."""
    import json
    import threading
    import urllib.error
    import urllib.request

    import serve

    root = tmp / "served"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")    # changed: an agreed one takes none
    httpd = serve.server(root, 0)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    def ask(path: str) -> tuple[int, bytes, str]:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as r:
                return r.status, r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            return e.code, e.read(), e.headers.get("Content-Type", "")

    def asked(path: str) -> object:
        status, body, _ = ask(path)
        return json.loads(body) if status == 200 else None

    checks = []
    try:
        checks.append(("the server listens on 127.0.0.1 only", httpd.server_address[0] == "127.0.0.1"))
        summary = asked("/api/summary") or {}
        checks.append(("the application asks what is built, and says where no code is known",
                       "no code is known" in str((asked("/api/built") or {}).get("none"))))
        checks.append(("the server answers its summary: built, clean, every kind counted",
                       summary.get("built") is True and not summary.get("problems") and
                       {k["kind"]: k["count"] for k in summary.get("kinds", [])}.get("requirement") == 16))
        b1 = asked("/api/node/B1") or {}
        checks.append(("a rule is told what enforces it, though its file never says",
                       {(l["rel"], l["id"]) for l in b1.get("back", [])} >= {("enforced by", "R4"), ("enforced by", "R5")}))
        r4 = asked("/api/node/R4") or {}
        checks.append(("a requirement comes with its links, its criteria and who may do it",
                       {("serves", "G2"), ("serves", "G3")} <= {(l["rel"], l["id"]) for l in r4.get("links", [])}
                       and [p["id"] for p in r4.get("parts", [])] == ["R4.1", "R4.2", "R4.3", "R4.4"]
                       and ("may be done by", "U1") in {(l["rel"], l["id"]) for l in r4.get("back", [])}))
        graph = asked("/api/graph?around=R4") or {}
        near = {"R4"} | {e.dst for e in loading.load(root).edges if e.src == "R4"} | \
               {e.src for e in loading.load(root).edges if e.dst == "R4"}
        checks.append(("the graph around a node holds it and all one link away",
                       {n["id"] for n in graph.get("nodes", [])} == near
                       and any(e["rel"] == "serves" for e in graph.get("edges", []))))
        whole = asked("/api/graph") or {}
        shown = {n["id"] for n in whole.get("nodes", [])}
        held = [e for e in loading.load(root).edges if e.src.split(".")[0] != e.dst.split(".")[0]]
        checks.append(("the whole graph holds every node that stands on its own, and counts what a node holds as that node",
                       "R4" in shown and "R4.1" not in shown and "SC3" in shown and not any("." in i for i in shown)
                       and all(l["src"] in shown and l["dst"] in shown and l["src"] != l["dst"] for l in whole.get("links", []))
                       and sum(sum(l["rels"].values()) for l in whole.get("links", [])) == len(held)
                       and len({(l["src"], l["dst"]) for l in whole.get("links", [])}) == len(whole.get("links", []))))
        grid = asked("/api/matrix") or {}
        cells = {(c["from"], c["to"]): c for c in grid.get("cells", [])}
        total = sum(sum(l["rels"].values()) for l in whole.get("links", []))
        checks.append(("the Matrix's grid counts what the Graph draws: every node standing alone, every link between two, by the "
                       "kinds that hold its ends, and a gap is no cell",
                       grid.get("nodes") == len(shown) and grid.get("links") == total
                       and sum(c["count"] for c in grid.get("cells", [])) == total
                       and cells.get(("flow", "screen"), {}).get("rels", {}).get("passes") == 21 and ("term", "term") not in cells))
        cell = asked("/api/matrix/cell?from=flow&to=screen") or {}
        rest = asked("/api/matrix/cell?from=flow&to=screen&offset=5&limit=4") or {}
        checks.append(("a cell lists its links in ID order, a page at a time, with both ends named",
                       cell.get("total") == 21 and len(cell.get("links", [])) == 21 and cell["links"][0]["src"]["id"] == "F1"
                       and cell["links"][0]["dst"]["name"] == "The home page" and rest.get("links") == cell["links"][5:9]))
        tree = asked("/api/matrix/tree?kind=requirement") or {}
        at = asked("/api/matrix/tree?kind=requirement&at=R10") or {}
        rows = asked("/api/matrix/tree?parent=SC3") or {}
        checks.append(("the tree answers one kind or one node's rows, in ID order, and finds the page an ID is on",
                       tree.get("total") == 16 and [r["id"] for r in tree.get("rows", [])][:2] == ["R1", "R2"]
                       and tree["rows"][9]["id"] == "R10" and tree["rows"][0]["parts"] > 0 and at.get("position") == 9
                       and rows.get("total", 0) > 10 and rows["rows"][1]["id"] == "SC3.2"))
        held = asked("/api/matrix/links/SC3") or {}
        sorts = {(s["way"], s["rel"]): s for s in held.get("groups", [])}
        shows = sorts.get(("out", "shows"), {})
        more = asked("/api/matrix/links/SC3?way=out&rel=shows&offset=1&limit=2") or {}
        line = next((r for r in tree.get("rows", []) if r["id"] == "R4"), {})
        checks.append(("a node's links are listed by sort, both ways, each with its count; a row's links are its node's, marked "
                       "with the row, and a link inside the node is left out; the tree's count is the same",
                       held.get("node", {}).get("top") == {"id": "SC3", "kind": "screen"} and shows.get("count", 0) > 0
                       and any(l["from"].startswith("SC3.") for s in held.get("groups", []) for l in s["links"])
                       and not any(l["far"]["id"].split(".")[0] == "SC3" for s in held.get("groups", []) for l in s["links"])
                       and more.get("links") == shows.get("links", [])[1:3]
                       and line.get("links") == sum(s["links count"] for s in (asked("/api/matrix/links/R4") or {}).get("groups", []))))
        far_ends = [l for s in held.get("groups", []) for l in s["links"]]
        checks.append(("a node's links in the Matrix name nodes, never a row they hold, one row to a node, and say how many links reach it",
                       far_ends and not any("." in l["far"]["id"] for l in far_ends)
                       and all(len({l["far"]["id"] for l in s["links"]}) == len(s["links"]) for s in held.get("groups", []))
                       and sum(s["links count"] for s in held.get("groups", [])) >= sum(s["count"] for s in held.get("groups", []))
                       and all(l["count"] >= 1 for l in far_ends)))
        told = asked("/api/matrix/link?src=F1&rel=passes&dst=SC1") or {}
        checks.append(("a link is told whole: both ends, how it reads from each, its file and line, what goes stale, and that it "
                       "is not stale now; a link that is not there is a 404",
                       told.get("reads") == "F1 passes SC1" and told.get("reads back") == "SC1 passed by F1"
                       and told.get("file") == "data/flows/F1.md" and told.get("line", 0) > 1
                       and told.get("stands") == [{"node": "F1", "on": "SC1"}] and told.get("stale") == []
                       and told.get("src", {}).get("kind") == "flow" and ask("/api/matrix/link?src=F1&rel=passes&dst=SC2000")[0] == 404
                       and ask("/api/matrix/link?src=R1&rel=has&dst=R1.1")[0] == 404))
        narrowed = asked("/api/matrix/links/R1?q=home") or {}
        by_kind = asked("/api/matrix/links/R1?by=kind") or {}
        plain = asked("/api/matrix/links/R1") or {}
        kinds_of = {s["kind"]: s for s in by_kind.get("groups", [])}
        page = asked("/api/matrix/links/R1?of=screen&offset=1&limit=2") or {}
        sparse = asked("/api/matrix/cell?from=flow&to=screen&q=home") or {}
        checks.append(("a node's links narrow to a few words, group by the kind at their far end and page there too, and a cell's "
                       "narrow; the sum is the same whichever way they are grouped",
                       narrowed.get("groups") and all("home" in l["far"]["name"].lower() or l["far"]["id"] for s in narrowed["groups"] for l in s["links"])
                       and sum(s["count"] for s in narrowed["groups"]) < sum(s["count"] for s in plain.get("groups", []))
                       and sum(s["count"] for s in by_kind.get("groups", [])) == sum(s["count"] for s in plain.get("groups", []))
                       and "screen" in kinds_of and kinds_of["screen"]["links"][0]["word"]
                       and page.get("links") == kinds_of["screen"]["links"][1:3]
                       and 0 < sparse.get("total", 0) < 21))
        problems_now = grid.get("problems", {})
        unlinked = asked("/api/matrix/tree?kind=foundation&problem=unlinked") or {}
        unsettled = asked("/api/matrix/tree?kind=requirement&problem=open") or {}
        checks.append(("the tree narrows to what has a problem: a node with an open question is found as its page finds it, and what "
                       "is joined to nothing, by kind, in pages of its own; a node that is not in the list stands nowhere",
                       set(problems_now) == {"stale", "unlinked", "open"} and problems_now["stale"] == {}
                       and any(r["id"] == "R4" for r in unsettled.get("rows", []))
                       and unsettled.get("total") == problems_now["open"].get("requirement")
                       and unlinked.get("total") == problems_now["unlinked"].get("foundation", 0)
                       and all(r["links"] == 0 for r in unlinked.get("rows", []))
                       and (asked("/api/matrix/tree?kind=requirement&problem=open&at=R999") or {}).get("position") is None))
        chain = asked("/api/matrix/path?from=F1&to=R1") or {}
        held_chain = asked("/api/matrix/path?from=SC2.6&to=F1") or {}
        checks.append(("a path is the shortest chain of real links between two nodes, each step joining the last, what a node holds "
                       "counted as it, by links a change passes along; a node that is not there is a 404",
                       chain.get("found") and chain.get("changing") and len(chain.get("steps", [])) == 2
                       and chain["steps"][0]["src"]["id"] == "F1" and chain["steps"][0]["rel"] == "passes"
                       and chain["steps"][-1]["rel"] == "shows" and chain["steps"][-1]["dst"]["id"] == "R1"
                       and held_chain.get("found") and ask("/api/matrix/path?from=F1&to=R999")[0] == 404))
        folded = asked("/api/map") or {}
        opened = asked("/api/map?open=screen:3,requirement:400") or {}
        every = ",".join(f"{k['kind']}:9999" for k in folded.get("kinds", []))
        unfolded = asked(f"/api/map?open={every}") or {}
        shows = {k["kind"]: k for k in opened.get("kinds", [])}
        keys = {n["id"] for k in opened.get("kinds", []) for n in k["nodes"]} | {f"kind:{k['kind']}" for k in opened.get("kinds", [])}
        checks.append(("the Graph's map opens from counts alone; a kind opens to its most linked nodes and no more; every link joins what "
                       "shows, each pair once; and with all open it is every link there is",
                       all(k["nodes"] == [] for k in folded.get("kinds", [])) and folded.get("total") == total and folded.get("nodes") == len(shown)
                       and len(shows.get("screen", {}).get("nodes", [])) == 3 and shows["screen"]["count"] == 18
                       and shows["screen"]["nodes"][0]["links"] >= shows["screen"]["nodes"][2]["links"]
                       and all(l["a"] in keys and l["b"] in keys for l in opened.get("links", []))
                       and len({(l["a"], l["b"]) for l in opened.get("links", [])}) == len(opened.get("links", []))
                       and sum(l["count"] for l in unfolded.get("links", [])) == total))
        window = asked("/api/map?open=screen:3@2") or {}
        first_three = next(k for k in opened.get("kinds", []) if k["kind"] == "screen")["nodes"]
        later = next((k for k in window.get("kinds", []) if k["kind"] == "screen"), {}).get("nodes", [])
        trace = asked("/api/map/layers?id=R4") or {}
        near_trace = {n["id"] for k in (asked("/api/map/layers?id=R4&steps=1") or {}).get("kinds", []) for n in k["nodes"]}
        wider_trace = {n["id"] for k in (asked("/api/map/layers?id=R4&steps=2") or {}).get("kinds", []) for n in k["nodes"]}
        column = {k: i for i, held in enumerate(trace.get("layers", [])) for k in held}
        groups_js = (SKILL / "app/web/engine.js").read_text(encoding="utf-8")
        menu_kinds = re.findall(r'"([a-z]+)"', groups_js[groups_js.index("const GROUPS"):groups_js.index("const TEXTS")])
        in_columns = [menu_kinds.index(k) for held in trace.get("layers", []) for k in held]
        checks.append(("the columns of Layers stand in the top menu's order", len(in_columns) > 10 and in_columns == sorted(in_columns)))
        said_first = (asked("/api/summary") or {}).get("version")
        checks.append(("the summary says which state of the data it is, the same until the data changes, so a page asks every name only then",
                       bool(said_first) and said_first == (asked("/api/summary") or {}).get("version") and "state.namesOf" in groups_js))
        one_step = (asked("/api/map/layers?id=R4&steps=1") or {}).get("links", [])
        whole = trace.get("links", [])
        checks.append(("Layers of a node says which links the trace walked: one step walks only that node's own, and a link not walked is kept for a pause",
                       one_step and all(l["walked"] == ("R4" in (l["a"], l["b"])) for l in one_step)
                       and any(not l["walked"] for l in whole) and sum(l["walked"] for l in whole) > sum(l["walked"] for l in one_step)))
        each_row = [n["id"] for k in trace.get("kinds", []) for n in k["nodes"]]
        look = (SKILL / "app/web/style.css").read_text(encoding="utf-8")
        checks.append(("Layers of a node stands each row beside what it links to, each node once, and shows strong and waiting links",
                       "rows = in_rows(kept," in (SKILL / "app/matrix.py").read_text(encoding="utf-8") and len(each_row) == len(set(each_row)) > 10
                       and ".map-link.aside" in look and ".map-link.own" in look and "--tray:" in look and ".graph-bar .live-seg" in look))
        reached = {n["id"]: k["kind"] for k in trace.get("kinds", []) for n in k["nodes"]}
        checks.append(("a kind is walked a window at a time, and the layers of one node hold it and what connects to it in the columns "
                       "either side, each link between two that show, each kind saying how many it reached",
                       len(later) == 3 and first_three[2:3] == later[:1]
                       and "R4" in near_trace and near_trace < wider_trace <= set(reached)
                       and trace.get("node", {}).get("id") == "R4" and "R4" in reached and "goal" in reached.values() and "screen" in reached.values()
                       and all(column[k] is not None for k in reached.values())
                       and all(l["a"] in reached and l["b"] in reached for l in trace.get("links", []))
                       and all(k["count"] >= len(k["nodes"]) for k in trace.get("kinds", []))
                       and ask("/api/map/layers?id=R999")[0] == 404))
        carded = asked("/api/card/R4") or {}
        carded_kinds = {k["kind"]: k for k in (carded.get("linked") or {}).get("kinds", [])}
        checks.append(("a card lists the node's links by kind, the most first, with how many and the first few",
                       "screen" in carded_kinds and carded_kinds["screen"]["count"] >= len(carded_kinds["screen"]["nodes"]) > 0
                       and len(carded_kinds["screen"]["nodes"]) <= 6
                       and [k["count"] for k in carded["linked"]["kinds"]] == sorted((k["count"] for k in carded["linked"]["kinds"]), reverse=True)))
        near_r4 = asked("/api/map/around?id=R4") or {}
        near_row = asked("/api/map/around?id=R4.1") or {}
        tops = {n["id"] for n in near_r4.get("neighbours", [])}
        checks.append(("focus holds one node and what it is linked to, what it holds counted as it, each saying which way its links run",
                       near_r4.get("centre", {}).get("id") == "R4" and "G2" in tops or "G1" in tops
                       and not any("." in i for i in tops) and near_row.get("centre", {}).get("id") == "R4"
                       and all(n["rels"] and (n["out"] or n["in"]) for n in near_r4.get("neighbours", []))
                       and ask("/api/map/around?id=R999")[0] == 404))
        standing = asked("/api/map/stands?id=R4") or {}
        said_impact = asked("/api/node/R4") or {}
        checks.append(("impact says what stands on a node, the opposite of what it stands on, and how many stand on each in turn",
                       standing.get("node", {}).get("id") == "R4" and standing.get("stands")
                       and not ({n["id"] for n in standing["stands"]} & {l["id"] for l in said_impact.get("links", []) if l["rel"] == "serves"})
                       and all("next" in n and n["rels"] for n in standing["stands"]) and ask("/api/map/stands?id=R999")[0] == 404))
        owing = [{"node": "SC1.2", "on": "R2", "link": "SC1.2 shows R2", "was": {}, "now": {}}]
        troubled = serve.matrix.problems(root, owing)
        marked = serve.matrix.grid(root, owing, troubled) or {}
        marks = {(c["from"], c["to"]): c["stale"] for c in marked.get("cells", []) if c["stale"]}
        row = next((l for s in (serve.matrix.links(root, owing, "SC1") or {}).get("groups", []) for l in s["links"]
                    if l["from"] == "SC1.2" and l["far"]["id"] == "R2"), {})
        checks.append(("what is stale reaches the Matrix: a row's node in the tree's filter, its holder's kinds in the grid, and a mark on "
                       "the link itself",
                       troubled["stale"] == {"screen": ["SC1"]} and marks == {("screen", "requirement"): 1} and marked.get("stale") == 1
                       and row.get("stale") is True))
        hits = asked("/api/matrix/find?q=r1") or []
        checks.append(("Find puts an ID typed whole first, reaches rows and every word, and takes % as a character",
                       hits[:1] and hits[0]["id"] == "R1" and len(hits) <= 30
                       and any(h["id"] == "SC3.2" for h in asked("/api/matrix/find?q=SC3.2") or [])
                       and asked("/api/matrix/find?q=%25%25%25") == []))
        checks.append(("a node the Matrix is asked for that is not there is a 404", ask("/api/matrix/links/R99")[0] == 404))
        checks.append(("a node that is not there is a 404", ask("/api/node/R99")[0] == 404))
        checks.append(("a question the server does not have is a 404", ask("/api/nothing")[0] == 404))
        checks.append(("nothing outside app/web/ is served", all(ask(p)[0] == 404 for p in
                       ("/..%2fload.py", "/%2e%2e/load.py", "/..%2f..%2fdata/requirements/R4.md"))))
        status, page, kind = ask("/")
        checks.append(("the engine is served", status == 200 and kind.startswith("text/html") and b"engine.js" in page))
        status, page, _ = ask("/prototype/SC3.html")
        checks.append(("a screen is drawn in the product's shell, the runtime and its place given first",
                       status == 200 and b'<base href="/prototype/">' in page and b"/runtime/live.js" in page
                       and b"<title>SC3 A product</title>" in page and b'data-el="9"' in page
                       and page.index(b"/runtime/live.js") < page.index(b"assets/js/prototype.js")))
        status, page, _ = ask("/prototype/components/C1.html")
        checks.append(("a component's drawings are drawn in the shell", status == 200 and b"drawings.css" in page
                       and b'data-variant="disabled"' in page))
        checks.append(("the product's assets are served", ask("/prototype/assets/css/product.css")[0] == 200))
        checks.append(("a prototype's file is served only drawn, and nothing outside the prototypes",
                       all(ask(p)[0] == 404 for p in ("/prototype/screens/SC3.html", "/prototype/..%2fdata/goals/G1.md",
                                                      "/prototype/tokens.json", "/prototype/SC99.html"))))
        design = asked("/api/design") or {}
        checks.append(("the design system holds the tokens and every component",
                       len(design.get("components", [])) == 13 and any(t["type"] == "color" for t in design.get("tokens", []))))
        menu = asked("/api/menu") or {}
        kinds = menu.get("kinds", {})
        checks.append(("the menu's panels hold each kind's count and its first five, in order",
                       kinds.get("requirement", {}).get("count") == 16 and kinds.get("question", {}).get("count") == 1
                       and [n["id"] for n in kinds.get("requirement", {}).get("first", [])] == ["R1", "R2", "R3", "R4", "R5"]
                       and "criterion" not in kinds))
        checks.append(("the menu tells the document, how much is not settled, and whether it may be agreed",
                       menu.get("document", {}).get("status") == "draft" and (menu.get("open") or 0) >= 1
                       and isinstance(menu.get("ready"), list)
                       and {f["folder"] for f in menu.get("evidence", [])} >= {"reports", "captures/site"}))
        flows = {f["id"]: [s["id"] for s in f["screens"]] for f in menu.get("prototype", {}).get("flows", [])}
        checks.append(("the prototype is told flow by flow, each screen as its flow passes it, then the rest",
                       flows.get("F1", [])[:3] == ["SC1", "SC2", "SC3"] and flows.get("F1", [""])[-1] == "SC12"
                       and [s["id"] for s in menu.get("prototype", {}).get("elsewhere", [])] == ["SC10", "SC17", "SC18"]
                       and asked("/api/prototypes") == menu.get("prototype")))
        checks.append(("the theme, the menu and the help are served",
                       all(ask(f"/{f}")[0] == 200 for f in ("theme.js", "menu.js", "help.js"))))
        by_id = asked("/api/search?q=r4") or []
        by_name = asked("/api/search?q=checkout") or []
        by_text = asked("/api/search?q=visitor%20cart") or []
        checks.append(("search finds an ID typed whole first, its rows after it, and a whole name before a word in one",
                       [f["id"] for f in by_id[:2]] == ["R4", "R4.1"] and by_id[1]["parent"] == "R4"
                       and by_id[1]["name"].startswith("Given")
                       and [f["id"] for f in by_name].index("SC6") < [f["id"] for f in by_name].index("E3")))
        checks.append(("search wants every word, says where in a text it found one, and finds nothing for nothing",
                       by_text and all("visitor" in (f["name"] + f["snippet"]).lower() for f in by_text)
                       and any(f["snippet"] for f in asked("/api/search?q=pay") or [])
                       and asked("/api/search?q=zzzz") == [] and asked("/api/search?q=") == []))
        told_r4, price, fd1 = (asked(f"/api/card/{i}") or {} for i in ("R4", "SC3.9", "FD1"))
        facts = {f["label"]: f for f in told_r4.get("facts", [])}
        checks.append(("a card says what an ID is: its kind, its name, its statement and the facts its grammar lists",
                       told_r4.get("kind") == "requirement" and "shall" in told_r4.get("said", "")
                       and facts.get("Priority", {}).get("text") and facts.get("Serves", {}).get("ids") and facts.get("Accepted when", {}).get("text", "").endswith("criteria")
                       and "unsettled" in told_r4 and "stale" in told_r4))
        checks.append(("a row has its card too, under what holds it, a column's heading its label; a table is never quoted",
                       (price.get("parent") or {}).get("id") == "SC3"
                       and any(f["label"] == "Component" and f.get("ids") == ["C4"] for f in price.get("facts", []))
                       and any(f["label"] == "Kind" for f in price.get("facts", []))
                       and fd1.get("said") == "" and ask("/api/card/ZZ9")[0] == 404))
        sc3 = asked("/api/node/SC3") or {}
        nine = next((p for p in sc3.get("parts", []) if p["id"] == "SC3.9"), {})
        checks.append(("a screen comes with each element and its links",
                       len(sc3.get("parts", [])) == 25 and ("shows", "R2") in {(l["rel"], l["id"]) for l in nine.get("links", [])}))
        edit(root, "data/requirements/R4.md", "serves: G2, G3", "serves: G2, G3, B1")
        after = asked("/api/summary") or {}
        told = [(p["file"], p["line"]) for p in after.get("problems", [])]
        checks.append(("a file edited while the server runs is noticed, its problem told at its line",
                       told == [("data/requirements/R4.md", 5)]))
        checks.append(("while the data has a problem, the last good data is what is read",
                       (asked("/api/node/R4") or {}).get("fingerprint") == r4.get("fingerprint")))
        # a good edit while it runs is built and read at once -- the new database put in place of the one in use
        edit(root, "data/requirements/R4.md", "serves: G2, G3, B1", "serves: G2")
        edit(root, "data/requirements/R4.md", "name: Add a product to the cart", "name: Put a product in the cart")
        now = asked("/api/node/R4") or {}
        exported = urllib.request.Request(f"http://127.0.0.1:{port}/api/export", data=b"", method="POST")
        with urllib.request.urlopen(exported) as answer:
            whole, disposition = answer.read(), answer.headers.get("Content-Disposition", "")
        foreign = urllib.request.Request(f"http://127.0.0.1:{port}/api/export", data=b"", method="POST",
                                         headers={"Origin": "http://elsewhere.example"})
        try:
            urllib.request.urlopen(foreign)
            refused_export = False
        except urllib.error.HTTPError as wrong:
            refused_export = wrong.code == 403
        checks.append(("the Export button's question gives the whole file to keep, and only to this application",
                       whole.startswith(b"<!doctype html>") and b"window.cards" in whole and refused_export
                       and disposition.startswith("attachment;") and disposition.endswith('.html"')))

        def post(body: dict, origin: str | None = None, path: str = "/api/inbox") -> tuple[int, dict]:
            raw = json.dumps(body).encode("utf-8")
            request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=raw, method="POST",
                                             headers={"Content-Type": "application/json",
                                                      **({"Origin": origin} if origin else {})})
            try:
                with urllib.request.urlopen(request, timeout=30) as r:
                    return r.status, json.loads(r.read())
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read() or b"{}")

        import inbox
        import logic
        here = f"http://127.0.0.1:{port}"
        status, said = post({"says": "The limit should be six", "about": ["B1"], "by": "A reader"}, origin=here)
        waits = (asked("/api/open") or {}).get("asked", [])
        checks.append(("a change requested in the application waits in the inbox with who asked and what about, and the data does not move",
                       status == 200 and [(e["by"], e["about"], e["question"]) for e in waits] == [("A reader", ["B1"], "The limit should be six")]
                       and (asked("/api/node/B1") or {}).get("name") == "Up to five of a product" and (asked("/api/summary") or {}).get("problems") == []))
        checks.append(("a request says what it asks and who asks it, about nodes that exist",
                       post({"says": " ", "about": ["B1"], "by": "A reader"}, origin=here)[0] == 400
                       and post({"says": "Well", "about": ["B1"], "by": ""}, origin=here)[0] == 400
                       and post({"says": "Well", "about": ["R999"], "by": "A reader"}, origin=here)[0] == 400))
        checks.append(("a request from another site is refused, 403", post({"says": "Well", "by": "Someone"}, origin="http://evil.example")[0] == 403))
        checks.append(("nothing in the application changes the data: the change route is gone",
                       post({"operations": [["set", "B1", "name", "x"]]}, origin=here, path="/api/changes")[0] == 404
                       and (asked("/api/node/B1") or {}).get("name") == "Up to five of a product"))
        inbox.take(root, said["no"])
        logic.apply(root, [logic.parse('set B1 name "Six at most"')], who="selftest")
        checks.append(("a change made by the operations is read at once",
                       (asked("/api/node/B1") or {}).get("name") == "Six at most"))
        rules = ((asked("/api/menu") or {}).get("kinds", {}).get("rule", {}).get("first", []))
        checks.append(("the menu's panels are worked out again once the data changes",
                       any(n["id"] == "B1" and n["name"] == "Six at most" for n in rules)))
        told = asked("/api/history?id=B1") or []
        checks.append(("the history of a node is answered", any(e.get("who") == "selftest" for e in told)))
        checks.append(("a good edit while the server runs is built and read at once",
                       not (asked("/api/summary") or {}).get("problems") and now.get("name") == "Put a product in the cart"
                       and [l["id"] for l in now.get("links", []) if l["rel"] == "serves"] == ["G2"]
                       and now.get("fingerprint") != r4.get("fingerprint")))
    finally:
        httpd.shutdown()
        httpd.server_close()
    return checks


def main() -> int:
    started = time.perf_counter()
    bad: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean"
        shutil.copytree(EXAMPLE, clean, ignore=shutil.ignore_patterns(".cache", "__pycache__"))
        done = loading.load(clean)
        if done.problems:
            bad.append(f"the shop example should load clean, and has {done.problems[:3]}")
        print(f"{'ok  ' if not done.problems else 'FAIL'} the shop example loads clean: {len(done.nodes)} nodes, "
              f"{len(done.edges)} links")

        for title, plant, (file, line, words) in SEEDS:
            root = Path(tmp) / f"seed{SEEDS.index((title, plant, (file, line, words)))}"
            shutil.copytree(clean, root)
            plant(root)
            found = loading.load(root).problems
            if isinstance(line, str):           # the line that holds those words, as the file now stands
                held = (root / file).read_text(encoding="utf-8").splitlines()
                line = next((i + 1 for i, text in enumerate(held) if line in text), -1)
            hit = [p for p in found if p[0] == file and p[1] == line and words in p[2]]
            print(f"{'ok  ' if hit else 'FAIL'} {title}")
            if not hit:
                bad.append(f"{title}: expected {file}:{line} with {words!r}; got {found[:3]}")

        # the database: built whole, its joins held by a trigger, its old copy kept when a load fails
        database = loading.build(done)
        con = sqlite3.connect(database)
        con.execute("PRAGMA foreign_keys = ON")
        counts = (con.execute("SELECT count(*) FROM nodes").fetchone()[0],
                  con.execute("SELECT count(*) FROM edges").fetchone()[0])
        checks = [("the database holds every node and link", counts == (len(done.nodes), len(done.edges)))]
        try:
            con.execute("INSERT INTO edges VALUES ('R4', 'serves', 'R3', 'x', 1)")
            checks.append(("the database refuses a join the grammar does not allow", False))
        except sqlite3.DatabaseError:
            checks.append(("the database refuses a join the grammar does not allow", True))
        try:
            con.execute("INSERT INTO edges VALUES ('R4', 'serves', 'G99', 'x', 1)")
            checks.append(("the database refuses a link to a node that is not there", False))
        except sqlite3.DatabaseError:
            checks.append(("the database refuses a link to a node that is not there", True))
        con.close()
        checks.append(("a build leaves no half-written file", not database.with_name(database.name + ".new").exists()))
        before = database.stat().st_mtime_ns
        broken = loading.load(Path(tmp) / "seed2")
        try:
            loading.build(broken, database)
            checks.append(("a load with problems builds nothing", False))
        except ValueError:
            checks.append(("a load with problems builds nothing, and the last database stays",
                           database.stat().st_mtime_ns == before))

        # what a node means: spacing is no change, wording is
        g = loading.grammar()
        r4 = done.nodes["R4"]
        same = loading.Node(r4.id, r4.kind, r4.file, r4.line,
                            {**r4.fields, "statement": "  " + str(r4.fields["statement"]).replace(" ", "   ")})
        moved = loading.Node(r4.id, r4.kind, r4.file, r4.line,
                             {**r4.fields, "statement": str(r4.fields["statement"]).replace("one to five", "one to six")})
        checks.append(("a change of spacing leaves the fingerprint", loading.fingerprint(g, same) ==
                       loading.fingerprint(g, r4)))
        checks.append(("a change of wording moves the fingerprint", loading.fingerprint(g, moved) !=
                       loading.fingerprint(g, r4)))
        # a table's rows by what they say: moved down its file it is the same, its words changed it is not
        shifted = Path(tmp) / "shifted"
        shutil.copytree(clean, shifted)
        edit(shifted, "data/components/C1.md", "## Variants", "\n\n## Variants")
        worded = Path(tmp) / "worded"
        shutil.copytree(clean, worded)
        edit(worded, "data/components/C1.md", "a darker blue", "a darker green")
        c1 = loading.fingerprint(g, done.nodes["C1"])
        checks.append(("a table moved down its file leaves the fingerprint",
                       loading.fingerprint(g, loading.load(shifted).nodes["C1"]) == c1))
        checks.append(("a table's words changed move the fingerprint",
                       loading.fingerprint(g, loading.load(worded).nodes["C1"]) != c1))
        # the application: the real server, on a free port, asked as the engine asks it
        checks += served(Path(tmp), clean)

        # the logic: every change one transaction, all or none, logged
        checks += operations(Path(tmp), clean)

        # staleness: a change reaches every node that stands on it, until each is confirmed
        checks += staleness(Path(tmp), clean)

        # the builder's questions, and what the code was built from
        checks += builder(Path(tmp), clean)

        # the procedures: answer, additions, tables, agree, what is open, impact, trace, a new specification
        checks += procedures(Path(tmp), clean)
        checks += documents(Path(tmp), clean)

        # reading material: staging files merged, what was read held to what it is now, the evidence served
        checks += reading(Path(tmp), clean)

        # what a change is held to, and the export
        checks += guarded(Path(tmp), clean)

        # each specification carries the app it was made with (decision 7): every example's is the skill's own,
        # and every example loads clean
        mine = {p.relative_to(SKILL / "app").as_posix(): p.read_bytes()
                for p in (SKILL / "app").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        for example in sorted((SKILL / "examples").glob("*/specs")):
            theirs = {p.relative_to(example / "app").as_posix(): p.read_bytes()
                      for p in (example / "app").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
            drift = sorted(n for n in mine.keys() | theirs.keys() if mine.get(n) != theirs.get(n))
            name = example.parent.name
            checks.append((f"the {name} example carries the skill's app as it is{': ' + ', '.join(drift) if drift else ''}",
                           not drift))
            copy = Path(tmp) / f"example-{name}"
            shutil.copytree(example, copy, ignore=shutil.ignore_patterns(".cache", "__pycache__"))
            found = loading.load(copy)
            checks.append((f"the {name} example loads clean: {len(found.nodes)} nodes"
                           + (f" -- {found.problems[:2]}" if found.problems else ""), not found.problems))
            import evidence
            here = loading.load(example)
            missed = []
            for n in here.nodes.values():
                if n.kind != "finding" or not n.fields.get("quote"):
                    continue
                src = next((e.dst for e in here.edges if e.src == n.id and e.rel == "from"), "")
                there = evidence.source_place(example, here.nodes[src].fields.get("where", "")) if src else None
                file = evidence.file_of(there, n.fields.get("where", "")) if there is not None else None
                if file is None or evidence.squeeze(n.fields["quote"]) not in evidence.squeeze(
                        file.read_text(encoding="utf-8", errors="replace")):
                    missed.append(n.id)
            checks.append((f"every quote of the {name} example is in the file its finding names"
                           + (f" -- not: {', '.join(missed[:5])}" if missed else ""), not missed))
        for title, held in checks:
            print(f"{'ok  ' if held else 'FAIL'} {title}")
            if not held:
                bad.append(title)
    for line in bad:
        print(f"ERROR {line}")
    print(f"{'PASSED' if not bad else 'FAILED'} -- {len(bad)} problem(s) in {time.perf_counter() - started:.1f}s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
