"""What whoever builds from a specification asks of it, and how each is answered: what the product is, the slices to
build, all one piece of work needs, how a screen looks, its tests, what is not settled, and how to find a thing.

An agent of any make asks these in any technology: `guide/build.md` is the procedure, `guide/query.md` every command.
The specification says what and why, never how. Each answer is read from the data as it stands, and says first if
anything in it is stale.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import api
import build
import drawn
import finish
import load as loading
import meant
import prototypes
import redrawn
import review
from answer import BUDGET, Answer, cell, table  # noqa: F401 -- BUDGET is the command line's default
from load import natural
from model import EVIDENCE, Model

BUILD_ORDER = ("document", "foundation", "term", "entity", "rule", "role", "component", "endpoint", "screen", "flow",
               "requirement", "question")


def plural(count: int, kind: str) -> str:
    return f"{count} {kind if count == 1 else kind[:-1] + 'ies' if kind.endswith('y') else kind + 's'}"


def said_nothing(value: object) -> bool:
    """Whether a cell of a table says nothing: empty, or a dash or `none` written in its place."""
    return str(value or "").strip().lower() in ("", "-", "--", "—", "none", "n/a")


def in_order(model: Model, refs: list[str]) -> list[str]:
    """Nodes in the order they are built: what others stand on first."""
    return sorted(refs, key=lambda r: (BUILD_ORDER.index(model.kind(r)) if model.kind(r) in BUILD_ORDER else 99, natural(r)))


def whole(model: Model, ref: str) -> str:
    """An ID with all its node says of itself, uncut."""
    return f"{ref} {model.text(ref)}".strip()


def stands_on(model: Model, ref: str) -> str:
    return "; ".join(drawn.stands_on(model, ref))


# --- what a node says, kind by kind ----------------------------------------------------------------------------------
def said_of(model: Model, ref: str, brief: bool = False) -> list[str]:
    """What a node says, in markdown, by its kind: all a builder needs of it; `brief` leaves out its rows."""
    node = model.need(ref)
    f, kind = node.fields, node.kind
    out: list[str] = []

    def line(label: str, value: object) -> None:
        if value:
            out.append(f"- {label}: {cell(value) if not isinstance(value, str) else ' '.join(value.split())}")

    def text(value: object) -> None:
        if value:
            out.extend(["", str(value).strip()])

    def unsettled() -> None:
        questions = model.questions_on([ref])
        if questions:
            out.append(f"- ⚠ Not settled: {'; '.join(whole(model, q) for q in questions)} -- ask before building what they touch")

    if kind == "requirement":
        out += [f"**{model.named(ref)}** ({f.get('priority', '')})" + (f", stands {f['confidence']}" if f.get("confidence") else ""),
                "", str(f.get("statement", ""))]
        text(f.get("why") and f"Why: {f['why']}")
        text(f.get("details"))
        if model.rows(ref):
            out += ["", "Accepted when:", *(f"{c} {model.nodes[c].fields.get('says', '')}" for c in model.rows(ref)), ""]
        line("Serves", [model.named(g) for g in model.out(ref, "serves")])
        line("Enforces", [model.named(b) for b in model.out(ref, "enforces")])
        line("Depends on", [model.named(r) for r in model.out(ref, "depends on")])
        line("Refines", [model.named(r) for r in model.out(ref, "refines")])
        line("Conflicts with", [model.named(r) for r in model.out(ref, "conflicts with")])
        unsettled()
        out += [f"- Added, not confirmed: {model.nodes[a].fields.get('says', '')}" for a in model.into(ref, "adds to")]
    elif kind == "screen":
        out += [f"**{model.named(ref)}**: {f.get('purpose', '')}", ""]
        for key in ("kind", "address", "who", "reached by"):
            line(key[0].upper() + key[1:], f.get(key))
        line("Prototype", drawn.prototype_of(model, ref))
        line("Leads to", [model.named(s) for s in model.out(ref, "leads to")])
        line("Shows", [model.named(r) for r in model.out(ref, "shows")])
        unsettled()
        if f.get("data"):
            out += ["", "What it shows or changes:", *table(["What", "Shows", "About"], [
                [r.get("what it shows or changes"), r.get("shows"), ", ".join(model.building(re.split(r"[,\s]+", r.get("about") or "")))]
                for r in f["data"]])]
        if f.get("states"):
            out += ["", "States:", *table(["State", "Status", "What it shows"], [[r.get("state"), r.get("status"), r.get("what it shows")]
                                                                                 for r in f["states"]])]
        if f.get("transitions"):
            out += ["", "Transitions:", *table(["From", "When", "To", "Requirements"], [
                [m.get("from"), m.get("event"), m.get("to") or m.get("leads to"), m.get("shows")] for m in f["transitions"]])]
        if f.get("layout"):
            out += ["", "Layout:", *table(["What", "Must be"], [[r.get("what"), r.get("must be")] for r in f["layout"]])]
        if f.get("variants"):
            out += ["", "Variants:", *(f"- {r.get('what differs, and for whom')}" for r in f["variants"])]
        if not brief and model.rows(ref):
            out += ["", "Elements, each `data-el=\"<#>\"` in the prototype:",
                    *table(["#", "Element", "Is", "Does", "States", "Stands on"], [
                        [e.split(".", 1)[1], model.nodes[e].fields.get("name"), model.nodes[e].fields.get("is"),
                         model.nodes[e].fields.get("does"), model.nodes[e].fields.get("states"), stands_on(model, e)]
                        for e in model.rows(ref)])]
    elif kind == "component":
        out += [f"**{model.named(ref)}**: {f.get('purpose', '')}", ""]
        line("Prototype, with its drawings", drawn.prototype_of(model, ref))
        line("Made of", [model.named(c) for c in model.out(ref, "made of")])
        unsettled()
        if f.get("variants"):
            out += ["", "Variants:", *table(["Variant", "When"], [[v.get("variant"), v.get("when")] for v in f["variants"]])]
        text(f.get("rules") and f"Rules:\n\n{f['rules']}")
        if not brief and model.rows(ref):
            out += ["", "Parts, each `data-part=\"<id>\"` where it is drawn:",
                    *table(["Part", "Name", "Is", "Does", "States", "Stands on"], [
                        [p, model.nodes[p].fields.get("name"), model.nodes[p].fields.get("is"), model.nodes[p].fields.get("does"),
                         model.nodes[p].fields.get("states"), stands_on(model, p)] for p in model.rows(ref)])]
    elif kind == "flow":
        out += [f"**{model.named(ref)}**: {f.get('purpose', '')}", ""]
        line("Who", f.get("user"))
        line("Started by", f.get("trigger"))
        line("Passes", [model.named(s) for s in model.out(ref, "passes")])
        line("Calls", [model.named(x) for x in model.out(ref, "calls")])
        line("Serves", [model.named(g) for g in model.out(ref, "serves")])
        text(f.get("steps") and f"Steps:\n\n{f['steps']}")
        text(f.get("goes wrong") and f"When it goes wrong:\n\n{f['goes wrong']}")
    elif kind == "endpoint":
        out += [f"**{model.named(ref)}**: {f.get('purpose', '')}", ""]
        line("Surface", f.get("surface"))
        line("Kind", f.get("kind"))
        line("Shows", [model.named(r) for r in model.out(ref, "shows")])
        line("About", [model.named(x) for x in model.building(model.out(ref, "about"))])
        unsettled()
        for key in ("who may call", "takes", "answers", "fails", "limits"):
            rows = f.get(key) or []
            if rows:
                head = [k for k in rows[0] if k != "line"]
                out += ["", f"{key[0].upper() + key[1:]}:", *table([h[0].upper() + h[1:] for h in head], [[r.get(h) for h in head] for r in rows])]
        text(f.get("example") and f"Example:\n\n{f['example']}")
    elif kind == "entity":
        out += [f"**{model.named(ref)}**: {f.get('about', '')}", ""]
        if f.get("fields"):
            out += ["Fields:", *table(["Field", "Means"], [[r.get("field"), r.get("meaning")] for r in f["fields"]])]
        if model.rows(ref):
            out += ["", "States:", *table(["State", "Means", "Moves to"], [
                [s.split(".", 1)[1], model.nodes[s].fields.get("means"), ", ".join(model.out(s, "moves"))] for s in model.rows(ref)])]
        if f.get("lifecycle"):
            out += ["", "Lifecycle:", *table(["State", "Event", "Guard", "Effect", "Next"], [
                [m.get("state"), m.get("event"), m.get("guard"), m.get("effect"), m.get("next")] for m in f["lifecycle"]])]
        line("Governed by", [model.named(b) for b in model.into(ref, "governs")])
        unsettled()
    elif kind == "rule":
        out.append(f"**{model.named(ref)}**: {f.get('says', '')}")
        line("Except", f.get("except"))
        line("Governs", [model.named(n) for n in model.out(ref, "governs")])
        line("Made true by", [model.named(r) for r in model.into(ref, "enforces")])
    elif kind == "role":
        out.append(f"**{model.named(ref)}**: {f.get('who', '') or f.get('about', '')}")
        if f.get("actions"):
            out += ["", *table(["Action", "May"], [[f"{x.get('about')} {x.get('action', '')}", x.get("answer")] for x in f["actions"]])]
    elif kind == "foundation":
        out += [f"**{f.get('name', ref)}**", "", str(f.get("says", ""))]
    elif kind == "question":
        out.append(f"**{ref}** {f.get('question', '')}")
        line("Why it matters", f.get("why"))
        line("Who answers", f.get("answers"))
        line("About", [model.named(x) for x in model.building(model.out(ref, "about"))])
    elif kind == "document":
        for key, value in f.items():
            if value:
                out += [f"### {key[0].upper() + key[1:]}", "", str(value), ""]
    else:
        out.append(f"**{model.named(ref)}** ({kind})")
        for key, value in f.items():
            if key != "name" and value:
                line(key, value)
        for rel, other in model.outward.get(ref, []):
            if rel != "has" and (kind in EVIDENCE or model.kind(other) not in EVIDENCE):
                line(rel, model.named(other))
    return out


# --- the first questions ---------------------------------------------------------------------------------------------
def looks(root: Path) -> dict[str, str]:
    """Where the look is, of what there is of it."""
    held = {"page": prototypes.SHELL, "styles": f"{prototypes.PROTOTYPES}/assets/css/product.css", "tokens": prototypes.TOKENS,
            "sample data": drawn.SAMPLE, "script": f"{prototypes.PROTOTYPES}/assets/js/prototype.js"}
    return {k: v for k, v in held.items() if (root / v).is_file()}


def capability_rows(model: Model) -> list[str]:
    return table(["Outcome", "Who", "Rules", "Requirements", "Through"], [
        [f"{c['flow']} {c['outcome']}".strip(), ", ".join(c["who"]), ", ".join(c["rules"]), ", ".join(c["requirements"]), ", ".join(c["through"])]
        for c in finish.capabilities(loading.grammar(), model.done)])


def capabilities(model: Model, args) -> Answer:
    a = Answer("What it lets people do: each flow, who may take it, the rules it meets, what it carries")
    a.add("", capability_rows(model) or ["No flow yet: what the product lets people do is read from its flows."], 10)
    return a


def overview(model: Model, args) -> Answer:
    done = model.done
    doc = model.nodes.get("document")
    f = doc.fields if doc else {}
    a = Answer(f"{f.get('name') or api.title(model.root)}: what it is, and how to build it")
    a.add("", [f"Status: {f.get('status') or '?'}. Ask this tool for what the specification says; open a prototype only "
               f"for what is drawn, which `look` gives. An agent that builds changes nothing in `data/` or `prototypes/`."], 10)
    for key, weight in (("summary", 9), ("problem", 6), ("users", 8), ("non-goals", 7), ("release plan", 8), ("journey", 4),
                        ("assumptions", 3), ("boundary", 6), ("interface", 6)):
        if f.get(key):
            a.add(key[0].upper() + key[1:], [str(f[key]).strip()], weight, "node document")
        elif key == "release plan":
            a.add("Release plan", ["None stated: ask if there are any."], weight)
    qualities = model.of_kind("quality")
    a.add("Quality requirements", table(["Quality", "Status", "Requirement"], [
        [model.named(q), model.nodes[q].fields.get("status"), model.nodes[q].fields.get("says")] for q in qualities])
        or ["None stated: ask if there are any."], 8, "qualities")
    constraints = model.of_kind("constraint")
    a.add("Constraints", [f"- {c} {model.nodes[c].fields.get('says', '')}" for c in constraints]
          or ["None stated: ask if there are any."], 8, "qualities")
    a.add("Decisions", table(["ID", "Decision", "Because", "Instead of"], [
        [d, model.nodes[d].fields.get("decision"), model.nodes[d].fields.get("because"), model.nodes[d].fields.get("instead")]
        for d in model.of_kind("decision")]), 6, "list decision")
    a.add("Risks", table(["Risk", "If it happens", "Likelihood", "What is done about it"], [
        [f"{k} {model.nodes[k].fields.get('risk', '')}", model.nodes[k].fields.get("if"), model.nodes[k].fields.get("likelihood"),
         model.nodes[k].fields.get("mitigation")] for k in model.of_kind("risk")]), 7, "list risk")
    counts: dict[str, int] = {}
    for n in done.nodes.values():
        counts[n.kind] = counts.get(n.kind, 0) + 1
    musts = [r for r in model.of_kind("requirement") if model.priority(r) == "must"]
    building = {k: n for k, n in sorted(counts.items()) if k not in EVIDENCE}
    a.add("What it holds", [", ".join(plural(n, k) for k, n in building.items()) + f"; {len(done.edges)} links; "
                            f"{plural(len(musts), 'requirement')} a must."], 7)
    slices = model.slices()
    a.add("The slices, in the order to build them", table(["Slice", "Builds", "Completes", "Criteria", "Blocked by"], [
        [f"{p['id']} {p['name']}", len(p["new"]), len(p["new requirements"]), p["criteria"], ", ".join(p["blocked by"])]
        for p in slices]), 9, "plan")
    held = looks(model.root)
    if held:
        a.add("Where the look is", [f"- {k}: `{v}`" for k, v in held.items()], 7)
    wont = [model.named(r) for r in model.of_kind("requirement") if model.priority(r) == "wont"]
    a.add("Never build", [f"- {w}" for w in wont], 6)
    a.add("What it lets people do", capability_rows(model), 7, "capabilities")
    a.add("How to build it", [
        "1. `plan`, then each slice in order: `unit <slice>` for all it needs, `open <slice>` for what is not settled in "
        "it, `tests <slice>` for its tests, `look <screen>` for how each screen looks. Write the tests first, then the "
        "code; name each criterion's ID in its test, and each requirement's ID in the code and the commit that carry it.",
        "2. A must before a should; never a wont. Where `open <slice>` lists something, ask: never decide it in code.",
        "3. What is drawn -- the prototypes, the components' drawings, the styles, the tokens -- is a picture to build to "
        "in your technology, never code to copy.",
        "4. A slice is done when its tests pass and `coverage --target <your code>` names every criterion of every "
        "requirement it completes.",
        "5. When the specification changes, `changed --target <your code>` names what to build again; `app/guide/build.md` "
        "is the whole procedure."], 10)
    stale = sorted({s["node"] for s in build.stale_of(model.root, done)}, key=natural)
    a.data = {"name": f.get("name") or api.title(model.root), "kind": f.get("kind", ""), "status": f.get("status", ""),
              "summary": f.get("summary", ""), "counts": dict(sorted(counts.items())), "links": len(done.edges),
              "open questions": model.of_kind("question"), "stale": stale,
              "slices": [{k: p[k] for k in ("id", "name", "criteria", "blocked by")} for p in slices], "look": held}
    a.next = ["plan", f"unit {slices[0]['id']}" if slices else "list requirement", "open"]
    return a


def plan(model: Model, args) -> Answer:
    slices = model.slices()
    a = Answer(f"{model.name('document') or api.title(model.root)}: the slices to build, in order")
    a.add("", ["Each slice builds its nodes in the order listed: what they stand on first. A requirement shown in more "
               "than one slice is completed in the last slice that builds something showing it, never before the first "
               "flow that names it or what it depends on, and each earlier slice builds its part of it. A requirement is done when its criteria "
               "pass. A screen may lead to one a later slice builds: build the link, and it leads there once that slice "
               "is built."], 10)
    for n, p in enumerate(slices, 1):
        made = [model.named(r) if r != "document" else "what holds over the whole (`node document`)" for r in in_order(model, p["new"])]
        lines = [f"- Builds: {', '.join(made) or 'nothing new'}",
                 *([f"- Uses, built in an earlier slice: {', '.join(in_order(model, p['earlier']))}"] if p["earlier"] else []),
                 "- Requirements it completes: " + (", ".join(f"{r} ({model.priority(r)}{model.release_name(r)})" for r in p["new requirements"]) or "none"),
                 *([f"- Requirements it carries on, completed in another slice: {', '.join(r for r in p['requirements'] if r not in p['new requirements'])}"]
                   if len(p["requirements"]) > len(p["new requirements"]) else []),
                 *([f"- A should, or a later release: {', '.join(p['later'])} -- build after the musts"] if p["later"] else []),
                 *([f"- Needs first, from a later slice: {', '.join(p['needs first'])}"] if p["needs first"] else []),
                 f"- Rules: {', '.join(p['rules']) or 'none'}",
                 f"- Done when: {p['criteria']} acceptance criteria pass" if p["criteria"]
                 else f"- Done when: the rules and transitions `tests {p['id']}` lists hold, and what it builds stands for the slices after it"]
        if p["blocked by"]:
            lines.append(f"- ⚠ Blocked by: {', '.join(p['blocked by'])} -- `open {p['id']}` says each; ask first")
        a.add(f"{n}. {p['id']} · {p['name']}", lines, 10 - min(n, 8), f"unit {p['id']}")
    wont = [model.named(r) for r in model.of_kind("requirement") if model.priority(r) == "wont"]
    a.add("Never build", [f"- {w}" for w in wont], 9)
    a.data = {"slices": slices, "never": wont}
    a.next = [f"unit {slices[0]['id']}" if slices else "list requirement", "open"]
    return a


def limits_of(model: Model, refs: list[str]) -> list[str]:
    """What each finding behind these nodes says it does not establish."""
    found = sorted({x for r in refs for x in model.into(r, "became") if model.kind(x) == "finding"}, key=natural)
    return [f"- {x} (behind {', '.join(r for r in model.out(x, 'became') if r in refs)}): {model.nodes[x].fields.get('limits')}"
            for x in found if model.nodes[x].fields.get("limits")]


def unit(model: Model, args) -> Answer:
    ref = args.id
    piece = model.slice(ref)
    if piece is None:
        model.need(ref)
        nodes, requirements = [ref], [r for r in model.shown_by([ref]) if r != ref]
        title = f"{model.named(ref)}: all it needs"
    else:
        nodes, requirements = piece["nodes"], piece["requirements"]
        title = f"Slice {piece['id']} · {piece['name']}: all it needs"
    earlier = set(piece["earlier"]) if piece else set()
    a = Answer(title)
    order = in_order(model, nodes)
    if "document" in order:
        a.add("What holds over the whole product", ["The users, the qualities, the constraints and the decisions bind every "
                                                    "slice: `overview` says them, `node document` in full."], 9)
    told = ("quality", "constraint", "decision") if piece and piece["id"] == "foundation" else ()     # `overview` says these
    for weight, refs in ((9, [r for r in order if model.kind(r) == "flow"]),
                         (8, [r for r in order if model.kind(r) not in ("flow", "screen", "document", "foundation", *told)]),
                         (5, [r for r in order if model.kind(r) == "foundation"])):
        for r in refs:
            a.add(model.named(r), said_of(model, r), weight, f"node {r}")
    for r in [x for x in order if model.kind(x) == "screen"]:
        if r in earlier:
            a.add(f"{model.named(r)}, built in an earlier slice", said_of(model, r, brief=True)[:1], 4, f"node {r}")
            continue
        brief = said_of(model, r, brief=True)
        a.add(model.named(r), brief, 8, f"node {r}")
        a.add(f"{r}: its elements", said_of(model, r)[len(brief):], 5, f"look {r}")
    a.add("The requirements it carries", [line for r in requirements for line in [*said_of(model, r), ""]], 9, f"tests {ref}")
    if model.kind(ref) == "requirement":
        flows = [f for f in model.of_kind("flow") if ref in model.carried(f)]
        a.add("Where it shows", [f"- {model.named(x)}" + (f", on {model.top(x)}" if model.top(x) != x else "") for x in model.into(ref, "shows")]
              + [f"- {model.named(f)}, a step names it" for f in flows], 8)
    rules = sorted({b for r in requirements for b in model.out(r, "enforces")} - set(nodes), key=natural)
    a.add("The rules they enforce", [line for b in rules for line in said_of(model, b)], 7, "rules")
    entities = {e for b in rules for e in model.out(b, "governs")}
    for r in nodes:
        for node in (r, *model.rows(r)):
            entities |= {model.top(s) for s in model.out(node, "displays")}
            entities |= {model.top(x) for x in model.out(node, "about") if model.kind(model.top(x)) == "entity"}
    entities = sorted(entities - set(nodes), key=natural)
    a.add("The entities they touch", [line for n in entities for line in [*said_of(model, n), ""]], 6, "schema")
    may = []
    for u in model.of_kind("role"):
        for action in model.nodes[u].fields.get("actions", []):
            if action.get("about") in {*requirements, *nodes}:
                may.append([model.named(u), f"{action.get('about')} {action.get('action', '')}", action.get("answer")])
    a.add("Who may", table(["Role", "Action", "May"], may), 7, "permissions")
    blocked = model.questions_on([*nodes, *requirements])
    a.add("⚠ Not settled -- ask before building what these touch", [line for q in blocked for line in said_of(model, q)], 10, f"open {ref}")
    a.add("What the evidence did not establish -- ask, or build only what it did", limits_of(model, [*requirements, *nodes]), 7, f"open {ref}")
    touched = {*nodes, *requirements}
    risks = [k for k in model.of_kind("risk") if touched & set(model.out(k, "about"))]
    a.add("Risks on it", [f"- {k} {model.nodes[k].fields.get('risk', '')} ({model.nodes[k].fields.get('likelihood', '')}) -- "
                          f"{model.nodes[k].fields.get('mitigation', '')}" for k in risks], 7, "list risk")
    if not model.of_kind("endpoint") and piece and piece["id"] != "foundation" and model.of_kind("screen"):
        a.add("The API", ["The specification holds no endpoint: what the screens send and receive is not specified as an "
                          "API. Design it from the screens' data and the requirements, and say so in your plan."], 8)
    drawn_here = [r for r in nodes if model.kind(r) in ("screen", "component")]
    if drawn_here:
        a.add("Where its look is", [f"- {model.named(r)}: `{drawn.prototype_of(model, r)}` -- `look {r}`" for r in drawn_here], 6)
    if args.evidence:
        found = sorted({x for r in [*requirements, *nodes] for x in model.into(r, "became") if model.kind(x) == "finding"}, key=natural)
        a.add("The evidence behind it", [f"- {x}: {model.nodes[x].fields.get('found', '')}"
                                         + (f" -- `{model.nodes[x].fields['quote']}`" if model.nodes[x].fields.get("quote") else "")
                                         for x in found], 2)
    a.data = {"slice": ref, "nodes": nodes, "requirements": requirements, "rules": rules, "entities": entities, "blocked by": blocked}
    if piece is None:
        held = build.unit(model.root, ref, model.done)
        if not args.evidence:
            held["links"] = [x for x in held["links"] if x["kind"] not in EVIDENCE]
            held["back"] = [x for x in held["back"] if x["kind"] not in EVIDENCE]
        a.data |= held
    a.next = [f"open {ref}", f"tests {ref}", *(f"look {r}" for r in drawn_here[:2])]
    return a


def look(model: Model, args) -> Answer:
    ref = args.id
    node = model.need(ref)
    if node.kind not in ("screen", "component"):
        raise KeyError(f"{ref} is a {node.kind}: `look` answers for a screen or a component")
    a = Answer(f"{model.named(ref)}: how it looks")
    rel = drawn.prototype_of(model, ref)
    drawn_there = (model.root / rel).is_file()
    route = f"/prototype/{ref}.html" if node.kind == "screen" else f"/prototype/components/{ref}.html"
    how = (f"`{rel}` is the part of the page this one adds; `python app/serve.py --port 8765` shows it whole, in the "
           f"product's look, at `http://127.0.0.1:8765{route}`.")
    if node.kind == "screen":
        a.add("", [f"The prototype is the screen working, in the product's look, on sample data: a picture to build to, "
                   f"never code to copy. {how} Each element below is found in it by its selector." if drawn_there else
                   "This screen has no prototype: build its look from the foundations and the components below."], 10)
        a.add("Its elements", table(["#", "Selector", "Element", "Is", "Does", "States", "Heard as", "Component"], [
            [e.split(".", 1)[1], f"[data-el=\"{e.split('.', 1)[1]}\"]", model.nodes[e].fields.get("name"), model.nodes[e].fields.get("is"),
             model.nodes[e].fields.get("does"), model.nodes[e].fields.get("states"), model.nodes[e].fields.get("heard as"),
             ", ".join(model.named(c) for c in model.out(e, "is"))] for e in model.rows(ref)]), 9)
        a.add("Its states", table(["State", "Status", "What it shows"], [
            [r.get("state"), r.get("status"), r.get("what it shows")] for r in node.fields.get("states", [])]), 6, f"states {ref}")
        a.add("Layout", table(["What", "Must be", "From"], [[r.get("what"), r.get("must be"), r.get("from")]
                                                            for r in node.fields.get("layout", [])]), 8)
        components = sorted({c for e in model.rows(ref) for c in model.out(e, "is")}, key=natural)
        a.add("The components it is made of", [f"- {model.named(c)}: `{drawn.prototype_of(model, c)}` -- `look {c}`" for c in components], 7)
    else:
        a.add("", [f"`{rel}` draws each variant: a picture to build to, never code to copy. {how}"], 10)
        a.add("Variants", table(["Variant", "When"], [[v.get("variant"), v.get("when")] for v in node.fields.get("variants", [])]), 9)
        a.add("Parts", table(["Part", "Selector", "Name", "Is", "Does", "States", "Heard as"], [
            [p, f"[data-part=\"{p}\"]", model.nodes[p].fields.get("name"), model.nodes[p].fields.get("is"), model.nodes[p].fields.get("does"),
             model.nodes[p].fields.get("states"), model.nodes[p].fields.get("heard as")] for p in model.rows(ref)]), 8)
        a.add("Rules", [str(node.fields["rules"])] if node.fields.get("rules") else [], 8)
    held = looks(model.root)
    a.add("The product's values", [f"- {k}: `{v}`" for k, v in held.items()]
          + ["- `spec.py tokens` gives the tokens as CSS, which the page links as `assets/css/tokens.css`; no such file is kept.",
             "- The tokens and the styles' values become the theme of the technology the product is built in."], 7)
    foundations = model.of_kind("foundation")
    followed = model.out(ref, "follows")
    a.add("The foundations it follows", [f"- {model.named(f)}: `node {f}`" for f in followed]
          + ([f"- and the rest: {', '.join(f for f in foundations if f not in followed)}"] if len(followed) < len(foundations) else [])
          if followed else [f"- {model.named(f)}: `node {f}`" for f in foundations]
          or ["No design system is written yet: ask for the look, never pick one."], 6)
    a.data = {"id": ref, "prototype": rel if drawn_there else "", "address": route,
              "elements": [{"id": e, "name": model.name(e)} for e in model.rows(ref)]}
    a.next = [f"outline {ref}", f"words {ref}", f"forms {ref}", f"states {ref}", f"styles {ref}"]
    return a


def tests(model: Model, args) -> Answer:
    ref = args.id or "all"
    piece = model.slice(ref) if ref != "all" else None
    if ref == "all":
        requirements = model.order()
    elif piece:
        requirements = piece["requirements"]
    else:
        node = model.need(ref)
        requirements = ([ref] if node.kind == "requirement" else [node.parent] if node.kind == "criterion" else
                        model.into(ref, "enforces") if node.kind == "rule" else
                        sorted({r for b in model.into(ref, "governs") for r in model.into(b, "enforces")}, key=natural)
                        if node.kind == "entity" else model.shown_by([ref]))
    if args.ui:
        screens = (model.of_kind("screen") if ref == "all" else [s for s in piece["nodes"] if model.kind(s) == "screen"] if piece
                   else [model.top(ref)] if model.kind(model.top(ref)) == "screen" else [])
        if not screens:
            raise KeyError(f"{ref}: no screen in it, so nothing on a screen to test -- `tests {ref}` gives its criteria")
        return drawn.ui_cases(model, screens)
    a = Answer(f"The tests of {ref}")
    completes = set(piece["new requirements"]) if piece else set(requirements)
    found = [{"id": c, "requirement": r, "says": model.nodes[c].fields.get("says", "")} for r in requirements if r in completes
             for c in model.rows(r)]
    if args.gherkin:
        for r in [r for r in requirements if r in completes]:
            lines = ["```gherkin", f"Feature: {model.named(r)}", f"  {model.nodes[r].fields.get('statement', '')}", ""]
            for t in (t for t in found if t["requirement"] == r):
                lines += ["  " + row for row in build.gherkin(t).splitlines()] + [""]
            a.add(f"{r}.feature", lines + ["```"], 8)
    else:
        home = {r: p["id"] for p in model.slices() for r in p["new requirements"]}
        for r in [r for r in requirements if r in completes]:
            a.add(f"{model.named(r)} ({model.priority(r)}{model.release_name(r)})",
                  [f"- `{t['id']}` {t['says']}" for t in found if t["requirement"] == r], 8)
        carried = [f"- {model.named(r)}: completed in {home.get(r, '?')}, where its criteria are tested" for r in requirements if r not in completes]
        a.add("Carried on: tested where each is completed", ["This slice builds its part of each, and the transitions below.", "", *carried]
              if carried else [], 6)
        nodes = piece["nodes"] if piece else list(model.nodes) if ref == "all" else [ref]
        rules = (piece["rules"] if piece else sorted({b for r in completes for b in model.out(r, "enforces")}
                                                     | {n for n in nodes if model.kind(n) == "rule"}
                                                     | {b for n in nodes if model.kind(n) == "entity" for b in model.into(n, "governs")}, key=natural))
        a.add("Each rule holds", [f"- `{b}` {model.nodes[b].fields.get('says', '')}" for b in rules], 7)
        moves = []
        for s in in_order(model, list(nodes)):
            fields = model.nodes[s].fields
            for m in fields.get("transitions", []) if model.kind(s) == "screen" else []:
                moves.append(f"- `{s}` {m.get('from')} -- {m.get('event')} --> {m.get('to') or m.get('leads to')}")
            for m in fields.get("lifecycle", []) if model.kind(s) == "entity" else []:
                if said_nothing(m.get("event")) or said_nothing(m.get("next")):
                    continue                            # a state nothing moves on from
                guard = "" if said_nothing(m.get("guard")) else f" [{m.get('guard')}]"
                effect = "" if said_nothing(m.get("effect")) else f"; then {m.get('effect')}"
                moves.append(f"- `{s}` {m.get('state')} -- {m.get('event')}{guard} --> {m.get('next')}{effect}")
        a.add("Each transition happens", moves, 6)
    if not found and not a.sections:
        a.add("", [f"{ref} has no criterion to test."], 9)
    a.add("", ["Name each test with its case's ID, as `R4.1`, so that `coverage` finds it."], 9)
    a.data = {"tests": found, "requirements": requirements}
    a.next = ["coverage --target <your code>"]
    return a


def opened(model: Model, args) -> Answer:
    """What is not settled in one slice or node; `spec.py open` alone is the keeper's whole list."""
    ref = args.id
    piece = model.slice(ref)
    if piece is None:
        model.need(ref)
    refs = [*piece["nodes"], *piece["requirements"]] if piece else [ref]
    a = Answer(f"What is not settled in {ref}")
    questions = model.questions_on(refs)
    for q in questions:
        blocks = [p["id"] for p in model.slices() if q in p["blocked by"]]
        a.add(q, said_of(model, q) + ([f"- Blocks: {', '.join(blocks)}"] if blocks else []), 9)
    a.add("What the evidence did not establish", limits_of(model, refs), 7)
    added = [f"- {r}: {model.nodes[x].fields.get('says', '')}" for r in refs for x in model.into(r, "adds to")]
    a.add("Added by the skill, not yet confirmed", added, 6)
    stamps = review.held(model.root)
    mine = set(refs)
    leaning = [r for r in finish.opened(model.g, model.done, stamps)["to investigate"] if r["id"] in mine]
    a.add("To investigate", table(["Weight", "What", "ID", "Says"], [[r["weight"], r["what"], r["id"], r["says"]] for r in leaning]), 5)
    a.exit = 1 if a.sections else 0
    a.add("", ["Ask the person the specification is for; never decide what is not settled in code. "
               "`ask \"<question>\" --about <IDs> --by \"<who>\"` leaves it for whoever keeps the specification."
               if a.sections else f"Nothing is unsettled in {ref}."], 10)
    a.data = {"questions": questions, "added": added, "to investigate": leaning}
    a.next = [f"tests {ref}"] if piece else ["plan"]
    return a


# --- finding your way ------------------------------------------------------------------------------------------------
def node(model: Model, args) -> Answer:
    ref = args.id
    found = model.need(ref)
    depth = max(1, args.depth)
    a = Answer(f"{model.named(ref)} ({found.kind})")
    a.add("", said_of(model, ref) + ["", f"File: `{found.file}`, line {found.line} · fingerprint "
                                         f"{loading.fingerprint(model.g, found)}"], 10)
    reached = {r: 0 for r in [ref, *model.rows(ref)]}
    rim = set(reached)
    for step in range(1, depth + 1):
        next_rim = set()
        for here in rim:
            for rel, there in [*model.outward.get(here, []), *model.inward.get(here, [])]:
                if rel != "has" and there not in reached:
                    next_rim.add(there)
        reached |= {r: step for r in next_rim}
        rim = next_rim
    rows = [[model.named(r), d, model.kind(r), model.nodes[r].file]
            for r, d in sorted(reached.items(), key=lambda i: (i[1], natural(i[0]))) if d]
    a.add("Around it", table(["Node", "Edges away", "Kind", "File"], rows), 6, f"node {ref} --depth 1")
    a.data = {"id": ref, "kind": found.kind, "file": found.file, "line": found.line, "fields": found.fields,
              "around": [{"id": r, "depth": d} for r, d in reached.items() if d]}
    a.next = [f"edges {ref}", f"unit {ref}"]
    return a


def edges(model: Model, args) -> Answer:
    ref = args.id
    model.need(ref)
    wanted = args.rel
    a = Answer(f"The edges of {model.named(ref)}")
    out = [(r, b) for r, b in model.outward.get(ref, []) if not wanted or r == wanted]
    into = [(x, r) for r, x in model.inward.get(ref, []) if not wanted or r == wanted]
    a.add("From it", [f"- {ref} {r} {model.named(b)}" for r, b in out], 9)
    a.add("To it", [f"- {model.named(x)} {r} {ref}" for x, r in into], 9)
    if not out and not into:
        a.add("", [f"{ref} has no edge" + (f" of the relation {wanted}" if wanted else "") + "."], 9)
    a.data = {"out": out, "in": into}
    a.next = [f"node {ref}"]
    return a


def listed(model: Model, args) -> Answer:
    kind = args.id
    kinds = model.g["kinds"]
    if kind in ("kinds", "kind"):
        counts: dict[str, int] = {}
        for n in model.nodes.values():
            counts[n.kind] = counts.get(n.kind, 0) + 1
        a = Answer("Every kind of node")
        a.add("", table(["Kind", "Nodes", "Is"], [[k, counts.get(k, 0), kinds[k].get("is", "")] for k in kinds]), 9)
        a.data = {"kinds": {k: counts.get(k, 0) for k in kinds}}
        a.next = ["list requirement"]
        return a
    if kind not in kinds:
        raise KeyError(f"{kind}: no node is of that kind; the kinds are {', '.join(kinds)}")
    refs = model.of_kind(kind)
    a = Answer(f"Every {kind}")
    if not refs:
        a.add("", [f"The specification holds no {kind}." + (" What the screens send and receive is not specified as an API: "
                                                              "design it from the screens' data and the requirements."
                                                              if kind == "endpoint" else "")], 9)
        a.next = ["plan"]
        return a
    a.add("", [f"- {whole(model, r)}" + (f" ({model.priority(r)})" if kind == "requirement" else "") for r in refs], 9)
    a.data = {"nodes": [{"id": r, "name": model.name(r)} for r in refs]}
    a.next = [f"node {refs[0]}"]
    return a


def folded(text: str) -> str:
    """Words as a search reads them: in small letters, without their accents -- Inês is ines."""
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


def find(model: Model, args) -> Answer:
    words = folded(args.id)
    hits = []
    for ref in sorted(model.nodes, key=lambda r: (model.kind(r) in EVIDENCE, natural(r))):
        for key, value in model.nodes[ref].fields.items():
            text = api.said_in(value) if not isinstance(value, (int, float)) else ""
            at = folded(text).find(words)
            if at >= 0:
                hits.append([model.named(ref), key, "…" + " ".join(text[max(0, at - 50):at + len(words) + 50].split()) + "…"])
                break
    a = Answer(f"What says \"{args.id}\"")
    a.add("", table(["Node", "Field", "Where"], hits[:60]) if hits else ["Nothing says it."], 9)
    if len(hits) > 60:
        a.add("", [f"{len(hits) - 60} more, left out: `--json` holds them all."], 8)
    a.data = {"hits": [{"node": h[0].split()[0], "field": h[1]} for h in hits]}
    a.next = [f"node {hits[0][0].split()[0]}"] if hits else ["list requirement"]
    return a


# --- what moved ------------------------------------------------------------------------------------------------------
def changed(model: Model, args) -> Answer:
    if not args.target:
        raise ValueError("changed needs the code built from it: --target <folder>")
    c = build.changed(model.root, args.target.resolve(), args.since, args.until)
    a = Answer(f"What changed since {c['since']}" + (f", up to {c['until']}" if c["until"] != "now" else ""))
    told = [build.told(change) for change in c["changes"]]
    a.add("The nodes", told, 9)
    for word in ("new", "gone", "changed"):
        if c["files"][word]:
            a.add(f"Files of the prototypes, {word}", [f"- `{f}`" for f in c["files"][word]], 6)
    moved = c["drawn"]
    if moved is None:
        a.add("", ["This snapshot was taken before snapshots kept what the prototypes draw: their files are told, not their "
                   "elements. The next snapshot keeps them."], 8)
    else:
        a.add("On the screens, as their prototypes draw them", table(["Screen", "Element", "What", "Was", "Is"], redrawn.changes_table(moved["screens"])), 8)
        a.add("The product's styles", table(["Under", "Selector", "Property", "Was", "Is"], [
            [s["media"] or "-", s["selector"], s["property"], s["was"], s["is"]] for s in moved["styles"]]), 7)
        a.add("The design tokens", table(["Token", "Was", "Is"], [list(t) for t in moved["tokens"]]), 6)
        a.add("The sample data", table(["Value", "Was", "Is"], [list(t) for t in moved["sample"]]), 6)
    a.add("Slices to build again", [f"- {s}" for s in c["slices"]], 10)
    a.add("What to build again", [f"- {k}: {', '.join(v)}" for k, v in c["build again"].items()], 10)
    a.add("Tests to run again", [f"- `{t}`" for t in c["tests to run again"]] + [f"- `tests {s} --ui`" for s in c["ui tests"]], 10)
    a.add("Tests to take out", [f"- `{t}`" for t in c["tests to remove"]], 10)
    a.add("Screens to look at again", [f"- {model.named(s)}" for s in c["screens reached"] if s in model.nodes], 5)
    if not (c["changes"] or any(c["files"].values())):
        a.add("", ["Nothing moved: the code was built from the specification as it stands."], 10)
    a.data = c
    a.next = [f"unit {s}" for s in c["slices"][:3]]
    return a


# --- the model as files, for a program that reads JSON rather than asking --------------------------------------------
def export_model(model: Model, into: Path | None = None) -> Path:
    """The data as `export/model/`: index.json lists every node, nodes/ holds one file for each, edges.tsv every link,
    stands.tsv what stands on what, and openapi.json the API's description where there is one."""
    place = into or model.root / "export/model"
    (place / "nodes").mkdir(parents=True, exist_ok=True)
    for old in (place / "nodes").glob("*.json"):
        old.unlink()
    for ref, n in model.nodes.items():
        held = {"id": ref, "kind": n.kind, "parent": n.parent, "file": n.file, "fields": n.fields,
                "out": {}, "in": {}}
        for rel, other in model.outward.get(ref, []):
            held["out"].setdefault(rel, []).append(other)
        for rel, other in model.inward.get(ref, []):
            held["in"].setdefault(rel, []).append(other)
        (place / "nodes" / f"{ref}.json").write_text(json.dumps(held, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    index = {"name": model.name("document"), "nodes": [{"id": r, "kind": model.kind(r), "name": model.name(r), "file": f"nodes/{r}.json"}
                                                       for r in sorted(model.nodes, key=natural)], "slices": model.slices()}
    (place / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    (place / "edges.tsv").write_text("src\trel\tdst\n" + "".join(f"{e.src}\t{e.rel}\t{e.dst}\n" for e in model.done.edges),
                                     encoding="utf-8", newline="\n")
    grammar = loading.grammar()
    stands = sorted({(near, e.rel, far) for e in model.done.edges if e.rel != "has" for near, far in review.ends(grammar, e)})
    (place / "stands.tsv").write_text("node\trel\ton\n" + "".join(f"{near}\t{rel}\t{far}\n" for near, rel, far in stands),
                                      encoding="utf-8", newline="\n")
    held = meant.api_of(model)
    if held is not None:
        (place / "openapi.json").write_text(json.dumps(held, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return place


COMMANDS = {"overview": overview, "capabilities": capabilities, "plan": plan, "unit": unit, "look": look, "tests": tests, "node": node, "edges": edges,
            "list": listed, "find": find, "changed": changed, "outline": drawn.outline, "words": drawn.words, "forms": drawn.forms,
            "links": drawn.links, "states": drawn.states, "styles": drawn.styles, "tokens": drawn.tokens, "sample": drawn.sample,
            "messages": drawn.messages, "schema": meant.schema, "lifecycle": meant.lifecycle,
            "permissions": meant.permissions, "rules": meant.rules, "glossary": meant.glossary,
            "qualities": meant.qualities, "openapi": meant.openapi}
NEEDS_ID = {"unit", "look", "node", "edges", "list", "find", "outline", "words", "forms", "links", "states", "styles", "lifecycle"}


def answer(root: Path, args) -> int:
    """One question answered and printed; how the command exits."""
    if args.command in NEEDS_ID and not args.id:
        print(f"{args.command} needs what it is asked about: `spec.py {args.command} <...>`", file=sys.stderr)
        return 2
    model = Model(root, build.loaded(root))
    said = opened(model, args) if args.command == "open" else COMMANDS[args.command](model, args)
    stale = sorted({s["node"] for s in build.stale_of(root, model.done)}, key=natural)
    if stale:
        said.warning = (f"{plural(len(stale), 'node')} stale -- {', '.join(stale[:6])}{' and more' if len(stale) > 6 else ''}: "
                        f"each stands on something that changed since it was reviewed. Say so before building from them.")
    print(said.json() if args.json else said.markdown(args.budget), end="")
    return said.exit
