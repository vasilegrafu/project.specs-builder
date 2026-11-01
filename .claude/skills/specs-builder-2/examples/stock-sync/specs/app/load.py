"""The data of a specification, loaded: every node's file held to the grammar, every link resolved, and -- only when
nothing is wrong -- the model written into SQLite in one transaction.

Nothing is guessed and nothing is dropped. A key the kind does not have, a section it does not declare, a value
outside its choices, an ID that is not there, a link between kinds the grammar does not join, a relation short of
its least, a cycle where the grammar wants none: each is a problem, told at its file and line, and a load with any
problem builds nothing. The database repeats the grammar's joins as a trigger, so a later write that bypasses the
loader is refused there too.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

import nodefile
import prototypes

APP = Path(__file__).resolve().parent
GRAMMAR = APP / "grammar.json"
DATA = "data"
CACHE = ".cache"
DATABASE = f"{CACHE}/spec.db"
ID_RE = re.compile(r"document|[A-Z]+\d+(?:\.(?:\d+|[a-z][a-z0-9-]*))*")      # R4, R4.2, N2.open, the document
ANSWER_RE = re.compile(r"(yes|no|\?):\s*(\S+)\s*(.*)")
OBSERVED = {"seen", "run"}                              # the words of Seen that mean the product itself

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE nodes (
    id          TEXT PRIMARY KEY,
    kind        TEXT NOT NULL,
    parent      TEXT REFERENCES nodes(id),
    name        TEXT,
    file        TEXT NOT NULL,
    line        INTEGER NOT NULL,
    fields      TEXT NOT NULL CHECK (json_valid(fields)),
    fingerprint TEXT NOT NULL
);
CREATE TABLE joins (rel TEXT NOT NULL, from_kind TEXT NOT NULL, to_kind TEXT NOT NULL,
                    PRIMARY KEY (rel, from_kind, to_kind));
CREATE TABLE edges (
    src  TEXT NOT NULL REFERENCES nodes(id),
    rel  TEXT NOT NULL,
    dst  TEXT NOT NULL REFERENCES nodes(id),
    file TEXT NOT NULL,
    line INTEGER NOT NULL,
    PRIMARY KEY (src, rel, dst),
    CHECK (src <> dst OR rel IN ('leads to', 'moves'))
);
CREATE INDEX edges_to ON edges (dst, rel);
CREATE INDEX nodes_of_kind ON nodes (kind, parent);
CREATE INDEX nodes_in ON nodes (parent);
CREATE TABLE crossings (                                -- each link between two nodes, by the kinds of the nodes that hold its ends
    from_kind TEXT NOT NULL,
    to_kind   TEXT NOT NULL,
    place     INTEGER NOT NULL,                         -- in ID order: a page of a cell is read off the key
    src       TEXT NOT NULL,
    rel       TEXT NOT NULL,
    dst       TEXT NOT NULL,
    PRIMARY KEY (from_kind, to_kind, place)
) WITHOUT ROWID;
CREATE TRIGGER edges_join BEFORE INSERT ON edges
WHEN NOT EXISTS (SELECT 1 FROM joins j JOIN nodes s ON s.id = NEW.src JOIN nodes d ON d.id = NEW.dst
                 WHERE j.rel = NEW.rel AND j.from_kind = s.kind AND (j.to_kind = d.kind OR j.to_kind = 'any'))
BEGIN SELECT RAISE(ABORT, 'the grammar does not join these kinds by this relation'); END;
"""


@dataclass
class Node:
    id: str
    kind: str
    file: str
    line: int
    fields: dict[str, object] = field(default_factory=dict)
    parent: str | None = None


@dataclass
class Edge:
    src: str
    rel: str
    dst: str
    file: str
    line: int


@dataclass
class Load:
    root: Path
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    problems: list[tuple[str, int, str]] = field(default_factory=list)

    def fault(self, file: str, line: int, message: str) -> None:
        self.problems.append((file, line, message))


def grammar() -> dict:
    return json.loads(GRAMMAR.read_text(encoding="utf-8"))


def load(root: Path, retired: dict | None = None) -> Load:
    """The specification in `root` read and held to the grammar: its nodes, its edges and what is wrong. An ID
    retired in stamps/ids.json -- or in `retired`, while a change is being made -- is refused wherever it is
    written again."""
    g = grammar()
    out = Load(root)
    data = root / DATA
    if not data.is_dir():
        out.fault(DATA, 0, f"there is no {DATA}/ folder: a specification keeps its nodes there")
        return out
    folders = {spec["folder"]: kind for kind, spec in g["kinds"].items() if "folder" in spec}
    singles = {spec["single"]: kind for kind, spec in g["kinds"].items() if "single" in spec}
    pending: list[tuple[Edge, bool]] = []          # each link, and whether saying it twice is a fault
    for path in sorted(p for p in data.rglob("*") if p.is_file()):
        name = path.relative_to(root).as_posix()
        parts = path.relative_to(data).parts
        if len(parts) == 1 and parts[0] in singles:
            read_node(g, singles[parts[0]], path, name, out, pending)
            continue
        if len(parts) != 2 or parts[0] not in folders or path.suffix != ".md":
            out.fault(name, 0, f"not a node's file: a node is {DATA}/<{'|'.join(sorted(folders))}>/<its ID>.md")
            continue
        read_node(g, folders[parts[0]], path, name, out, pending)
    resolve(g, out, pending)
    least(g, out)
    prototypes.check(g, out)
    if retired is None:
        try:
            retired = json.loads((root / "stamps" / "ids.json").read_text(encoding="utf-8")).get("retired", {})
        except (OSError, ValueError):
            retired = {}
    for ident in sorted(set(retired) & set(out.nodes)):
        node = out.nodes[ident]
        out.fault(node.file, node.line, f"{ident} was removed on {retired[ident]}, and an ID is never used again: "
                                        f"a new {node.kind} takes the next number")
    cycles(g, out)
    standing(g, out)
    out.problems.sort(key=lambda p: (p[0], p[1]))
    return out


def read_node(g: dict, kind: str, path: Path, name: str, out: Load, pending: list) -> None:
    spec = g["kinds"][kind]
    held = nodefile.read(path)
    for line, message in held.faults:
        out.fault(name, line, message)
    if spec.get("single"):                      # the one node of its kind: its ID is its kind's
        ident, at = held.header.get("id", (spec["id"], 1))
        if ident != spec["id"]:
            out.fault(name, at, f"the {kind}'s ID is `{spec['id']}`, and this says `{ident}`")
            return
    elif "id" not in held.header:
        if held.header or not held.faults:
            out.fault(name, 1, "the header has no `id:`")
        return
    else:
        ident, at = held.header["id"]
    if not spec.get("single") and not re.fullmatch(rf"{spec['id']}\d+", ident):
        out.fault(name, at, f"`{ident}` is no {kind}'s ID: a {kind} is {spec['id']}1, {spec['id']}2 and on")
        return
    if not spec.get("single") and path.stem != ident:
        out.fault(name, at, f"the file of {ident} is named {ident}.md")
    if ident in out.nodes:
        out.fault(name, at, f"{ident} is defined twice; first in {out.nodes[ident].file}")
        return
    links = {r["field"]: rel for rel, r in g["relations"].items() if kind in r["from"] and "field" in r}
    allowed = {"id", *spec["fields"], *links}
    for key, (_, line) in held.header.items():
        if key not in allowed:
            out.fault(name, line, f"`{key}:` is no field of a {kind}; it has {', '.join(sorted(allowed - {'id'}))}")
    node = out.nodes[ident] = Node(ident, kind, name, at)
    for key, f in spec["fields"].items():
        value, line = held.header.get(key, ("", at))
        if not value:
            if f.get("required"):
                out.fault(name, at, f"{ident} has no `{key}:`, which every {kind} needs")
            continue
        if f["type"] == "choice" and value not in g["choices"][f["of"]]:
            out.fault(name, line, f"`{key}: {value}` is not one of: {', '.join(g['choices'][f['of']])}")
            continue
        node.fields[key] = value
    for key, rel in links.items():
        value, line = held.header.get(key, ("", at))
        tokens = [t.strip() for t in value.split(",") if t.strip()]
        for token in tokens:
            if not ID_RE.fullmatch(token):
                out.fault(name, line, f"`{token}` in `{key}:` is not an ID: a link names what it joins by its ID")
            else:
                pending.append((Edge(ident, rel, token, name, line), True))
    declared = spec.get("sections", {})
    for title, section in held.sections.items():
        if title not in declared:
            if title or section.text():
                where = "text before any heading" if not title else f"`## {title}`"
                sections = ", ".join(f"`## {t}`" for t in declared if t) or "none"
                out.fault(name, section.line, f"{where} is no section of a {kind}; its sections are {sections}")
            continue
        kind_of = declared[title]["type"]
        if kind_of == "text":
            if section.text():
                node.fields[declared[title]["as"]] = section.text()
        elif kind_of == "children" and declared[title].get("table"):
            rows_of(g, declared[title]["kind"], node, section, out, pending)
        elif kind_of == "children":
            children(g, declared[title]["kind"], node, section, out, pending)
        elif kind_of == "table":
            table(declared[title], node, section, out, pending)
        elif kind_of == "actions":
            actions(g, node, section, out, pending)
    for title, d in declared.items():
        if d["type"] != "text":
            continue
        said = node.fields.get(d["as"], "")
        line = held.sections[title].first() if title in held.sections and node.fields.get(d["as"]) else at
        if d.get("required") and not said:
            where = "its text, under the header" if not title else f"`## {title}`"
            out.fault(name, line, f"{ident} says nothing in {where}: a {kind} needs its {d['as']}")
        elif d.get("holds") and said and not re.search(rf"\b{d['holds']}\b", str(said)):
            out.fault(name, line, f"{ident}'s {d['as']} says what the product `{d['holds']}` do, and this does not")


def children(g: dict, kind: str, parent: Node, section: nodefile.Section, out: Load, pending: list) -> None:
    items, stray = section.items()
    for line in stray:
        out.fault(parent.file, line, f"`## {section.name}` holds only its list, `- {parent.id}.1 …`")
    for line, text in items:
        found = re.fullmatch(rf"({re.escape(parent.id)}\.\d+)\s+(.+)", text)
        if not found:
            other = re.match(r"([A-Z]+\d+\.\d+)\b", text)
            out.fault(parent.file, line, f"{other.group(1)} is not {parent.id}'s: its {kind}s are {parent.id}.1, "
                                         f"{parent.id}.2 and on" if other else
                                         f"each item is a {kind} with its ID first: `- {parent.id}.1 …`")
            continue
        ident, says = found.groups()
        if ident in out.nodes:
            out.fault(parent.file, line, f"{ident} is defined twice; first on line {out.nodes[ident].line}")
            continue
        out.nodes[ident] = Node(ident, kind, parent.file, line, {"says": says}, parent.id)
        pending.append((Edge(parent.id, "has", ident, parent.file, line), True))


def ids_in(cell: str) -> list[str]:
    return [t for t in re.split(r"[,\s]+", cell) if t]


def rows_of(g: dict, kind: str, parent: Node, section: nodefile.Section, out: Load, pending: list) -> None:
    """A table whose every row is a node of its own -- an element of a screen, a part of a component -- its `#`
    the last number of its ID, each column a field or the IDs of a relation."""
    columns = g["kinds"][kind]["columns"]
    names = [c["name"] for c in columns]
    head, rows, faults = section.table()
    for line, message in faults:
        out.fault(parent.file, line, message)
    if not head:
        return
    if head != names:
        out.fault(parent.file, section.first(), f"`## {section.name}` has the columns {' | '.join(names)}, in that "
                                                f"order; this table has {' | '.join(head)}")
        return
    id_column = next(c for c in columns if c.get("id"))
    for line, row in rows:
        values = dict(zip(names, row))
        number = values[id_column["name"]]
        if id_column["id"] == "name":           # a row named, not numbered: N2.open
            number = re.sub(r"[^a-z0-9]+", "-", number.lower()).strip("-")
            if not re.fullmatch(r"[a-z][a-z0-9-]*", number):
                out.fault(parent.file, line, f"a {kind} is named by a word: `{values[id_column['name']]}` is none")
                continue
        elif not re.fullmatch(r"\d+", number):
            out.fault(parent.file, line, f"`{number}` is not a row's number: a {kind} is numbered 1, 2 and on")
            continue
        ident = f"{parent.id}.{number}"
        if ident in out.nodes:
            out.fault(parent.file, line, f"{ident} is defined twice; first on line {out.nodes[ident].line}")
            continue
        node = out.nodes[ident] = Node(ident, kind, parent.file, line, {}, parent.id)
        if id_column["id"] == "name":
            node.fields["name"] = values[id_column["name"]]
        for column in columns:
            value = values[column["name"]]
            if column.get("id"):
                continue
            if "relation" in column:
                for token in ids_in(value):
                    if not ID_RE.fullmatch(token):
                        out.fault(parent.file, line, f"`{token}` in {ident}'s {column['name']} is not an ID")
                    else:
                        pending.append((Edge(ident, column["relation"], token, parent.file, line), True))
            elif value:
                node.fields[column["as"]] = value
            elif column.get("required"):
                out.fault(parent.file, line, f"{ident} has no {column['name']}, which every {kind} needs")
        pending.append((Edge(parent.id, "has", ident, parent.file, line), True))


def table(declared: dict, node: Node, section: nodefile.Section, out: Load, pending: list) -> None:
    """A table kept as a field: its rows, each by its columns' names; a column the grammar gives a relation links
    the node to the IDs in its cells."""
    names = [c["name"] for c in declared["columns"]]
    head, rows, faults = section.table()
    for line, message in faults:
        out.fault(node.file, line, message)
    if not head:
        return
    if head != names:
        out.fault(node.file, section.first(), f"`## {section.name}` has the columns {' | '.join(names)}, in that "
                                              f"order; this table has {' | '.join(head)}")
        return
    kept = []
    for line, row in rows:
        values = dict(zip(names, row))
        for column in declared["columns"]:
            if column.get("required") and not values[column["name"]]:
                out.fault(node.file, line, f"a row of `## {section.name}` with no {column['name']}")
            if "relation" in column:
                for token in ids_in(values[column["name"]]):
                    if not ID_RE.fullmatch(token):
                        out.fault(node.file, line, f"`{token}` in `## {section.name}`'s {column['name']} is not an ID")
                    else:
                        pending.append((Edge(node.id, column["relation"], token, node.file, line), False))
        kept.append({k.lower(): v for k, v in values.items()} | {"line": line})
    node.fields[declared["as"]] = kept


def actions(g: dict, node: Node, section: nodefile.Section, out: Load, pending: list) -> None:
    by_answer = {r["answer"]: rel for rel, r in g["relations"].items()
                 if node.kind in r["from"] and r.get("section") == section.name}
    items, stray = section.items()
    for line in stray:
        out.fault(node.file, line, f"`## {section.name}` holds only its list, `- yes: R1 what they may do`")
    said = []
    for line, text in items:
        found = ANSWER_RE.fullmatch(text)
        if not found or not ID_RE.fullmatch(found.group(2)):
            out.fault(node.file, line, "each action is `- yes: R1 …`, `- no: R1 …` or `- ?: R1 …`: the answer, "
                                       "then the requirement it is about, then the action in words")
            continue
        answer, ident, words = found.groups()
        said.append({"answer": answer, "about": ident, "action": words})
        pending.append((Edge(node.id, by_answer[answer], ident, node.file, line), False))
    if said:
        node.fields["actions"] = said


def resolve(g: dict, out: Load, pending: list) -> None:
    seen: set[tuple[str, str, str]] = set()
    for edge, once in pending:
        r = g["relations"][edge.rel]
        target = out.nodes.get(edge.dst)
        key = (edge.src, edge.rel, edge.dst)
        if target is None:
            out.fault(edge.file, edge.line, f"{edge.dst} is not defined: {nearest_said(out, edge.dst)}")
        elif target.kind not in r["to"] and "any" not in r["to"]:
            out.fault(edge.file, edge.line, f"`{edge.rel}` joins a {' or a '.join(r['from'])} to a "
                                            f"{' or a '.join(r['to'])}, and {edge.dst} is a {target.kind}")
        elif edge.dst == edge.src and not r.get("self"):
            out.fault(edge.file, edge.line, f"{edge.src} {edge.rel} itself")
        elif key in seen:
            if once:
                out.fault(edge.file, edge.line, f"{edge.src} {edge.rel} {edge.dst} is said twice")
        else:
            seen.add(key)
            out.edges.append(edge)


def settled(contradiction: Node) -> bool:
    return contradiction.fields.get("settled", "").strip().lower() in ("yes", "settled")


def standing(g: dict, out: Load) -> None:
    """How well each node that the grammar says has it worked out stands on the material, never written in a file: its
    `confidence`, the first word of the grammar's that holds, from the findings that became it or a row of it. Quoted
    findings count by source, and the product itself -- at rest or running -- outranks what a document says of it."""
    nodes = out.nodes

    def top(ident: str) -> str:
        while nodes[ident].parent:
            ident = nodes[ident].parent
        return ident

    behind: dict[str, list[str]] = {}
    sources: dict[str, set[str]] = {}
    disputed: set[str] = set()
    added: set[str] = set()
    for e in out.edges:
        if e.rel == "became" and nodes[e.src].kind == "finding":
            behind.setdefault(top(e.dst), []).append(e.src)
        elif e.rel == "from" and nodes[e.src].kind == "finding":
            sources.setdefault(e.src, set()).add(e.dst)
        elif e.rel == "between" and not settled(nodes[e.src]):
            disputed.add(e.dst)
        elif e.rel == "adds to":
            added.add(e.dst)
    for node in nodes.values():
        if "confidence" in g["kinds"][node.kind].get("worked out", ()):
            findings = behind.get(node.id, [])
            seen = {nodes[f].fields.get("seen", "") for f in findings}
            quoted = {s for f in findings if nodes[f].fields.get("seen") != "inferred" for s in sources.get(f, ())}
            node.fields["confidence"] = ("disputed" if disputed & set(findings) else
                                         ("corroborated" if len(quoted) >= 2 else "seen") if seen & OBSERVED else
                                         "documented" if "said" in seen else
                                         "inferred" if findings else
                                         "added" if node.id in added else "stated")


def nearest_said(out: Load, ident: str) -> str:
    head = re.match(r"[A-Z]+", ident)
    same = sorted((n for n in out.nodes if head and re.fullmatch(rf"{head.group(0)}\d+(?:\.\d+)*", n)),
                  key=lambda n: [int(x) for x in re.findall(r"\d+", n)])
    return f"no file defines it; the {head.group(0)} IDs there are run {same[0]} to {same[-1]}" if same and head \
        else "no file defines it, nor anything of its kind"


def least(g: dict, out: Load) -> None:
    """Each relation's least and most, per node of the kinds it is counted for."""
    for rel, r in g["relations"].items():
        count: dict[str, list[Edge]] = {}
        for edge in out.edges:
            if edge.rel == rel:
                count.setdefault(edge.src, []).append(edge)
        if "most" in r:
            for src, said in count.items():
                if len(said) > r["most"]:
                    out.fault(said[0].file, said[0].line, f"{src} {rel} {', '.join(e.dst for e in said)}: no more "
                                                          f"than {r['most']}")
        if "least" not in r:
            continue
        for node in out.nodes.values():
            if node.kind not in r.get("least of", r["from"]):
                continue
            if "field" in r:
                where = f"`{r['field']}:`"
            else:
                titles = [t for t, d in g["kinds"][node.kind].get("sections", {}).items()
                          if d.get("kind") in r["to"] or d.get("type") == "actions"]
                where = f"`## {titles[0]}`" if titles else "its sections"
            if any(node.fields.get(k) == v for k, v in r.get("unless", {}).items()):
                continue
            if len(count.get(node.id, [])) < r["least"]:
                but = " ".join(f"(unless its {k} is {v})" for k, v in r.get("unless", {}).items())
                out.fault(node.file, node.line, f"{node.id} {rel} nothing: every {node.kind} needs at least "
                                                f"{r['least']}, in {where} {but}".rstrip())


def cycles(g: dict, out: Load) -> None:
    for rel, r in g["relations"].items():
        if not r.get("acyclic"):
            continue
        ahead: dict[str, list[Edge]] = {}
        for edge in out.edges:
            if edge.rel == rel:
                ahead.setdefault(edge.src, []).append(edge)
        state: dict[str, str] = {}                      # "open" while on the path, "done" once walked
        told: set[frozenset] = set()

        def visit(at: str, path: list[str], trail: list[Edge]) -> None:
            state[at] = "open"
            for edge in ahead.get(at, []):
                if state.get(edge.dst) == "open":
                    i = path.index(edge.dst)
                    loop = path[i:]
                    if frozenset(loop) not in told:
                        told.add(frozenset(loop))
                        first = trail[i] if i < len(trail) else edge     # the loop's first edge, where it is said
                        chain = f" {rel} ".join([*loop, edge.dst])
                        out.fault(first.file, first.line, f"{chain}: a cycle, and `{rel}` allows none")
                elif state.get(edge.dst) != "done":
                    visit(edge.dst, [*path, edge.dst], [*trail, edge])
            state[at] = "done"

        for start in sorted(ahead):
            if start not in state:
                visit(start, [start], [])


def meaning(g: dict, node: Node) -> dict[str, object]:
    """What a node means, as its kind declares it: the fields and sections marked `meaning`, each as said, with its
    spaces made one -- so a change of wording is a change, and a change of spacing is not."""
    spec = g["kinds"][node.kind]
    keys = [k for k, f in spec.get("fields", {}).items() if f.get("meaning")]
    keys += [d.get("as", "actions") for d in spec.get("sections", {}).values() if d.get("meaning")]
    keys += [c["as"] for c in spec.get("columns", []) if c.get("meaning") and "as" in c]
    said: dict[str, object] = {}
    for key in keys:
        value = node.fields.get(key)
        if isinstance(value, str):
            said[key] = " ".join(value.split())
        elif isinstance(value, list):         # a table's rows: what they say, not the lines they stand on
            said[key] = [{k: " ".join(str(v).split()) for k, v in row.items() if k != "line"}
                         if isinstance(row, dict) else row for row in value]
        elif value is not None:
            said[key] = value
    return said


def fingerprint(g: dict, node: Node) -> str:
    raw = json.dumps(meaning(g, node), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def version_of(prints: list[str]) -> str:
    """A node's version, from its fingerprint and its rows', in that order: what a form drawn from it was drawn
    from, so that a change made since is told before another is made over it."""
    return hashlib.sha256("".join(prints).encode("utf-8")).hexdigest()[:16]


def version(g: dict, done: Load, ident: str) -> str:
    node = done.nodes[ident]
    rows = sorted((n for n in done.nodes.values() if n.parent == ident), key=lambda n: n.id)
    return version_of([fingerprint(g, node), *(fingerprint(g, r) for r in rows)])


def crossings(done: Load) -> list[tuple]:
    """Each link that joins two nodes, what a node holds counted as that node: what the Matrix reads a cell from."""
    top = lambda ident: done.nodes[ident].parent or ident                 # noqa: E731
    rows = [(e.src, e.rel, e.dst) for e in done.edges if e.rel != "has" and top(e.src) != top(e.dst)]
    rows.sort(key=lambda r: (len(r[0]), r[0], len(r[2]), r[2], r[1]))
    return [(done.nodes[top(src)].kind, done.nodes[top(dst)].kind, place, src, rel, dst)
            for place, (src, rel, dst) in enumerate(rows)]


def build(done: Load, database: Path | None = None) -> Path:
    """The model written into SQLite: a new file, filled in one transaction, put in place of the old one only
    once it is whole. Refuses a load with any problem."""
    if done.problems:
        raise ValueError(f"{len(done.problems)} problem(s): nothing is built from a specification that does not load")
    g = grammar()
    path = database or done.root / DATABASE
    path.parent.mkdir(parents=True, exist_ok=True)
    ignore = path.parent / ".gitignore"
    if path.parent.name == CACHE and not ignore.exists():
        ignore.write_text("*\n", encoding="utf-8")      # the database is built, never committed
    fresh = path.with_name(path.name + ".new")
    fresh.unlink(missing_ok=True)
    con = sqlite3.connect(fresh)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(SCHEMA)
        with con:
            con.execute("INSERT INTO meta VALUES ('schema', ?)", (str(g["schema"]),))
            con.executemany("INSERT INTO joins VALUES (?, ?, ?)",
                            [(rel, a, b) for rel, r in g["relations"].items() for a in r["from"] for b in r["to"]])
            ordered = sorted(done.nodes.values(), key=lambda n: n.parent is not None)
            con.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            [(n.id, n.kind, n.parent, n.fields.get("name"), n.file, n.line,
                              json.dumps(n.fields, ensure_ascii=False), fingerprint(g, n)) for n in ordered])
            con.executemany("INSERT INTO edges VALUES (?, ?, ?, ?, ?)",
                            [(e.src, e.rel, e.dst, e.file, e.line) for e in done.edges])
            con.executemany("INSERT INTO crossings VALUES (?, ?, ?, ?, ?, ?)", crossings(done))
    finally:
        con.close()
    os.replace(fresh, path)
    return path
