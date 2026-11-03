"""What a specification says, held to what it must say.

`spec.py check` holds the data's shape, and a file that fails it cannot be kept. What is here holds the content, which a
specification under way falls short of as a matter of course: so nothing here refuses a change. `faults` are what `spec.py open`
lists and `spec.py ready` will not pass: a claim with nothing under it, a state nobody accounted for, a prototype that draws what
the data does not hold. `gaps` are what a review reads: each may be right as it stands, so each is listed and none holds an
agreement.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import evidence
import load as loading
from load import natural
import markup
import prototypes
import shared

NEVER_SAID = ("", "-", "--", "none", "tbd")
NUMBER = re.compile(r"\d")
IDS = re.compile(r"(?<![\w.-])([A-Z]+\d+(?:\.(?:\d+|[a-z][a-z0-9-]*))?)(?![\w-])")
SCREEN = re.compile(r"SC\d+")
SCENARIO = re.compile(r"\bgiven\b.*\bwhen\b.*\bthen\b", re.IGNORECASE | re.DOTALL)
BARE_AMPERSAND = re.compile(r"&(?![a-zA-Z][a-zA-Z0-9]*;|#\d+;|#x[0-9a-fA-F]+;)")
SEPARATE = re.compile(r"[,\s]+")
SHOT = re.compile(r"[\w./-]+\.(?:png|jpe?g|gif|webp)", re.IGNORECASE)
SPECIAL_STATES = ("normal", "any")

# what a prototype draws that shows, says or does something: each carries its own anchor, or stands inside an element that is
# one thing, a link, a button, a line, a heading, an item, a cell, whose anchor is its own
CONTENT_TAGS = frozenset("a button input select textarea img svg picture video audio canvas table h1 h2 h3 h4 h5 h6 p ul ol dl pre "
                         "figure dialog form output progress meter th td dt dd li legend caption figcaption summary label".split())
# an element that holds others, each of which says or does something of its own: its anchor covers none of them
REGION_TAGS = frozenset("main header footer nav section article aside div form fieldset table thead tbody tfoot ul ol dl figure "
                        "details dialog".split())


def fault(node: loading.Node, says: str, line: int = 0) -> dict:
    return {"id": node.id, "file": node.file, "line": line or node.line, "says": says}


def slug(word: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(word).lower()).strip("-")


def said(value: object) -> bool:
    return str(value or "").strip().lower() not in NEVER_SAID


def named(g: dict, state: str) -> str:
    """A state by the one name the grammar knows it by: `Signed out` is `unauthorized`."""
    word = slug(state.split(":", 1)[0])
    return next((one for one, others in g["words"]["states that are one"].items() if word in others), word)


class Links:
    """Each kind's nodes, and each node's links both ways, by relation: what the checks ask of a node, read once."""

    def __init__(self, done: loading.Load) -> None:
        self.nodes: dict[str, list[loading.Node]] = {}
        for node in sorted(done.nodes.values(), key=lambda n: natural(n.id)):
            self.nodes.setdefault(node.kind, []).append(node)
        self.out: dict[tuple[str, str], list[str]] = {}
        self.into: dict[tuple[str, str], list[str]] = {}
        for e in done.edges:
            self.out.setdefault((e.src, e.rel), []).append(e.dst)
            self.into.setdefault((e.dst, e.rel), []).append(e.src)

    def kind(self, kind: str) -> list[loading.Node]:
        return self.nodes.get(kind, [])

    def of(self, ident: str, rel: str) -> list[str]:
        return self.out.get((ident, rel), [])

    def to(self, ident: str, rel: str) -> list[str]:
        return self.into.get((ident, rel), [])


def backed(links: Links, ident: str) -> bool:
    """Whether what a node says stands on something: a finding or a contradiction became it, or an addition says it was added."""
    return bool(links.to(ident, "became") or links.to(ident, "adds to"))


# --- the screens ------------------------------------------------------------------------------------------------------
def screen_faults(g: dict, node: loading.Node, root: Path) -> list[dict]:
    """A screen's States accounted for: a line for every state its kind likely has and every behaviour, each status borne out;
    its Transitions from its states to its states or another screen; its Layout fixed by something."""
    words, out = g["words"], []
    rows = node.fields.get("states") or []
    kind = node.fields.get("kind")
    if not kind:
        out.append(fault(node, f"{node.id} says no kind, so the states it likely has cannot be accounted for: "
                               f"`kind:` -- {', '.join(g['choices']['screen kind'])}"))
    held = {named(g, row["state"]) for row in rows}
    for state in words["screen states"].get(kind, []):
        if state not in held:
            out.append(fault(node, f"{node.id} is a {kind}, which likely has the state `{state}`: a line of its States -- observed, "
                                   f"likely, or n/a and why"))
    for behaviour in words["behaviours"]:
        if behaviour not in held:
            out.append(fault(node, f"{node.id} has no `{behaviour}` line under States: what is established of it, or that it is "
                                   f"likely and how it would be found out"))
    for row in rows:
        what, line = f"{node.id}: its state `{row['state']}`", row["line"]
        status = str(row.get("status", "")).strip("` ").lower()
        shown = str(row.get("what it shows", "")).strip()
        if status not in words["statuses"]:
            out.append(fault(node, f"{what} says {f'`{status}`' if status else 'no status'}: one of {', '.join(words['statuses'])}", line))
        elif status == "observed" and not (said(row.get("evidence")) or SHOT.search(shown)):
            out.append(fault(node, f"{what} is observed and names nothing it was seen in: a finding, under Evidence, or a "
                                   f"screenshot in what it shows", line))
        elif status == "likely" and not said(row.get("investigation")):
            out.append(fault(node, f"{what} is likely and does not say how it would be found out: under Investigation, how it is "
                                   f"reached without harm", line))
        elif status == "n/a" and not said(shown):
            out.append(fault(node, f"{what} is n/a and does not say why", line))
        elif status in ("observed", "stated", "added") and not said(shown):
            out.append(fault(node, f"{what} says nothing of what it shows", line))
        for shot in SHOT.findall(shown):
            if not (root / shot).is_file():
                out.append(fault(node, f"{what} names the screenshot {shot}, and it is not there", line))
    moves = node.fields.get("transitions") or []
    if not moves and kind != "message":
        out.append(fault(node, f"{node.id} has no Transitions: what moves it from one state to another"))
    known = held | set(SPECIAL_STATES)
    for row in moves:
        start, end, line = named(g, row["from"]), str(row.get("to", "")).strip(), row["line"]
        if start not in known:
            out.append(fault(node, f"{node.id}: a transition goes from `{row['from']}`, which is not one of its states", line))
        if said(end) and not SCREEN.fullmatch(end.split(":", 1)[0].strip()) and named(g, end) not in known and not said(row.get("leads to")):
            out.append(fault(node, f"{node.id}: a transition goes to `{end}`, which is neither one of its states nor a screen", line))
        if not said(row.get("event")):
            out.append(fault(node, f"{node.id}: a transition from `{row['from']}` says no event: what the user does, or what happens", line))
        if not said(row.get("shows")) and not said(row.get("evidence")):
            out.append(fault(node, f"{node.id}: a transition names neither the requirement it carries nor the finding it was seen in", line))
    for row in node.fields.get("layout") or []:
        fixed = str(row.get("from", ""))
        if not (said(row.get("what")) and said(row.get("must be")) and said(fixed)):
            out.append(fault(node, f"{node.id}: a row of its Layout needs all three: what, what it must be, and what fixes it", row["line"]))
        elif not IDS.search(fixed) and "foundations" not in fixed.lower():
            out.append(fault(node, f"{node.id}: what fixes `{row['what']}` is `{fixed}`: a requirement or a finding by its ID, or the "
                                   f"word foundations", row["line"]))
    return out


def stands_on_nothing(links: Links) -> list[dict]:
    """Every element and part says what it stands on: the requirement it shows, what it is about, or where it leads."""
    return [fault(node, f"{node.id} stands on nothing: the requirement it shows, what it is about -- a rule, an entity, a foundation "
                        f"-- the screen it leads to, or the component it is")
            for kind in ("element", "part") for node in links.kind(kind)
            if not any(links.of(node.id, rel) for rel in ("shows", "about", "leads to", "is", "asks"))]


# --- the look ----------------------------------------------------------------------------------------------------------------
def design_faults(links: Links) -> list[dict]:
    """Where there are foundations, every screen and component says which it follows: the rules of the look it is drawn by, so
    that a foundation changed reaches it."""
    if not links.kind("foundation"):
        return []
    return [fault(node, f"{node.id} follows no foundation: `follows:` names the foundations its look obeys -- the colours, the "
                        f"text, the spacing, the patterns it draws by")
            for kind in ("screen", "component") for node in links.kind(kind) if not links.of(node.id, "follows")]


# --- what a program calls, and the rest of the product --------------------------------------------------------------------
def endpoint_faults(links: Links) -> list[dict]:
    """An endpoint says who may call it and what it answers, stands on a requirement, and has a surface of its own."""
    out, surfaces = [], {}
    for node in links.kind("endpoint"):
        key = " ".join(str(node.fields.get("surface", "")).lower().split())
        if key in surfaces:
            out.append(fault(node, f"{node.id} has the surface of {surfaces[key]}, `{node.fields['surface']}`: one endpoint per surface"))
        surfaces.setdefault(key, node.id)
        if not node.fields.get("who may call"):
            out.append(fault(node, f"{node.id} does not say who may call it, and what a caller without the right gets: a row of Who may call"))
        if not node.fields.get("answers"):
            out.append(fault(node, f"{node.id} does not say what it answers, status by status: a row of Answers"))
        if not links.of(node.id, "shows"):
            out.append(fault(node, f"{node.id} stands on no requirement: name one, `shows`"))
    return out


def product_faults(done: loading.Load, links: Links) -> list[dict]:
    """What the document, the goals, the requirements and the domain must say to mean anything."""
    out = []
    read_from_material = bool(links.kind("source"))
    document = done.nodes.get("document")
    if document is None:
        out.append({"id": "document", "file": loading.DATA, "line": 0, "says": "there is no document: what the product is, and for whom"})
    else:
        for title, key in (("Problem", "problem"), ("Users", "users"), ("Non-goals", "non-goals")):
            if not said(document.fields.get(key)):
                out.append(fault(document, f"the document says nothing under `## {title}`"))
    for node in links.kind("goal"):
        if not NUMBER.search(str(node.fields.get("target", ""))):
            out.append(fault(node, f"{node.id}'s target has no number: what value counts as success, and by when"))
        today = str(node.fields.get("today", ""))
        if not NUMBER.search(today) and "not measured" not in today.lower():
            out.append(fault(node, f"{node.id}: today has no number: today's value, or `not measured`"))
    for node in links.kind("requirement"):
        if node.fields.get("priority") == "wont" and not said(node.fields.get("why")):
            out.append(fault(node, f"{node.id} is a wont and does not say why: under `## Why`"))
        if said(node.fields.get("from")) and not links.to(node.id, "became") and not any(
                links.to(row, "became") for row in links.of(node.id, "has")):
            out.append(fault(node, f"{node.id} is taken from material, by its `from:`, and no finding became it"))
    for node in links.kind("criterion"):
        if not SCENARIO.search(str(node.fields.get("says", ""))) and done.nodes[node.parent].fields.get("priority") != "wont":
            out.append(fault(node, f"{node.id}: a criterion is `Given ..., when ..., then ...`"))
    for node in links.kind("decision"):
        for key, title in (("because", "Because"), ("instead", "Instead of")):
            if not said(node.fields.get(key)):
                out.append(fault(node, f"{node.id} does not say `## {title}`: a decision says what was chosen, why, and instead of what"))
    for node in links.kind("question"):
        answers = str(node.fields.get("answers", "")).strip()
        if answers.lower().startswith("investigate") and not said(answers.partition(":")[2]):
            out.append(fault(node, f"{node.id} is for the skill to find out, and does not say how: `investigate: how`"))
    for node in links.kind("rule"):
        if not links.of(node.id, "governs"):
            out.append(fault(node, f"{node.id} governs no entity: `applies to:`"))
    for kind in ("rule", "entity") if read_from_material else ():
        for node in links.kind(kind):
            if not backed(links, node.id):
                out.append(fault(node, f"{node.id} stands on no finding and no addition, in a specification read from material"))
    for node in links.kind("flow"):
        if not said(node.fields.get("steps")):
            out.append(fault(node, f"{node.id} has no steps: a line per step, under `## Steps`"))
    return out


# --- the prototypes ------------------------------------------------------------------------------------------------------
class Strict(HTMLParser):
    """What keeps a prototype's markup from being read one way by everyone: a tag left open, a closing tag out of place, an id used
    twice, an image with nothing said of it, a link to nowhere, styles or a script of its own."""

    def __init__(self, links: bool) -> None:
        super().__init__(convert_charrefs=False)
        self.links = links
        self.found: list[tuple[int, str]] = []
        self.stack: list[tuple[str, int]] = []
        self.ids: dict[str, int] = {}

    def say(self, message: str) -> None:
        self.found.append((self.getpos()[0], message))

    def opened(self, tag: str, attrs: list) -> None:
        held = {name: (value or "") for name, value in attrs}
        if tag == "style" or "style" in held:
            self.say(f"<{tag}> carries styles of its own: a prototype takes its look from the product's stylesheet, by a class")
        if tag == "script":
            self.say("a script written in the prototype: what it does belongs in assets/js/prototype.js")
        for name in held:
            if name.startswith("on"):
                self.say(f"an {name} attribute on <{tag}>: a prototype carries no script of its own")
        if "id" in held:
            if held["id"] in self.ids:
                self.say(f"the id `{held['id']}` is used twice, here and at line {self.ids[held['id']]}")
            self.ids.setdefault(held["id"], self.getpos()[0])
        if tag == "img" and "alt" not in held:
            self.say("an image without alt: say what it shows, or alt=\"\" where it shows nothing")
        if tag == "a" and self.links and not (held.get("href") or "data-open" in held or "data-close" in held):
            self.say("a link without href")

    def handle_starttag(self, tag: str, attrs: list) -> None:
        self.opened(tag, attrs)
        if tag not in markup.VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.opened(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag in markup.VOID:
            return
        if not self.stack:
            self.say(f"</{tag}> closes nothing")
        elif self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.say(f"</{tag}> stands where <{self.stack[-1][0]}>, opened at line {self.stack[-1][1]}, is still open")
            for depth in range(len(self.stack) - 1, -1, -1):
                if self.stack[depth][0] == tag:
                    del self.stack[depth:]
                    break


def strict(text: str, links: bool = True) -> list[tuple[int, str]]:
    """What is wrong with a prototype's markup, each at its line. A component's drawing shows what a link looks like, and leads nowhere."""
    reader = Strict(links)
    reader.feed(text)
    reader.close()
    out = list(reader.found) + [(line, f"<{tag}> is never closed") for tag, line in reader.stack]
    for number, line in enumerate(text.splitlines(), 1):
        if BARE_AMPERSAND.search(line):
            out.append((number, "a bare &: write &amp;"))
    return sorted(out)


def linked_to(page: markup.Page, node: markup.Mark) -> str:
    """The screen an element leads to, by a link to that screen's prototype. A link inside an element of its own is that element's."""
    held = re.match(r"(SC\d+)\.html", node.attrs.get("href", "")) if node.tag == "a" else None
    if held:
        return held.group(1)
    for child in node.children:
        if isinstance(child, markup.Mark) and not page.handle(child):
            found = linked_to(page, child)
            if found:
                return found
    return ""


def holds_anchor(page: markup.Page, node: markup.Mark) -> bool:
    return any(isinstance(n, markup.Mark) and n is not node and page.handle(n) for n in node.walk())


def holds_control(node: markup.Mark) -> bool:
    return any(isinstance(n, markup.Mark) and (n.tag in ("button", "form", "input", "select") or "data-open" in n.attrs) for n in node.walk())


def unhandled(page: markup.Page, node: markup.Mark, covered: bool, say) -> None:
    """Every element that shows, says or does something has an anchor of its own, or stands inside one that is one thing. A region
    covers nothing inside it, and what is hidden from everyone who reads the page says nothing."""
    for child in node.children:
        if not isinstance(child, markup.Mark) or child.tag in markup.UNSEEN or child.attrs.get("aria-hidden") == "true":
            continue
        here = covered
        if page.handle(child):
            here = child.tag not in REGION_TAGS
        elif not covered and child.tag in CONTENT_TAGS and not holds_anchor(page, child) \
                and not (child.tag == "label" and child.attrs.get("for")):
            words = child.attrs.get("alt", "") if child.tag == "img" else " ".join(child.text().split())
            say(child.line, f"it draws <{child.tag}> {words[:40]!r} with no anchor: a row of its Elements, or of a component's Parts")
            here = True
        unhandled(page, child, here, say)


READ: dict[str, tuple] = {}         # each prototype read, by its time and size and those of the page around it


def drawing(root: Path, rel: str, links: bool) -> tuple[list[tuple[int, str]], markup.Page, str]:
    """What is wrong with a prototype as markup, the prototype read, and its text: read again only when one of its files has changed."""
    path, shell = root / rel, root / prototypes.SHELL
    seen = path.stat()
    around = shell.stat() if shell.is_file() else None
    stamp = (seen.st_mtime_ns, seen.st_size, around.st_mtime_ns if around else 0, around.st_size if around else 0)
    held = READ.get(str(path))
    if held is None or held[0] != stamp:
        text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        held = READ[str(path)] = (stamp, strict(text, links), markup.Page(root, rel, path.stem), text)
    return held[1], held[2], held[3]


def screen_drawing(g: dict, done: loading.Load, links: Links, node: loading.Node, page: markup.Page, told) -> None:
    """A screen's prototype held to its rows: everything shown anchored, no state its States do not list, and every link said."""
    if page.main.attrs.get("data-prototype") != node.id:
        told(0, f"it does not say whose prototype it is: <main data-prototype=\"{node.id}\">")
    unhandled(page, page.main, False, told)
    listed = {named(g, row["state"]) for row in node.fields.get("states") or []} | {"normal"}
    shown = {word for mark in page.tree.walk() for attribute in ("data-when", "data-unless", "data-states")
             for word in SEPARATE.split(mark.attrs.get(attribute, "").strip()) if word}
    for state in sorted(shown):
        if named(g, state) not in listed:
            told(0, f"it shows the state `{state}`, and {node.id}'s States do not list it")
    anchored: dict[str, list[markup.Mark]] = {}
    for mark in page.main.walk():
        if mark.attrs.get("data-el"):
            anchored.setdefault(f"{node.id}.{mark.attrs['data-el']}", []).append(mark)
    for ident, marks in anchored.items():
        if ident not in done.nodes:
            continue
        says = links.of(ident, "leads to")
        drawn = {linked_to(page, mark) for mark in marks} - {"", node.id}
        for to in sorted(drawn - set(says), key=natural):
            told(marks[0].line, f"{ident} leads to {to} in the prototype, and its row's Leads to does not say so")
        for to in sorted(set(says) - drawn - {node.id}, key=natural):
            if not any(mark.tag in ("button", "form") or "data-open" in mark.attrs or holds_control(mark) for mark in marks):
                told(marks[0].line, f"{ident} leads to {to} by its row, and the prototype draws no link there")
    for reached in sorted(set(SCREEN.findall(str(node.fields.get("reached by", ""))))):
        if reached not in done.nodes:
            told(0, f"{node.id} is reached by {reached}, and no screen has that ID")


def prototype_faults(g: dict, done: loading.Load, links: Links) -> list[dict]:
    """Each prototype read as a browser reads it, its markup strict, and each screen's held to its rows."""
    out = []
    root = done.root
    for kind in ("screen", "component"):
        folder = g["kinds"][kind]["prototype"]
        for node in links.kind(kind):
            rel = f"{prototypes.PROTOTYPES}/{folder}/{node.id}.html"
            if not (root / rel).is_file():
                continue

            def told(line: int, says: str, ident: str = node.id, where: str = rel) -> None:
                out.append({"id": ident, "file": where, "line": line, "says": says})

            wrong, page, text = drawing(root, rel, kind == "screen")
            for line, says in wrong:
                told(line, says)
            if "spec-new" in text:
                told(0, "it still holds an element that says it is to be drawn")
            for mark in page.main.walk():
                target = mark.attrs.get("href", "").split("#")[0].split("?")[0].removesuffix(".html") if mark.tag == "a" else ""
                if SCREEN.fullmatch(target) and target not in done.nodes:
                    told(mark.line, f"it links to {target}, and no screen has that ID")
            if kind == "screen":
                screen_drawing(g, done, links, node, page, told)
    return out


def script_faults(root: Path) -> list[dict]:
    """A prototype's script that finds its elements by the names they had before: it finds nothing, and every screen stops at it."""
    folder = root / prototypes.PROTOTYPES / "assets/js"
    return [{"id": path.name, "file": path.relative_to(root).as_posix(), "line": 0,
             "says": "it finds its elements by `data-spec-element` or `data-spec-part`, and they are `data-el` and `data-part` now: it stops on every screen"}
            for path in sorted(folder.glob("*.js")) if folder.is_dir() and "data-spec-" in path.read_text(encoding="utf-8")]


# --- all of it ------------------------------------------------------------------------------------------------------------
def faults(g: dict, done: loading.Load) -> list[dict]:
    """Everything the content falls short of, in the order of the nodes it is about."""
    links = Links(done)
    out = [item for node in links.kind("screen") for item in screen_faults(g, node, done.root)]
    out += stands_on_nothing(links) + design_faults(links) + endpoint_faults(links) + product_faults(done, links)
    out += prototype_faults(g, done, links) + shared.faults(done) + script_faults(done.root)
    return sorted(out, key=lambda f: (natural(f["id"]), f["line"]))


def gaps(done: loading.Load) -> dict[str, list[dict]]:
    """What a review reads: rules nothing enforces, musts tied to nothing, requirements in no story, what was not read."""
    links = Links(done)
    name = lambda n: {"id": n.id, "name": str(n.fields.get("name") or "")}  # noqa: E731
    requirements = [n for n in links.kind("requirement") if n.fields.get("priority") != "wont"]
    musts = [n for n in requirements if n.fields.get("priority") == "must"]
    shown = {done.nodes[ident].parent or ident for ident, rel in links.into if rel == "shows"}
    told = {found for flow in links.kind("flow")
            for found in IDS.findall(f"{flow.fields.get('steps') or ''}\n{flow.fields.get('goes wrong') or ''}")}
    return {"rules unenforced": [name(n) for n in links.kind("rule") if not links.to(n.id, "enforces")],
            "musts unshown": [name(n) for n in musts if n.id not in shown],
            "musts tied to nothing": [name(n) for n in musts if n.id not in shown and not links.of(n.id, "enforces")],
            "in no story": [name(n) for n in requirements if n.id not in told] if links.kind("flow") else [],
            "endpoints with no fails": [name(n) for n in links.kind("endpoint") if not n.fields.get("fails")],
            "foundations unfollowed": [name(n) for n in links.kind("foundation") if not links.to(n.id, "follows")],
            "read in part": [{"id": n.id, "part": row.get("part", ""), "read": row.get("read", ""), "note": row.get("note", "")}
                             for n in links.kind("source") for row in n.fields.get("coverage") or []
                             if str(row.get("read", "")).strip().lower() != "full"],
            "not captured": evidence.not_captured(done.root)}
