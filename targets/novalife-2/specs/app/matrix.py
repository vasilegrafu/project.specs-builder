"""What the Matrix page asks, a small part at a time, so that a specification of any size opens at once.

The page never holds the whole specification. It asks for the counts between kinds; for one kind's nodes or one node's
rows, a page of them; for one node's links, each sort or each kind with its first few; and for one link. Each of these is
one query on the indexes of the database, read-only, and nothing here loads the data. What takes a look at everything --
which nodes have a problem, how the nodes join -- is worked out once for each state of the data and held by the server.

What a node holds -- a requirement's criterion, a screen's element -- is counted as that node, as in the Graph: its
links are the node's, each said with the row that states it, and a link inside one node is no link between two.
Rows are in ID order: IDs of one kind, or of one node, differ in their number, so the shorter comes first.
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

import api
import load as loading
import review

PAGE = 200                            # the nodes of a kind, or the rows of a node, in one answer
LINKS_FIRST = 50                      # the links of one sort a node's answer starts with
LINKS_MOST = 500                      # the links of one sort, or of one cell, in one answer
FOUND_MOST = 30                       # what one Find answers
AROUND_EACH = 20                      # the nodes of each kind one node in focus shows
STANDS_MOST = 40                      # the nodes one step of an impact tree shows
CARD_EACH = 6                         # the nodes of each kind a card names among its links
TRACE_EACH = 40                       # the nodes of each kind the layers of one node show
ROW_SWEEPS = 8                        # the times the rows of those layers are set beside what they link to
LAYERS = [["goal"], ["requirement", "quality", "constraint"], ["term", "rule", "role", "entity"], ["endpoint"], ["flow"], ["screen"],
          ["component"]]                              # left to right, in the top menu's order (GROUPS in engine.js)
TRACE_WALK = [["goal"], ["requirement", "quality", "constraint"], ["screen"], ["flow"], ["component", "endpoint"],
              ["rule", "entity", "role", "term"]]     # the way a trace goes: why, what, where, how it is used, what makes it

OWN_LINKS = """
    FROM edges e JOIN nodes far ON far.id = e.{far} JOIN nodes top ON top.id = COALESCE(far.parent, far.id)
    WHERE e.rel <> 'has' AND e.{near} IN (SELECT id FROM nodes WHERE id = :id OR parent = :id)
      AND COALESCE(far.parent, far.id) <> :id"""
FAR_SAID = ("far.id", "far.name", "far.fields", "e.rel")
EVERY_LINK = "GROUP_CONCAT({0}src || char(9) || {0}rel || char(9) || {0}dst, char(10)) AS every"   # those one row of the list stands for
UNLINKED = """
    SELECT id, kind FROM nodes WHERE parent IS NULL AND kind <> 'document' AND id NOT IN (
        SELECT COALESCE(n.parent, n.id) FROM crossings c JOIN nodes n ON n.id = c.src
        UNION SELECT COALESCE(n.parent, n.id) FROM crossings c JOIN nodes n ON n.id = c.dst)"""
UNSETTLED = """
    SELECT id, kind FROM nodes WHERE kind NOT IN ('question', 'addition') AND id IN (
        SELECT COALESCE(t.parent, t.id) FROM edges e JOIN nodes q ON q.id = e.src JOIN nodes t ON t.id = e.dst
            WHERE q.kind IN ('question', 'addition') AND e.rel IN ('about', 'adds to')
        UNION SELECT COALESCE(s.parent, s.id) FROM edges e JOIN nodes q ON q.id = e.dst JOIN nodes s ON s.id = e.src
            WHERE q.kind = 'question' AND e.rel = 'asks')"""


def named(g: dict, row) -> str:
    """What a node is called, whole: its name, or what it says. The page cuts it where it has to, and wraps it elsewhere."""
    fields = json.loads(row["fields"])
    return api.label(g, row["kind"], fields, None) or " ".join(str(fields.get("says") or fields.get("does") or "").split())


def end(g: dict, row) -> dict:
    return {"id": row["id"], "kind": row["kind"], "name": named(g, row), "parent": row["parent"]}


def wanted(query: str) -> list[str]:
    """The words of a query, as LIKE takes them: a % or a _ is a character here."""
    return [w.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") for w in query.lower().split()]


def matching(words: list[str], *columns: str) -> tuple[str, dict]:
    """What keeps a row that has every word in one of its columns: SQL to add to a WHERE, and its values."""
    every = [" OR ".join(f"{c} LIKE :q{i} ESCAPE '\\'" for c in columns) for i in range(len(words))]
    return "".join(f" AND ({one})" for one in every), {f"q{i}": f"%{w}%" for i, w in enumerate(words)}


def in_order(idents: list[str]) -> list[str]:
    return sorted(idents, key=lambda i: (len(i), i))


def problems(root: Path, stale: list) -> dict:
    """Each node that has something to look at, what it holds counted as it, by kind and in ID order: `stale`, standing on
    something changed since it was reviewed; `unlinked`, joined to nothing; `open`, with a question or an addition on it."""
    out: dict[str, dict[str, list[str]]] = {"stale": {}, "unlinked": {}, "open": {}}
    with api.connect(root) as con:
        if not con:
            return out
        if stale:
            nodes = {r["id"]: (r["kind"], r["parent"]) for r in con.execute("SELECT id, kind, parent FROM nodes")}
            for ident in {nodes[s["node"]][1] or s["node"] for s in stale if s["node"] in nodes}:
                out["stale"].setdefault(nodes[ident][0], []).append(ident)
        for what, asked in (("unlinked", UNLINKED), ("open", UNSETTLED)):
            for r in con.execute(asked):
                out[what].setdefault(r["kind"], []).append(r["id"])
    return {what: {kind: in_order(ids) for kind, ids in held.items()} for what, held in out.items()}


def grid(root: Path, stale: list, troubled: dict) -> dict | None:
    """How many links go from each kind to each other, by sort, how many of them are stale, how many nodes each kind has,
    and how many of them have a problem."""
    with api.connect(root) as con:
        if not con:
            return None
        kinds = con.execute("SELECT kind, count(*) AS n FROM nodes WHERE parent IS NULL GROUP BY kind").fetchall()
        cells: dict[tuple[str, str], dict[str, int]] = {}
        for r in con.execute("SELECT from_kind, to_kind, rel, count(*) AS n FROM crossings GROUP BY from_kind, to_kind, rel"):
            cells.setdefault((r["from_kind"], r["to_kind"]), {})[r["rel"]] = r["n"]
        owed: dict[tuple[str, str], int] = {}
        said = {s["link"] for s in stale}
        if said:
            for r in con.execute("SELECT from_kind, to_kind, src, rel, dst FROM crossings"):
                if f"{r['src']} {r['rel']} {r['dst']}" in said:
                    owed[(r["from_kind"], r["to_kind"])] = owed.get((r["from_kind"], r["to_kind"]), 0) + 1
        return {"kinds": [{"kind": r["kind"], "count": r["n"]} for r in kinds],
                "cells": [{"from": a, "to": b, "count": sum(rels.values()), "rels": rels, "stale": owed.get((a, b), 0)}
                          for (a, b), rels in cells.items()],
                "nodes": sum(r["n"] for r in kinds), "links": sum(sum(rels.values()) for rels in cells.values()),
                "stale": sum(owed.values()),
                "problems": {what: {kind: len(ids) for kind, ids in held.items()} for what, held in troubled.items()}}


def cell(root: Path, stale: list, source: str, target: str, offset: int = 0, limit: int = LINKS_FIRST, query: str = "") -> dict | None:
    """The links from one kind to another, a page of them, in ID order, between nodes as the Graph has them -- what a node holds
    counts as that node, one row to a pair, with how many links it stands for; with `query`, those it finds."""
    limit = min(limit, LINKS_MOST)
    with api.connect(root) as con:
        if not con:
            return None
        g = loading.grammar()
        words, values = matching(wanted(query), "s.id", "s.name", "s.fields", "d.id", "d.name", "d.fields", "c.rel")
        asked = {"a": source, "b": target, **values}
        ends = "JOIN nodes s ON s.id = c.src JOIN nodes d ON d.id = c.dst"
        kept = "c.from_kind = :a AND c.to_kind = :b"
        tops = f"""SELECT COALESCE(s.parent, s.id) AS a, COALESCE(d.parent, d.id) AS b, c.src, c.rel, c.dst, c.place
                   FROM crossings c {ends} WHERE {kept}{words}"""
        total, links = con.execute(f"SELECT count(DISTINCT a || char(9) || b || char(9) || rel), count(*) FROM ({tops})", asked).fetchone()
        rows = con.execute(f"""SELECT a, b, rel, MIN(place) AS first, {EVERY_LINK.format("")} FROM ({tops})
                               GROUP BY a, b, rel ORDER BY first LIMIT :limit OFFSET :offset""",
                           {**asked, "limit": limit, "offset": offset}).fetchall()
        named = named_nodes(con, g, sorted({r["a"] for r in rows} | {r["b"] for r in rows}))
        owed = {s["link"] for s in stale}

        def row(r) -> dict:
            every = sorted((link.replace("\t", " ") for link in r["every"].split("\n")), key=api.natural)
            behind = [link for link in every if link in owed]
            return {"src": named[r["a"]], "rel": r["rel"], "dst": named[r["b"]], "said": (behind or every)[0], "count": len(every), "stale": bool(behind)}

        return {"from": source, "to": target, "total": total, "links count": links, "offset": offset, "links": [row(r) for r in rows]}


def tree(root: Path, kind: str = "", parent: str = "", offset: int = 0, at: str = "", within: list[str] | None = None) -> dict | None:
    """A page of one kind's nodes, or of one node's rows, each with how many rows it holds and how many links it has,
    what it holds counted; of `within`, those IDs alone. With `at`, the page that ID is on, and where in the list it
    stands: nowhere, if it is not in the list."""
    with api.connect(root) as con:
        if not con:
            return None
        g = loading.grammar()
        position = None
        if within is not None:
            total = len(within)
            if at in within:
                position = within.index(at)
                offset = position - position % PAGE
            chosen = within[offset:offset + PAGE]
            page = f"SELECT value AS id FROM json_each(?)"
            values: tuple = (json.dumps(chosen),)
        else:
            whose, asked = ("parent = ?", parent) if parent else ("kind = ? AND parent IS NULL", kind)
            total = con.execute(f"SELECT count(*) FROM nodes WHERE {whose}", (asked,)).fetchone()[0]
            if at:
                position = con.execute(f"SELECT count(*) FROM nodes WHERE {whose} AND (length(id) < length(?) OR "
                                       f"(length(id) = length(?) AND id < ?))", (asked, at, at, at)).fetchone()[0]
                offset = position - position % PAGE
            page = f"SELECT id FROM nodes WHERE {whose} ORDER BY length(id), id LIMIT ? OFFSET ?"
            values = (asked, PAGE, offset)
        rows = con.execute(f"""
            WITH page AS ({page})
            SELECT n.id, n.kind, n.parent, n.fields,
                   (SELECT count(*) FROM nodes c WHERE c.parent = n.id) AS parts,
                   (SELECT count(*) FROM edges e JOIN nodes f ON f.id = e.dst WHERE e.rel <> 'has' AND e.src IN
                        (SELECT id FROM nodes WHERE id = n.id OR parent = n.id) AND COALESCE(f.parent, f.id) <> n.id) +
                   (SELECT count(*) FROM edges e JOIN nodes f ON f.id = e.src WHERE e.rel <> 'has' AND e.dst IN
                        (SELECT id FROM nodes WHERE id = n.id OR parent = n.id) AND COALESCE(f.parent, f.id) <> n.id) AS linked
            FROM page JOIN nodes n ON n.id = page.id ORDER BY length(n.id), n.id""", values).fetchall()
        return {"total": total, "offset": offset, "position": position,
                "rows": [{**end(g, r), "parts": r["parts"], "links": r["linked"]} for r in rows]}


def find(root: Path, query: str) -> list[dict]:
    """The nodes a few words find, rows too: every word in the ID, the name or the text, an ID typed whole first, then an
    ID it begins, then a name it is in. Asked of the database, so that it stays quick."""
    words = wanted(query)
    if not words:
        return []
    with api.connect(root) as con:
        if not con:
            return []
        g = loading.grammar()
        every, values = matching(words, "id", "name", "fields")
        rows = con.execute(f"""SELECT id, kind, parent, fields FROM nodes WHERE 1{every}
                               ORDER BY lower(id) = :whole DESC, lower(id) LIKE :starts ESCAPE '\\' DESC, name LIKE :q0 ESCAPE '\\' DESC,
                                        parent IS NOT NULL, length(id), id LIMIT :most""",
                           {**values, "whole": words[0], "starts": f"{words[0]}%", "most": FOUND_MOST}).fetchall()
        return [end(g, r) for r in rows]


def link_row(g: dict, r, way: str, ident: str, owed: set) -> dict:
    """One row of a node's links: the node at the far end, never a row it holds, and how many links reach it. The one opened
    from it is the first stale one, or the first."""
    every = sorted((link.split("\t") for link in r["every"].split("\n")), key=lambda l: (api.natural(l[0]), api.natural(l[2])))
    stale = [link for link in every if " ".join(link) in owed]
    src, rel, dst = (stale or every)[0]
    near = src if way == "out" else dst
    return {"src": src, "rel": rel, "dst": dst, "far": end(g, r), "from": near if near != ident else "", "count": len(every),
            "word": rel if way == "out" else g["relations"][rel].get("back", rel), "stale": bool(stale)}


def sort_of(con, g: dict, ident: str, way: str, rel: str, offset: int, limit: int, words: list[str], owed: set) -> list[dict]:
    near, far = ("src", "dst") if way == "out" else ("dst", "src")
    said, values = matching(words, *FAR_SAID)
    rows = con.execute(f"""SELECT top.id, top.kind, top.fields, top.parent, {EVERY_LINK.format("e.")}
                           {OWN_LINKS.format(far=far, near=near)} AND e.rel = :rel{said}
                           GROUP BY top.id ORDER BY length(top.id), top.id LIMIT :limit OFFSET :offset""",
                       {"id": ident, "rel": rel, "limit": limit, "offset": offset, **values}).fetchall()
    return [link_row(g, r, way, ident, owed) for r in rows]


def both_ways(words: list[str]) -> tuple[str, dict]:
    """A node's links either way, each with the kind that holds its far end, as one list to count and to page."""
    said, values = matching(words, *FAR_SAID)
    return " UNION ALL ".join(
        f"""SELECT e.src, e.rel, e.dst, top.id, top.kind, top.fields, top.parent, '{way}' AS way,
                   top.kind AS top_kind, top.id AS top_id
            {OWN_LINKS.format(far=far, near=near)}{said}"""
        for way, near, far in (("out", "src", "dst"), ("back", "dst", "src"))), values


def kind_of(con, g: dict, ident: str, kind: str, offset: int, limit: int, words: list[str], owed: set) -> list[dict]:
    joined, values = both_ways(words)
    rows = con.execute(f"""SELECT id, kind, fields, parent, way, {EVERY_LINK.format("")} FROM ({joined}) WHERE top_kind = :kind
                           GROUP BY top_id, rel, way ORDER BY length(top_id), top_id, way LIMIT :limit OFFSET :offset""",
                       {"id": ident, "kind": kind, "limit": limit, "offset": offset, **values}).fetchall()
    return [link_row(g, r, r["way"], ident, owed) for r in rows]


def links(root: Path, stale: list, ident: str, way: str = "", rel: str = "", offset: int = 0, limit: int = LINKS_FIRST,
          query: str = "", by: str = "sort", of: str = "") -> dict | None:
    """One node and its links both ways, each sort -- or with `by` kind, each kind that holds a far end -- with its count
    and its first few; with `way` and `rel`, or `of`, more of that one. With `query`, only the links it finds."""
    limit = min(limit, LINKS_MOST)
    words = wanted(query)
    owed = {s["link"] for s in stale}
    with api.connect(root) as con:
        if not con:
            return None
        row = con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id = ?", (ident,)).fetchone()
        if row is None:
            return None
        g = loading.grammar()
        if way:
            return {"links": sort_of(con, g, ident, way, rel, offset, limit, words, owed)}
        if of:
            return {"links": kind_of(con, g, ident, of, offset, limit, words, owed)}
        top = con.execute("SELECT id, kind FROM nodes WHERE id = ?", (row["parent"],)).fetchone() if row["parent"] else row
        parts = con.execute("SELECT count(*) FROM nodes WHERE parent = ?", (ident,)).fetchone()[0]
        groups = []
        if by == "kind":
            joined, values = both_ways(words)
            for r in con.execute(f"""SELECT top_kind, count(*) AS n, count(DISTINCT top_id || char(9) || rel || char(9) || way) AS rows
                                     FROM ({joined}) GROUP BY top_kind ORDER BY rows DESC, top_kind""",
                                 {"id": ident, **values}).fetchall():
                groups.append({"kind": r["top_kind"], "count": r["rows"], "links count": r["n"],
                               "links": kind_of(con, g, ident, r["top_kind"], 0, limit, words, owed)})
        else:
            order = {rel: i for i, rel in enumerate(g["relations"])}
            said, values = matching(words, *FAR_SAID)
            for w, near, far in (("out", "src", "dst"), ("back", "dst", "src")):
                counts = con.execute(f"""SELECT e.rel, count(*) AS n, count(DISTINCT top.id) AS rows
                                         {OWN_LINKS.format(far=far, near=near)}{said} GROUP BY e.rel""",
                                     {"id": ident, **values}).fetchall()
                for r in sorted(counts, key=lambda r: order.get(r["rel"], len(order))):
                    word = r["rel"] if w == "out" else g["relations"][r["rel"]].get("back", r["rel"])
                    groups.append({"way": w, "rel": r["rel"], "label": word[:1].upper() + word[1:], "count": r["rows"], "links count": r["n"],
                                   "links": sort_of(con, g, ident, w, r["rel"], 0, limit, words, owed)})
        return {"node": {**end(g, row), "parts": parts, "top": {"id": top["id"], "kind": top["kind"]}}, "groups": groups}


def link(root: Path, stale: list, src: str, rel: str, dst: str) -> dict | None:
    """One link: both ends, how it reads from each, where it is written, which end goes stale when the other changes,
    and whether it is stale now."""
    with api.connect(root) as con:
        if not con:
            return None
        edge = con.execute("SELECT src, rel, dst, file, line FROM edges WHERE src = ? AND rel = ? AND dst = ?",
                           (src, rel, dst)).fetchone()
        if edge is None or rel == "has":
            return None
        g = loading.grammar()
        ends = [end(g, con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id = ?", (i,)).fetchone())
                for i in (src, dst)]
        said = f"{src} {rel} {dst}"
        owed = [{"node": s["node"], "on": s["on"], "was": s["was"], "now": s["now"]} for s in stale if s["link"] == said]
        back = g["relations"][rel].get("back", rel)
        stands = review.ends(g, loading.Edge(src, rel, dst, edge["file"], edge["line"]))
        return {"src": ends[0], "rel": rel, "dst": ends[1], "reads": said, "back": back, "reads back": f"{dst} {back} {src}",
                "file": edge["file"], "line": edge["line"], "stands": [{"node": a, "on": b} for a, b in stands], "stale": owed}


def joins(root: Path) -> dict[str, list[tuple]]:
    """Every node standing alone and what it is joined to, either way: (the node, src, rel, dst, how a change passes along
    it, whether this end states the link). What a node holds counts as it. Held by the server: a path looks at all of it."""
    ways: dict[str, list[tuple]] = {}
    with api.connect(root) as con:
        if not con:
            return ways
        g = loading.grammar()
        passes = {rel: r.get("stale", "to") for rel, r in g["relations"].items()}
        for r in con.execute("""SELECT c.src, c.rel, c.dst, COALESCE(s.parent, s.id) AS a, COALESCE(d.parent, d.id) AS b
                                FROM crossings c JOIN nodes s ON s.id = c.src JOIN nodes d ON d.id = c.dst"""):
            ways.setdefault(r["a"], []).append((r["b"], r["src"], r["rel"], r["dst"], passes[r["rel"]], True))
            ways.setdefault(r["b"], []).append((r["a"], r["src"], r["rel"], r["dst"], passes[r["rel"]], False))
    return ways


def walk(ways: dict[str, list[tuple]], start: str, goal: str, changing: bool) -> list[tuple] | None:
    """The fewest links from one node to another, breadth first, either way along each."""
    came: dict[str, tuple | None] = {start: None}
    queue = deque([start])
    while queue:
        at = queue.popleft()
        if at == goal:
            steps = []
            while came[at] is not None:
                before, step = came[at]
                steps.append(step)
                at = before
            return steps[::-1]
        for other, src, rel, dst, passes, _ in ways.get(at, ()):
            if other not in came and (passes != "none" or not changing):
                came[other] = (at, (src, rel, dst))
                queue.append(other)
    return None


def path(root: Path, ways: dict[str, list[tuple]], source: str, target: str) -> dict | None:
    """The shortest chain of links between two nodes: by links a change passes along, if there is one -- it says why the
    one bears on the other -- or by any links, and it says which."""
    with api.connect(root) as con:
        if not con:
            return None
        g = loading.grammar()
        one = lambda ident: con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id = ?", (ident,)).fetchone()  # noqa: E731
        node = lambda ident: end(g, one(one(ident)["parent"] or ident))      # noqa: E731 -- as the Graph has it, not a row it holds
        a, b = one(source), one(target)
        if a is None or b is None:
            return None
        start, goal = a["parent"] or a["id"], b["parent"] or b["id"]
        steps = walk(ways, start, goal, True)
        changing = steps is not None
        if steps is None:
            steps = walk(ways, start, goal, False)
        return {"from": end(g, a), "to": end(g, b), "found": steps is not None, "changing": changing,
                "steps": [{"src": node(src), "rel": rel, "dst": node(dst), "said": f"{src} {rel} {dst}"} for src, rel, dst in steps or []]}


def named_nodes(con, g: dict, idents: list[str]) -> dict[str, dict]:
    rows = con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id IN (SELECT value FROM json_each(?))", (json.dumps(idents),))
    return {r["id"]: end(g, r) for r in rows}


def picture(root: Path, ways: dict[str, list[tuple]], cells: list[dict], opened: dict[str, tuple[int, int]]) -> dict | None:
    """The Graph's map and its layers: each kind with its count, an open kind with its nodes, the most linked first, as many as
    `opened` says from where it says; and what joins all that shows, each pair once. A link reaches a node where it shows, and
    its kind where it does not; what lies between two kinds and shows at neither end stays their count."""
    with api.connect(root) as con:
        if not con:
            return None
        g = loading.grammar()
        kinds = {r["id"]: r["kind"] for r in con.execute("SELECT id, kind FROM nodes WHERE parent IS NULL")}
        held: dict[str, list[str]] = {}
        for ident, kind in kinds.items():
            held.setdefault(kind, []).append(ident)
        chosen: dict[str, list[str]] = {}
        for kind, (most, start) in opened.items():
            chosen[kind] = sorted(held.get(kind, []), key=lambda i: (-len(ways.get(i, ())), len(i), i))[start:start + most]
        showing = {i for ids in chosen.values() for i in ids}
        named = named_nodes(con, g, sorted(showing))
        pairs: dict[tuple[str, str], dict[str, int]] = {}

        def add(a: str, b: str, rel: str, n: int = 1) -> None:
            said = pairs.setdefault((a, b) if a < b else (b, a), {})
            said[rel] = said.get(rel, 0) + n

        left = {(c["from"], c["to"]): dict(c["rels"]) for c in cells}
        for ident in showing:
            for other, _, rel, _, _, states in ways.get(ident, ()):
                if other in showing and ident > other:
                    continue                                    # the other end says it
                add(ident, other if other in showing else f"kind:{kinds[other]}", rel)
                a, b = (kinds[ident], kinds[other]) if states else (kinds[other], kinds[ident])
                left[(a, b)][rel] -= 1
        for (a, b), rels in left.items():
            for rel, n in rels.items():
                if n > 0 and a != b:
                    add(f"kind:{a}", f"kind:{b}", rel, n)
        return {"kinds": [{"kind": kind, "count": len(ids), "nodes": [{**named[i], "links": len(ways.get(i, ()))} for i in chosen.get(kind, [])]}
                          for kind, ids in held.items()],
                "links": [{"a": a, "b": b, "count": sum(rels.values()), "rels": rels} for (a, b), rels in pairs.items()],
                "nodes": len(kinds), "total": sum(sum(c["rels"].values()) for c in cells), "layers": LAYERS}


def around(root: Path, ways: dict[str, list[tuple]], ident: str, each: int = AROUND_EACH) -> dict | None:
    """One node and what it is linked to, what it holds counted: of each kind the most linked to it first, and how many
    are left out. Each says which sorts of link join them, and whether they run out of it, into it, or both."""
    with api.connect(root) as con:
        if not con:
            return None
        row = con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id = ?", (ident,)).fetchone()
        if row is None:
            return None
        g = loading.grammar()
        top = row["parent"] or row["id"]
        joined: dict[str, dict] = {}
        for other, _, rel, _, _, states in ways.get(top, ()):
            said = joined.setdefault(other, {"rels": {}, "out": False, "in": False})
            said["rels"][rel] = said["rels"].get(rel, 0) + 1
            said["out" if states else "in"] = True
        kinds = {} if not joined else {r["id"]: r["kind"] for r in con.execute(
            "SELECT id, kind FROM nodes WHERE id IN (SELECT value FROM json_each(?))", (json.dumps(sorted(joined)),))}
        by_kind: dict[str, list[str]] = {}
        for other in joined:
            by_kind.setdefault(kinds[other], []).append(other)
        kept = [i for ids in by_kind.values() for i in sorted(ids, key=lambda i: (-sum(joined[i]["rels"].values()), len(i), i))[:each]]
        named = named_nodes(con, g, kept)
        centre = row if not row["parent"] else con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id = ?", (top,)).fetchone()
        return {"centre": end(g, centre), "neighbours": [{**named[i], **joined[i]} for i in kept], "left": len(joined) - len(kept),
                "counts": {kind: len(ids) for kind, ids in by_kind.items()}}


def linked(root: Path, ways: dict[str, list[tuple]], ident: str, each: int = CARD_EACH) -> dict | None:
    """What a card says of a node's links: each kind it is joined to, the most first, with how many and the closest few."""
    found = around(root, ways, ident, each)
    if found is None:
        return None
    return {"kinds": [{"kind": kind, "count": count, "nodes": [{"id": n["id"], "name": n["name"]} for n in found["neighbours"] if n["kind"] == kind]}
                      for kind, count in sorted(found["counts"].items(), key=lambda k: (-k[1], k[0]))]}


def stands(root: Path, ways: dict[str, list[tuple]], ident: str, most: int = STANDS_MOST) -> dict | None:
    """What stands on a node: each node a change to it would turn stale at once, by which sorts of link, with how many stand
    on that in turn, so that the page can say so before it asks."""
    def on(at: str) -> dict[str, dict[str, int]]:
        found: dict[str, dict[str, int]] = {}
        for other, _, rel, _, passes, states in ways.get(at, ()):
            if passes == "both" or (passes == "to" and not states) or (passes == "from" and states):
                said = found.setdefault(other, {})
                said[rel] = said.get(rel, 0) + 1
        return found

    with api.connect(root) as con:
        if not con:
            return None
        row = con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id = ?", (ident,)).fetchone()
        if row is None:
            return None
        g = loading.grammar()
        top = row if not row["parent"] else con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id = ?", (row["parent"],)).fetchone()
        found = on(top["id"])
        kept = in_order(list(found))[:most]
        named = named_nodes(con, g, kept)
        return {"node": end(g, top), "stands": [{**named[i], "rels": found[i], "next": len(on(i))} for i in kept], "more": len(found) - len(kept)}


def in_rows(kept: dict[str, list[str]], joined: list[tuple[str, str]]) -> dict[str, list[str]]:
    """The rows of each kind in Layers, each beside what it links to, so that fewer links cross: a node goes to the mean height of
    the nodes it joins in other columns, sweeping the columns one way and back. Kinds keep their place in a column."""
    near: dict[str, list[str]] = {}
    for a, b in joined:
        near.setdefault(a, []).append(b)
        near.setdefault(b, []).append(a)
    rows = {kind: list(ids) for kind, ids in kept.items()}

    def standing() -> dict[str, tuple[int, float]]:
        spots = {}
        for c, held in enumerate(LAYERS):
            tall = sum(len(rows.get(kind, [])) + 1 for kind in held if rows.get(kind))
            y = 0.0
            for kind in held:
                ids = rows.get(kind, [])
                if ids:
                    y += 1
                for i in ids:
                    spots[i] = (c, y - tall / 2)
                    y += 1
        return spots

    order = [kind for held in LAYERS for kind in held if kind in rows]
    for sweep in range(ROW_SWEEPS):
        for kind in order if sweep % 2 == 0 else order[::-1]:
            spots = standing()

            def height(i: str) -> float:
                ys = [spots[o][1] for o in near.get(i, ()) if o in spots and spots[o][0] != spots[i][0]]
                return sum(ys) / len(ys) if ys else spots[i][1]

            rows[kind] = sorted(rows[kind], key=height)
    return rows


def traced(root: Path, ways: dict[str, list[tuple]], ident: str, steps: int = 0, each: int = TRACE_EACH) -> dict | None:
    """The layers of one node: what connects to it, always going on in one direction of TRACE_WALK -- back towards why, on towards
    what makes it -- so that a trace never turns back through the whole specification; `steps` links out from it, or all the
    way at 0. Of each kind the nearest are kept, and `count` says how many are reached; their rows stand beside what they link to
    (`in_rows`). What joins those shown comes with them, each link saying whether the trace `walked` it."""
    with api.connect(root) as con:
        if not con:
            return None
        row = con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id = ?", (ident,)).fetchone()
        if row is None:
            return None
        g = loading.grammar()
        top = row if not row["parent"] else con.execute("SELECT id, kind, parent, fields FROM nodes WHERE id = ?", (row["parent"],)).fetchone()
        kinds = {r["id"]: r["kind"] for r in con.execute("SELECT id, kind FROM nodes WHERE parent IS NULL")}
        column = {kind: i for i, held in enumerate(TRACE_WALK) for kind in held}
        start = top["id"]
        reached = {start: 0}
        walked: set[tuple[str, str]] = set()
        for sign in (-1, 1):
            seen = {start}
            wave = [start]
            step = 0
            while wave and (not steps or step < steps):
                step += 1
                ahead: dict[str, None] = {}
                for at in wave:
                    here = column.get(kinds[at])
                    for other, *_ in ways.get(at, ()):
                        there = column.get(kinds[other])
                        if there is None or (here is not None and sign * (there - here) <= 0) or (other in seen and other not in ahead):
                            continue
                        seen.add(other)
                        ahead[other] = None
                        reached.setdefault(other, step)
                        walked.add((at, other) if at < other else (other, at))
                wave = list(ahead)
        by_kind: dict[str, list[str]] = {}
        for i in sorted(reached, key=lambda i: (reached[i], len(i), i)):
            by_kind.setdefault(kinds[i], []).append(i)
        kept = {kind: ids[:each] for kind, ids in by_kind.items()}
        if start not in kept.get(kinds[start], []):
            kept[kinds[start]] = [start, *kept.get(kinds[start], [])][:each]
        showing = {i for ids in kept.values() for i in ids}
        named = named_nodes(con, g, sorted(showing))
        pairs: dict[tuple[str, str], dict[str, int]] = {}
        for ident_at in showing:
            for other, _, rel, _, _, _ in ways.get(ident_at, ()):
                if other in showing and ident_at < other:
                    said = pairs.setdefault((ident_at, other), {})
                    said[rel] = said.get(rel, 0) + 1
        rows = in_rows(kept, [pair for pair in pairs if pair in walked])
        return {"node": end(g, top), "layers": LAYERS,
                "kinds": [{"kind": kind, "count": len(by_kind[kind]), "nodes": [named[i] for i in ids]} for kind, ids in rows.items()],
                "links": [{"a": a, "b": b, "count": sum(rels.values()), "rels": rels, "walked": (a, b) in walked} for (a, b), rels in pairs.items()]}
