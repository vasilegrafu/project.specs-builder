"""The specification as one file, for whoever has no Python: an HTML page that holds everything -- the document, every
node of every kind with its fields, texts, tables, rows and links both ways, what is open, and each screen's prototype
drawn with the product's own styles, scripts and pictures inlined -- and needs nothing beside it to be read. As in the
application, a right click on an ID opens its card and each flow has its diagram: by the application's own card.js and
flowmap.js, over what the file holds. Mermaid alone comes from the CDN, as there; without a connection a flow shows its
diagram's text, and its steps say the same.

    python app/spec.py export                      writes <the specification>/export/<name>.html
    python app/spec.py export --into report.html   writes it there

Every ID in it is a link to where that node is said in the same file. Text from the data is escaped wherever it
stands; a prototype is drawn in a sandboxed frame that may run its scripts and nothing else.
"""
from __future__ import annotations

import base64
import html
import json
import mimetypes
import re
from datetime import datetime, timezone
from pathlib import Path

import api
import finish
import load as loading
import prototypes
import review

ORDER = [("The document", ["document"]),
         ("Evidence", ["source", "finding", "contradiction"]),
         ("Decisions and what is open", ["decision", "question", "addition"]),
         ("Requirements", ["goal", "requirement", "quality", "constraint", "risk"]),
         ("Domain", ["term", "rule", "role", "entity"]),
         ("What programs call", ["endpoint"]),
         ("How it is used and how it looks", ["flow", "screen", "component", "foundation"])]
PLURAL = {"goal": "Goals", "requirement": "Requirements", "quality": "Qualities", "constraint": "Constraints",
          "risk": "Risks", "term": "Terms", "rule": "Rules", "role": "Roles", "entity": "Entities", "flow": "Flows",
          "screen": "Screens", "component": "Components", "foundation": "Foundations", "endpoint": "Endpoints",
          "decision": "Decisions", "question": "Open questions", "addition": "Additions not confirmed",
          "source": "Sources", "finding": "Findings", "contradiction": "Contradictions", "document": "The document"}
ID_RE = re.compile(r"\b([A-Z]+\d+(?:\.[\w-]+)?)\b")
RUNTIME = Path(__file__).resolve().parent / "web" / "runtime"
WEB = Path(__file__).resolve().parent / "web"
THEME = (WEB / "theme.js").read_text(encoding="utf-8")
CSS = (WEB / "style.css").read_text(encoding="utf-8")
ENGINE = (WEB / "engine.js").read_text(encoding="utf-8")
TOKENS = CSS[CSS.index(":root {"):CSS.index("/* a kind's colour is its part's")]
DARK = TOKENS[TOKENS.index("{", TOKENS.index(':root[data-theme="dark"]')) + 1:TOKENS.rindex("}")]


def rules(first: str) -> str:
    """The application's own rules for a thing: from the first of them to the blank line after."""
    at = CSS.index(first)
    return CSS[at:CSS.index("\n\n", at)]


# what the application's card.js and flowmap.js ask of its engine: one page holds what the server would give them
AIDS = (ENGINE[ENGINE.index("function h(tag"):ENGINE.index("\n}\n", ENGINE.index("function h(tag")) + 3] + """
const nodeHref = (id) => `#${id}`;
const chip = (id) => h("a", { class: "id", href: nodeHref(id) }, id);
const linkify = (text) => String(text).split(/\\b([A-Z]+\\d+(?:\\.[\\w-]+)?)\\b/)
  .map((part, i) => (i % 2 && state.names[part] ? chip(part) : part));
""")
DRAW = """
for (const slot of document.querySelectorAll(".flow-slot")) {
  const box = flowMap(window.flows[slot.dataset.flow]);
  if (box) slot.replaceWith(box);
}
window.addEventListener("beforeprint", () => document.documentElement.setAttribute("data-theme", "light"));
window.addEventListener("afterprint", () => window.theme.set(window.theme.choice()));
"""
LOOKS = (("system", "As the system"), ("light", "Light"), ("dark", "Dark"))
# the reader's choice of appearance, kept as the application keeps it: the buttons told which is chosen
LOOKS_SCRIPT = """
(function () {
  var buttons = document.querySelectorAll("[data-look]");
  function mark() {
    var now = window.theme ? window.theme.choice() : "system";
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute("aria-pressed", String(buttons[i].getAttribute("data-look") === now));
    }
  }
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function () { window.theme.set(this.getAttribute("data-look")); mark(); });
  }
  mark();
}());
"""
STYLE = TOKENS + """
:root { --warn: var(--warn-ink); color-scheme: light; }
:root[data-theme="dark"] { color-scheme: dark; }
@media (prefers-color-scheme: dark) { :root:not([data-theme]) { """ + DARK + """ } }
.looks { display: flex; justify-content: flex-end; gap: .3rem; margin-bottom: .6rem; }
.looks button { font: inherit; font-size: .85rem; padding: .2rem .65rem; border: 1px solid var(--line); border-radius: 999px;
  background: transparent; color: var(--muted); cursor: pointer; }
.looks button[aria-pressed="true"] { border-color: var(--accent); color: var(--accent); }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1100px; margin: 0 auto; padding: 24px 16px 64px; }
a { color: var(--accent); text-decoration: none; } a:hover { text-decoration: underline; }
h1 { font-size: 2rem; margin: .2rem 0 .4rem; } h2 { margin: 2.6rem 0 .8rem; border-bottom: 1px solid var(--line); padding-bottom: .3rem; }
h3 { margin: 1.6rem 0 .5rem; font-size: 1.15rem; } h4 { margin: 1rem 0 .3rem; font-size: 1rem; color: var(--muted); }
.lead, .meta { color: var(--muted); } .meta { font-size: .88rem; }
.node { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); padding: 14px 18px; margin: 14px 0; }
.node:target { outline: 2px solid var(--accent); }
.id { font-family: var(--mono); font-size: .92em; }
.badge { display: inline-block; font-size: .78rem; padding: 0 .45rem; border: 1px solid var(--line); border-radius: 999px; color: var(--muted); }
dl.fields { display: grid; grid-template-columns: max-content 1fr; gap: .2rem 1rem; margin: .4rem 0; }
dl.fields dt { color: var(--muted); } dl.fields dd { margin: 0; overflow-wrap: anywhere; }
.story { padding: .7rem .9rem; border-left: 3px solid var(--accent); background: var(--bg); border-radius: 6px; }
.frame { overflow-x: auto; } table { border-collapse: collapse; width: 100%; margin: .4rem 0; font-size: .92rem; }
th, td { border-bottom: 1px solid var(--line); padding: .35rem .5rem; text-align: left; vertical-align: top; }
th { color: var(--muted); font-weight: 600; }
pre { overflow-x: auto; background: var(--bg); border: 1px solid var(--line); border-radius: 6px; padding: .6rem .8rem; }
code { font-family: var(--mono); font-size: .9em; }
.warn { background: var(--warn-bg); color: var(--warn); border-radius: var(--radius); padding: .7rem 1rem; margin: .8rem 0; }
nav.toc ol { columns: 2 16rem; padding-left: 1.2rem; }
iframe.proto { width: 100%; height: 640px; border: 1px solid var(--line); border-radius: var(--radius); background: #fff; }
iframe.drawn { width: 100%; height: 260px; border: 1px solid var(--line); border-radius: var(--radius); background: #fff; }
@page { size: A4; margin: 18mm; }
@media print {
  iframe, .looks, .id-card { display: none !important; }
  body { background: #fff; }
  main { max-width: none; padding: 0; }
  .node { border: 0; padding: 0; }
  h2, h3, h4 { break-after: avoid; }
  .flow-diagram { break-inside: avoid; }
  .flow-diagram-canvas svg { display: block; max-height: 230mm; margin: 0 auto; }
""" + CSS[CSS.index("  /* a diagram is drawn ahead"):CSS.index("}\n", CSS.index("  .flow-diagram .nodeLabel")) + 2] + """}
""" + rules(".flow-diagram {") + "\n" + rules(".id-card {") + """
main a.id { white-space: nowrap; padding: 0 .3em; border: 1px solid color-mix(in srgb, currentColor 38%, transparent); border-radius: 4px; }
.id-card a.id { margin-right: .35rem; }
"""


def esc(text: object) -> str:
    return html.escape(str(text or ""), quote=True)


class Page:
    """What the export writes, with what it knows: every node, so an ID becomes a link to it."""

    def __init__(self, root: Path, built: bool = False) -> None:
        self.root = root
        self.built = built                              # the server keeps the database as the data stands
        self.g = loading.grammar()
        self.done = loading.load(root)
        if self.done.problems:
            raise ValueError(f"{len(self.done.problems)} problem(s) in the data: `spec.py check` says them; "
                             f"nothing is exported from a specification that does not load")
        self.out: dict[str, list[loading.Edge]] = {}
        self.into: dict[str, list[loading.Edge]] = {}
        for e in self.done.edges:
            if e.rel != "has":
                self.out.setdefault(e.src, []).append(e)
                self.into.setdefault(e.dst, []).append(e)

    # ---- text
    def linked(self, escaped: str) -> str:
        """IDs in escaped text, made links to where each is said; an ID no node has stays text."""
        return ID_RE.sub(lambda m: f'<a class="id" href="#{m.group(1)}">{m.group(1)}</a>'
                         if m.group(1) in self.done.nodes else m.group(1), escaped)

    def inline(self, text: str) -> str:
        out, last = [], 0
        for m in re.finditer(r"`([^`]+)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\((https?://[^)\s]+|#[\w.-]+)\)", text):
            out.append(self.linked(esc(text[last:m.start()])))
            if m.group(1) is not None:
                out.append(f"<code>{esc(m.group(1))}</code>")
            elif m.group(2) is not None:
                out.append(f"<strong>{self.linked(esc(m.group(2)))}</strong>")
            else:
                out.append(f'<a href="{esc(m.group(4))}">{esc(m.group(3))}</a>')
            last = m.end()
        out.append(self.linked(esc(text[last:])))
        return "".join(out)

    def markdown(self, text: str) -> str:
        """The Markdown the data holds, as HTML: headings, lists, tables, code, paragraphs; everything escaped."""
        lines = str(text or "").replace("\r\n", "\n").split("\n")
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if line.startswith("```"):
                block = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    block.append(lines[i])
                    i += 1
                out.append(f"<pre><code>{esc(chr(10).join(block))}</code></pre>")
                i += 1
                continue
            heading = re.match(r"(#{1,4})\s+(.*)", line)
            if heading:
                level = min(len(heading.group(1)) + 3, 6)
                out.append(f"<h{level}>{self.inline(heading.group(2))}</h{level}>")
                i += 1
                continue
            block = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("```") and not re.match(r"#{1,4}\s", lines[i]):
                block.append(lines[i])
                i += 1
            if all(re.match(r"\s*[-*] ", b) or re.match(r"\s{2,}\S", b) for b in block):
                items, current = [], ""
                for b in block:
                    if re.match(r"\s*[-*] ", b):
                        if current:
                            items.append(current)
                        current = re.sub(r"^\s*[-*] ", "", b)
                    else:
                        current += " " + b.strip()
                items.append(current)
                out.append("<ul>" + "".join(f"<li>{self.inline(x)}</li>" for x in items) + "</ul>")
            elif all(re.match(r"\d+\.\s", b) for b in block):
                out.append("<ol>" + "".join(f"<li>{self.inline(re.sub(r'^\d+\.\s+', '', b))}</li>" for b in block) + "</ol>")
            elif len(block) > 1 and all(b.strip().startswith("|") for b in block) and re.fullmatch(r"\|[\s:|-]+\|", block[1].strip()):
                cells = lambda b: [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", b.strip().strip("|"))]  # noqa: E731
                out.append(self.table(cells(block[0]), [cells(b) for b in block[2:]]))
            else:
                out.append("<p>" + "<br>".join(self.inline(b) for b in block) + "</p>")
        return "\n".join(out)

    def table(self, head: list[str], rows: list[list[object]], ids: list[str] | None = None) -> str:
        """A table; with `ids`, each line anchored by its row's ID, so that a link to the row lands on it."""
        line = lambda n, r: (f'<tr id="{esc(ids[n])}">' if ids else "<tr>") + "".join(  # noqa: E731
            f"<td>{self.inline(str(c or ''))}</td>" for c in r) + "</tr>"
        return ('<div class="frame"><table><thead><tr>' + "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr></thead><tbody>"
                + "".join(line(n, r) for n, r in enumerate(rows)) + "</tbody></table></div>")

    # ---- prototypes
    def asset(self, rel: str) -> str:
        """A file of the prototypes' assets as a data address; what is not there, or too large, as it was."""
        path = (self.root / prototypes.PROTOTYPES / rel).resolve()
        place = (self.root / prototypes.PROTOTYPES).resolve()
        if not path.is_relative_to(place) or not path.is_file() or path.stat().st_size > 400_000:
            return rel
        kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return f"data:{kind};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"

    def drawn(self, body_file: Path, drawings: bool = False) -> str:
        """A prototype as a page that needs nothing beside it: the product's shell, its styles and scripts inlined,
        its pictures as data, the application's live.js to show its states."""
        shell_path = self.root / prototypes.SHELL
        if not body_file.is_file() or not shell_path.is_file():
            return ""
        shell = shell_path.read_text(encoding="utf-8")
        body = body_file.read_text(encoding="utf-8")
        page = shell.replace("{{title}}", "").replace("{{body}}", body)

        def styles(m: re.Match) -> str:
            if m.group(1) == prototypes.TOKENS_CSS:
                return f"<style>{prototypes.tokens_css(self.root)}</style>"
            path = self.root / prototypes.PROTOTYPES / m.group(1)
            return f"<style>{path.read_text(encoding='utf-8')}</style>" if path.is_file() else ""

        def scripts(m: re.Match) -> str:
            path = self.root / prototypes.PROTOTYPES / m.group(1)
            return f"<script>{path.read_text(encoding='utf-8')}</script>" if path.is_file() else ""

        page = re.sub(r'<link rel="stylesheet" href="(assets/[^"]+)">', styles, page)
        page = re.sub(r'<script src="(assets/[^"]+)"[^>]*></script>', scripts, page)
        page = re.sub(r'(src|href)="(assets/[^"]+)"', lambda m: f'{m.group(1)}="{self.asset(m.group(2))}"', page)
        page = re.sub(r'url\((["\']?)(\.\./img/[^)"\']+|assets/[^)"\']+)\1\)',
                      lambda m: f"url({self.asset(m.group(2).replace('../img/', 'assets/img/'))})", page)
        page = re.sub(r'href="(SC\d+)\.html"', r'href="#"', page)           # a link to another screen goes nowhere here
        runtime = f"<style>{(RUNTIME / 'live.css').read_text(encoding='utf-8')}</style>"
        if drawings:
            runtime += f"<style>{(RUNTIME / 'drawings.css').read_text(encoding='utf-8')}</style>"
        runtime += f"<script>{(RUNTIME / 'live.js').read_text(encoding='utf-8')}</script>"
        head = page.find("<head>")
        page = page[:head + 6] + runtime + page[head + 6:] if head >= 0 else runtime + page
        return esc(page)

    # ---- what the application's scripts ask of it
    def held(self) -> str:
        """Every ID's card, its name and each flow's words, for card.js and flowmap.js: as data, never as markup."""
        def safe(value: object) -> str:
            return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")

        if not self.built:
            loading.build(self.done)
        stale = api.owed(self.root)
        cards = {i: api.card(self.root, i, stale) for i in self.done.nodes}
        flows = {n.id: {"id": n.id, "fields": {k: v for k, v in n.fields.items() if isinstance(v, str)}}
                 for n in self.done.nodes.values() if n.kind == "flow"}
        return (f"window.cards = {safe(cards)};\nwindow.flows = {safe(flows)};\n"
                f"const state = {{ names: {safe(api.names(self.root))} }};\n{AIDS}")

    # ---- nodes
    def label(self, n: loading.Node) -> str:
        return api.label(self.g, n.kind, n.fields)

    def story(self, ident: str) -> str:
        s = finish.story(self.g, self.done, ident)
        out = [f'<p class="story">{self.inline(s["story"])}</p>']
        if s["requirements"]:
            out.append(f"<h4>What it carries</h4><p class='meta'>{len(s['requirements'])} requirement(s) named in its "
                       f"steps, {s['must']} must, with {s['criteria']} criteria to pass.</p>")
            rows = "".join(
                f"<tr><td>{self.inline(r['id'] + ' ' + r['name'])}</td><td>{esc(r['priority'])}</td>"
                f"<td>{esc(r['backed'])}</td><td>" + "<br>".join(self.inline(f"{c['id']} {c['says']}") for c in r["criteria"])
                + "</td></tr>" for r in s["requirements"])
            out.append('<div class="frame"><table><thead><tr><th>Requirement</th><th>Priority</th><th>Backed</th>'
                       f"<th>Accepted when</th></tr></thead><tbody>{rows}</tbody></table></div>")
        return "\n".join(out)

    def node(self, n: loading.Node) -> str:
        spec = self.g["kinds"][n.kind]
        form = api.form(self.g, n.kind)
        title = n.fields.get("name") or ("" if n.kind == "document" else self.label(n))
        heading = esc(title) if n.kind == "document" else f'<span class="id">{esc(n.id)}</span> {esc(title)}'
        if n.fields.get("priority"):
            heading += f' <span class="badge">{esc(n.fields["priority"])}</span>'
        parts = [f'<section class="node" id="{esc(n.id)}"><h3>{heading}</h3>']
        slot = f'<div class="flow-slot" data-flow="{esc(n.id)}"></div>'
        if n.kind == "flow":                             # its story and what it carries, first: what a team plans from
            parts.append(self.story(n.id))
        plain = [(f["key"], n.fields.get(f["key"])) for f in form["fields"] if f["key"] not in ("name",) and n.fields.get(f["key"])]
        if plain:
            parts.append('<dl class="fields">' + "".join(f"<dt>{esc(k)}</dt><dd>{self.inline(str(v))}</dd>" for k, v in plain) + "</dl>")
        first = spec.get("sections", {}).get("", {}).get("as")   # the text under the header needs no heading
        if n.kind == "flow" and not n.fields.get("steps"):
            parts.append(slot)
        for text in form["texts"]:
            if n.kind == "flow" and text["as"] == "diagram":    # drawn in its slot, above the steps
                continue
            if n.kind == "flow" and text["as"] == "steps" and n.fields.get("steps"):
                parts.append(slot)
            if n.fields.get(text["as"]):
                parts.append(("" if text["as"] == first else f"<h4>{esc(text['title'])}</h4>") +
                             self.markdown(n.fields[text["as"]]))
        for table in form["tables"]:
            rows = n.fields.get(table["as"]) or []
            if rows:
                head = [c["name"] for c in table["columns"]]
                parts.append(f"<h4>{esc(table['title'])}</h4>" + self.table(head, [[r.get(h.lower(), "") for h in head] for r in rows]))
        children = sorted((c for c in self.done.nodes.values() if c.parent == n.id), key=lambda c: loading_natural(c.id))
        if children and form["rows"]:
            if form["rows"]["list"]:
                parts.append(f"<h4>{esc(form['rows']['section'])}</h4><ol>" + "".join(
                    f'<li id="{esc(c.id)}"><span class="id">{esc(c.id)}</span> {self.inline(c.fields.get("says", ""))}</li>'
                    for c in children) + "</ol>")
            else:
                columns = form["rows"]["columns"]
                head = ["ID", *[c["name"] for c in columns if not c.get("id")]]
                body = []
                for c in children:
                    cells = [f"{c.id}"]
                    for col in columns:
                        if col.get("id"):
                            continue
                        if col.get("relation"):
                            cells.append(", ".join(e.dst for e in self.out.get(c.id, []) if e.rel == col["relation"]))
                        else:
                            cells.append(str(c.fields.get(col["key"], "")))
                    body.append(cells)
                parts.append(f"<h4>{esc(form['rows']['section'])}</h4>" + self.table(head, body, [c.id for c in children]))
        if n.fields.get("actions"):
            word = {"yes": "may", "no": "may not", "?": "not known"}
            parts.append("<h4>What they may do</h4>" + self.table(["", "About", "Action"], [
                [word.get(a.get("answer"), a.get("answer")), a.get("about", ""), a.get("action", "")] for a in n.fields["actions"]]))
        links = self.out.get(n.id, [])
        back = self.into.get(n.id, [])
        if links or back:
            grouped: dict[str, list[str]] = {}
            for e in links:
                grouped.setdefault(e.rel, []).append(e.dst)
            for e in back:
                grouped.setdefault(self.g["relations"][e.rel].get("back", e.rel), []).append(e.src)
            parts.append('<dl class="fields">' + "".join(
                f"<dt>{esc(rel)}</dt><dd>{self.linked(esc(', '.join(sorted(set(ids), key=loading_natural))))}</dd>"
                for rel, ids in grouped.items()) + "</dl>")
        if n.kind == "screen" and (self.root / prototypes.PROTOTYPES / "screens" / f"{n.id}.html").is_file():
            parts.append(f'<p><a href="#prototype-{esc(n.id)}">Its prototype</a></p>')
        if n.kind == "component":
            drawn = self.drawn(self.root / prototypes.PROTOTYPES / "components" / f"{n.id}.html", drawings=True)
            if drawn:
                parts.append(f'<h4>Drawn</h4><iframe class="drawn" sandbox="allow-scripts" title="The variants of '
                             f'{esc(n.id)}" srcdoc="{drawn}"></iframe>')
        parts.append("</section>")
        return "\n".join(parts)

    def prototype(self) -> list[str]:
        """The prototype, a part of its own: each flow with the screens it passes, in its order, then the screens no
        flow passes; each screen drawn once, under the first flow that passes it, and named again under the rest."""
        screens = sorted((n for n in self.done.nodes.values() if n.kind == "screen" and n.parent is None),
                         key=lambda n: loading_natural(n.id))
        if not screens:
            return []
        flows = sorted((n for n in self.done.nodes.values() if n.kind == "flow"), key=lambda n: loading_natural(n.id))
        body, placed = ['<h2 id="prototype">Prototype</h2>'], set()

        def drawn(n: loading.Node, under: str) -> str:
            if n.id in placed:
                return (f'<p class="meta">{self.linked(esc(n.id))} {esc(self.label(n))} -- drawn under '
                        f'<a href="#prototype-{esc(n.id)}">{esc(placed_under[n.id])}</a></p>')
            page = self.drawn(self.root / prototypes.PROTOTYPES / "screens" / f"{n.id}.html")
            if not page:
                return f'<p class="meta">{self.linked(esc(n.id))} {esc(self.label(n))} -- no prototype drawn yet</p>'
            placed.add(n.id)
            placed_under[n.id] = under
            return (f'<h4 id="prototype-{esc(n.id)}">{self.linked(esc(n.id))} {esc(self.label(n))}</h4>'
                    f'<iframe class="proto" sandbox="allow-scripts" title="The prototype of {esc(n.id)}" '
                    f'srcdoc="{page}"></iframe>')

        placed_under: dict[str, str] = {}
        passed = set()
        for f in flows:
            order = [e.dst for e in self.done.edges if e.src == f.id and e.rel == "passes"
                     and e.dst in self.done.nodes]
            if not order:
                continue
            passed.update(order)
            body.append(f"<h3>{self.linked(esc(f.id))} {esc(self.label(f))}</h3>")
            body += [drawn(self.done.nodes[s], f.id) for s in order]
        rest = [n for n in screens if n.id not in passed]
        if rest:
            body.append("<h3>In no flow</h3>")
            body += [drawn(n, "in no flow") for n in rest]
        return body

    def write(self) -> str:
        doc = self.done.nodes.get("document")
        name = doc.fields.get("name") if doc else api.title(self.root)
        stamps = review.held(self.root)
        o = finish.opened(self.g, self.done, stamps)
        held = finish.ready(self.g, self.done, stamps)
        when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        counts = {}
        for n in self.done.nodes.values():
            if n.parent is None:
                counts[n.kind] = counts.get(n.kind, 0) + 1
        toc, body = [], []
        for part, kinds in ORDER:
            here = [k for k in kinds if counts.get(k)]
            if not here:
                continue
            anchor = re.sub(r"[^a-z]+", "-", part.lower()).strip("-")
            toc.append(f'<li><a href="#{anchor}">{esc(part)}</a></li>')
            body.append(f'<h2 id="{anchor}">{esc(part)}</h2>')
            for kind in here:
                nodes = sorted((n for n in self.done.nodes.values() if n.kind == kind and n.parent is None),
                               key=lambda n: loading_natural(n.id))
                if kind != "document":
                    body.append(f"<h3>{esc(PLURAL.get(kind, kind))} <span class='meta'>({len(nodes)})</span></h3>")
                body += [self.node(n) for n in nodes]
        if (shown := self.prototype()):
            toc.append('<li><a href="#prototype">Prototype</a></li>')
            body += shown
        status = doc.fields.get("status", "") if doc else ""
        verdict = ("<p>Agreed: nothing stands in the way.</p>" if status == "agreed" and not held else
                   "<p>Ready to be agreed.</p>" if not held else
                   "<div class='warn'><strong>Not ready to be agreed:</strong><ul>" +
                   "".join(f"<li>{self.linked(esc(x))}</li>" for x in held) + "</ul></div>")
        summary = self.markdown(doc.fields.get("summary", "")) if doc else ""
        stale = f"<p class='meta'>Stale, to be read again: {self.linked(esc(', '.join(o['stale'])))}</p>" if o["stale"] else ""
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(name)}</title>
<script>{THEME}</script>
<style>{STYLE}</style>
</head>
<body>
<main>
<div class="looks" role="group" aria-label="Appearance">{''.join(f'<button type="button" data-look="{k}" aria-pressed="false">{v}</button>' for k, v in LOOKS)}</div>
<p class="meta">Product specification · {esc(doc.fields.get('kind', '') if doc else '')} · {esc(status)} · exported {esc(when)}</p>
<h1>{esc(name)}</h1>
{summary}
<p class="lead">{sum(counts.values())} nodes: {esc(', '.join(f'{v} {k if v == 1 else PLURAL.get(k, k).lower()}' for k, v in sorted(counts.items()) if k != 'document'))}.</p>
{verdict}
{stale}
<nav class="toc"><h2>Contents</h2><ol>{''.join(toc)}</ol></nav>
{chr(10).join(body)}
</main>
<script>{LOOKS_SCRIPT}</script>
<script>{self.held()}</script>
<script>{(WEB / "card.js").read_text(encoding="utf-8")}</script>
<script>{(WEB / "flowmap.js").read_text(encoding="utf-8")}</script>
<script>{DRAW}</script>
</body>
</html>
"""


def loading_natural(ident: str) -> list:
    return [int(x) if x.isdigit() else x for x in re.findall(r"\d+|\D+", str(ident))]


def export(root: Path, into: Path | None = None, built: bool = False) -> Path:
    page = Page(root, built)
    text = page.write()
    doc = page.done.nodes.get("document")
    name = re.sub(r"[^a-z0-9]+", "-", (doc.fields.get("name") if doc else api.title(root)).lower()).strip("-") or "specification"
    path = into or root / "export" / f"{name}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path
