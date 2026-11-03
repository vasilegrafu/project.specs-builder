"""What a change is held to, and the export."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from support import edit, ENGINE, loading, SKILL, STYLES, web_text


def contrast_faults(css: str) -> list:
    """Each text colour of the stylesheet -- the text in its three steps, the accent, a colour for each part and the
    signals -- against the page and a panel, in the light and the dark appearance: those under 4.5:1."""
    def tokens(block):
        return dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", block))
    light = tokens(css[css.index(":root {"):css.index(":root[data-theme=\"dark\"]")])
    dark = {**light, **tokens(css[css.index(":root[data-theme=\"dark\"]"):css.index("/* a kind's colour is its part's")])}

    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
        return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]

    def ratio(a, b):
        a, b = lum(a), lum(b)
        return (max(a, b) + .05) / (min(a, b) + .05)
    texts = ["ink", "ink-2", "ink-3", "accent", "p-evidence", "p-decisions", "p-requirements", "p-domain", "p-api",
             "p-ux", "s-open", "s-bad", "warn-ink"]
    out = []
    for name, t in (("light", light), ("dark", dark)):
        for fg in texts:
            for bg in ("bg", "panel"):
                if fg in t and bg in t and ratio(t[fg], t[bg]) < 4.5:
                    out.append(f"{name} {fg} on {bg} {ratio(t[fg], t[bg]):.1f}")
    return out


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """What a change is held to, and the export: what a kind holds, a change refused when what it was made against moved
    since, and one file that holds the whole specification."""
    import json
    import re

    import api
    import export
    import logic

    root = tmp / "editing"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")
    loading.build(loading.load(root))
    logic.notice(root, loading.load(root))
    g = loading.grammar()
    checks = []
    requirement, screen = api.form(g, "requirement"), api.form(g, "screen")
    checks.append(("a form says what a kind holds: a requirement needs its goal and a first criterion; a screen is tied "
                   "only by what is written as a whole, not in its tables' cells",
                   any(r["rel"] == "serves" and r.get("least") == 1 for r in requirement["relations"])
                   and requirement["rows"]["least"] == 1 and requirement["rows"]["list"]
                   and {r["rel"] for r in screen["relations"]} == {"shows", "about", "displays", "follows"}))
    try:
        logic.apply(root, [logic.parse("tie SC3 leads to SC4")])
        checks.append(("a link written only in a table's cell is refused when tied to the node as a whole", False))
    except logic.Refused as why:
        checks.append(("a link written only in a table's cell is refused when tied to the node as a whole",
                       "cell of a table" in str(why)))
    held = loading.version(g, loading.load(root), "R4")
    loading.build(loading.load(root))
    checks.append(("a node's version is the same read from the database as from the files",
                   api.node(root, "R4")["version"] == held))
    result = logic.apply(root, [logic.parse("set R4 priority should")], expect={"R4": held})
    try:
        logic.apply(root, [logic.parse("set R4 priority must")], expect={"R4": held})
        refused = ""
    except logic.Refused as why:
        refused = str(why)
    checks.append(("a change made against a node that moved since is refused, and the first one kept",
                   not result.problems and "changed since you opened it" in refused
                   and "priority: should" in (root / "data/requirements/R4.md").read_text(encoding="utf-8")))
    try:
        logic.apply(root, [logic.parse("set R99 priority must")], expect={"R99": "0"})
        gone = ""
    except logic.Refused as why:
        gone = str(why)
    checks.append(("a change made against a node gone since is refused", "gone since you opened it" in gone))
    print_of = lambda: loading.fingerprint(g, loading.load(root).nodes["R3"])    # noqa: E731
    first_print = print_of()
    logic.apply(root, [logic.parse('set R3 why "Shoppers leave when they cannot find a product."')], who="selftest")
    why_print = print_of()
    logic.apply(root, [logic.parse('set R3 details "It covers names, not descriptions."')], who="selftest")
    told_fields = loading.load(root).nodes["R3"].fields
    written = (root / "data/requirements/R3.md").read_text(encoding="utf-8")
    checks.append(("a requirement's Why and Details stand between its statement and its criteria: a Why turns nothing stale, Details does",
                   why_print == first_print and print_of() != first_print and not loading.load(root).problems
                   and told_fields["why"].startswith("Shoppers") and told_fields["details"].startswith("It covers")
                   and written.index("## Why") < written.index("## Details") < written.index("## Accepted when")))
    edit(root, "data/requirements/R5.md", "the shop shall", "the shop <script>alert(1)</script> shall")
    out = export.export(root, tmp / "export.html")
    text = out.read_text(encoding="utf-8")
    ids = set(re.findall(r' id="([^"]+)"', text))
    hrefs = set(re.findall(r'href="#([^"]+)"', text))
    tops = {i for i, n in loading.load(root).nodes.items() if n.parent is None}
    checks.append(("the export holds every node, each where a link to it lands, and every link lands",
                   tops <= ids and not (hrefs - ids)))
    checks.append(("the export tells each flow as a user story, with what it carries",
                   text.count('<p class="story">') == sum(1 for n in loading.load(root).nodes.values() if n.kind == "flow")
                   and "I want to buy a product" in text))
    checks.append(("the export draws each screen's prototype in a sandboxed frame, needing nothing beside it",
                   text.count('<iframe class="proto" sandbox="allow-scripts"') == sum(
                       1 for n in loading.load(root).nodes.values() if n.kind == "screen")
                   and 'src="assets/' not in text.split("srcdoc=")[1][:200_000]))
    held = loading.load(root).nodes
    flows = sum(1 for n in held.values() if n.kind == "flow")
    blocks = re.findall(r"<script>(.*?)</script>", text, re.S)
    cards = json.loads(re.search(r"window\.cards = (\{.*?\});\nwindow\.flows", text, re.S).group(1))
    checks.append(("the export holds every ID's card, by the application's own card.js: a right click opens it and it needs "
                   "no server",
                   set(cards) == set(held) and all(cards[i] for i in cards) and cards["R4"]["kind"] == "requirement"
                   and any("function openCard" in b and "inExport" in b for b in blocks) and "id-card" in text))
    checks.append(("the export gives each flow its diagram above its steps, by the application's own flowmap.js, in "
                   "place of the diagram's bare text",
                   text.count('class="flow-slot"') == flows and any("function flowMap" in b for b in blocks)
                   and "<code>flowchart" not in text and "language-mermaid" not in text
                   and text.index('data-flow="F1"') < text.index("<h4>Steps</h4>", text.index('id="F1"'))))
    checks.append(("the bar has an Export button beside the printer, which asks the server for the whole file",
                   'id="export-button"' in (SKILL / "app/web/index.html").read_text(encoding="utf-8")
                   and '"/api/export"' in (SKILL / "app/web/aids.js").read_text(encoding="utf-8")
                   and "export: [" in (SKILL / "app/web/menu.js").read_text(encoding="utf-8")))
    checks.append(("the export is on A4 on paper, and keeps its dark appearance off it",
                   "size: A4" in text and "beforeprint" in text and ".id-card { display" not in text.split("@media print")[0]))
    checks.append(("the export escapes what the data says: no markup of it runs",
                   "<script>alert(1)</script>" not in text and "&lt;script&gt;alert(1)&lt;/script&gt;" in text))
    web = (SKILL / "app/web/index.html").read_text(encoding="utf-8")
    checks.append(("the page loads the request, the menu and the help before the engine, and has no way to edit",
                   web.index("request.js") < web.index("menu.js") < web.index("help.js") < web.index("engine.js")
                   and "edit" not in web and not (SKILL / "app/web/edit.js").exists()))
    checks.append(("the bar has two rows: the name, search, help and the appearance above; the parts below",
                   web.index('class="bar-top"') < web.index('id="search"') < web.index('id="help-link"')
                   < web.index('id="theme"') < web.index('<nav id="nav"')
                   and "open-link" not in web and "brand-kicker" not in web))
    menu = (SKILL / "app/web/menu.js").read_text(encoding="utf-8")
    card = (SKILL / "app/web/card.js").read_text(encoding="utf-8")
    g = json.loads((SKILL / "app/grammar.json").read_text(encoding="utf-8"))
    named = []                                       # what a kind's card names that the kind does not hold
    for kind, spec in g["kinds"].items():
        held = (set(spec.get("fields") or {}) | set(spec.get("worked out") or ())
                | {d.get("as") for d in (spec.get("sections") or {}).values()})
        held |= {c.get("as") for c in spec.get("columns", [])}
        shape = spec.get("card")
        if shape is None:
            named.append(f"{kind}: no card")
            continue
        named += [f"{kind}: {w}" for w in shape.get("facts", []) if ("field" in w and w["field"] not in held)
                  or ("text" in w and w["text"] not in held) or ("rows" in w and w["rows"] not in (spec.get("sections") or {}))
                  or any(k in w and w[k] not in g["relations"] for k in ("link", "back"))]
        named += [f"{kind}: said {shape['said']}"] if shape.get("said") and shape["said"] not in held else []
    checks.append((f"every kind has a card, naming only what the kind holds{': ' + ', '.join(named) if named else ''}",
                   not named))
    side = (SKILL / "app/web/side.js").read_text(encoding="utf-8")
    css = web_text(STYLES)
    faint = contrast_faults(css)
    checks.append((f"every text colour reads at 4.5:1 or more on the surfaces it stands on, light and dark"
                   f"{': ' + ', '.join(faint) if faint else ''}", not faint))
    checks.append(("a part's pages have its tree down the left -- its kinds folding to their nodes, the part's own page at "
                   "its head -- a button under 1024px, and none in the preview",
                   web.index("side.js") < web.index("engine.js") and "has-side" in side and "partView" in side
                   and '"peeked"' in side and 'id="side"' in web and "side-grip" in side and "SIDE_WIDTHS" in side
                   and "side-folded" in side and "side-tip" in side and "drawSide(" in web_text(ENGINE)
                   and "max-width: 1023px" in web_text(STYLES)))
    flowmap = (SKILL / "app/web/flowmap.js").read_text(encoding="utf-8")
    grammar = json.loads((SKILL / "app/grammar.json").read_text(encoding="utf-8"))
    checks.append(("a flow's page draws its diagram with Mermaid, fetched at one exact version and kept out of the "
                   "repository -- the one its Diagram section holds, else one made from its steps",
                   web.index("flowmap.js") < web.index("engine.js") and "function flowMap" in flowmap
                   and "function made" in flowmap and "cdn.jsdelivr.net/npm/mermaid@11.9.0/" in flowmap
                   and not (SKILL / "app/web/vendor").exists()
                   and "Diagram" in grammar["kinds"]["flow"]["sections"]
                   and "flowMap(n)" in web_text(ENGINE)))
    engine_js = web_text(ENGINE)
    graphmap = (SKILL / "app/web/graphmap.js").read_text(encoding="utf-8")
    menu_js = (SKILL / "app/web/menu.js").read_text(encoding="utf-8")
    style = web_text(STYLES)
    checks.append(("the Graph page draws the whole specification with D3, fetched at one exact version and kept out of the "
                   "repository, loaded before the engine and after the file it keeps its folds with; it says so without a "
                   "connection; the graph around one node is still there",
                   web.index("side.js") < web.index("graphmap.js") < web.index("engine.js")
                   and "cdn.jsdelivr.net/npm/d3@7.9.0/" in graphmap and "The graph is not drawn" in graphmap
                   and "if (!id) return await wholeGraph();" in graphmap and "await graphPage(decoded)" in engine_js))
    checks.append(("the Graph is in the bar, straight to its page, and fills the window under it",
                   'Graph: "#/graph"' in menu_js and '"Graph"].filter(Boolean)' in menu_js
                   and 'where === "matrix" || where === "graph"' in engine_js and 'if (active === "graph") return "Graph";' in menu_js))
    checks.append(("a kind folds to a bubble and opens to a box, what shows is what is joined, a node is an ID's link with its "
                   "card, and the picture prints flat in SVG",
                   "function mapBubble" in graphmap and "function mapBox" in graphmap and "function mapLinks" in graphmap
                   and 'class: `ref map-node' in graphmap and "href: mapHref(n.id)" in graphmap and "<canvas" not in graphmap
                   and "function focusGraph" in graphmap and "function impactGraph" in graphmap and "function layersGraph" in graphmap
                   and 'get("graph")' not in graphmap and "function mapMore" in graphmap
                   and 'svg("a", { class: `ref map-tag' in graphmap and 'class: `mx-tool${on ? " on" : ""}`' in graphmap
                   and graphmap.count(".wheelDelta(mapWheel)") == 2 and 'id.startsWith("layers:")' in graphmap and "map-band" in graphmap
                   and "function mapPick" in graphmap and "&steps=${mapState.steps}" in graphmap and '"graph-scope"' in graphmap
                   and "onwheel: wheel" in graphmap and "MAP_LAYER_HIDDEN" in graphmap
                   and "if (SHEET)" in graphmap and ".graph-map.flat" in style and "MAP_OPEN" in graphmap))
    matrix_js = (SKILL / "app/web/matrix.js").read_text(encoding="utf-8")
    loader = (SKILL / "app/load.py").read_text(encoding="utf-8")
    checks.append(("a node's ways into the Graph stand under its title, not at the foot of its page",
                   engine_js.index('class: "actions-row node-ways"') < engine_js.index("if (n.stale && n.stale.length)")
                   and "waysOf([...pictureWays(n.id)," in engine_js and 'waysOf([["prototype", "Prototype: open it"' in engine_js
                   and 'scrolling: whole ? "no" : null' in engine_js
                   and "waysOf(pictureWays(" in (SKILL / "app/web/matrix.js").read_text(encoding="utf-8")
                   and ".node-ways .live-seg" in style))
    checks.append(("a view is built whole before anything on the page moves, and one overtaken by another is never shown",
                   engine_js.index("content = await overview()") < engine_js.index("if (turn !== routed) return;\n    nav(active);") < engine_js.index("view.replaceChildren(...withAids(")
                   and "if (turn !== routed) return;" in engine_js))
    checks.append(("the Matrix is in the bar before the Graph, straight to its page, fills the window, and stays on the page as "
                   "it is walked, asking only for what the address changed",
                   'Matrix: "#/matrix"' in menu_js and '"Matrix", "Graph"].filter(Boolean)' in menu_js
                   and 'if (active === "matrix") return "Matrix";' in menu_js and 'where === "prototype" || where === "matrix"' in engine_js
                   and 'where === "matrix" && matrixShowing()' in engine_js
                   and web.index("side.js") < web.index("matrix.js") < web.index("engine.js")))
    checks.append(("the Matrix never holds the whole specification: the tree draws the rows in view and fetches a page as it is "
                   "scrolled to, a node's links come a few at a time, and it asks for no library and no whole graph",
                   "function mxAsk" in matrix_js and "mxDraw" in matrix_js and "MX_SPARE" in matrix_js and "matrix/tree?" in matrix_js
                   and "Show more" in matrix_js and "loadD3" not in matrix_js and 'get("graph")' not in matrix_js
                   and "https://" not in matrix_js and "CREATE TABLE crossings" in loader and "nodes_of_kind" in loader))
    checks.append(("the Matrix's tree reads as the other trees do: names cut by the same words(), the menu's icons and letters, a "
                   "row measured for a name that wraps, and its width dragged at the same edge and kept with theirs; the grid is "
                   "drawn whole, and the pane scrolls",
                   "words(n.name" in matrix_js and "lettersOf(row.kind)" in matrix_js and "PARTS[row.name].icon" in matrix_js
                   and "function mxRowAt" in matrix_js and 'wireGrip(mx.root.querySelector(".mx-left"), "Matrix")' in matrix_js
                   and "sideState.widths.Matrix" in matrix_js and 'wireTips(mx.root.querySelector(".mx-left"))' in matrix_js
                   and "var(--side-w, 288px)" in style and ".mx-grid-frame { width: max-content;" in style
                   and "var(--mx-far-w, 340px)" in style and "{ set: mxFarWide," in matrix_js))
    checks.append(("every label in the Matrix's tree shows something in the middle, and only a chevron folds; nothing in the middle "
                   "is cut: it wraps",
                   "function mxPartView" in matrix_js and "function mxKindView" in matrix_js and "place: `kind:${kind}`" in matrix_js
                   and "onclick: mxCollapse" in matrix_js and "function mxRemember" in matrix_js and "mxTravel(-1)" in matrix_js and "mxTravel(1)" in matrix_js
                   and "function mxFilter" in matrix_js and "function mxNarrow" in matrix_js and "function mxPathView" in matrix_js
                   and "mxKindHref(k.kind)" in matrix_js and "mx-owed" in style
                   and "onclick: fold, title:" in matrix_js and ".mx-link-main .mx-name { flex: 1; overflow: visible; white-space: normal;" in style))
    checks.append(("the Matrix prints what is in view, the whole grid on A4; on a phone its sides are tabs",
                   "if (SHEET) return matrixSheet" in matrix_js and "html.sheet .mx-grid" in style and '.mx-panes[data-pane="told"]' in style))
    checks.append(("the prototype folds the bars away, the screen nearly full height, and shows them again from a strip",
                   "proto-folded" in engine_js and "live-strip" in engine_js and "PROTO_FOLDED" in engine_js
                   and "html.proto-folded .bar" in web_text(STYLES)))
    aids = (SKILL / "app/web/aids.js").read_text(encoding="utf-8")
    theme_js = (SKILL / "app/web/theme.js").read_text(encoding="utf-8")
    on_paper = css[css.index("@media print {\n  .bar"):css.index("/* what the code carries")]
    checks.append(("a page has its outline and the nodes beside it, and neither a preview, the prototype nor a sheet has them",
                   web.index("side.js") < web.index("aids.js") < web.index("engine.js")
                   and "withAids(view, where, decoded, content)" in engine_js and "function outline" in aids
                   and "function pager" in aids and "peeked" in aids and 'where === "prototype"' in aids
                   and "if (SHEET) return onSheet(content)" in aids))
    checks.append(("a node's page has small links to the nodes beside it at its top and its foot, an icon and an ID on "
                   "each, its name on a pause, and none on paper",
                   "crumbs.append(above)" in aids and 'h("footer", { class: "page-foot" }, pager(arg))' in aids
                   and 'icon("chevron")' in aids and "title: said" in aids and ".pager," in on_paper))
    checks.append(("the printer in the bar opens the page alone on a sheet of A4 in a tab of its own, shown first, light "
                   "and not to be edited, a prototype in the state it is shown in",
                   'id="print-link"' in web and 'target="_blank"' in web[web.index('id="print-link"'):web.index('id="help-link"')]
                   and "print: [" in (SKILL / "app/web/menu.js").read_text(encoding="utf-8") and "/?print=1" in aids
                   and 'classList.add("peeked", "sheet")' in theme_js and 'sheet ? "light"' in theme_js
                   and "width: 210mm" in css and "tool.shown = query()" in engine_js
                   and "screenOnSheet(decoded)" in engine_js and "window.print()" in aids
                   and "window.print()" not in aids[aids.index("function withAids"):]))
    checks.append(("on paper a page is A4 with margins of its own and a foot saying what it is, with no frame, ink on white "
                   "in either theme, a diagram whole and in its colours, and no row kept whole at the cost of half a sheet",
                   "size: A4" in css and "@bottom-left" in aids and "counter(pages)" in aids
                   and all(part in on_paper for part in (".bar", ".side", ".outline", ".sheet-bar", ".filter", ".flow-diagram, .card"))
                   and ".label-container" in on_paper and not re.search(r"(^|[\s,])tr[\s,].*break-inside", on_paper, re.M)
                   and "beforeprint" in aids and "afterprint" in aids and '"data-theme", "light"' in aids))
    checks.append(("a screen on paper fills the width of A4, whatever the window, and runs on from sheet to sheet: one frame "
                   "to a sheet in a box no taller than it, the page moved and not scrolled, no cut through what it holds",
                   "SHEET_WIDE / wide" in aids and "clientWidth / wide" not in aids and "SHEET_TALL / tall" not in aids
                   and ".sheet-part { width: 174mm; overflow: hidden; }" in css and ".sheet-part { break-inside: avoid; }" in on_paper
                   and "translateY(" in aids and "scrollTo" not in aids and "cutAt(held, at, room)" in aids
                   and ".frame-box, " not in on_paper))
    views = set(re.findall(r'where === "\w+"\) content = await (?:\(SHEET \? (\w+)\(\w+\) : )?(\w+)\(', engine_js)) | set()
    called = {name for pair in views for name in pair if name}
    written = "".join(p.read_text(encoding="utf-8") for p in (SKILL / "app/web").glob("*.js"))
    missing = sorted(name for name in called if f"function {name}(" not in written)
    checks.append((f"every view a route opens is written{': ' + ', '.join(missing) if missing else ''}",
                   len(called) >= 10 and not missing and "function gallery(" in written))
    request_js = (SKILL / "app/web/request.js").read_text(encoding="utf-8")
    card_js = (SKILL / "app/web/card.js").read_text(encoding="utf-8")
    checks.append(("a node's page and its card ask for a change, and only the inbox hears it: no page posts a change to the data",
                   "requestChange(n.id, n.name)" in engine_js and "requestChange(c.id, c.name)" in card_js
                   and '"/api/inbox"' in request_js and "editing." not in written and "/api/changes" not in written))
    story = (SKILL / "app/web/story.js").read_text(encoding="utf-8")
    checks.append(("a flow's page begins with its story and a table of the requirements its steps name, told by the "
                   "server",
                   web.index("story.js") < web.index("engine.js") and "function flowStory" in story
                   and "story/" in story and "flowStory(n)" in web_text(ENGINE)))
    foundations = (SKILL / "app/web/foundations.js").read_text(encoding="utf-8")
    checks.append(("a foundation's page draws what each row of its tables looks like, from the row's own values",
                   web.index("foundations.js") < web.index("engine.js") and "function foundationBody" in foundations
                   and "Looks like" in foundations and "foundationBody(f[key], n.tokens || {})" in web_text(ENGINE)))
    checks.append(("the menu of a part holds its kinds and its own pages; a click on the part opens its page",
                   "Everything in" not in (SKILL / "app/web/menu.js").read_text(encoding="utf-8")))
    tips = card[card.index("function wireTips"):card.index("function wireCards")]
    cards_alone = card.replace(tips, "")
    lessons = list((SKILL / "tutorial").glob("*.html"))
    told = "".join(p.read_text(encoding="utf-8") for p in lessons)
    leaves = [*(SKILL / "user-manual").glob("*.html"), *lessons]
    pictures = re.findall(r'<img[^>]*src="([^"]+)"', told)
    checks.append(("the manual and the tutorial are folders of pages, each with its own shared/ folder, one list of the manual's pages, every picture used, each entered from a page at the skill's root, with no Markdown behind them",
                   len(leaves) >= 50 and len(lessons) == 21 and len(pictures) >= 30 and all((SKILL / "tutorial" / p).is_file() for p in pictures)
                   and {p.name for p in (SKILL / "tutorial/pictures").glob("*.webp")} == {p.split("/")[-1] for p in pictures}
                   and set(re.findall(r'\[\s*"([^"]+)",\s*"', (SKILL / "tutorial/shared/chapters.js").read_text(encoding="utf-8"))) == {p.stem for p in lessons}
                   and not list((SKILL / "tutorial").glob("*.webp"))
                   and all('href="shared/style.css"' in p.read_text(encoding="utf-8") and "<style" not in p.read_text(encoding="utf-8") for p in leaves)
                   and not (SKILL / "shared").exists()
                   and set(re.findall(r'\[\s*"([^"]+)",\s*"', (SKILL / "user-manual/shared/chapters.js").read_text(encoding="utf-8"))) == {p.stem for p in (SKILL / "user-manual").glob("*.html")}
                   and {p.name for p in (SKILL / "user-manual/pictures").glob("*.webp")} == set(re.findall(r'src="pictures/([^"]+)"', "".join(p.read_text(encoding="utf-8") for p in (SKILL / "user-manual").glob("*.html"))))
                   and all(f"url={to}/index.html" in (SKILL / n).read_text(encoding="utf-8") for n, to in (("USER-MANUAL.html", "user-manual"), ("TUTORIAL.html", "tutorial")))
                   and not any((SKILL / n).exists() for n in ("TUTORIAL.md", "USER-MANUAL.md"))))
    bar_js = (SKILL / "app/web/menu.js").read_text(encoding="utf-8")
    checks.append(("a part's word opens its page and a small arrow its menu, and nothing opens on a hover",
                   'href: partPage(key)' in bar_js and 'class: "nav-arrow"' in bar_js and "mouseenter" not in bar_js and "mouseleave" not in bar_js
                   and ".nav-arrow {" in style))
    checks.append(("a pause on an ID only says what it is: the tip opens no card and closes none",
                   "openCard" not in tips and "closeCard" not in tips and "shutCard" not in tips and "function idKind" in card))
    checks.append(("a right click on an ID opens its card, and nothing else does, whose Preview shows the node in a popup without the bar",
                   web.index("card.js") < web.index("engine.js") and "/?peek=1" in card
                   and "peeked" in (SKILL / "app/web/theme.js").read_text(encoding="utf-8")
                   and 'target: "_blank"' in card and 'icon("preview")' in card and 'icon("newtab")' in card
                   and '"contextmenu"' in card and '"mouseover"' not in cards_alone and '"focusin"' not in cards_alone and "[data-card]" in card
                   and "function pinCard" in card and "function shutCard" in card and "function flashCard" in card
                   and '"pointerdown"' in card and ".id-card-head { cursor: move;" in style
                   and "id-card-graph" in card and "mapHref(`impact:${id}`)" in card and "mapHref(`layers:${id}`)" in card and "mxNode(top)" in card
                   and 'class: "mx-tool away"' in card and "ways.map((way) => wayAway(...way))" in card and ".mx-tool.away .icon:last-child" in style
                   and "const beside = sideOf(at);" in card and "function wireTips" in card and ".id-tip { position: fixed;" in style and graphmap.count("mapOpen(") == 3 and "MAP_TWICE" in graphmap and "ondblclick: twice" in graphmap and "CARD_PRESS" in card and 'e.pointerType === "mouse"' in card and "if (!press.done) openCard(link)" in card
                   and "-webkit-touch-callout: none" in style and ".map-tag.selected rect, .map-tag.centre rect { fill: var(--accent);" in style and ".live-bar.graph-bar { min-height: 38px;" in style and '"live-bar graph-bar"' in graphmap
                   and 'link.closest("#view, .id-card")' in card and "CARD_MOST" in card and '"scroll"' not in cards_alone))
    engine = web_text(ENGINE)
    runtime = (SKILL / "app/web/runtime/live.js").read_text(encoding="utf-8")
    checks.append(("a part opens a plain menu of its kinds with their counts, and the prototype is a link straight to it",
                   'Prototype: "#/prototype"' in menu and "href: DIRECT[key]" in menu and "drop-count" in menu and "mega" not in menu + web
                   and "mega" not in web_text(STYLES)))
    checks.append(("the prototype is a tool: a toolbar, the screen full size, an inspector fed by the runtime's messages",
                   all(w in engine for w in ('class: "live-bar"', 'class: "live-inspector"', "postMessage", 'what.live === "pick"'))
                   and "function history(" not in engine))           # a function of that name hides window.history
    checks.append(("the runtime reads data-el and data-part as handles, and marks nothing unless asked",
                   '[data-el], [data-part]' in runtime and 'params.get("marks") === "hover" ? "hover" : "off"' in runtime))
    head, css = web.split("</head>")[0], web_text(STYLES)
    checks.append(("the appearance is set in the head before the page paints, and dark is the reader's choice",
                   '<script src="theme.js"></script>' in head and "defer" not in head
                   and ':root[data-theme="dark"]' in css and "prefers-color-scheme" not in css))
    checks.append(("the export lets its reader choose the appearance, and is dark without a script where the system is",
                   'data-look="dark"' in text and ':root[data-theme="dark"]' in text and ":root:not([data-theme])" in text))
    order = [text.find(f'<h2 id="{a}"') for a in ("the-document", "evidence", "decisions-and-what-is-open",
                                                  "requirements", "domain", "what-programs-call",
                                                  "how-it-is-used-and-how-it-looks", "prototype")]
    checks.append(("the export follows the menu's order, the prototype a part of its own, each screen drawn once in it",
                   -1 not in order and order == sorted(order)
                   and text.find('<iframe class="proto"') > order[-1] and 'href="#prototype-SC7"' in text))
    return checks
