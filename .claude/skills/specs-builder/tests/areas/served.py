"""The application: the real server, on a free port, asked as the engine asks it."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from support import edit, ENGINE, loading, SKILL, STYLES, web_text


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """The server started on a copy of the example, every question the engine asks put to it, and a hand edit made
    while it runs."""
    import json
    import threading
    import urllib.error
    import urllib.request

    import serve

    root = tmp / "served"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")    # changed: an agreed one takes none
    httpd = serve.server(root, 0)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    def ask(path: str) -> tuple[int, bytes, str]:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as r:
                return r.status, r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            return e.code, e.read(), e.headers.get("Content-Type", "")

    def asked(path: str) -> object:
        status, body, _ = ask(path)
        return json.loads(body) if status == 200 else None

    checks = []
    try:
        checks.append(("the server listens on 127.0.0.1 only", httpd.server_address[0] == "127.0.0.1"))
        summary = asked("/api/summary") or {}
        checks.append(("the application asks what is built, and says where no code is known",
                       "no code is known" in str((asked("/api/built") or {}).get("none"))))
        checks.append(("the server answers its summary: built, clean, every kind counted",
                       summary.get("built") is True and not summary.get("problems") and
                       {k["kind"]: k["count"] for k in summary.get("kinds", [])}.get("requirement") == 16))
        b1 = asked("/api/node/B1") or {}
        checks.append(("a rule is told what enforces it, though its file never says",
                       {(l["rel"], l["id"]) for l in b1.get("back", [])} >= {("enforced by", "R4"), ("enforced by", "R5")}))
        r4 = asked("/api/node/R4") or {}
        checks.append(("a requirement comes with its links, its criteria and who may do it",
                       {("serves", "G2"), ("serves", "G3")} <= {(l["rel"], l["id"]) for l in r4.get("links", [])}
                       and [p["id"] for p in r4.get("parts", [])] == ["R4.1", "R4.2", "R4.3", "R4.4"]
                       and ("may be done by", "U1") in {(l["rel"], l["id"]) for l in r4.get("back", [])}))
        graph = asked("/api/graph?around=R4") or {}
        near = {"R4"} | {e.dst for e in loading.load(root).edges if e.src == "R4"} | \
               {e.src for e in loading.load(root).edges if e.dst == "R4"}
        checks.append(("the graph around a node holds it and all one link away",
                       {n["id"] for n in graph.get("nodes", [])} == near
                       and any(e["rel"] == "serves" for e in graph.get("edges", []))))
        whole = asked("/api/graph") or {}
        shown = {n["id"] for n in whole.get("nodes", [])}
        held = [e for e in loading.load(root).edges if e.src.split(".")[0] != e.dst.split(".")[0]]
        checks.append(("the whole graph holds every node that stands on its own, and counts what a node holds as that node",
                       "R4" in shown and "R4.1" not in shown and "SC3" in shown and not any("." in i for i in shown)
                       and all(l["src"] in shown and l["dst"] in shown and l["src"] != l["dst"] for l in whole.get("links", []))
                       and sum(sum(l["rels"].values()) for l in whole.get("links", [])) == len(held)
                       and len({(l["src"], l["dst"]) for l in whole.get("links", [])}) == len(whole.get("links", []))))
        grid = asked("/api/matrix") or {}
        cells = {(c["from"], c["to"]): c for c in grid.get("cells", [])}
        total = sum(sum(l["rels"].values()) for l in whole.get("links", []))
        checks.append(("the Matrix's grid counts what the Graph draws: every node standing alone, every link between two, by the "
                       "kinds that hold its ends, and a gap is no cell",
                       grid.get("nodes") == len(shown) and grid.get("links") == total
                       and sum(c["count"] for c in grid.get("cells", [])) == total
                       and cells.get(("flow", "screen"), {}).get("rels", {}).get("passes") == 21 and ("term", "term") not in cells))
        cell = asked("/api/matrix/cell?from=flow&to=screen") or {}
        rest = asked("/api/matrix/cell?from=flow&to=screen&offset=5&limit=4") or {}
        checks.append(("a cell lists its links in ID order, a page at a time, with both ends named",
                       cell.get("total") == 21 and len(cell.get("links", [])) == 21 and cell["links"][0]["src"]["id"] == "F1"
                       and cell["links"][0]["dst"]["name"] == "The home page" and rest.get("links") == cell["links"][5:9]))
        tree = asked("/api/matrix/tree?kind=requirement") or {}
        at = asked("/api/matrix/tree?kind=requirement&at=R10") or {}
        rows = asked("/api/matrix/tree?parent=SC3") or {}
        checks.append(("the tree answers one kind or one node's rows, in ID order, and finds the page an ID is on",
                       tree.get("total") == 16 and [r["id"] for r in tree.get("rows", [])][:2] == ["R1", "R2"]
                       and tree["rows"][9]["id"] == "R10" and tree["rows"][0]["parts"] > 0 and at.get("position") == 9
                       and rows.get("total", 0) > 10 and rows["rows"][1]["id"] == "SC3.2"))
        held = asked("/api/matrix/links/SC3") or {}
        sorts = {(s["way"], s["rel"]): s for s in held.get("groups", [])}
        shows = sorts.get(("out", "shows"), {})
        more = asked("/api/matrix/links/SC3?way=out&rel=shows&offset=1&limit=2") or {}
        line = next((r for r in tree.get("rows", []) if r["id"] == "R4"), {})
        checks.append(("a node's links are listed by sort, both ways, each with its count; a row's links are its node's, marked "
                       "with the row, and a link inside the node is left out; the tree's count is the same",
                       held.get("node", {}).get("top") == {"id": "SC3", "kind": "screen"} and shows.get("count", 0) > 0
                       and any(l["from"].startswith("SC3.") for s in held.get("groups", []) for l in s["links"])
                       and not any(l["far"]["id"].split(".")[0] == "SC3" for s in held.get("groups", []) for l in s["links"])
                       and more.get("links") == shows.get("links", [])[1:3]
                       and line.get("links") == sum(s["links count"] for s in (asked("/api/matrix/links/R4") or {}).get("groups", []))))
        far_ends = [l for s in held.get("groups", []) for l in s["links"]]
        checks.append(("a node's links in the Matrix name nodes, never a row they hold, one row to a node, and say how many links reach it",
                       far_ends and not any("." in l["far"]["id"] for l in far_ends)
                       and all(len({l["far"]["id"] for l in s["links"]}) == len(s["links"]) for s in held.get("groups", []))
                       and sum(s["links count"] for s in held.get("groups", [])) >= sum(s["count"] for s in held.get("groups", []))
                       and all(l["count"] >= 1 for l in far_ends)))
        told = asked("/api/matrix/link?src=F1&rel=passes&dst=SC1") or {}
        checks.append(("a link is told whole: both ends, how it reads from each, its file and line, what goes stale, and that it "
                       "is not stale now; a link that is not there is a 404",
                       told.get("reads") == "F1 passes SC1" and told.get("reads back") == "SC1 passed by F1"
                       and told.get("file") == "data/flows/F1.md" and told.get("line", 0) > 1
                       and told.get("stands") == [{"node": "F1", "on": "SC1", "fields": []}] and told.get("stale") == []
                       and told.get("src", {}).get("kind") == "flow" and ask("/api/matrix/link?src=F1&rel=passes&dst=SC2000")[0] == 404
                       and ask("/api/matrix/link?src=R1&rel=has&dst=R1.1")[0] == 404))
        narrowed = asked("/api/matrix/links/R1?q=home") or {}
        by_kind = asked("/api/matrix/links/R1?by=kind") or {}
        plain = asked("/api/matrix/links/R1") or {}
        kinds_of = {s["kind"]: s for s in by_kind.get("groups", [])}
        page = asked("/api/matrix/links/R1?of=screen&offset=1&limit=2") or {}
        sparse = asked("/api/matrix/cell?from=flow&to=screen&q=home") or {}
        checks.append(("a node's links narrow to a few words, group by the kind at their far end and page there too, and a cell's "
                       "narrow; the sum is the same whichever way they are grouped",
                       narrowed.get("groups") and all("home" in l["far"]["name"].lower() or l["far"]["id"] for s in narrowed["groups"] for l in s["links"])
                       and sum(s["count"] for s in narrowed["groups"]) < sum(s["count"] for s in plain.get("groups", []))
                       and sum(s["count"] for s in by_kind.get("groups", [])) == sum(s["count"] for s in plain.get("groups", []))
                       and "screen" in kinds_of and kinds_of["screen"]["links"][0]["word"]
                       and page.get("links") == kinds_of["screen"]["links"][1:3]
                       and 0 < sparse.get("total", 0) < 21))
        problems_now = grid.get("problems", {})
        unlinked = asked("/api/matrix/tree?kind=foundation&problem=unlinked") or {}
        unsettled = asked("/api/matrix/tree?kind=requirement&problem=open") or {}
        checks.append(("the tree narrows to what has a problem: a node with an open question is found as its page finds it, and what "
                       "is joined to nothing, by kind, in pages of its own; a node that is not in the list stands nowhere",
                       set(problems_now) == {"stale", "unlinked", "open"} and problems_now["stale"] == {}
                       and any(r["id"] == "R4" for r in unsettled.get("rows", []))
                       and unsettled.get("total") == problems_now["open"].get("requirement")
                       and unlinked.get("total") == problems_now["unlinked"].get("foundation", 0)
                       and all(r["links"] == 0 for r in unlinked.get("rows", []))
                       and (asked("/api/matrix/tree?kind=requirement&problem=open&at=R999") or {}).get("position") is None))
        chain = asked("/api/matrix/path?from=F1&to=R1") or {}
        held_chain = asked("/api/matrix/path?from=SC2.6&to=F1") or {}
        checks.append(("a path is the shortest chain of real links between two nodes, each step joining the last, what a node holds "
                       "counted as it, by links a change passes along; a node that is not there is a 404",
                       chain.get("found") and chain.get("changing") and len(chain.get("steps", [])) == 1
                       and chain["steps"][0]["src"]["id"] == "F1" and chain["steps"][0]["rel"] == "carries"
                       and chain["steps"][-1]["dst"]["id"] == "R1"
                       and held_chain.get("found") and ask("/api/matrix/path?from=F1&to=R999")[0] == 404))
        folded = asked("/api/map") or {}
        opened = asked("/api/map?open=screen:3,requirement:400") or {}
        every = ",".join(f"{k['kind']}:9999" for k in folded.get("kinds", []))
        unfolded = asked(f"/api/map?open={every}") or {}
        shows = {k["kind"]: k for k in opened.get("kinds", [])}
        keys = {n["id"] for k in opened.get("kinds", []) for n in k["nodes"]} | {f"kind:{k['kind']}" for k in opened.get("kinds", [])}
        checks.append(("the Graph's map opens from counts alone; a kind opens to its most linked nodes and no more; every link joins what "
                       "shows, each pair once; and with all open it is every link there is",
                       all(k["nodes"] == [] for k in folded.get("kinds", [])) and folded.get("total") == total and folded.get("nodes") == len(shown)
                       and len(shows.get("screen", {}).get("nodes", [])) == 3 and shows["screen"]["count"] == 18
                       and shows["screen"]["nodes"][0]["links"] >= shows["screen"]["nodes"][2]["links"]
                       and all(l["a"] in keys and l["b"] in keys for l in opened.get("links", []))
                       and len({(l["a"], l["b"]) for l in opened.get("links", [])}) == len(opened.get("links", []))
                       and sum(l["count"] for l in unfolded.get("links", [])) == total))
        window = asked("/api/map?open=screen:3@2") or {}
        first_three = next(k for k in opened.get("kinds", []) if k["kind"] == "screen")["nodes"]
        later = next((k for k in window.get("kinds", []) if k["kind"] == "screen"), {}).get("nodes", [])
        trace = asked("/api/map/layers?id=R4") or {}
        near_trace = {n["id"] for k in (asked("/api/map/layers?id=R4&steps=1") or {}).get("kinds", []) for n in k["nodes"]}
        wider_trace = {n["id"] for k in (asked("/api/map/layers?id=R4&steps=2") or {}).get("kinds", []) for n in k["nodes"]}
        column = {k: i for i, held in enumerate(trace.get("layers", [])) for k in held}
        groups_js = web_text(ENGINE)
        menu_kinds = re.findall(r'"([a-z]+)"', groups_js[groups_js.index("const GROUPS"):groups_js.index("const TEXTS")])
        in_columns = [menu_kinds.index(k) for held in trace.get("layers", []) for k in held]
        checks.append(("the columns of Layers stand in the top menu's order", len(in_columns) > 10 and in_columns == sorted(in_columns)))
        said_first = (asked("/api/summary") or {}).get("version")
        checks.append(("the summary says which state of the data it is, the same until the data changes, so a page asks every name only then",
                       bool(said_first) and said_first == (asked("/api/summary") or {}).get("version") and "state.namesOf" in groups_js))
        one_step = (asked("/api/map/layers?id=R4&steps=1") or {}).get("links", [])
        whole = trace.get("links", [])
        checks.append(("Layers of a node says which links the trace walked: one step walks only that node's own, and a link not walked is kept for a pause",
                       one_step and all(l["walked"] == ("R4" in (l["a"], l["b"])) for l in one_step)
                       and any(not l["walked"] for l in whole) and sum(l["walked"] for l in whole) > sum(l["walked"] for l in one_step)))
        each_row = [n["id"] for k in trace.get("kinds", []) for n in k["nodes"]]
        look = web_text(STYLES)
        checks.append(("Layers of a node stands each row beside what it links to, each node once, and shows strong and waiting links",
                       "rows = in_rows(kept," in (SKILL / "app/matrix.py").read_text(encoding="utf-8") and len(each_row) == len(set(each_row)) > 10
                       and ".map-link.aside" in look and ".map-link.own" in look and "--tray:" in look and ".graph-bar .live-seg" in look))
        reached = {n["id"]: k["kind"] for k in trace.get("kinds", []) for n in k["nodes"]}
        checks.append(("a kind is walked a window at a time, and the layers of one node hold it and what connects to it in the columns "
                       "either side, each link between two that show, each kind saying how many it reached",
                       len(later) == 3 and first_three[2:3] == later[:1]
                       and "R4" in near_trace and near_trace < wider_trace <= set(reached)
                       and trace.get("node", {}).get("id") == "R4" and "R4" in reached and "goal" in reached.values() and "screen" in reached.values()
                       and all(column[k] is not None for k in reached.values())
                       and all(l["a"] in reached and l["b"] in reached for l in trace.get("links", []))
                       and all(k["count"] >= len(k["nodes"]) for k in trace.get("kinds", []))
                       and ask("/api/map/layers?id=R999")[0] == 404))
        carded = asked("/api/card/R4") or {}
        carded_kinds = {k["kind"]: k for k in (carded.get("linked") or {}).get("kinds", [])}
        checks.append(("a card lists the node's links by kind, the most first, with how many and the first few",
                       "screen" in carded_kinds and carded_kinds["screen"]["count"] >= len(carded_kinds["screen"]["nodes"]) > 0
                       and len(carded_kinds["screen"]["nodes"]) <= 6
                       and [k["count"] for k in carded["linked"]["kinds"]] == sorted((k["count"] for k in carded["linked"]["kinds"]), reverse=True)))
        near_r4 = asked("/api/map/around?id=R4") or {}
        near_row = asked("/api/map/around?id=R4.1") or {}
        tops = {n["id"] for n in near_r4.get("neighbours", [])}
        checks.append(("focus holds one node and what it is linked to, what it holds counted as it, each saying which way its links run",
                       near_r4.get("centre", {}).get("id") == "R4" and "G2" in tops or "G1" in tops
                       and not any("." in i for i in tops) and near_row.get("centre", {}).get("id") == "R4"
                       and all(n["rels"] and (n["out"] or n["in"]) for n in near_r4.get("neighbours", []))
                       and ask("/api/map/around?id=R999")[0] == 404))
        standing = asked("/api/map/stands?id=R4") or {}
        said_impact = asked("/api/node/R4") or {}
        checks.append(("impact says what stands on a node, the opposite of what it stands on, and how many stand on each in turn",
                       standing.get("node", {}).get("id") == "R4" and standing.get("stands")
                       and not ({n["id"] for n in standing["stands"]} & {l["id"] for l in said_impact.get("links", []) if l["rel"] == "serves"})
                       and all("next" in n and n["rels"] for n in standing["stands"]) and ask("/api/map/stands?id=R999")[0] == 404))
        owing = [{"node": "SC1.2", "on": "R2", "link": "SC1.2 shows R2", "was": {}, "now": {}}]
        troubled = serve.matrix.problems(root, owing)
        marked = serve.matrix.grid(root, owing, troubled) or {}
        marks = {(c["from"], c["to"]): c["stale"] for c in marked.get("cells", []) if c["stale"]}
        row = next((l for s in (serve.matrix.links(root, owing, "SC1") or {}).get("groups", []) for l in s["links"]
                    if l["from"] == "SC1.2" and l["far"]["id"] == "R2"), {})
        checks.append(("what is stale reaches the Matrix: a row's node in the tree's filter, its holder's kinds in the grid, and a mark on "
                       "the link itself",
                       troubled["stale"] == {"screen": ["SC1"]} and marks == {("screen", "requirement"): 1} and marked.get("stale") == 1
                       and row.get("stale") is True))
        hits = asked("/api/matrix/find?q=r1") or []
        checks.append(("Find puts an ID typed whole first, reaches rows and every word, and takes % as a character",
                       hits[:1] and hits[0]["id"] == "R1" and len(hits) <= 30
                       and any(h["id"] == "SC3.2" for h in asked("/api/matrix/find?q=SC3.2") or [])
                       and asked("/api/matrix/find?q=%25%25%25") == []))
        checks.append(("a node the Matrix is asked for that is not there is a 404", ask("/api/matrix/links/R99")[0] == 404))
        checks.append(("a node that is not there is a 404", ask("/api/node/R99")[0] == 404))
        checks.append(("a question the server does not have is a 404", ask("/api/nothing")[0] == 404))
        checks.append(("nothing outside app/web/ is served", all(ask(p)[0] == 404 for p in
                       ("/..%2fload.py", "/%2e%2e/load.py", "/..%2f..%2fdata/requirements/R4.md"))))
        status, page, kind = ask("/")
        checks.append(("the engine is served", status == 200 and kind.startswith("text/html") and b"engine.js" in page))
        status, page, _ = ask("/prototype/SC3.html")
        checks.append(("a screen is drawn in the product's shell, the runtime and its place given first",
                       status == 200 and b'<base href="/prototype/">' in page and b"/runtime/live.js" in page
                       and b"<title>SC3 A product</title>" in page and b'data-el="9"' in page
                       and page.index(b"/runtime/live.js") < page.index(b"assets/js/prototype.js")))
        status, page, _ = ask("/prototype/components/C1.html")
        checks.append(("a component's drawings are drawn in the shell", status == 200 and b"drawings.css" in page
                       and b'data-variant="disabled"' in page))
        checks.append(("the product's assets are served", ask("/prototype/assets/css/product.css")[0] == 200))
        checks.append(("a prototype's file is served only drawn, and nothing outside the prototypes",
                       all(ask(p)[0] == 404 for p in ("/prototype/screens/SC3.html", "/prototype/..%2fdata/goals/G1.md",
                                                      "/prototype/tokens.json", "/prototype/SC99.html"))))
        design = asked("/api/design") or {}
        checks.append(("the design system holds the tokens and every component",
                       len(design.get("components", [])) == 13 and any(t["type"] == "color" for t in design.get("tokens", []))))
        menu = asked("/api/menu") or {}
        kinds = menu.get("kinds", {})
        checks.append(("the menu's panels hold each kind's count and its first five, in order",
                       kinds.get("requirement", {}).get("count") == 16 and kinds.get("question", {}).get("count") == 1
                       and [n["id"] for n in kinds.get("requirement", {}).get("first", [])] == ["R1", "R2", "R3", "R4", "R5"]
                       and "criterion" not in kinds))
        checks.append(("the menu tells the document, how much is not settled, and whether it may be agreed",
                       menu.get("document", {}).get("status") == "draft" and (menu.get("open") or 0) >= 1
                       and isinstance(menu.get("ready"), list)
                       and {f["folder"] for f in menu.get("evidence", [])} >= {"reports", "captures/site"}))
        flows = {f["id"]: [s["id"] for s in f["screens"]] for f in menu.get("prototype", {}).get("flows", [])}
        checks.append(("the prototype is told flow by flow, each screen as its flow passes it, then the rest",
                       flows.get("F1", [])[:3] == ["SC1", "SC2", "SC3"] and flows.get("F1", [""])[-1] == "SC12"
                       and [s["id"] for s in menu.get("prototype", {}).get("elsewhere", [])] == ["SC10", "SC17", "SC18"]
                       and asked("/api/prototypes") == menu.get("prototype")))
        checks.append(("the theme, the menu and the help are served",
                       all(ask(f"/{f}")[0] == 200 for f in ("theme.js", "menu.js", "help.js"))))
        by_id = asked("/api/search?q=r4") or []
        by_name = asked("/api/search?q=checkout") or []
        by_text = asked("/api/search?q=visitor%20cart") or []
        checks.append(("search finds an ID typed whole first, its rows after it, and a whole name before a word in one",
                       [f["id"] for f in by_id[:2]] == ["R4", "R4.1"] and by_id[1]["parent"] == "R4"
                       and by_id[1]["name"].startswith("Given")
                       and [f["id"] for f in by_name].index("SC6") < [f["id"] for f in by_name].index("E3")))
        checks.append(("search wants every word, says where in a text it found one, and finds nothing for nothing",
                       by_text and all("visitor" in (f["name"] + f["snippet"]).lower() for f in by_text)
                       and any(f["snippet"] for f in asked("/api/search?q=pay") or [])
                       and asked("/api/search?q=zzzz") == [] and asked("/api/search?q=") == []))
        told_r4, price, fd1 = (asked(f"/api/card/{i}") or {} for i in ("R4", "SC3.9", "FD1"))
        facts = {f["label"]: f for f in told_r4.get("facts", [])}
        checks.append(("a card says what an ID is: its kind, its name, its statement and the facts its grammar lists",
                       told_r4.get("kind") == "requirement" and "shall" in told_r4.get("said", "")
                       and facts.get("Priority", {}).get("text") and facts.get("Serves", {}).get("ids") and facts.get("Accepted when", {}).get("text", "").endswith("criteria")
                       and "unsettled" in told_r4 and "stale" in told_r4))
        checks.append(("a row has its card too, under what holds it, a column's heading its label; a table is never quoted",
                       (price.get("parent") or {}).get("id") == "SC3"
                       and any(f["label"] == "Component" and f.get("ids") == ["C4"] for f in price.get("facts", []))
                       and any(f["label"] == "Kind" for f in price.get("facts", []))
                       and fd1.get("said") == "" and ask("/api/card/ZZ9")[0] == 404))
        sc3 = asked("/api/node/SC3") or {}
        nine = next((p for p in sc3.get("parts", []) if p["id"] == "SC3.9"), {})
        checks.append(("a screen comes with each element and its links",
                       len(sc3.get("parts", [])) == 25 and ("shows", "R2") in {(l["rel"], l["id"]) for l in nine.get("links", [])}))
        edit(root, "data/requirements/R4.md", "serves: G2, G3", "serves: G2, G3, B1")
        after = asked("/api/summary") or {}
        told = [(p["file"], p["line"]) for p in after.get("problems", [])]
        checks.append(("a file edited while the server runs is noticed, its problem told at its line",
                       told == [("data/requirements/R4.md", 5)]))
        checks.append(("while the data has a problem, the last good data is what is read",
                       (asked("/api/node/R4") or {}).get("fingerprint") == r4.get("fingerprint")))
        # a good edit while it runs is built and read at once -- the new database put in place of the one in use
        edit(root, "data/requirements/R4.md", "serves: G2, G3, B1", "serves: G2")
        edit(root, "data/requirements/R4.md", "name: Add a product to the cart", "name: Put a product in the cart")
        now = asked("/api/node/R4") or {}
        exported = urllib.request.Request(f"http://127.0.0.1:{port}/api/export", data=b"", method="POST")
        with urllib.request.urlopen(exported) as answer:
            whole, disposition = answer.read(), answer.headers.get("Content-Disposition", "")
        foreign = urllib.request.Request(f"http://127.0.0.1:{port}/api/export", data=b"", method="POST",
                                         headers={"Origin": "http://elsewhere.example"})
        try:
            urllib.request.urlopen(foreign)
            refused_export = False
        except urllib.error.HTTPError as wrong:
            refused_export = wrong.code == 403
        checks.append(("the Export button's question gives the whole file to keep, and only to this application",
                       whole.startswith(b"<!doctype html>") and b"window.cards" in whole and refused_export
                       and disposition.startswith("attachment;") and disposition.endswith('.html"')))

        def post(body: dict, origin: str | None = None, path: str = "/api/inbox") -> tuple[int, dict]:
            raw = json.dumps(body).encode("utf-8")
            request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=raw, method="POST",
                                             headers={"Content-Type": "application/json",
                                                      **({"Origin": origin} if origin else {})})
            try:
                with urllib.request.urlopen(request, timeout=30) as r:
                    return r.status, json.loads(r.read())
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read() or b"{}")

        import inbox
        import logic
        here = f"http://127.0.0.1:{port}"
        status, said = post({"says": "The limit should be six", "about": ["B1"], "by": "A reader"}, origin=here)
        waits = (asked("/api/open") or {}).get("asked", [])
        checks.append(("a change requested in the application waits in the inbox with who asked and what about, and the data does not move",
                       status == 200 and [(e["by"], e["about"], e["question"]) for e in waits] == [("A reader", ["B1"], "The limit should be six")]
                       and (asked("/api/node/B1") or {}).get("name") == "Up to five of a product" and (asked("/api/summary") or {}).get("problems") == []))
        checks.append(("a request says what it asks and who asks it, about nodes that exist",
                       post({"says": " ", "about": ["B1"], "by": "A reader"}, origin=here)[0] == 400
                       and post({"says": "Well", "about": ["B1"], "by": ""}, origin=here)[0] == 400
                       and post({"says": "Well", "about": ["R999"], "by": "A reader"}, origin=here)[0] == 400))
        checks.append(("a request from another site is refused, 403", post({"says": "Well", "by": "Someone"}, origin="http://evil.example")[0] == 403))
        checks.append(("nothing in the application changes the data: the change route is gone",
                       post({"operations": [["set", "B1", "name", "x"]]}, origin=here, path="/api/changes")[0] == 404
                       and (asked("/api/node/B1") or {}).get("name") == "Up to five of a product"))
        inbox.take(root, said["no"])
        logic.apply(root, [logic.parse('set B1 name "Six at most"')], who="selftest")
        checks.append(("a change made by the operations is read at once",
                       (asked("/api/node/B1") or {}).get("name") == "Six at most"))
        rules = ((asked("/api/menu") or {}).get("kinds", {}).get("rule", {}).get("first", []))
        checks.append(("the menu's panels are worked out again once the data changes",
                       any(n["id"] == "B1" and n["name"] == "Six at most" for n in rules)))
        told = asked("/api/history?id=B1") or []
        checks.append(("the history of a node is answered", any(e.get("who") == "selftest" for e in told)))
        checks.append(("a good edit while the server runs is built and read at once",
                       not (asked("/api/summary") or {}).get("problems") and now.get("name") == "Put a product in the cart"
                       and [l["id"] for l in now.get("links", []) if l["rel"] == "serves"] == ["G2"]
                       and now.get("fingerprint") != r4.get("fingerprint")))
    finally:
        httpd.shutdown()
        httpd.server_close()
    return checks
