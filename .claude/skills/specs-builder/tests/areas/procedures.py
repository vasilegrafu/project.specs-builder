"""The procedures: answer, additions, tables, agree, what is open, impact, trace, a new specification."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from support import edit, loading, natural, SKILL, WISH, WISH_TEST


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
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
    # what is stale, confirmed, and the prototypes looked at; then it may be agreed, and nothing missing
    owed_now = review.stale(g, loading.load(root), review.held(root))
    for s_ in sorted({s["node"] for s in owed_now}, key=natural):
        logic.apply(root, [logic.parse(f"confirm {s_} {review.owed_print(owed_now, s_)}")])
    why = refused(["set document status agreed"])
    checks.append(("nothing stale, a prototype not looked at since what it shows changed still holds an agreement", "prototypes to look at" in why))
    for s_ in review.undrawn(g, loading.load(root), review.held(root)):
        logic.apply(root, [logic.parse(f"confirm-drawn {s_}")])
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
    checks.append(("impact of a criterion reaches what stands on its requirement, and says apart what stands on its name alone",
                   {"SC3.13", "F1"} <= {n["id"] for n in impact["stale at once"]} and "U1" in {n["id"] for n in impact["stale on name"]}))
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
                   {"SC3.13", "F1"} <= {s["node"] for s in tried.stale} and "U1" not in {s["node"] for s in tried.stale}
                   and {s["on"] for s in tried.stale} == {"R4"}
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
    made = logic.raise_from_inbox(root, first["no"], "the product side")
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
