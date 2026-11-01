"""What the application answers, read from the database: plain functions from a question to a JSON-ready answer,
so the server, the command line and the selftest ask the same thing the same way.

Every read opens the database read-only. A node's links come back in both directions, each named from where it
is seen -- R4 `enforces` B1, B1 `enforced by` R4 -- by the grammar's `back` label, so no relation is ever written
twice to be read from both ends.
"""
from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import evidence
import finish
import load as loading
import prototypes as drawing
import review

GRAPH_LIMIT = 60                      # nodes in one picture: more than a reader follows
MENU_FIRST = 5                        # the nodes of a kind the menu's answer names before "All"
CARD_SAID = 280                       # the characters of its text a card quotes, cut at a word
CARD_IDS = 8                          # the IDs one fact of a card names before "and so many more"
ROWS = {"criterion": ("criterion", "criteria"), "element": ("element", "elements"), "part": ("part", "parts"),
        "state": ("state", "states")}
SEARCH_LIMIT = 30                     # what one search answers, the best first
PICTURES = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def natural(ident: str) -> list:
    return [int(x) if x.isdigit() else x for x in re.findall(r"\d+|\D+", ident)]


@contextmanager
def connect(root: Path):
    """The database, read-only, for one answer, and closed after it: an open file cannot be replaced on Windows,
    so a connection left open would stop the next build from putting the new database in place."""
    path = root / loading.DATABASE
    if not path.is_file():
        yield None
        return
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def title(root: Path) -> str:
    """What the specification is called, until it says: the folder that holds `specs/`, or its own."""
    return root.parent.name if root.name == "specs" else root.name


def owed(root: Path) -> list[dict]:
    """Every node stale: standing on something that changed since it was reviewed against it. A stamps file that
    cannot be read is raised, never taken as empty: that would forgive every stale node at once."""
    done = loading.load(root)
    return [] if done.problems else review.stale(loading.grammar(), done, review.held(root))


def opened(root: Path) -> dict:
    """All that is not settled -- empty while the data does not load: its problems come first."""
    done = loading.load(root)
    if done.problems:
        return {}
    return finish.opened(loading.grammar(), done, review.held(root))


def summary(root: Path, problems: list, stale: list | None = None) -> dict:
    g = loading.grammar()
    with connect(root) as con:
        counts = dict(con.execute("SELECT kind, count(*) FROM nodes GROUP BY kind").fetchall()) if con else {}
        links = con.execute("SELECT count(*) FROM edges").fetchone()[0] if con else 0
        stale = owed(root) if stale is None else stale
        named = con.execute("SELECT name FROM nodes WHERE id = 'document'").fetchone() if con else None
        words = [json.loads(r[0]).get("confidence") for r in con.execute(
            "SELECT fields FROM nodes WHERE kind = 'requirement'").fetchall()] if con else []
        return {"title": (named[0] if named and named[0] else title(root)), "built": con is not None, "links": links,
                "stands": {w: words.count(w) for w in g["choices"]["confidence"] if w in words},
                "stale": {"nodes": len({s["node"] for s in stale}), "links": len(stale)},
                "kinds": [{"kind": k, "is": spec["is"], "count": counts.get(k, 0), "listed": "folder" in spec}
                          for k, spec in g["kinds"].items()],
                "problems": [{"file": f, "line": n, "message": m} for f, n, m in problems]}


def label(g: dict, kind: str, fields: dict, most: int | None = 90) -> str:
    """What a node is called in a list: its name, or the first words of its text where its kind has no name -- all
    of them where `most` is None."""
    if fields.get("name"):
        return fields["name"]
    for d in g["kinds"][kind].get("sections", {}).values():
        said = fields.get(d.get("as", ""))
        if d["type"] == "text" and isinstance(said, str) and said:
            words = " ".join(said.split())
            return words if most is None or len(words) <= most else words[:most - 3].rsplit(" ", 1)[0] + "..."
    return ""


def form(g: dict, kind: str) -> dict:
    """What a kind holds, as a form needs it: each field with its choices, each link it states, each text, each
    table with its columns, its rows' columns, and every relation it may be tied by -- the names the operations
    take."""
    s = g["kinds"][kind]
    sections = s.get("sections", {})
    title = lambda t, d: t or d["as"][0].upper() + d["as"][1:]      # noqa: E731
    column = lambda c: {"name": c["name"], "key": c.get("as") or c.get("relation") or c["name"].lower(),  # noqa: E731
                        **({"relation": c["relation"]} if c.get("relation") else {}),
                        **({"id": c["id"]} if c.get("id") else {}),
                        **({"required": True} if c.get("required") else {})}
    has = g["relations"]["has"]
    rows = next(({"kind": d["kind"], "section": t, "list": not d.get("table"),
                  "least": has.get("least", 0) if kind in has.get("least of", has["from"]) else 0,
                  "columns": [column(c) for c in g["kinds"][d["kind"]].get("columns", [])]}
                 for t, d in sections.items() if d["type"] == "children"), None)
    relations = []                                      # what a node of this kind is tied by, where it is written
    for rel, r in g["relations"].items():
        if kind not in r["from"] or rel == "has":
            continue
        if s.get("columns"):                            # a row: its links are its cells
            place = "column" if "column" in r else None
        else:
            place = "field" if "field" in r else "actions" if isinstance(r.get("section"), str) else None
        if place:
            needed = r.get("least", 0) if kind in r.get("least of", r["from"]) else 0
            relations.append({"rel": rel, "to": r["to"], "where": place, "words": place == "actions",
                              **({"field": r["field"]} if place == "field" else {}),
                              **({"least": needed, "unless": r.get("unless", {})} if needed else {})})
    return {"listed": "folder" in s, "named": "name" in s.get("fields", {}),
            "fields": [{"key": k, "choices": g["choices"][f["of"]] if f.get("type") == "choice" else None,
                        "required": bool(f.get("required"))} for k, f in s.get("fields", {}).items()],
            "texts": [{"as": d["as"], "title": title(t, d), "required": bool(d.get("required"))}
                      for t, d in sections.items() if d["type"] == "text"],
            "tables": [{"as": d["as"], "title": title(t, d), "columns": [column(c) for c in d["columns"]]}
                       for t, d in sections.items() if d["type"] == "table"],
            "rows": rows, "relations": relations}


def grammar_view() -> dict:
    g = loading.grammar()
    return {"kinds": {k: {"is": s["is"], "id": s["id"], "single": bool(s.get("single")),
                          "texts": [{"as": d["as"], "title": t or d["as"][0].upper() + d["as"][1:]}
                                    for t, d in s.get("sections", {}).items() if d["type"] == "text"],
                          "form": form(g, k)}
                      for k, s in g["kinds"].items()},
            "relations": {r: {"back": v.get("back", r), "from": v["from"], "to": v["to"]}
                          for r, v in g["relations"].items()}}


def names(root: Path) -> dict:
    """Every ID with its kind and name: what the engine needs to turn an ID in a text into a link."""
    with connect(root) as con:
        if not con:
            return {}
        g = loading.grammar()
        return {row["id"]: {"kind": row["kind"], "name": label(g, row["kind"], json.loads(row["fields"]))}
                for row in con.execute("SELECT id, kind, fields FROM nodes")}


def nodes(root: Path, kind: str) -> list[dict]:
    with connect(root) as con:
        if not con:
            return []
        rows = con.execute("""
            SELECT n.id, n.name, n.fields,
                   (SELECT count(*) FROM edges e WHERE e.src = n.id) AS out_count,
                   (SELECT count(*) FROM edges e WHERE e.dst = n.id) AS in_count,
                   (SELECT count(*) FROM nodes c WHERE c.parent = n.id) AS parts
            FROM nodes n WHERE n.kind = ? AND n.parent IS NULL""", (kind,)).fetchall()
        out = []
        g = loading.grammar()
        for row in rows:
            fields = json.loads(row["fields"])
            out.append({"id": row["id"], "name": label(g, kind, fields), "whole": label(g, kind, fields, None),
                        "priority": fields.get("priority"), "backed": fields.get("confidence"),
                        "links": row["out_count"], "linked from": row["in_count"], "parts": row["parts"]})
        return sorted(out, key=lambda r: natural(r["id"]))


def said_in(value: object) -> str:
    """Every word a field holds, a table's cells too."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(said_in(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(said_in(v) for v in value)
    return ""


def search(root: Path, query: str, limit: int = SEARCH_LIMIT) -> list[dict]:
    """The nodes a few words find, rows too, the best first: an ID typed whole, then an ID it begins, then a word
    of a name -- the whole name, a whole word, the start of one, anywhere in it -- then anywhere in what the node
    says; every word found, or the node is not. Each comes with the words around where its text was found."""
    words = query.lower().split()
    if not words:
        return []
    g = loading.grammar()
    found = []
    with connect(root) as con:
        if not con:
            return []
        for r in con.execute("SELECT id, kind, parent, fields FROM nodes"):
            fields = json.loads(r["fields"])
            row = " ".join(str(fields.get("says") or fields.get("does") or "").split())   # a row's words
            name = label(g, r["kind"], fields) or (row if len(row) <= 90 else row[:87].rsplit(" ", 1)[0] + "...")
            ident, low_name = r["id"].lower(), name.lower()
            text = " ".join(said_in(fields).split())
            low_text = text.lower()
            score, in_text = 0, None
            for w in words:
                if ident == w:
                    score += 100
                elif ident.startswith(w):
                    score += 60
                elif re.search(r"\b" + re.escape(w) + r"\b", low_name):
                    score += 40 if low_name == w else 35
                elif re.search(r"\b" + re.escape(w), low_name):
                    score += 30
                elif w in low_name:
                    score += 20
                elif w in low_text:
                    score += 8
                    in_text = in_text if in_text is not None else low_text.index(w)
                else:
                    score = 0
                    break
            if not score:
                continue
            snippet = ""
            if in_text is not None:
                start = max(0, in_text - 40)
                start = text.rfind(" ", 0, start) + 1 if start else 0
                snippet = ("... " if start else "") + text[start:start + 120] + (" ..." if start + 120 < len(text) else "")
            found.append({"id": r["id"], "kind": r["kind"], "parent": r["parent"], "name": name or r["id"],
                          "snippet": snippet, "score": score})
    found.sort(key=lambda f: (-f["score"], f["parent"] is not None, natural(f["id"])))
    return found[:limit]


def menu(root: Path, done: loading.Load | None = None, stale: list | None = None) -> dict:
    """What each part of the menu opens on, so its panel shows what its page holds before the page is opened:
    every kind's count and first nodes, the document and whether it may be agreed, how much is not settled, the
    evidence's folders and the prototype's flows. `done` is the data as loaded and `stale` what is stale in it, where the asker
    already holds them."""
    g = loading.grammar()
    out: dict = {"kinds": {}, "document": {}, "open": None, "investigate": 0, "ready": None, "evidence": [],
                 "prototype": prototypes(root)}
    with connect(root) as con:
        if not con:
            return out
        for kind in g["kinds"]:
            rows = sorted(con.execute("SELECT id, fields FROM nodes WHERE kind = ? AND parent IS NULL", (kind,)),
                          key=lambda r: natural(r["id"]))
            if rows:
                out["kinds"][kind] = {"count": len(rows), "first": [
                    {"id": r["id"], "name": label(g, kind, json.loads(r["fields"]))} for r in rows[:MENU_FIRST]]}
        doc = con.execute("SELECT fields FROM nodes WHERE id = 'document'").fetchone()
    if doc:
        fields = json.loads(doc["fields"])
        first = next((p for p in re.split(r"\n\s*\n", fields.get("summary", "")) if p.strip()), "")
        first = " ".join(first.split())
        out["document"] = {"name": fields.get("name", ""), "kind": fields.get("kind", ""),
                           "status": fields.get("status", ""),
                           "summary": first if len(first) <= 320 else first[:320].rsplit(" ", 1)[0] + " ..."}
    done = done or loading.load(root)
    if not done.problems:
        try:
            stamps = review.held(root)
        except ValueError:                              # said on every view; the panel leaves it out
            stamps = None
        if stamps is not None:
            unsettled = finish.opened(g, done, stamps, stale)
            out["open"] = sum(len(v) for k, v in unsettled.items() if k != "to investigate" and isinstance(v, list))
            out["investigate"] = len(unsettled.get("to investigate", []))
            out["ready"] = finish.ready(g, done, stamps, unsettled)
    folders: dict[str, int] = {}
    for f in evidence.files(root):
        if not f.lower().endswith(PICTURES):
            folder = "/".join(f.split("/")[1:-1]) or "evidence"
            folders[folder] = folders.get(folder, 0) + 1
    out["evidence"] = [{"folder": k, "files": v} for k, v in folders.items()]
    return out


def prototypes(root: Path) -> dict:
    """The screens as the prototype is walked: each flow with the screens it passes, in the order it passes them,
    then the screens no flow passes; each screen with whether its prototype is drawn."""
    with connect(root) as con:
        if not con:
            return {"flows": [], "elsewhere": []}
        g = loading.grammar()
        folder = root / drawing.PROTOTYPES / g["kinds"]["screen"]["prototype"]
        screens = {r["id"]: {"id": r["id"], "name": label(g, "screen", json.loads(r["fields"])),
                             "drawn": (folder / f"{r['id']}.html").is_file()}
                   for r in con.execute("SELECT id, fields FROM nodes WHERE kind = 'screen' AND parent IS NULL")}
        flows, passed = [], set()
        for r in sorted(con.execute("SELECT id, fields FROM nodes WHERE kind = 'flow'").fetchall(),
                        key=lambda r: natural(r["id"])):
            fields = json.loads(r["fields"])
            order = [e["dst"] for e in con.execute(
                "SELECT dst FROM edges WHERE src = ? AND rel = 'passes' ORDER BY rowid", (r["id"],))]
            passed.update(order)
            flows.append({"id": r["id"], "name": label(g, "flow", fields), "user": fields.get("user", ""),
                          "screens": [screens[s] for s in order if s in screens]})
        return {"flows": flows,
                "elsewhere": [screens[s] for s in sorted(screens, key=natural) if s not in passed]}


def node(root: Path, ident: str, stale: list | None = None) -> dict | None:
    with connect(root) as con:
        if not con:
            return None
        row = con.execute("SELECT * FROM nodes WHERE id = ?", (ident,)).fetchone()
        if row is None:
            return None
        g = loading.grammar()
        fields = json.loads(row["fields"])
        links = [{"rel": r["rel"], "id": r["dst"], "kind": r["kind"], "name": r["name"]} for r in con.execute(
            "SELECT e.rel, e.dst, n.kind, n.name FROM edges e JOIN nodes n ON n.id = e.dst "
            "WHERE e.src = ? AND e.rel <> 'has'", (ident,))]
        back = [{"rel": g["relations"][r["rel"]].get("back", r["rel"]), "id": r["src"], "kind": r["kind"],
                 "name": r["name"]} for r in con.execute(
            "SELECT e.rel, e.src, n.kind, n.name FROM edges e JOIN nodes n ON n.id = e.src "
            "WHERE e.dst = ? AND e.rel <> 'has'", (ident,))]
        parts = []
        for r in con.execute("SELECT id, kind, fields FROM nodes WHERE parent = ?", (ident,)).fetchall():
            said = json.loads(r["fields"])
            ties = [{"rel": t["rel"], "id": t["dst"], "kind": t["kind"], "name": t["name"]} for t in con.execute(
                "SELECT e.rel, e.dst, n.kind, n.name FROM edges e JOIN nodes n ON n.id = e.dst WHERE e.src = ?",
                (r["id"],))]
            parts.append({"id": r["id"], "kind": r["kind"], "says": said.get("says", ""), "fields": said,
                          "links": sorted(ties, key=lambda l: (l["rel"], natural(l["id"])))})
        unsettled = unsettled_on(con, g, ident, row["kind"])
        parent = None
        if row["parent"]:
            up = con.execute("SELECT id, kind, name FROM nodes WHERE id = ?", (row["parent"],)).fetchone()
            parent = {"id": up["id"], "kind": up["kind"], "name": up["name"]}
        prints = [row["fingerprint"], *(r["fingerprint"] for r in con.execute(
            "SELECT fingerprint FROM nodes WHERE parent = ? ORDER BY id", (ident,)))]
        return {"id": row["id"], "kind": row["kind"], "name": row["name"], "file": row["file"], "line": row["line"],
                "fingerprint": row["fingerprint"], "version": loading.version_of(prints), "fields": fields,
                "parent": parent,
                "stale": [s for s in (owed(root) if stale is None else stale) if s["node"] == ident],
                "parts": sorted(parts, key=lambda p: natural(p["id"])),
                "unsettled": unsettled,
                "opens": opens(root, con, row) if row["kind"] == "finding" else "",
                "links": sorted(links, key=lambda l: (l["rel"], natural(l["id"]))),
                "back": sorted(back, key=lambda l: (l["rel"], natural(l["id"])))}


def unsettled_on(con, g: dict, ident: str, kind: str) -> list[dict]:
    """What is not settled about a node or any of its rows: each question or addition about it once, with what it is
    on, and each question a row of it asks. A question or an addition is not unsettled about itself."""
    if kind in ("question", "addition"):
        return []
    found: dict[str, dict] = {}
    for r in con.execute(
            "SELECT DISTINCT n.id, n.kind, n.fields, e.dst AS on_ FROM edges e JOIN nodes n ON n.id = e.src "
            "WHERE n.kind IN ('question', 'addition') AND e.rel IN ('about', 'adds to') "
            "AND (e.dst = ? OR e.dst IN (SELECT id FROM nodes WHERE parent = ?)) "
            "UNION SELECT DISTINCT n.id, n.kind, n.fields, e.src FROM edges e JOIN nodes n ON n.id = e.dst "
            "WHERE n.kind = 'question' AND (e.src = ? OR e.src IN (SELECT id FROM nodes WHERE parent = ?))",
            (ident, ident, ident, ident)).fetchall():
        entry = found.setdefault(r["id"], {"id": r["id"], "kind": r["kind"], "on": [],
                                           "name": label(g, r["kind"], json.loads(r["fields"]))})
        entry["on"] = sorted({*entry["on"], r["on_"]}, key=natural)
    return sorted(found.values(), key=lambda u: natural(u["id"]))


def cut(text: str, most: int) -> str:
    """A text on one line, cut at a word where it is longer than a card has room for."""
    words = " ".join(text.split())
    return words if len(words) <= most else words[:most - 3].rsplit(" ", 1)[0] + "..."


def card(root: Path, ident: str, stale: list | None = None) -> dict | None:
    """What an ID is, for the card a pause over its link opens: its kind, its name, a sentence or two of its text --
    the one its card names, or the one its kind opens with, its first paragraph of prose -- and the facts that place
    it, as the grammar's `card` for its kind lists them: a field, a text, the nodes it is tied to or tied from, how
    many rows it has. Then what is not settled about it, and whether it is stale. All of it is the specification's
    own words; nothing is written for the card."""
    with connect(root) as con:
        if not con:
            return None
        row = con.execute("SELECT id, kind, name, parent, fields FROM nodes WHERE id = ?", (ident,)).fetchone()
        if row is None:
            return None
        g = loading.grammar()
        spec = g["kinds"][row["kind"]]
        shape = spec.get("card", {})
        fields = json.loads(row["fields"])
        heads = {d.get("as"): head for head, d in (spec.get("sections") or {}).items() if d.get("as")}
        heads.update({c["as"]: c["name"] for c in spec.get("columns", []) if c.get("as")})   # a row's, by its column
        name = row["name"] or label(g, row["kind"], fields)
        facts: list[dict] = []
        for want in shape.get("facts", []):
            if "field" in want or "text" in want:
                key = want.get("field") or want.get("text")
                value = said_in(fields.get(key)).strip()
                if value:
                    facts.append({"label": want.get("label") or heads.get(key) or key.capitalize(),
                                  "text": cut(value, 160)})
            elif "link" in want or "back" in want:
                rel = want.get("link") or want.get("back")
                ids = sorted({r[0] for r in con.execute(
                    "SELECT dst FROM edges WHERE src = ? AND rel = ?" if "link" in want else
                    "SELECT src FROM edges WHERE dst = ? AND rel = ?", (ident, rel))}, key=natural)
                if ids:
                    said = rel if "link" in want else g["relations"][rel].get("back", rel)
                    facts.append({"label": want.get("label") or said.capitalize(), "ids": ids[:CARD_IDS],
                                  "more": max(0, len(ids) - CARD_IDS)})
            elif "rows" in want:
                kind = spec["sections"][want["rows"]]["kind"]
                count = con.execute("SELECT count(*) FROM nodes WHERE parent = ?", (ident,)).fetchone()[0]
                if count:
                    one, many = ROWS.get(kind, (kind, kind + "s"))
                    facts.append({"label": want["rows"], "text": f"{count} {one if count == 1 else many}"})
        main = (spec.get("sections") or {}).get("", {}).get("as", "")     # the text a kind opens with, unless it says
        said = next((p for p in re.split(r"\n\s*\n", said_in(fields.get(shape.get("said") or main)).strip())
                     if p.strip() and not p.lstrip().startswith(("|", "#", "<"))), "")
        said = cut(said, CARD_SAID)
        stem = name[:-3] if name.endswith("...") else name
        if said and stem and not fields.get("name") and said.startswith(stem):   # a name taken from this very text
            name = ""
        parent = None
        if row["parent"]:
            up = con.execute("SELECT id, kind, name FROM nodes WHERE id = ?", (row["parent"],)).fetchone()
            parent = {"id": up["id"], "kind": up["kind"], "name": up["name"]}
        return {"id": row["id"], "kind": row["kind"], "name": name, "said": said, "facts": facts, "parent": parent,
                "unsettled": [{"id": u["id"], "name": u["name"]} for u in unsettled_on(con, g, ident, row["kind"])],
                "stale": sum(1 for s in (owed(root) if stale is None else stale) if s["node"] == ident)}


def opens(root: Path, con, row) -> str:
    """The file of the evidence a finding was read in, where its source is kept there: what its node leads to."""
    source = con.execute("SELECT n.fields FROM edges e JOIN nodes n ON n.id = e.dst WHERE e.src = ? AND e.rel = 'from'",
                         (row["id"],)).fetchone()
    if source is None:
        return ""
    where = json.loads(source["fields"]).get("where", "").strip().rstrip("/")
    there = evidence.source_place(root, where)
    if there is None or not where.startswith(evidence.EVIDENCE):
        return ""
    file = evidence.file_of(there, json.loads(row["fields"]).get("where", ""))
    return file.relative_to(root).as_posix() if file is not None else ""


def design(root: Path) -> dict:
    """The design system: the tokens, flattened, each with its group, its type and its value -- a colour by its hex
    -- and every component with how many variants and parts it has and how many elements use it."""
    tokens = []
    path = root / "prototypes" / "tokens.json"
    if path.is_file():
        def walk(group: str, held: dict, kind: str | None) -> None:
            kind = held.get("$type", kind)
            for key, value in held.items():
                if key.startswith("$") or not isinstance(value, dict):
                    continue
                if "$value" in value:
                    said = value["$value"]
                    shown = said.get("hex") if isinstance(said, dict) and "hex" in said else \
                        f"{said.get('value')}{said.get('unit', '')}" if isinstance(said, dict) and "value" in said \
                        else said if isinstance(said, (str, int, float)) else json.dumps(said)
                    tokens.append({"group": group, "name": key, "type": value.get("$type", kind),
                                   "value": shown, "about": value.get("$description", "")})
                else:
                    walk(f"{group}.{key}" if group else key, value, kind)
        walk("", json.loads(path.read_text(encoding="utf-8")), None)
    with connect(root) as con:
        components = []
        if con:
            for r in con.execute("""
                SELECT n.id, n.name, n.fields,
                       (SELECT count(*) FROM nodes c WHERE c.parent = n.id) AS parts,
                       (SELECT count(*) FROM edges e WHERE e.dst = n.id AND e.rel = 'is') AS used
                FROM nodes n WHERE n.kind = 'component'""").fetchall():
                said = json.loads(r["fields"])
                components.append({"id": r["id"], "name": r["name"], "purpose": said.get("purpose", ""),
                                   "variants": len(said.get("variants", [])), "parts": r["parts"],
                                   "used": r["used"]})
    return {"tokens": tokens, "components": sorted(components, key=lambda c: natural(c["id"]))}


def graph(root: Path, around: str, depth: int = 1) -> dict | None:
    """The nodes within `depth` links of one, either way, and the links among them; no more than GRAPH_LIMIT."""
    with connect(root) as con:
        if not con or con.execute("SELECT 1 FROM nodes WHERE id = ?", (around,)).fetchone() is None:
            return None
        edges = con.execute("SELECT src, rel, dst FROM edges").fetchall()
        near: dict[str, int] = {around: 0}
        frontier = [around]
        for step in range(1, max(1, min(depth, 3)) + 1):
            ahead = []
            for e in edges:
                for a, b in ((e["src"], e["dst"]), (e["dst"], e["src"])):
                    if a in frontier and b not in near and len(near) < GRAPH_LIMIT:
                        near[b] = step
                        ahead.append(b)
            frontier = ahead
        rows = con.execute(f"SELECT id, kind, name FROM nodes WHERE id IN ({','.join('?' * len(near))})",
                           list(near)).fetchall()
        return {"around": around,
                "nodes": [{"id": r["id"], "kind": r["kind"], "name": r["name"], "step": near[r["id"]]} for r in rows],
                "edges": [{"src": e["src"], "rel": e["rel"], "dst": e["dst"]} for e in edges
                          if e["src"] in near and e["dst"] in near],
                "cut": len(near) >= GRAPH_LIMIT}


def whole_graph(root: Path) -> dict | None:
    """Every node that stands on its own, and how they are linked. What is held inside a node -- a requirement's
    criterion, a screen's element -- is counted as that node, so its links are the node's, each pair said once with
    how many links of each sort stand behind it."""
    with connect(root) as con:
        if not con:
            return None
        rows = con.execute("SELECT id, kind, name, parent FROM nodes").fetchall()
        above = {r["id"]: r["parent"] for r in rows if r["parent"]}

        def top(ident: str) -> str:
            while ident in above:
                ident = above[ident]
            return ident

        pairs: dict[tuple[str, str], dict[str, int]] = {}
        for e in con.execute("SELECT src, rel, dst FROM edges").fetchall():
            src, dst = top(e["src"]), top(e["dst"])
            if src != dst:
                said = pairs.setdefault((src, dst), {})
                said[e["rel"]] = said.get(e["rel"], 0) + 1
        return {"nodes": [{"id": r["id"], "kind": r["kind"], "name": r["name"]} for r in rows if not r["parent"]],
                "links": [{"src": src, "dst": dst, "rels": said} for (src, dst), said in pairs.items()]}
