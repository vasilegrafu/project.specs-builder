"""The logic: every change to a specification, made as one transaction over its files.

    add <kind> <name> [key=value ...]          a new node, numbered from the counter: `add requirement "Keep a
                                               wish list" priority=should serves=G2 statement="... shall ..."`; a
                                               kind with no name -- a finding -- by its words
    add-row <parent> [key=value ...]           a criterion, an element or a part: `add-row R4 says="Given ..."`,
                                               `add-row SC3 name="Wish list" is=button component=C1 shows=R17`;
                                               an entity's state, named by its word: `add-row N2 state=open`
    set <id> <key> <value>                     a field, a text, a cell: `set R4 priority should`; a table whole,
                                               its lines parted by `\n`
    add-line <id> <table> [first] [col=value ...]
                                               a line of a table that is not a node's rows -- a screen's states,
                                               transitions, data, variants or layout; an entity's fields or
                                               lifecycle; an endpoint's takes, answers, fails: `add-line SC3 states
                                               empty status=likely investigation="open it with nothing in the cart"`
    remove-line <id> <table> <first cell>      the line of that table whose first cell says it
    tie <id> <relation> <id> [words]           a link, written where the grammar says it is written
    untie <id> <relation> <id>                 a link taken out
    remove <id> [--untie]                      a node and its rows; refused while anything links to it, unless
                                               --untie takes those links out too; its ID is retired for good
    confirm <id>                               read against what it stands on as that is now: its links stamped
                                               again, so it is stale no more
    answer <question> "<decided>" [because="..."] [instead="..."] [name="..."]
                                               a question settled: a decision made of the answer, about what the
                                               question was about; every link to the question moved to the
                                               decision, a row that asked it now about it; the question removed.
                                               Refused while a text still names it: write the answer there first
    confirm-added <addition | id>              an addition the user confirmed: taken out, its ID retired; given a
                                               node, every addition to it and to its rows
    retarget <id> <id>                         every link to the first, and every mention of it in a text, moved to
                                               the second; what defines the first is left as it is

A specification whose document is agreed takes no change but one that sets it back to draft; it is agreed only
when nothing stands in the way -- nothing stale, every addition confirmed, every open question one for engineering,
no quality or risk left open, no contradiction unsettled, no finding that became nothing.

In a change set, `$1` is the ID the first operation made or touched, `$2` the second's: `add requirement ...` then
`add-row $1 says="..."`. A change set is applied in order, each operation on what the one before left, and then
held whole to the grammar:
if anything in the result does not load clean, every file goes back as it was, and nothing is said to have
changed. Only one writer works at a time: a lock in .cache/ holds the others back. What was applied is appended to
stamps/changes.jsonl -- when, who, why, the operations, and each node's fields before and after -- and the IDs
handed out raise the counters in stamps/ids.json, which never go down; a removed ID is retired there and refused if
it is ever written again.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import edit
import finish
import load as loading
import nodefile
import prototypes
import review

STAMPS = "stamps"
IDS = f"{STAMPS}/ids.json"
CHANGES = f"{STAMPS}/changes.jsonl"
KNOWN = f"{STAMPS}/known.json"
LOCK = f"{loading.CACHE}/write.lock"
LOCK_STALE = 120                      # seconds after which a lock nobody let go of is taken as abandoned
LOCK_WAIT = 10


class Refused(Exception):
    """An operation that cannot be done as asked: said, and nothing is changed."""


@dataclass
class Change:
    """The files a change set touches, each as it was before, so that a refusal puts every one back."""
    root: Path
    before: dict[str, bytes | None] = field(default_factory=dict)

    def path(self, name: str) -> Path:
        return self.root / name

    def read(self, name: str) -> str:
        return self.path(name).read_text(encoding="utf-8")

    def keep(self, name: str) -> None:
        if name not in self.before:
            path = self.path(name)
            self.before[name] = path.read_bytes() if path.exists() else None

    def write(self, name: str, text: str) -> None:
        self.keep(name)
        path = self.path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        fresh = path.with_name(path.name + ".new")
        fresh.write_text(text, encoding="utf-8", newline="\n")
        os.replace(fresh, path)

    def delete(self, name: str) -> None:
        self.keep(name)
        self.path(name).unlink(missing_ok=True)

    def restore(self) -> None:
        for name, raw in self.before.items():
            path = self.path(name)
            if raw is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)


class Lock:
    """The one writer: a file made only if it is not there, holding who made it and when."""

    def __init__(self, root: Path) -> None:
        self.path = root / LOCK

    def __enter__(self) -> "Lock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        waited = 0.0
        while True:
            try:
                handle = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(handle, json.dumps({"pid": os.getpid(), "at": time.time()}).encode())
                os.close(handle)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > LOCK_STALE:
                        self.path.unlink(missing_ok=True)       # abandoned: whoever held it is long gone
                        continue
                except FileNotFoundError:
                    continue
                if waited >= LOCK_WAIT:
                    raise Refused("another change is being written to this specification; try again in a moment")
                time.sleep(0.2)
                waited += 0.2

    def __exit__(self, *exc) -> None:
        self.path.unlink(missing_ok=True)


def held_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


@dataclass
class State:
    """What the operations work on: the grammar, the data as it stands, and the counters."""
    root: Path
    g: dict
    done: loading.Load
    ids: dict
    confirmed: set = field(default_factory=set)
    gone: set = field(default_factory=set)

    def again(self) -> None:
        self.done = loading.load(self.root)

    def node(self, ident: str) -> loading.Node:
        found = self.done.nodes.get(ident)
        if found is None:
            raise Refused(f"{ident}: no node has that ID")
        return found


def natural(ident: str) -> list:
    return [int(x) if x.isdigit() else x for x in re.findall(r"\d+|\D+", ident)]


def next_id(state: State, head: str, existing: list[str]) -> str:
    """One above the highest of its kind ever handed out -- the counter, or what the data holds, whichever is
    higher -- and the counter raised to it: a removed ID is never given again."""
    numbers = [int(i[len(head):]) for i in existing if re.fullmatch(rf"{re.escape(head)}\d+", i)]
    numbers += [int(r[len(head):]) for r in state.ids.get("retired", {}) if re.fullmatch(rf"{re.escape(head)}\d+", r)]
    number = max([state.ids.get("next", {}).get(head, 1) - 1, *numbers, 0]) + 1
    state.ids.setdefault("next", {})[head] = number + 1
    return f"{head}{number}"


def header_order(g: dict, kind: str) -> list[str]:
    return ["id", *g["kinds"][kind].get("fields", {}),
            *[r["field"] for r in g["relations"].values() if kind in r["from"] and "field" in r]]


def section_order(g: dict, kind: str) -> list[str]:
    return list(g["kinds"][kind].get("sections", {}))


def key_of(word: str) -> str:
    return word.replace("_", " ").replace("-", " ").strip().lower()


def pairs(args: list[str]) -> dict[str, str]:
    out = {}
    for arg in args:
        key, eq, value = arg.partition("=")
        if not eq:
            raise Refused(f"`{arg}` is not key=value")
        out[key_of(key)] = value
    return out


def op_add(state: State, change: Change, args: list[str]) -> str:
    if len(args) < 2:
        raise Refused("add <kind> <name> [key=value ...]")
    kind, name, given = args[0], args[1], pairs(args[2:])
    spec = state.g["kinds"].get(kind)
    if spec is None or "folder" not in spec:
        listed = ", ".join(k for k, s in state.g["kinds"].items() if "folder" in s)
        raise Refused(f"{kind}: no kind that has a file of its own; they are {listed}")
    ident = next_id(state, spec["id"], list(state.done.nodes))
    links = {r["field"]: rel for rel, r in state.g["relations"].items() if kind in r["from"] and "field" in r}
    texts = {d.get("as"): title for title, d in spec.get("sections", {}).items() if d["type"] == "text"}
    header = [("id", ident)]
    said: dict[str, str] = {}
    if "name" in spec.get("fields", {}):
        header.append(("name", name))
    else:                                               # a kind with no name -- a finding -- is added by its words
        said[next(t for t, d in spec.get("sections", {}).items() if d["type"] == "text")] = name
    for key, value in given.items():
        if key in spec.get("fields", {}) or key in links:
            header.append((key, value))
        elif key in texts:
            said[texts[key]] = value
        else:
            raise Refused(f"`{key}` is no field, link or text of a {kind}")
    order = header_order(state.g, kind)
    header.sort(key=lambda kv: order.index(kv[0]) if kv[0] in order else len(order))
    body = [(t, said.get(t, "")) for t in section_order(state.g, kind)]
    change.write(f"{loading.DATA}/{spec['folder']}/{ident}.md", edit.new_node(header, body))
    if spec.get("prototype") == "screens":           # grey, until the product has a look of its own
        grey = "" if change.path(f"{prototypes.PROTOTYPES}/assets/css/product.css").is_file() else ' class="wire"'
        change.write(f"{prototypes.PROTOTYPES}/screens/{ident}.html",
                     f'<main data-prototype="{ident}"{grey}>\n<h1>{name}</h1>\n</main>\n')
    elif spec.get("prototype") == "components":
        change.write(f"{prototypes.PROTOTYPES}/components/{ident}.html", "")
    return ident


def child_section(state: State, parent: loading.Node) -> tuple[str, dict]:
    for title, d in state.g["kinds"][parent.kind].get("sections", {}).items():
        if d["type"] == "children":
            return title, d
    raise Refused(f"{parent.id}: a {parent.kind} has no rows of its own")


def op_add_row(state: State, change: Change, args: list[str]) -> str:
    if not args:
        raise Refused("add-row <parent> [key=value ...]")
    parent = state.node(args[0])
    given = pairs(args[1:])
    title, d = child_section(state, parent)
    kind = d["kind"]
    ident = next_id(state, f"{parent.id}.", list(state.done.nodes))
    number = ident.rsplit(".", 1)[1]
    text = change.read(parent.file)
    order = section_order(state.g, parent.kind)
    if not d.get("table"):
        says = given.pop("says", "")
        if given or not says:
            raise Refused(f"a {kind} is added with says=\"...\" and nothing else")
        change.write(parent.file, edit.append_item(text, title, f"{ident} {says}", order))
    else:
        columns = state.g["kinds"][kind]["columns"]
        named = next((c for c in columns if c.get("id") == "name"), None)
        if named is not None:                           # a row named by a word, not numbered: N2.open
            key = next((k for k in given if k in {key_of(named["name"]), "name"}), None)
            word = given.pop(key, "") if key else ""
            slug = re.sub(r"[^a-z0-9]+", "-", word.lower()).strip("-")
            if not re.fullmatch(r"[a-z][a-z0-9-]*", slug):
                raise Refused(f"a {kind} is named by a word: `{key_of(named['name'])}=<word>`")
            ident = f"{parent.id}.{slug}"
            if ident in state.done.nodes or ident in state.ids.get("retired", {}):
                raise Refused(f"{ident} is there already, or was once and is retired")
            state.ids.setdefault("next", {}).pop(f"{parent.id}.", None)    # no counter for words
            number = word
        cells = []
        for column in columns:
            if column.get("id"):
                cells.append(number)
                continue
            names = {key_of(column["name"]), key_of(column.get("as", "")), key_of(column.get("relation", ""))} - {""}
            cells.append(next((given.pop(n) for n in list(given) if n in names), ""))
        if given:
            raise Refused(f"{', '.join(given)}: no column of a {kind}; they are "
                          f"{', '.join(c['name'] for c in columns if not c.get('id'))}")
        change.write(parent.file, edit.append_row(text, title, cells, [c["name"] for c in columns], order))
        # an element is drawn: until someone draws it, a placeholder holds its anchor where everyone sees it
        anchor = state.g["kinds"][kind].get("anchor")
        folder = state.g["kinds"][parent.kind].get("prototype")
        markup = f"{prototypes.PROTOTYPES}/{folder}/{parent.id}.html"
        if anchor == "data-el" and folder and change.path(markup).exists():
            label = next((c for c, col in zip(cells, columns) if col.get("as") == "name"), ident)
            held = change.read(markup)
            place = held.rfind("</main>")
            stub = f'<div data-el="{number}" class="spec-new">{label} -- to be drawn</div>\n'
            change.write(markup, held[:place] + stub + held[place:] if place >= 0 else held + stub)
    return ident


def op_set(state: State, change: Change, args: list[str]) -> str:
    if len(args) != 3:
        raise Refused("set <id> <key> <value>")
    node = state.node(args[0])
    key, value = key_of(args[1]), args[2]
    spec = state.g["kinds"][node.kind]
    text = change.read(node.file)
    if node.parent is None:
        texts = {d.get("as"): title for title, d in spec.get("sections", {}).items() if d["type"] == "text"}
        tables = {d.get("as"): title for title, d in spec.get("sections", {}).items() if d["type"] == "table"}
        if key in spec.get("fields", {}):
            change.write(node.file, edit.set_header(text, key, value, header_order(state.g, node.kind)))
        elif key in texts:
            change.write(node.file, edit.set_section(text, texts[key], value, section_order(state.g, node.kind)))
        elif key in tables:
            change.write(node.file, edit.set_section(text, tables[key], value.replace("\\n", "\n"),
                                                     section_order(state.g, node.kind)))
        else:
            raise Refused(f"`{key}` is no field, text or table of a {node.kind}; links are tied and untied")
        return node.id
    columns = spec.get("columns")
    if columns is None:                                 # an item of a list: a criterion
        if key != "says":
            raise Refused(f"a {node.kind} has only says")
        change.write(node.file, edit.set_line(text, node.line, f"- {node.id} {value}"))
        return node.id
    index = next((i for i, c in enumerate(columns) if key in (key_of(c.get("as", "")), key_of(c["name"]))
                  and "relation" not in c), None)
    if index is None:
        raise Refused(f"`{key}` is no column of a {node.kind}; links are tied and untied")
    change.write(node.file, edit.set_cell(text, node.line, index, value))
    return node.id


def stated(state: State, node: loading.Node, rel: str) -> dict:
    r = state.g["relations"].get(rel)
    if r is None:
        raise Refused(f"`{rel}` is no relation; they are {', '.join(state.g['relations'])}")
    if rel == "has":
        raise Refused("rows are added with add-row and taken out with remove, not tied")
    if node.kind not in r["from"]:
        raise Refused(f"`{rel}` joins a {' or a '.join(r['from'])}, and {node.id} is a {node.kind}")
    return r


def op_tie(state: State, change: Change, args: list[str], untie: bool = False) -> str:
    if len(args) < 3:
        raise Refused(f"{'untie' if untie else 'tie'} <id> <relation> <id>" + ("" if untie else " [words]"))
    node = state.node(args[0])
    rest = args[1:]
    width = next((n for n in (4, 3, 2, 1) if len(rest) > n and key_of(" ".join(rest[:n])) in state.g["relations"]), 1)
    rel = key_of(" ".join(rest[:width]))                # `depends on`, `may not`: a relation of several words
    if len(rest) <= width:
        raise Refused(f"{'untie' if untie else 'tie'} <id> <relation> <id>: what does {node.id} {rel}?")
    other, words = rest[width], " ".join(rest[width + 1:])
    r = stated(state, node, rel)
    text = change.read(node.file)
    in_row = node.parent is not None and "column" in r      # a row's link is its cell; a node's, its header line
    if "field" in r and not in_row:
        now = loading.ids_in(node_value(change, node, r["field"]))
        if untie and other not in now:
            raise Refused(f"{node.id} does not {rel} {other}")
        changed = [i for i in now if i != other] if untie else ([*now, other] if other not in now else now)
        change.write(node.file, edit.set_header(text, r["field"], ", ".join(changed), header_order(state.g, node.kind)))
    elif in_row:
        columns = state.g["kinds"][node.kind]["columns"]
        index = next(i for i, c in enumerate(columns) if c.get("relation") == rel)
        now = loading.ids_in(edit.nodefile.cells(edit.split(text)[node.line - 1])[index])
        if untie and other not in now:
            raise Refused(f"{node.id} does not {rel} {other}")
        changed = [i for i in now if i != other] if untie else ([*now, other] if other not in now else now)
        change.write(node.file, edit.set_cell(text, node.line, index, ", ".join(changed)))
    elif r.get("section"):
        answer = r["answer"]
        if untie:
            lines = edit.split(text)
            gone = [i + 1 for i, line in enumerate(lines)
                    if re.fullmatch(rf"- {re.escape(answer)}:\s*{re.escape(other)}\b.*", line)]
            if not gone:
                raise Refused(f"{node.id} does not {rel} {other}")
            for line in reversed(gone):
                text = edit.delete_line(text, line)
            change.write(node.file, text)
        else:
            if not words:
                raise Refused(f"tie {node.id} {rel} {other} <the action, in words>")
            change.write(node.file, edit.append_item(text, r["section"], f"{answer}: {other} {words}",
                                                     section_order(state.g, node.kind)))
    else:                                               # written only in a table's cells: a line of that table
        raise Refused(f"`{rel}` is written in a cell of a table of {node.id}, not tied to it as a whole: change "
                      f"that table's line (add-line, remove-line, or set the table)")
    return node.id


def node_value(change: Change, node: loading.Node, key: str) -> str:
    for line in edit.split(change.read(node.file))[1:]:
        if line.strip() == edit.FENCE:
            break
        k, _, v = line.partition(":")
        if k.strip().lower() == key:
            return v.strip()
    return ""


def op_remove(state: State, change: Change, args: list[str]) -> str:
    untie = "--untie" in args
    args = [a for a in args if a != "--untie"]
    if len(args) != 1:
        raise Refused("remove <id> [--untie]")
    node = state.node(args[0])
    gone = {node.id} | {n.id for n in state.done.nodes.values() if n.parent == node.id}
    added = [e for e in state.done.edges if e.dst in gone and e.rel == "adds to"]
    moot = sorted({e.src for e in added if all(x.dst in gone for x in state.done.edges
                                                 if x.src == e.src and x.rel == "adds to")}, key=natural)
    for e in added:                                     # what was added to it goes with it, or lets go of it
        if e.src not in moot:
            op_tie(state, change, [e.src, e.rel, e.dst], untie=True)
            state.again()
    for addition in moot:
        change.delete(state.node(addition).file)
        state.ids.setdefault("retired", {})[addition] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        state.gone.add(addition)
    if moot:
        state.again()
    inbound = [e for e in state.done.edges if e.dst in gone and e.src not in gone and e.rel != "has"]
    if inbound and not untie:
        said = ", ".join(sorted({f"{e.src} {e.rel} {e.dst}" for e in inbound}, key=natural))
        raise Refused(f"{node.id} is linked from {said}: take those links out first, or remove it with --untie")
    for e in sorted(inbound, key=lambda e: (e.src, -state.done.nodes[e.src].line)):
        op_tie(state, change, [e.src, e.rel, e.dst], untie=True)
        state.again()
    node = state.node(node.id)
    if node.parent is None:
        spec = state.g["kinds"][node.kind]
        change.delete(node.file)
        if spec.get("prototype"):
            change.delete(f"{prototypes.PROTOTYPES}/{spec['prototype']}/{node.id}.html")
    else:
        change.write(node.file, edit.delete_line(change.read(node.file), node.line))
        anchor = state.g["kinds"][node.kind].get("anchor")
        parent = state.done.nodes[node.parent]
        folder = state.g["kinds"][parent.kind].get("prototype")
        markup = f"{prototypes.PROTOTYPES}/{folder}/{parent.id}.html"
        if anchor and folder and change.path(markup).exists():
            value = node.id.rsplit(".", 1)[1] if anchor == "data-el" else node.id
            change.write(markup, re.sub(rf'\s{anchor}="{re.escape(value)}"', "", change.read(markup)))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for ident in gone:
        state.ids.setdefault("retired", {})[ident] = stamp
    state.gone |= gone
    return node.id


def op_confirm(state: State, change: Change, args: list[str]) -> str:
    if len(args) != 1:
        raise Refused("confirm <id>")
    state.confirmed.add(state.node(args[0]).id)
    return args[0]


def table_of(state: State, node: loading.Node, key: str) -> tuple[str, dict]:
    if node.parent is not None:
        raise Refused(f"{node.id} is a row; its tables are its parent's")
    sections = state.g["kinds"][node.kind].get("sections", {})
    for title, d in sections.items():
        if d["type"] == "table" and key in (key_of(d.get("as", "")), key_of(title)):
            return title, d
    held = [d["as"] for d in sections.values() if d["type"] == "table"]
    raise Refused(f"`{key}` is no table of a {node.kind}" + (f"; its tables are {', '.join(held)}" if held else
                                                            "; it has none") +
                  ("; its rows are added with add-row" if any(d["type"] == "children" for d in sections.values()) else ""))


def op_add_line(state: State, change: Change, args: list[str]) -> str:
    if len(args) < 3:
        raise Refused("add-line <id> <table> [first cell] [column=value ...]")
    node = state.node(args[0])
    title, d = table_of(state, node, key_of(args[1]))
    rest = args[2:]
    first = rest.pop(0) if rest and not re.match(r"[\w -]+=", rest[0]) else None
    given = pairs(rest)
    columns = d["columns"]
    cells = []
    for i, column in enumerate(columns):
        names = {key_of(column["name"]), key_of(column.get("relation", ""))} - {""}
        cell = next((given.pop(n) for n in list(given) if n in names), "")
        cells.append(first if i == 0 and first is not None and not cell else cell)
    if given:
        raise Refused(f"{', '.join(given)}: no column of {node.id}'s {title}; they are "
                      f"{', '.join(c['name'] for c in columns)}")
    if not cells[0].strip():
        raise Refused(f"a line of {title} says its {columns[0]['name']} first")
    change.write(node.file, edit.append_row(change.read(node.file), title, cells, [c["name"] for c in columns],
                                            section_order(state.g, node.kind)))
    drawings = drawn_in(state, node, d)
    if drawings and change.path(drawings).exists():     # a variant is drawn: a placeholder until someone draws it
        word = cells[0].replace('"', "&quot;")
        held = change.read(drawings)
        change.write(drawings, (held.rstrip("\n") + "\n" if held.strip() else "") +
                     f'<figure>\n<figcaption>{word}</figcaption>\n'
                     f'<span class="stage spec-new" data-variant="{word}">{word} -- to be drawn</span>\n</figure>\n')
    return node.id


def drawn_in(state: State, node: loading.Node, d: dict) -> str | None:
    folder = state.g["kinds"][node.kind].get("prototype")
    return f"{prototypes.PROTOTYPES}/{folder}/{node.id}.html" if d.get("drawn") and folder else None


def op_remove_line(state: State, change: Change, args: list[str]) -> str:
    if len(args) != 3:
        raise Refused("remove-line <id> <table> <its first cell>")
    node = state.node(args[0])
    title, d = table_of(state, node, key_of(args[1]))
    text = change.read(node.file)
    lines = edit.split(text)
    found = {t: (start, stop) for t, start, stop in edit.sections(lines)}
    if title not in found:
        raise Refused(f"{node.id} has no {title}")
    start, stop = found[title]
    rows = [i for i in range(start + 1, stop) if lines[i].strip().startswith("|")][2:]     # past the head and the rule
    hits = [i for i in rows if nodefile.cells(lines[i])[0].lower() == args[2].lower()]
    if len(hits) != 1:
        firsts = ", ".join(nodefile.cells(lines[i])[0] for i in rows)
        raise Refused(f"{'no' if not hits else len(hits)} line(s) of {node.id}'s {title} start with `{args[2]}`; "
                      f"they start with {firsts or 'nothing'}")
    text = edit.delete_line(text, hits[0] + 1)
    word = nodefile.cells(lines[hits[0]])[0]
    if len(rows) == 1:                                  # the last line gone: the table goes, its heading with it
        text = edit.set_section(text, title, "", section_order(state.g, node.kind))
    change.write(node.file, text)
    drawings = drawn_in(state, node, d)
    if drawings and change.path(drawings).exists():     # its drawing stays, as markup; its anchor goes
        change.write(drawings, re.sub(rf'\sdata-variant="{re.escape(word)}"', "", change.read(drawings)))
    return node.id


ID_LIST = re.compile(r"\s*[A-Z]+\d+(?:\.[\w-]+)*(?:\s*,\s*[A-Z]+\d+(?:\.[\w-]+)*)*\s*")


def mentioned(state: State, ident: str) -> list[str]:
    """Where a text names a node, outside every link: each place as file:line."""
    fields = {r["field"] for r in state.g["relations"].values() if "field" in r}
    mention = re.compile(rf"(?<![\w.]){re.escape(ident)}(?!\w|\.\d)")
    node = state.node(ident)
    out = []
    for name in sorted({n.file for n in state.done.nodes.values()}):
        lines = edit.split((state.root / name).read_text(encoding="utf-8"))
        end = edit.fence_end(lines)
        for i, line in enumerate(lines):
            if not mention.search(line) or (name == node.file and (node.parent is None or i + 1 == node.line)):
                continue
            if 0 < i < end:
                if line.partition(":")[0].strip().lower() not in fields | {"id"}:
                    out.append(f"{name}:{i + 1}")
            elif i > end and line.lstrip().startswith("|"):
                if any(mention.search(c) and not ID_LIST.fullmatch(c) for c in nodefile.cells(line)):
                    out.append(f"{name}:{i + 1}")
            elif i > end and not re.match(r"\s*- (?:yes|no|\?):", line):
                out.append(f"{name}:{i + 1}")
    return out


def op_retarget(state: State, change: Change, args: list[str]) -> str:
    if len(args) != 2:
        raise Refused("retarget <id> <id>: every link to the first, and every mention of it, moved to the second")
    old, new = state.node(args[0]), state.node(args[1])
    if old.id == new.id:
        raise Refused(f"retarget {old.id} {new.id}: the same node")
    for e in state.done.edges:
        r = state.g["relations"][e.rel]
        if e.dst == old.id and e.rel != "has" and new.kind not in r["to"] and "any" not in r["to"]:
            raise Refused(f"{e.src} {e.rel} {old.id}: `{e.rel}` reaches a {' or a '.join(r['to'])}, and {new.id} is a "
                          f"{new.kind} -- untie it, or change it, first")
    fields = {r["field"] for r in state.g["relations"].values() if "field" in r}
    mention = re.compile(rf"(?<![\w.]){re.escape(old.id)}(?!\w|\.\d)")
    for name in sorted({n.file for n in state.done.nodes.values()}):
        lines = edit.split(change.read(name))
        end = edit.fence_end(lines)
        out, moved = [], False
        for i, line in enumerate(lines):
            defines = name == old.file and (old.parent is None or i + 1 == old.line)
            if defines or not mention.search(line):
                out.append(line)
                continue
            key = line.partition(":")[0].strip().lower()
            if 0 < i < end and key == "id":
                out.append(line)
                continue
            if 0 < i < end and key in fields:
                ids = list(dict.fromkeys(new.id if x == old.id else x for x in loading.ids_in(line.partition(":")[2])))
                line = f"{key}: {', '.join(ids)}"
            elif i > end and line.lstrip().startswith("|"):
                cells = [mention.sub(new.id, c) for c in nodefile.cells(line)]
                cells = [", ".join(dict.fromkeys(loading.ids_in(c))) if ID_LIST.fullmatch(c) else c for c in cells]
                line = edit.row(cells)
            else:
                line = mention.sub(new.id, line)
            out.append(line)
            moved = True
        if moved:
            change.write(name, edit.joined(out))
    return new.id


def op_answer(state: State, change: Change, args: list[str]) -> str:
    usage = 'answer <question> "<what was decided>" [because="..."] [instead="..."] [name="..."]'
    if len(args) < 2:
        raise Refused(usage)
    question = state.node(args[0])
    if question.kind != "question":
        raise Refused(f"{question.id} is a {question.kind}, not a question")
    given = pairs(args[2:])
    if set(given) - {"because", "instead", "name"}:
        raise Refused(f"{', '.join(sorted(set(given) - {'because', 'instead', 'name'}))}: not taken -- {usage}")
    named = mentioned(state, question.id)
    if named:
        raise Refused(f"{question.id} is still named in a text, at {', '.join(named)}: write the answer there first "
                      f"(`set`, in the same change), then answer it")
    about = sorted({e.dst for e in state.done.edges if e.src == question.id and e.rel == "about"}, key=natural)
    words = " ".join(args[1].split())
    name = given.get("name") or question.fields.get("name") or (words if len(words) <= 80
                                                                 else words[:77].rsplit(" ", 1)[0] + "...")
    made = op_add(state, change, ["decision", name, f"decision={args[1]}",
                                  *(f"{k}={given[k]}" for k in ("because", "instead") if given.get(k)),
                                  *([f"about={', '.join(about)}"] if about else [])])
    state.again()
    for e in [e for e in state.done.edges if e.dst == question.id and e.rel == "asks"]:
        op_tie(state, change, [e.src, "asks", question.id], untie=True)    # a row that asked it is now about it
        state.again()
        op_tie(state, change, [e.src, "about", question.id])
        state.again()
    op_retarget(state, change, [question.id, made])
    state.again()
    op_remove(state, change, [question.id])
    return made


def op_confirm_added(state: State, change: Change, args: list[str]) -> str:
    if len(args) != 1:
        raise Refused("confirm-added <addition>, or confirm-added <id> for every addition to it")
    target = state.node(args[0])
    if target.kind == "addition":
        op_remove(state, change, [target.id])
        return target.id
    covered = {target.id} | {n.id for n in state.done.nodes.values() if n.parent == target.id}
    additions = sorted({e.src for e in state.done.edges if e.dst in covered and e.rel == "adds to"}, key=natural)
    if not additions:
        raise Refused(f"nothing added to {target.id} or its rows waits to be confirmed")
    for addition in additions:
        to = [e.dst for e in state.done.edges if e.src == addition and e.rel == "adds to"]
        if all(t in covered for t in to):
            op_remove(state, change, [addition])
        else:                                           # it adds to something else too, which stays unconfirmed
            for t in (t for t in to if t in covered):
                op_tie(state, change, [addition, "adds to", t], untie=True)
                state.again()
        state.again()
    return target.id


OPERATIONS = {"add": op_add, "add-row": op_add_row, "set": op_set, "tie": op_tie,
              "untie": lambda s, c, a: op_tie(s, c, a, untie=True), "remove": op_remove,
              "confirm": op_confirm, "answer": op_answer, "confirm-added": op_confirm_added,
              "retarget": op_retarget, "add-line": op_add_line, "remove-line": op_remove_line}


@dataclass
class Result:
    applied: list[str]
    changes: list[dict]
    problems: list[tuple[str, int, str]]
    dry: bool
    stale: list[dict] = field(default_factory=list)   # a dry run: what the change would turn stale, not stale now


def parse(line: str) -> list[str]:
    return shlex.split(line, posix=True)


def apply(root: Path, operations: list[list[str]], who: str = "", because: str = "", dry: bool = False,
          expect: dict[str, str] | None = None) -> Result:
    """The operations applied in order as one change; the result held to the grammar; kept, logged and built only
    when it loads clean -- otherwise every file put back as it was. `expect` names the version of each node the
    change was made against -- a form drawn from it -- and a node changed or gone since refuses the change."""
    with Lock(root):
        g = loading.grammar()
        before = loading.load(root)
        for ident, held in (expect or {}).items():
            if ident not in before.nodes:
                raise Refused(f"{ident} is gone since you opened it")
            if loading.version(g, before, ident) != held:
                raise Refused(f"{ident} changed since you opened it -- by an agent, by hand or in another window: "
                              f"open it again to see what moved, then make your change on what it is now")
        notice(root, before)                    # an edit by hand since the last change is logged as one, apart
        try:
            stamps = review.held(root)
        except ValueError as wrong:
            raise Refused(str(wrong)) from None
        state = State(root, g, before, held_json(root / IDS) or {"next": {}, "retired": {}})
        change = Change(root)
        applied = []
        try:
            made: list[str] = []                # what each operation made or touched: `$1` names the first's
            resolved: list[str] = []                # each operation as it was applied, its `$n` named
            for words in operations:
                if not words:
                    continue
                words = [re.sub(r"\$(\d+)", lambda m: made[int(m.group(1)) - 1] if 0 < int(m.group(1)) <= len(made)
                                else m.group(0), w) for w in words]
                name, args = words[0], words[1:]
                if name not in OPERATIONS:
                    raise Refused(f"{name}: no such operation; they are {', '.join(OPERATIONS)}")
                done = OPERATIONS[name](state, change, args)
                made.append(done)
                resolved.append(" ".join(words))
                applied.append(f"{' '.join(words)}  ->  {done}")
                state.again()
            after = loading.load(root, retired=state.ids.get("retired", {}))
            if after.problems:
                change.restore()
                return Result(applied, [], after.problems, dry)
            changes = differences(g, before, after)
            agreed(g, before, after, changes, review.stamped(g, after, stamps, state.confirmed, state.gone))
            if state.confirmed:
                owed = {s["node"] for s in review.stale(g, after, stamps)}
                changes += [{"id": i, "kind": after.nodes[i].kind, "change": "confirmed" if i in owed else
                             "confirmed, owing nothing"} for i in sorted(state.confirmed, key=natural)]
            if dry:                             # and what it would turn stale that is not stale already
                was = {(s["node"], s["on"]) for s in review.stale(g, before, stamps)}
                would = review.stale(g, after, review.stamped(g, after, stamps, state.confirmed, state.gone))
                change.restore()
                return Result(applied, changes, [], True, [s for s in would if (s["node"], s["on"]) not in was])
            change.write(IDS, json.dumps(state.ids, indent=1, sort_keys=True) + "\n")
            change.write(review.REVIEWED, json.dumps(review.stamped(g, after, stamps, state.confirmed, state.gone),
                                                     ensure_ascii=False, indent=0, sort_keys=True) + "\n")
            loading.build(after)
        except Refused:
            change.restore()
            raise
        except Exception:
            change.restore()
            raise
        log(root, {"who": who or "someone", "because": because, "operations": resolved, "changes": changes})
        remember(root, g, after)
        return Result(applied, changes, [], False)


def agreed(g: dict, before: loading.Load, after: loading.Load, changes: list[dict], stamps: dict) -> None:
    """An agreed specification takes no change but going back to draft; it is agreed only when it is ready."""
    status = lambda done: done.nodes["document"].fields.get("status", "") if "document" in done.nodes else ""  # noqa: E731
    was, now = status(before), status(after)
    if was == "agreed" and now == "agreed":
        moved = [c["id"] for c in changes
                 if not (c["id"] == "document" and set(c.get("fields", {})) <= {"status"}
                         and not c.get("tied") and not c.get("untied"))]
        if moved:
            raise Refused(f"the specification is agreed, and this changes {', '.join(moved[:8])}"
                          f"{' ...' if len(moved) > 8 else ''}: `set document status draft` first, in the same "
                          f"change or before it")
    if now == "agreed" and was != "agreed":
        held = finish.ready(g, after, stamps)
        if held:
            raise Refused("not ready to be agreed -- " + "; ".join(held))


def summary_of(g: dict, done: loading.Load) -> dict[str, dict]:
    """Each node by what it means and what it links to: what a change is measured against."""
    links: dict[str, list[str]] = {}
    for e in done.edges:
        if e.rel != "has":
            links.setdefault(e.src, []).append(f"{e.rel} {e.dst}")
    return {ident: {"kind": n.kind, "meaning": loading.meaning(g, n), "links": sorted(links.get(ident, []))}
            for ident, n in done.nodes.items()}


def differences(g: dict, before: loading.Load, after: loading.Load) -> list[dict]:
    was, now = summary_of(g, before), summary_of(g, after)
    return compare(was, now)


def compare(was: dict, now: dict) -> list[dict]:
    out = []
    for ident in sorted(set(was) | set(now), key=natural):
        a, b = was.get(ident), now.get(ident)
        if a == b:
            continue
        if a is None:
            out.append({"id": ident, "kind": b["kind"], "change": "added", "fields": b["meaning"], "links": b["links"]})
        elif b is None:
            out.append({"id": ident, "kind": a["kind"], "change": "removed"})
        else:
            fields = {k: [a["meaning"].get(k), b["meaning"].get(k)]
                      for k in sorted(set(a["meaning"]) | set(b["meaning"])) if a["meaning"].get(k) != b["meaning"].get(k)}
            entry = {"id": ident, "kind": b["kind"], "change": "changed"}
            if fields:
                entry["fields"] = fields
            gained = sorted(set(b["links"]) - set(a["links"]))
            lost = sorted(set(a["links"]) - set(b["links"]))
            if gained:
                entry["tied"] = gained
            if lost:
                entry["untied"] = lost
            out.append(entry)
    return out


def log(root: Path, entry: dict) -> None:
    path = root / CHANGES
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **entry}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def remember(root: Path, g: dict, done: loading.Load) -> None:
    """What the data was when it was last logged: a later difference no operation made is an edit by hand."""
    path = root / KNOWN
    path.parent.mkdir(parents=True, exist_ok=True)
    fresh = path.with_name(path.name + ".new")
    fresh.write_text(json.dumps(summary_of(g, done), ensure_ascii=False, sort_keys=True, indent=0) + "\n",
                     encoding="utf-8", newline="\n")
    os.replace(fresh, path)


def notice(root: Path, done: loading.Load) -> list[dict]:
    """Edits made by hand since the data was last logged: each logged as one, so that the history holds every
    change, whoever made it. The first time, the data is taken as it is, and nothing is logged."""
    if done.problems:
        return []
    g = loading.grammar()
    path = root / KNOWN
    now = summary_of(g, done)
    if not (root / review.REVIEWED).is_file():          # the first stamping: every link reviewed as it is
        review.save(root, review.stamped(g, done, {}))
    if not path.is_file():
        remember(root, g, done)
        return []
    changes = compare(held_json(path), now)
    if changes:
        log(root, {"who": "by hand", "because": "", "operations": [], "changes": changes})
        remember(root, g, done)
        review.save(root, review.stamped(g, done, review.held(root)))    # a link new by hand: made against now
    return changes


def history(root: Path, ident: str | None = None) -> list[dict]:
    """The log, oldest first; with an ID, only the changes that touched that node, or one of its rows."""
    path = root / CHANGES
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if ident:
            touched = [c for c in entry.get("changes", []) if c["id"] == ident or c["id"].startswith(ident + ".")]
            if not touched:
                continue
            entry = {**entry, "changes": touched}
        out.append(entry)
    return out
