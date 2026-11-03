"""Staleness: a change reaches every node that stands on it, until each is confirmed."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from support import edit, loading


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """What each node was reviewed against, kept and told as it should be."""
    import dataclasses

    import finish
    import logic
    import review

    root = tmp / "reviewed"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")    # changed: an agreed one takes none
    (root / review.REVIEWED).unlink(missing_ok=True)
    g = loading.grammar()

    def owed() -> list[dict]:
        return review.stale(g, loading.load(root), review.held(root))

    def behind() -> list[str]:
        return review.undrawn(g, loading.load(root), review.held(root))

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
                   {"SC3.12", "SC3.13", "C3.5", "F1"} <= nodes() and "U1" not in nodes() and told
                   and "one to five" in told[0]["was"]["statement"] and "one to six" in told[0]["now"]["statement"]))
    checks.append(("a rule is not stale because a requirement that enforces it changed", "B1" not in nodes()))
    checks.append(("a role that may do a requirement stands on the action's name alone, not on every word of its statement",
                   "U1" not in nodes() and "U2" not in nodes()))
    checks.append(("a prototype whose screen stands on what changed, its file not having moved, is told", "SC3" in behind()))
    checks.append(("a specification stamped before drawings were tells of none",
                   not review.undrawn(g, loading.load(root), {k: v for k, v in review.held(root).items() if k != "drawn"})))
    drawing = root / "prototypes/screens/SC3.html"
    drawing.write_text(drawing.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    checks.append(("a prototype redrawn is told no more", "SC3" not in behind()))
    def confirm(ident: str) -> None:
        logic.apply(root, [logic.parse(f"confirm {ident} {review.owed_print(owed(), ident)}")])

    try:
        logic.apply(root, [logic.parse("confirm SC3.13")])
        checks.append(("a stale node is not confirmed without the print stale shows, nor with an older one", False))
    except logic.Refused as refused:
        try:
            logic.apply(root, [logic.parse("confirm SC3.13 00000000")])
            older = False
        except logic.Refused as again:
            older = "moved again" in str(again)
        checks.append(("a stale node is not confirmed without the print stale shows, nor with an older one",
                       "never confirm what you have not read" in str(refused) and older))
    confirm("SC3.13")
    checks.append(("confirmed, a node is stale no more, and the others still are",
                   "SC3.13" not in nodes() and "SC3.12" in nodes()))
    logic.apply(root, [logic.parse("untie SC3.12 shows R4"), logic.parse("tie SC3.12 shows R4")])
    checks.append(("untying and tying again does not clear what is owed", "SC3.12" in nodes()))
    for ident in sorted(nodes()):
        confirm(ident)
    checks.append(("every node confirmed: nothing is stale", not owed()))
    logic.apply(root, [logic.parse('set R4.2 says "Given the product is in the cart with quantity 5, when one more is '
                                   'added, then the shop refuses it."')])
    checks.append(("a criterion changed reaches what stands on its requirement", "SC3.13" in nodes() and "U1" not in nodes()))
    logic.apply(root, [logic.parse('set R4 name "Add a product to the cart, up to six"')])
    checks.append(("the action renamed reaches the roles that may do it", "U1" in nodes()))
    for ident in sorted(nodes()):
        confirm(ident)
    done = loading.load(root)
    checks.append(("what moves after a prototype was redrawn is told again, and holds an agreement though nothing is stale",
                   "SC3" in behind() and any("prototypes to look at" in w and "SC3" in w for w in finish.ready(g, done, review.held(root)))))
    logic.apply(root, [logic.parse("confirm-drawn SC3")])
    checks.append(("a prototype confirmed is told no more, and the confirmation is logged", "SC3" not in behind()
                   and "its drawing confirmed" in (root / logic.CHANGES).read_text(encoding="utf-8")))
    logic.apply(root, [logic.parse('set R4 why "A cart that takes more than the stock holds only disappoints."')])
    checks.append(("a Why reworded asks no prototype to be looked at again", "SC3" not in behind()))
    try:
        logic.apply(root, [logic.parse("confirm-drawn R4")])
        checks.append(("what has no prototype cannot have one confirmed", False))
    except logic.Refused as refused:
        checks.append(("what has no prototype cannot have one confirmed", "no prototype" in str(refused)))
    logic.apply(root, [logic.parse('set SC3.9 name "The price and the deal, C4"')])
    checks.append(("an element changed does not make stale the screens that lead to its screen",
                   not any(s["on"] == "SC3" for s in owed())))
    logic.apply(root, [logic.parse("remove U3 --untie")])        # findings say what became of it
    checks.append(("a node removed takes its stamps with it",
                   not any("U3" in k for k in review.held(root)["links"])))
    held = tmp / "no-look"
    shutil.copytree(clean, held)
    shutil.rmtree(held / "data/foundations")
    told = finish.opened(g, loading.load(held), {})
    checks.append(("a specification with screens and no design system says so, and no screen means no such word",
                   told["no look"] and "ask for the look" in " ".join(finish.ready(g, dataclasses.replace(loading.load(held), problems=[]), {}, told))
                   and not finish.opened(g, loading.load(root), review.held(root))["no look"]))
    # the look is in the graph: a foundation changed reaches every screen and component that follows it, and no other
    looked = tmp / "followed"
    shutil.copytree(clean, looked)
    logic.apply(looked, [logic.parse("set document status draft")])
    told = finish.impact(g, loading.load(looked), review.held(looked), "FD7")
    at_once = {n["id"] for n in told["stale at once"]}
    logic.apply(looked, [logic.parse('set FD7 says "| Rule | Value |\\n|---|---|\\n| The set | none but signs in the text: ★ for the stars |"')])
    owed_now = {s["node"] for s in review.stale(g, loading.load(looked), review.held(looked))}
    checks.append(("a foundation changed makes stale what follows it -- the screens and components drawn by its rule -- and nothing else",
                   {"SC1", "SC3", "C3"} <= at_once and "C1" not in at_once and at_once == owed_now and all(
                       i.startswith(("SC", "C")) for i in owed_now)))
    screen = looked / "data/screens/SC3.md"
    screen.write_text(re.sub(r"(?m)^follows:.*\n", "", screen.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    faults = [f["says"] for f in finish.opened(g, loading.load(looked), review.held(looked))["faults"] if f["id"] == "SC3"]
    checks.append(("a screen following no foundation, where there are foundations, is told", any("follows no foundation" in f for f in faults)))
    logic.apply(root, [logic.parse('set document non-goals "Nothing else, for now."')])
    checks.append(("a text whose name holds a hyphen is set as any other: the document's non-goals",
                   "Nothing else, for now." in (root / "data/document.md").read_text(encoding="utf-8")))
    (root / review.REVIEWED).write_text("<<<<<<< HEAD\n{}", encoding="utf-8")
    try:
        logic.apply(root, [logic.parse("set R4 priority should")])
        checks.append(("a stamps file that cannot be read stops a change, and is never taken as empty", False))
    except logic.Refused as refused:
        checks.append(("a stamps file that cannot be read stops a change, and is never taken as empty",
                       "cannot be read" in str(refused)))
    return checks
