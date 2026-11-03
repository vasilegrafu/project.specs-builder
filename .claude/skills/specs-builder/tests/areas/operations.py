"""The logic: every change one transaction, all or none, logged."""
from __future__ import annotations

import shutil
from pathlib import Path

from support import add, edit, loading, remove, WISH, WISH_TEST


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
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
    result = result_without = logic.apply(root, [logic.parse(WISH)])          # a requirement with no criterion: refused whole
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
    # a requirement and its first criterion in one line, and a change told what still says a number it took out
    made = logic.apply(root, [logic.parse(WISH + ' accepted="Given a signed-in customer on a product, when Save is selected, then it is kept."')])
    wish = next(c["id"] for c in made.changes if c["kind"] == "requirement")
    checks.append(("add requirement takes its first criterion as accepted=, and the refusal of one with none says how",
                   f"{wish}.1" in loading.load(root).nodes and "accepted=" in " ".join(p[2] for p in result_without.problems)))
    told = logic.apply(root, [logic.parse('set R4 statement "When a visitor selects Add to cart on a product in stock, the shop shall add it to their cart, one to six."')])
    checks.append(("a number taken out of a requirement is told where it still stands: the rule it enforces and its own criteria, never the evidence",
                   {d["id"] for d in told.disagree} >= {"B1", "R4.2"} and not any(d["id"].startswith("E") for d in told.disagree)
                   and all("five" in d["says"] for d in told.disagree if d["id"] in ("B1", "R4.2"))))
    return checks
