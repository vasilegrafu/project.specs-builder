"""What is done to a specification that exists: what is open in it, what a change would reach, where a node comes
from and where it shows, and whether it may be agreed.

    open      every question, the most deciding first; every addition not yet confirmed; each quality and risk
              left open, each contradiction unsettled, each finding that became nothing; what is stale; the
              requirements on weak ground; where the content falls short and the gaps a review reads (content.py);
              and, as notes, the words a review reads for (the grammar's `words`)
    impact    before a change: what the node stands on, what would be stale at once if it changed, and what
              further, if those changed in turn; what is unsettled about it, and what is stale already
    trace     why a node is there and where it shows: what it stands on, all the way up; the findings it came
              from, with their quotes and sources; what shows it, the screens and flows around that; who may do it
    ready     why the specification may not be agreed yet -- nothing, once it may
    story     a flow as a user story -- as its user, I want to do what it is named, so that the goals it serves -- and
              every requirement its steps name, with its priority, how well it is backed and its criteria
"""
from __future__ import annotations

import re
from pathlib import Path

import content
import evidence
import inbox
import load as loading
from load import natural
import prototypes
import review

WEAK = ("inferred", "disputed", "added")
PRIORITY = {"must": 0, "should": 1, "could": 2, "wont": 3}
ROWS = ("criterion", "element", "part", "state")


def text_of(g: dict, node: loading.Node) -> str:
    """A node's main words: its first text, or a row's own."""
    for d in g["kinds"][node.kind].get("sections", {}).values():
        said = node.fields.get(d.get("as", ""))
        if d["type"] == "text" and isinstance(said, str) and said:
            return " ".join(said.split())
    return " ".join(str(node.fields.get("says") or node.fields.get("does") or node.fields.get("name") or "").split())


STORY_ID = re.compile(r"\b([A-Z]+\d+)\b")


def lower_first(text: str) -> str:
    return text[:1].lower() + text[1:]


def story_index(done: loading.Load) -> tuple[dict, dict]:
    """What a story reads, gathered once: the goals each flow serves and each requirement's criteria, in their order. Telling
    every story would read every link once for each flow."""
    serves: dict[str, list[str]] = {}
    criteria: dict[str, list[loading.Node]] = {}
    for e in done.edges:
        if e.rel == "serves":
            serves.setdefault(e.src, []).append(e.dst)
    for n in done.nodes.values():
        if n.kind == "criterion" and n.parent:
            criteria.setdefault(n.parent, []).append(n)
    return serves, criteria


def story(g: dict, done: loading.Load, ident: str, index: tuple[dict, dict] | None = None) -> dict:
    """A flow as a user story: "As the visitor, I want to buy a product, so that <the goals it serves>" -- a job with
    no user, "Started by the timer: the nightly run, so that ..." -- and every requirement its steps and what goes
    wrong name, in the order the steps first name them, each with its priority, how well it is backed and its
    criteria. What a team plans from; nothing in it is written for it, all of it is the flow's and the requirements'
    own words. `untold` says what keeps the story from being told whole."""
    flow = done.nodes.get(ident)
    if flow is None or flow.kind != "flow":
        raise KeyError(f"{ident}: no flow has that ID")
    f = flow.fields
    name = str(f.get("name") or ident)
    serves, held = index or story_index(done)
    goals = [str(done.nodes[dst].fields.get("name") or dst).rstrip(".") for dst in serves.get(ident, []) if dst in done.nodes]
    goals = [lower_first(x) for x in goals]
    sep = ";" if any("," in x for x in goals) else ","          # a goal with a comma of its own: semicolons between
    so = (f"{f'{sep} '.join(goals[:-1])}{sep if len(goals) > 2 or sep == ';' else ''} and {goals[-1]}"
          if len(goals) > 1 else (goals[0] if goals else ""))
    who, trigger = str(f.get("user") or ""), str(f.get("trigger") or "")
    head = (f"As {who}, I want to {lower_first(name)}" if who            # a person's flow: its name is what they do
            else f"Started by {trigger}: {lower_first(name)}" if trigger  # a job's: its name is what runs
            else name)
    said = f"{f.get('steps') or ''}\n{f.get('goes wrong') or ''}"
    named_ids = list(dict.fromkeys(m.group(1) for m in STORY_ID.finditer(said)))
    requirements = []
    for rid in named_ids:
        req = done.nodes.get(rid)
        if req is None or req.kind != "requirement":
            continue
        criteria = sorted(held.get(rid, []), key=lambda n: natural(n.id))
        requirements.append({"id": rid, "name": str(req.fields.get("name") or ""),
                             "priority": str(req.fields.get("priority") or ""),
                             "backed": req.fields["confidence"],
                             "criteria": [{"id": c.id, "says": " ".join(str(c.fields.get("says") or "").split())}
                                          for c in criteria]})
    untold = ([] if who or trigger else ["no user and no trigger"]) + ([] if goals else ["serves no goal"]) + \
             ([] if requirements else ["its steps name no requirement"])
    return {"id": ident, "name": name, "story": f"{head}{f', so that {so}' if so else ''}.",
            "requirements": requirements, "must": sum(r["priority"] == "must" for r in requirements),
            "criteria": sum(len(r["criteria"]) for r in requirements), "untold": untold}


def stories(g: dict, done: loading.Load) -> list[dict]:
    index = story_index(done)
    return [story(g, done, n.id, index) for n in sorted(done.nodes.values(), key=lambda n: natural(n.id)) if n.kind == "flow"]


def named(g: dict, node: loading.Node) -> dict:
    words = node.fields.get("name") or text_of(g, node)
    return {"id": node.id, "kind": node.kind,
            "name": words if len(words) <= 90 else words[:87].rsplit(" ", 1)[0] + "..."}


class Graph:
    """The edges both ways, and each row's parent: what the questions below walk."""

    def __init__(self, g: dict, done: loading.Load) -> None:
        self.g, self.done = g, done
        self.out: dict[str, list[loading.Edge]] = {}
        self.into: dict[str, list[loading.Edge]] = {}
        for e in done.edges:
            if e.rel != "has":
                self.out.setdefault(e.src, []).append(e)
                self.into.setdefault(e.dst, []).append(e)

    def top(self, ident: str) -> str:
        node = self.done.nodes.get(ident)
        return node.parent if node is not None and node.parent else ident

    def rows(self, ident: str) -> list[str]:
        return sorted((n.id for n in self.done.nodes.values() if n.parent == ident), key=natural)

    def standing_on(self, ident: str) -> list[tuple[str, loading.Edge]]:
        """Each (node, link) that stands on `ident`: made stale when it changes."""
        out = []
        for e in self.done.edges:
            if e.rel == "has":
                continue
            for stands, on in review.ends(self.g, e):
                if on == ident:
                    out.append((stands, e))
        return out


def worded(g: dict, done: loading.Load) -> list[dict]:
    """Each vague word in a requirement, a criterion or a quality, each technology word in a requirement, and each
    requirement whose statement opens with none of the opening words: notes for a review, never refusals."""
    words = g.get("words", {})
    allowed = [a.lower() for a in words.get("allowed", [])]
    pattern = lambda w: re.compile(rf"(?<![\w-]){re.escape(w)}(?![\w-])", re.IGNORECASE)     # noqa: E731
    vague = [(w, pattern(w)) for w in words.get("vague", [])]
    technology = [(w, pattern(w)) for w in words.get("technology", [])]
    out = []
    for n in sorted(done.nodes.values(), key=lambda n: natural(n.id)):
        if n.kind == "requirement" and n.fields.get("priority") == "wont":
            continue
        said = {"requirement": n.fields.get("statement", ""), "criterion": n.fields.get("says", ""),
                "quality": n.fields.get("says", "")}.get(n.kind)
        if not said:
            continue
        plain = " ".join(str(said).split())
        bare = plain.lower()
        for phrase in allowed:
            bare = bare.replace(phrase, " ")
        found = [w for w, rx in vague if rx.search(bare)]
        if found:
            out.append({"id": n.id, "note": "vague", "words": found})
        if n.kind == "requirement":
            tech = [w for w, rx in technology if rx.search(plain)]
            if tech:
                out.append({"id": n.id, "note": "technology", "words": tech})
            opening = words.get("opening", [])
            if opening and not plain.startswith(tuple(o + end for o in opening for end in (" ", ","))):
                out.append({"id": n.id, "note": "opening", "words": [plain.split(" ", 1)[0]]})
    return out


def engineering(question: dict) -> bool:
    """A question for engineering: `engineering`, or `engineering: the cart team`."""
    return re.match(r"engineering\b", question["answers"].strip().lower()) is not None


def opened(g: dict, done: loading.Load, stamps: dict, stale: list | None = None, now: dict | None = None) -> dict:
    """All that is not settled, in one place. `stale` is what is stale and `now` the prints, where the asker already holds them."""
    graph = Graph(g, done)
    nodes = done.nodes

    def reach(ident: str) -> int:                       # how much stands on a node, rows and all
        return len(graph.into.get(ident, [])) + sum(len(graph.into.get(r, [])) for r in graph.rows(ident))

    questions = []
    for n in (n for n in nodes.values() if n.kind == "question"):
        about = [e.dst for e in graph.out.get(n.id, []) if e.rel == "about"]
        asked_by = [e.src for e in graph.into.get(n.id, [])]
        tops = {graph.top(a) for a in about + asked_by}
        rank = min((PRIORITY.get(nodes[t].fields.get("priority"), 4) for t in tops if t in nodes), default=4)
        weight = sum(reach(t) for t in tops) + len(asked_by)
        questions.append({**named(g, n), "question": n.fields.get("question", ""), "why": n.fields.get("why", ""),
                          "answers": n.fields.get("answers", ""), "about": sorted(about, key=natural),
                          "asked by": sorted(asked_by, key=natural), "rank": rank, "weight": weight})
    questions.sort(key=lambda q: (engineering(q), q["rank"], -q["weight"],
                                  natural(q["id"])))
    additions = [{**named(g, n), "says": n.fields.get("says", ""),
                  "added to": sorted((e.dst for e in graph.out.get(n.id, []) if e.rel == "adds to"), key=natural)}
                 for n in sorted(nodes.values(), key=lambda n: natural(n.id)) if n.kind == "addition"]
    by_kind = lambda kind: sorted((n for n in nodes.values() if n.kind == kind), key=lambda n: natural(n.id))  # noqa: E731
    qualities = [named(g, n) for n in by_kind("quality") if n.fields.get("status", "").strip().lower() not in ("met", "none")]
    held = {n.fields.get("name", "").strip().lower() for n in by_kind("quality")}
    missing = [q for q in g.get("words", {}).get("qualities", []) if q not in held]
    risks = [named(g, n) for n in by_kind("risk") if not n.fields.get("mitigation", "").strip()]
    contradictions = [named(g, n) for n in by_kind("contradiction") if not loading.settled(n)]
    findings = [named(g, n) for n in by_kind("finding")
                if not graph.out.get(n.id) or all(e.rel == "from" for e in graph.out.get(n.id, []))
                if not n.fields.get("became in", "").strip()]
    standing = by_kind("requirement") + by_kind("rule")
    weak = [{**named(g, n), "confidence": n.fields["confidence"]} for n in standing if n.fields["confidence"] in WEAK]
    documented = [named(g, n) for n in standing if n.fields["confidence"] == "documented"]
    now = review.prints(g, done) if now is None else now
    stale = review.stale(g, done, stamps, now) if stale is None else stale
    moved_look = review.look_moved(g, done, stamps)
    return {"questions": questions, "additions": additions, "qualities open": qualities,
            "qualities missing": missing, "risks open": risks,
            "contradictions": contradictions, "findings open": findings, "weak": weak, "documented": documented,
            "stale": sorted({s["node"] for s in stale}, key=natural), "words": worded(g, done),
            "undrawn": [{**named(g, nodes[i]), "look moved": moved_look.get(i, [])} for i in review.undrawn(g, done, stamps, now)],
            "no look": any(n.kind == "screen" for n in nodes.values()) and not any(n.kind == "foundation" for n in nodes.values()),
            "no tokens": any(n.kind == "screen" for n in nodes.values()) and any(n.kind == "foundation" for n in nodes.values())
            and not (done.root / prototypes.TOKENS).is_file(),
            "no domain": sum(n.kind == "requirement" for n in nodes.values()) >= 5
            and not any(n.kind in ("entity", "rule", "role", "term") for n in nodes.values())
            and "domain" not in str(nodes["document"].fields.get("without", "")).lower() if "document" in nodes else False,
            "asked": inbox.read(done.root), "faults": content.faults(g, done), "gaps": content.gaps(done), **material(done)}


LINE = 3                                                # at standard depth, what weighs this much is settled


def investigate(g: dict, done: loading.Load, moved: list[dict]) -> list[dict]:
    """What the skill finds out itself, before anyone is asked, the heaviest first: each question whose `answers`
    is `investigate:`, each screen state that is `likely`, each permission nobody knows, each entity's state no
    screen displays, each part of the material changed since it was read. A row weighs 3 for each `must` that leans
    on it, 1 for each other requirement, and 2 more where who may do what is in it."""
    graph = Graph(g, done)
    nodes = done.nodes

    def reaches(ids: set[str]) -> set[str]:             # the requirements a set of nodes leans on, rows and all
        out: set[str] = set()
        for ident in ids:
            for at in {ident, graph.top(ident), *graph.rows(ident)}:
                if at in nodes and nodes[at].kind == "requirement":
                    out.add(at)
                for e in graph.out.get(at, []):
                    top = graph.top(e.dst)
                    if top in nodes and nodes[top].kind == "requirement":
                        out.add(top)
        return out

    def weight(ids: set[str], access: bool = False) -> int:
        held = reaches(ids)
        return sum(3 if nodes[r].fields.get("priority") == "must" else 1 for r in held) + (2 if access else 0)

    out = []
    for n in nodes.values():
        if n.kind == "question" and n.fields.get("answers", "").strip().lower().startswith("investigate"):
            about = {e.dst for e in graph.out.get(n.id, []) if e.rel == "about"}
            out.append({"what": "question", "id": n.id, "says": text_of(g, n),
                        "how": n.fields["answers"].split(":", 1)[1].strip() if ":" in n.fields["answers"] else "",
                        "weight": weight(about)})
        elif n.kind == "screen":
            for row in n.fields.get("states") or []:
                if str(row.get("status", "")).strip().lower() == "likely":
                    out.append({"what": "state", "id": n.id, "says": f"{row.get('state', '')}: "
                                f"{row.get('what it shows', '') or 'what it shows is not known'}",
                                "how": row.get("investigation", ""), "weight": weight({n.id},
                                                                                      row.get("state") == "unauthorized")})
        elif n.kind == "entity":
            for state in (s for s in nodes.values() if s.parent == n.id and s.kind == "state"):
                if not any(e.rel == "displays" for e in graph.into.get(state.id, [])):
                    governed = {e.src for e in graph.into.get(n.id, []) if e.rel == "governs"}
                    out.append({"what": "lifecycle state no screen shows", "id": state.id,
                                "says": state.fields.get("means", "") or state.fields.get("name", ""), "how": "",
                                "weight": weight({r for b in governed for r in
                                                  (e.src for e in graph.into.get(b, []) if e.rel == "enforces")})})
    for e in done.edges:
        if e.rel == "may or may not":
            out.append({"what": "permission nobody knows", "id": e.src, "says": f"may {e.src} do {e.dst}?",
                        "how": "", "weight": weight({e.dst}, True)})
    for m in moved:
        resting = [n.id for n in nodes.values() if n.kind == "finding"
                   and any(x.rel == "from" and x.dst == m["source"] for x in graph.out.get(n.id, []))
                   and evidence.place_of(n.fields.get("where", "")) in (m["part"], evidence.place_of(m["part"]))]
        out.append({"what": "material changed since it was read", "id": m["source"], "says": m["part"],
                    "how": f"read it again; the findings resting on it: {', '.join(resting) or 'none'}",
                    "weight": weight({b for f in resting for b in (x.dst for x in graph.out.get(f, []) if x.rel == "became")})})
    return sorted(out, key=lambda r: (-r["weight"], natural(r["id"])))


def material(done: loading.Load) -> dict:
    """What the reading of material leaves open: staging files not merged, disagreements not reconciled, and each
    part read that is not what it was when it was read."""
    root = done.root
    staging = root / evidence.STAGING
    staged = sorted(p.relative_to(root).as_posix() for p in staging.glob("*.md")
                    if p.name != Path(evidence.DISAGREEMENTS).name) if staging.is_dir() else []
    kept = root / evidence.DISAGREEMENTS
    sources = {i: {"where": n.fields.get("where", ""), "coverage": n.fields.get("coverage") or []}
               for i, n in done.nodes.items() if n.kind == "source"}
    moved = evidence.moved(root, sources)
    return {"staged": staged, "disagreements": evidence.DISAGREEMENTS if kept.is_file() else "",
            "material moved": moved, "unaccounted": evidence.unaccounted(root, sources),
            "sites": evidence.sites(root), "to investigate": investigate(loading.grammar(), done, moved)}


def ready(g: dict, done: loading.Load, stamps: dict, o: dict | None = None, agreeing: bool = False) -> list[str]:
    """Why the specification may not be agreed: every reason, or none. `o` is what `opened` said, where the asker has it. `agreeing`
    says it is being agreed now, so what moved since the last agreement is what is being agreed, and holds nothing."""
    if done.problems:
        return [f"{len(done.problems)} problem(s) in the data"]
    o = opened(g, done, stamps) if o is None else o
    out = []
    if o["stale"]:
        out.append(f"stale, to be read again and confirmed: {', '.join(o['stale'])}")
    if o["undrawn"]:
        out.append(f"prototypes to look at, for what they show has changed: {', '.join(n['id'] for n in o['undrawn'])}")
    if o["no look"]:
        out.append("screens with no design system: ask for the look, and write it as foundations")
    if o["no tokens"]:
        out.append(f"a look with no {prototypes.TOKENS}: the values every page draws with live there, `scripts/tokens.py --apply` writes them")
    if o["no domain"]:
        out.append("no Domain: no entity, rule, role or term beside the requirements -- write what the product means, or say "
                   "`without: domain` in the document, with why under its Boundary")
    if o["staged"]:
        out.append(f"staged and not merged: {', '.join(o['staged'])}")
    if o["disagreements"]:
        out.append(f"disagreements not reconciled: {o['disagreements']}")
    if o["material moved"]:
        out.append("material changed since it was read: " +
                   ", ".join(f"{m['source']} {m['part']}" for m in o["material moved"]))
    if o["unaccounted"]:
        out.append(f"material not accounted for: {len(o['unaccounted'])} file(s), the first "
                   f"{o['unaccounted'][0]['source']} {o['unaccounted'][0]['file']}")
    faults = [x for x in o["sites"] if not x["note"]]
    if faults:
        out.append(f"captures not whole: {len(faults)}, the first {faults[0]['file']}: {faults[0]['says']}")
    if o["additions"]:
        out.append(f"added and not confirmed: {', '.join(a['id'] for a in o['additions'])}")
    if o["qualities missing"]:
        out.append(f"no quality says anything of {', '.join(o['qualities missing'])}")
    if o["asked"]:
        out.append("waiting in the inbox, not taken in: " +
                   ", ".join(f"#{a['no']} about {', '.join(a['about']) or 'nothing named'}" for a in o["asked"]))
    if o["faults"]:
        about = list(dict.fromkeys(f["id"] for f in o["faults"]))
        out.append(f"where the content falls short, `spec.py open` says each: {len(o['faults'])}, in {', '.join(about[:12])}"
                   f"{' ...' if len(about) > 12 else ''}")
    if review.status_of(done) == "agreed" and not agreeing:
        moved = review.since_agreed(g, done)
        if moved and moved["changes"]:
            out.append(f"changed since it was agreed on {moved['on']}: {', '.join(c['id'] for c in moved['changes'][:12])}"
                       f"{' ...' if len(moved['changes']) > 12 else ''}")
    product = [q["id"] for q in o["questions"] if not engineering(q)]
    if product:
        out.append(f"open for the product side: {', '.join(product)}")
    untold = [f"{s['id']} ({', '.join(s['untold'])})" for s in stories(g, done) if s["untold"]]
    if untold:
        out.append(f"flows whose story cannot be told: {'; '.join(untold)}")
    for key, said in (("qualities open", "qualities open"), ("risks open", "risks with no mitigation"),
                      ("contradictions", "contradictions unsettled"), ("findings open", "findings that became nothing")):
        if o[key]:
            out.append(f"{said}: {', '.join(n['id'] for n in o[key])}")
    return out


def capabilities(g: dict, done: loading.Load) -> list[dict]:
    """What the product lets people do, one row to a flow: the outcome, who may take it, the rules it meets, the requirements it carries,
    the screens and endpoints it goes through; and a last row for the requirements no flow carries. A view of the graph, with no ID and
    no page of its own."""
    graph = Graph(g, done)
    nodes = done.nodes
    rules_of = lambda ids: sorted({e.dst for r in ids for e in graph.out.get(r, []) if e.rel == "enforces"}, key=natural)  # noqa: E731
    index = story_index(done)
    rows, carried = [], set()
    for flow in sorted((n for n in nodes.values() if n.kind == "flow"), key=lambda n: natural(n.id)):
        ids = [r["id"] for r in story(g, done, flow.id, index)["requirements"]]
        carried |= set(ids)
        rows.append({"flow": flow.id, "outcome": flow.fields.get("name", ""),
                     "who": sorted({e.src for r in ids for e in graph.into.get(r, []) if e.rel == "may"}, key=natural),
                     "rules": rules_of(ids), "requirements": ids,
                     "through": [e.dst for e in graph.out.get(flow.id, []) if e.rel in ("passes", "calls")]})
    loose = sorted((n.id for n in nodes.values() if n.kind == "requirement" and n.id not in carried and n.fields.get("priority") != "wont"), key=natural)
    if rows and loose:
        rows.append({"flow": "", "outcome": "Carried by no flow", "who": [], "rules": rules_of(loose), "requirements": loose, "through": []})
    return rows


def impact(g: dict, done: loading.Load, stamps: dict, ident: str) -> dict:
    """What a change to `ident` would reach, said before the change is made."""
    graph = Graph(g, done)
    node = done.nodes.get(ident)
    if node is None:
        raise KeyError(f"{ident}: no node has that ID")
    changing = {ident}
    if node.parent and g["kinds"][done.nodes[node.parent].kind].get("print rows"):
        changing.add(node.parent)                       # a criterion changed changes its requirement
    at_once: dict[str, list[str]] = {}
    on_name: dict[str, list[str]] = {}                  # what stands on a few fields only, by its relation's `stale on`
    for c in changing:
        for stands, e in graph.standing_on(c):
            if stands not in changing:
                (on_name if review.stale_on(g, e) else at_once).setdefault(stands, []).append(f"{e.src} {e.rel} {e.dst}")
    further: set[str] = set()
    wave = set(at_once)
    while wave:
        nxt = set()
        for w in wave:
            ups = {w}
            parent = done.nodes[w].parent
            if parent and g["kinds"][done.nodes[parent].kind].get("print rows"):
                ups.add(parent)
            for u in ups:
                for stands, _ in graph.standing_on(u):
                    if stands not in changing and stands not in at_once and stands not in further:
                        nxt.add(stands)
        further |= nxt
        wave = nxt
    stands_on = [{"rel": e.rel, **named(g, done.nodes[on])} for e in done.edges if e.rel != "has"
                 for stands, on in review.ends(g, e) if stands == ident]
    unsettled = sorted({e.src for e in graph.into.get(ident, []) if done.nodes[e.src].kind in ("question", "addition")}
                       | {e.dst for e in graph.out.get(ident, []) if done.nodes[e.dst].kind == "question"}, key=natural)
    stale = [s for s in review.stale(g, done, stamps) if s["node"] in changing or s["on"] in changing]
    return {**named(g, node), "rows": graph.rows(ident), "stands on": stands_on,
            "stale at once": [{**named(g, done.nodes[i]), "by": at_once[i]} for i in sorted(at_once, key=natural)],
            "stale on name": [{**named(g, done.nodes[i]), "by": on_name[i]} for i in sorted(on_name, key=natural) if i not in at_once],
            "further": [named(g, done.nodes[i]) for i in sorted(further, key=natural)],
            "unsettled": [named(g, done.nodes[i]) for i in unsettled], "stale already": stale}


def trace(g: dict, done: loading.Load, ident: str) -> dict:
    """Why a node is there, and where it shows."""
    graph = Graph(g, done)
    node = done.nodes.get(ident)
    if node is None:
        raise KeyError(f"{ident}: no node has that ID")
    own = [ident, *graph.rows(ident)]
    up: list[dict] = []
    seen = set(own)
    wave = [(i, 0) for i in own]
    while wave:                                         # what it stands on, and what that stands on, upwards
        at, depth = wave.pop(0)
        for e in graph.out.get(at, []):
            far = done.nodes[e.dst]
            if e.dst in seen or far.kind in ("finding", "source", "question", "addition") or e.rel == "leads to":
                continue
            if not any(stands == at and on == e.dst for stands, on in review.ends(g, e)):
                continue
            seen.add(e.dst)
            up.append({"from": at, "rel": e.rel, "depth": depth + 1, **named(g, far)})
            if depth < 3:
                wave.append((e.dst, depth + 1))
    came = []
    for i in own:
        for e in graph.into.get(i, []):
            src = done.nodes[e.src]
            if src.kind in ("finding", "contradiction") and e.rel == "became":
                sources = [s.dst for s in graph.out.get(src.id, []) if s.rel == "from"]
                came.append({**named(g, src), "became": i, "quote": src.fields.get("quote", ""),
                             "where": src.fields.get("where", ""), "seen": src.fields.get("seen", ""),
                             "sources": [named(g, done.nodes[s]) for s in sources]})
    shown = []
    for i in own:
        for e in graph.into.get(i, []):
            if e.rel != "shows":
                continue
            top = graph.top(e.src)
            flows = sorted({f.src for f in graph.into.get(top, []) if f.rel == "passes"}, key=natural)
            shown.append({**named(g, done.nodes[e.src]), "shows": i, "on": top if top != e.src else "",
                          "flows": flows})
    done_by = [{"rel": g["relations"][e.rel]["back"], **named(g, done.nodes[e.src])}
               for e in graph.into.get(ident, []) if e.rel in ("may", "may not", "may or may not")]
    spoken = [{"rel": g["relations"][e.rel]["back"], **named(g, done.nodes[e.src])}
              for i in own for e in graph.into.get(i, [])
              if e.rel not in ("shows", "became", "may", "may not", "may or may not")]
    return {**named(g, node), "says": text_of(g, node), "backed": node.fields.get("confidence", ""), "stands on": up,
            "came from": came, "shown by": shown, "done by": done_by, "spoken of by": spoken}
