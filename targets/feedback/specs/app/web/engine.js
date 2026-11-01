// The application's engine: one page, a view per address, every view drawn from the API.
// Text from the data is always set as text, never as HTML, so nothing a specification says can run here.
"use strict";

const state = { summary: null, grammar: null, names: {}, menu: null };
const view = document.getElementById("view");
const PLURAL = { goal: "Goals", requirement: "Requirements", criterion: "Criteria", rule: "Rules", role: "Roles",
                 entity: "Entities", screen: "Screens", element: "Elements", component: "Components", part: "Parts",
                 quality: "Qualities", constraint: "Constraints", decision: "Decisions", question: "Questions",
                 risk: "Risks", term: "Terms", state: "States", foundation: "Foundations", flow: "Flows",
                 endpoint: "Endpoints", source: "Sources", finding: "Findings", contradiction: "Contradictions",
                 addition: "Additions",
                 document: "Document" };
// the menu: the specification as people read it, each group the kinds it holds
const GROUPS = [
  ["Evidence", ["source", "finding", "contradiction"]],
  ["Decisions", ["decision", "question", "addition"]],
  ["Requirements", ["goal", "requirement", "quality", "constraint", "risk"]],
  ["Domain", ["term", "rule", "role", "entity"]],
  ["API", ["endpoint"]],
  ["UX", ["flow", "screen", "component", "foundation"]],
];
const TEXTS = { does: "What it shows and does" };     // a row's text; a node's texts are titled by the grammar
const ROW_LINKS = ["is", "shows", "about", "leads to"];          // the columns of an element's or a part's row
const WIDTHS = { phone: 390, tablet: 768, desktop: null };
const ID_RE = /\b([A-Z]+\d+(?:\.\d+)*)\b/g;

async function get(path) {
  const response = await fetch("/api/" + path);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || response.statusText);
  return body;
}

function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") el.className = value;
    else if (key.startsWith("on")) el.addEventListener(key.slice(2), value);
    else el.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

function svg(tag, attrs, ...children) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key.startsWith("on")) el.addEventListener(key.slice(2), value);
    else el.setAttribute(key, value);
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

const nodeHref = (id) => `#/node/${encodeURIComponent(id)}`;

function chip(id, label) {
  const known = state.names[id];
  return h("a", { class: `chip kind-${known ? known.kind : "unknown"}`, href: nodeHref(id) }, label || id);
}

// An ID written in a text becomes a link where a node has it; any other text stays as it is.
function linkify(text) {
  const out = [];
  let last = 0;
  for (const match of String(text).matchAll(ID_RE)) {
    if (!state.names[match[1]]) continue;
    out.push(text.slice(last, match.index));
    out.push(h("a", { class: `ref kind-${state.names[match[1]].kind}`, href: nodeHref(match[1]) }, match[1]));
    last = match.index + match[1].length;
  }
  out.push(text.slice(last));
  return out;
}

// A text as Markdown is read: paragraphs, and a run of `- ` lines as a list.
function paragraphs(text) {
  return String(text).split(/\n\s*\n/).map((part) => {
    const lines = part.split("\n").map((l) => l.trim()).filter(Boolean);
    if (lines.length && lines.every((l) => l.startsWith("- "))) {
      return h("ul", {}, lines.map((l) => h("li", {}, linkify(l.slice(2)))));
    }
    if (lines.length && lines.every((l) => /^\d+\.\s/.test(l))) {
      return h("ol", {}, lines.map((l) => h("li", {}, linkify(l.replace(/^\d+\.\s+/, "")))));
    }
    if (lines.length > 1 && lines.every((l) => l.startsWith("|")) && /^\|[\s:|-]+\|$/.test(lines[1])) {
      const cells = (l) => l.replace(/^\||\|$/g, "").split(/(?<!\\)\|/).map((c) => c.trim().replace(/\\\|/g, "|"));
      return h("div", { class: "table-frame inline" }, h("table", {},
        h("thead", {}, h("tr", {}, cells(lines[0]).map((c) => h("th", {}, c)))),
        h("tbody", {}, lines.slice(2).map((l) => h("tr", {}, cells(l).map((c) => h("td", {}, linkify(c))))))));
    }
    return h("p", {}, linkify(lines.join(" ").replace(/^\\(#+ )/, "$1")));
  });
}

const counted = (n, one, many) => `${n} ${n === 1 ? one : many}`;

// What moved between two values: the words they share said once, plain, and only the words between marked --
// struck out what went, underlined what came. Anything not a text, both whole.
function moved(was, now) {
  if (Array.isArray(was) || Array.isArray(now)) {          // a table: the lines it lost and the lines it gained
    const line = (r) => (r && typeof r === "object" ? Object.values(r).join(" | ") : String(r));
    const before = (was || []).map(line), after = (now || []).map(line);
    return h("span", { class: "lines" },
      before.filter((l) => !after.includes(l)).map((l) => h("div", {}, h("del", {}, "− " + l))),
      after.filter((l) => !before.includes(l)).map((l) => h("div", {}, h("ins", {}, "+ " + l))));
  }
  if (typeof was !== "string" || typeof now !== "string") {
    return [h("del", {}, JSON.stringify(was ?? "")), " → ", h("ins", {}, JSON.stringify(now ?? ""))];
  }
  const a = was.split(/\s+/).filter(Boolean), b = now.split(/\s+/).filter(Boolean);
  let head = 0;
  while (head < Math.min(a.length, b.length) && a[head] === b[head]) head += 1;
  let tail = 0;
  while (tail < Math.min(a.length, b.length) - head && a[a.length - 1 - tail] === b[b.length - 1 - tail]) tail += 1;
  const same = (words) => (words.length ? words.join(" ") + " " : "");
  return [same(a.slice(0, head)), h("del", {}, a.slice(head, a.length - tail).join(" ")), " ",
          h("ins", {}, b.slice(head, b.length - tail).join(" ")), tail ? " " + a.slice(a.length - tail).join(" ") : ""];
}

// A message from the checks marks names with backticks: drawn as code, the rest as text.
function coded(text) {
  return String(text).split("`").map((piece, i) => (i % 2 ? h("code", {}, piece) : piece));
}

function problems() {
  const box = document.getElementById("problems");
  const found = state.summary.problems;
  box.hidden = found.length === 0;
  if (!found.length) return;
  box.replaceChildren(
    h("strong", {}, `${found.length} problem${found.length === 1 ? "" : "s"} in the data`),
    " -- what is shown is the last data that loaded clean.",
    h("ul", {}, found.map((p) => h("li", {}, h("code", {}, p.line ? `${p.file}:${p.line}` : p.file), " ", coded(p.message)))));
}

async function overview() {
  const s = state.summary;
  const total = s.kinds.reduce((sum, k) => sum + k.count, 0);
  const doc = state.names.document ? await get("node/document") : null;
  return [
    h("h1", {}, doc && doc.name ? doc.name : s.title),
    doc && doc.fields.summary ? h("div", { class: "panel text" }, paragraphs(doc.fields.summary),
      h("p", {}, h("a", { href: "#/node/document" }, "The whole document"))) : null,
    h("p", { class: "lead" }, `${total} nodes and ${s.links} links in this specification.`),
    Object.keys(s.stands).length ? h("p", {}, "How the requirements stand on the material: ",
      Object.entries(s.stands).map(([word, count]) => `${count} ${word}`).join(", "), ".") : null,
    s.stale && s.stale.nodes ? h("aside", { class: "stale" }, h("strong", {}, `${s.stale.nodes} nodes are stale`),
      ` -- each stands on something that changed since it was last reviewed. `,
      h("a", { href: "#/stale" }, "See them")) : null,
    s.kinds.some((k) => ["question", "addition"].includes(k.kind) && k.count)
      ? h("aside", { class: "unsettled" }, h("strong", {}, unsettledCount(s)),
        " -- not settled yet. ", h("a", { href: "#/open" }, "See what is open")) : null,
    GROUPS.map(([group, kinds]) => {
      const here = s.kinds.filter((k) => kinds.includes(k.kind) && k.count);
      return here.length ? [h("h2", { class: "part-head" }, icon(PARTS[group].icon), group), cards(here)] : null;
    }),
    s.kinds.some((k) => k.kind === "screen" && k.count) ? [h("h2", { class: "part-head" }, icon("prototype"), "Prototype"),
      h("p", { class: "lead" }, "Every screen drawn, flow by flow. ", h("a", { href: "#/prototypes" }, "See them all"))] : null,
  ];
}

function unsettledCount(s) {
  const count = Object.fromEntries(s.kinds.map((k) => [k.kind, k.count]));
  return [count.question ? counted(count.question, "open question", "open questions") : "",
          count.addition ? counted(count.addition, "addition", "additions") + " not confirmed" : ""]
    .filter(Boolean).join(" and ");
}

function cards(kinds) {
  return h("div", { class: "cards" }, kinds.map((k) =>
    h("a", { class: `card kind-${k.kind}`, href: `#/list/${k.kind}` },
      h("div", { class: "kind-label" }, PLURAL[k.kind] || k.kind),
      h("div", { class: "count" }, k.count),
      h("div", { class: "what" }, k.is))));
}

// The evidence's files, folder by folder: what its menu's Files opens.
async function evidenceIndex() {
  const files = await evidenceFiles();
  return [h("h1", {}, "Evidence files"),
    files ? files.slice(1) : h("p", { class: "empty" }, "No files are kept beside the evidence's nodes.")];
}

// The evidence that is not nodes: captures, each agent's report, the analyses, the scout's report.
async function evidenceFiles() {
  const files = (await get("evidence")).filter((f) => !/\.(png|jpe?g|webp|gif)$/i.test(f));
  if (!files.length) return null;
  const folders = new Map();
  for (const f of files) {
    const folder = f.split("/").slice(1, -1).join("/") || "evidence";
    if (!folders.has(folder)) folders.set(folder, []);
    folders.get(folder).push(f);
  }
  return [h("h2", {}, "Files"),
    h("p", { class: "lead" }, "What was read, kept as text: captures of what cannot be opened where it lives, " +
      "each agent's report, the analyses, the scout's report."),
    [...folders].map(([folder, items]) => h("div", { class: "panel" }, h("div", { class: "kind-label" }, folder),
      h("ul", { class: "files" }, items.map((f) => h("li", {}, h("a", { href: "#/evidence/" + encodeURIComponent(f) },
        f.split("/").pop())))))) ];
}

// A file of the evidence, drawn from its Markdown: headings, lists, tables, code, pictures, links.
async function evidenceFile(path) {
  const response = await fetch("/" + path.split("/").map(encodeURIComponent).join("/"));
  if (!response.ok) throw new Error(`${path}: not found`);
  const text = await response.text();
  const base = path.split("/").slice(0, -1).join("/");
  const body = /\.md$/i.test(path) ? markdown(text, base) : h("pre", { class: "code" }, text);
  const shots = ((text.match(/^- \*\*Screenshots:\*\*\s*(.+)$/m) || [])[1] || "").split(/,\s*/)
    .map((s) => s.trim()).filter((s) => /\.(png|jpe?g|webp)$/i.test(s));
  return [h("div", { class: "crumbs" }, h("a", { href: "#/evidence" }, "Evidence files")),
    h("div", { class: "meta" }, path),
    shots.length ? h("div", { class: "shots" }, shots.map((s) => h("figure", {},
      h("img", { src: "/" + [base, s].join("/"), alt: `${s}, as captured`, loading: "lazy" }),
      h("figcaption", { class: "meta" }, s)))) : null,
    h("div", { class: "panel text document" }, body)];
}

// Markdown, as the evidence's files are written: block by block; inline, bold, code, pictures and links.
function markdown(text, base) {
  const out = [];
  const lines = String(text).replace(/\r\n/g, "\n").split("\n");
  const inline = (s) => {
    const parts = [];
    const re = /!\[([^\]]*)\]\(([^)\s]+)\)|\[([^\]]+)\]\(([^)\s]+)\)|`([^`]+)`|\*\*([^*]+)\*\*/g;
    let last = 0;
    for (const m of s.matchAll(re)) {
      parts.push(linkify(s.slice(last, m.index)));
      if (m[2] !== undefined) parts.push(h("img", { src: resolve(m[2]), alt: m[1], loading: "lazy" }));
      else if (m[4] !== undefined) parts.push(h("a", { href: target(m[4]) }, m[3]));
      else if (m[5] !== undefined) parts.push(h("code", {}, m[5]));
      else parts.push(h("strong", {}, linkify(m[6])));
      last = m.index + m[0].length;
    }
    parts.push(linkify(s.slice(last)));
    return parts;
  };
  const resolve = (src) => /^[a-z]+:/i.test(src) ? src : "/" + [base, src].join("/").replace(/\/\.\//g, "/");
  const target = (href) => /^[a-z]+:/i.test(href) ? href
    : /\.md(#.*)?$/i.test(href) ? "#/evidence/" + encodeURIComponent([base, href.split("#")[0]].join("/")) : resolve(href);
  for (let i = 0; i < lines.length;) {
    const line = lines[i];
    if (!line.trim()) { i += 1; continue; }
    const fence = line.match(/^```/);
    if (fence) {
      const body = [];
      for (i += 1; i < lines.length && !/^```/.test(lines[i]); i += 1) body.push(lines[i]);
      out.push(h("pre", { class: "code" }, body.join("\n")));
      i += 1;
      continue;
    }
    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) { out.push(h("h" + Math.min(heading[1].length + 1, 5), {}, inline(heading[2]))); i += 1; continue; }
    const block = [];
    while (i < lines.length && lines[i].trim() && !/^(#{1,4})\s|^```/.test(lines[i])) { block.push(lines[i]); i += 1; }
    if (block.every((l) => /^\s*[-*] /.test(l) || /^\s{2,}\S/.test(l))) {
      out.push(h("ul", {}, block.filter((l) => /^\s*[-*] /.test(l)).map((l) => h("li", {}, inline(l.replace(/^\s*[-*] /, ""))))));
    } else if (block.every((l) => /^\d+\.\s/.test(l))) {
      out.push(h("ol", {}, block.map((l) => h("li", {}, inline(l.replace(/^\d+\.\s+/, ""))))));
    } else if (block.length > 1 && block.every((l) => l.trim().startsWith("|")) && /^\|[\s:|-]+\|$/.test(block[1].trim())) {
      const cells = (l) => l.trim().replace(/^\||\|$/g, "").split(/(?<!\\)\|/).map((c) => c.trim().replace(/\\\|/g, "|"));
      out.push(h("div", { class: "table-frame inline" }, h("table", {},
        h("thead", {}, h("tr", {}, cells(block[0]).map((c) => h("th", {}, inline(c))))),
        h("tbody", {}, block.slice(2).map((l) => h("tr", {}, cells(l).map((c) => h("td", {}, inline(c)))))))));
    } else {
      out.push(h("p", {}, block.flatMap((l, n) => (n ? [h("br"), inline(l)] : [inline(l)]))));
    }
  }
  return out;
}

async function list(kind) {
  const rows = await get(`nodes?kind=${encodeURIComponent(kind)}`);
  const spec = state.grammar.kinds[kind];
  if (!spec) throw new Error(`${kind}: no such kind`);
  const isRequirement = kind === "requirement";
  const stands = isRequirement || kind === "rule";
  const body = h("tbody");
  const draw = (filter) => {
    const needle = filter.trim().toLowerCase();
    body.replaceChildren(...rows.filter((r) => !needle || `${r.id} ${r.name || ""}`.toLowerCase().includes(needle))
      .map((r) => h("tr", {},
        h("td", {}, chip(r.id)),
        h("td", {}, h("a", { href: nodeHref(r.id) }, r.name || "")),
        isRequirement ? h("td", {}, r.priority ? h("span", { class: `badge ${r.priority}` }, r.priority) : "") : null,
        isRequirement ? h("td", { class: "num" }, r.parts) : null,
        stands ? h("td", {}, r.backed) : null,
        h("td", { class: "num wide" }, r.links),
        h("td", { class: "num wide" }, r["linked from"]))));
  };
  draw("");
  return [
    h("h1", {}, PLURAL[kind] || kind),
    h("p", { class: "lead" }, `${rows.length} ${rows.length === 1 ? kind : (PLURAL[kind] || kind).toLowerCase()}: ${spec.is}.`),
    h("input", { class: "filter", type: "search", placeholder: "Filter by ID or name", "aria-label": "Filter",
                 oninput: (e) => draw(e.target.value) }),
    h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "ID"), h("th", {}, "Name"),
        isRequirement ? h("th", {}, "Priority") : null, isRequirement ? h("th", { class: "num" }, "Criteria") : null,
        stands ? h("th", {}, "Backed") : null,
        h("th", { class: "num wide" }, "Links"), h("th", { class: "num wide" }, "Linked from"))),
      body)),
  ];
}

function grouped(links) {
  const groups = new Map();
  for (const link of links) {
    if (!groups.has(link.rel)) groups.set(link.rel, []);
    groups.get(link.rel).push(link);
  }
  if (!groups.size) return h("p", { class: "empty" }, "None.");
  return h("div", { class: "links" }, [...groups].map(([rel, items]) => [
    h("div", { class: "rel" }, rel),
    h("div", { class: "ids" }, items.map((l) => chip(l.id))),
  ]));
}

async function node(id) {
  const n = await get(`node/${encodeURIComponent(id)}`);
  const f = n.fields;
  const declared = (state.grammar.kinds[n.kind] || {}).texts || [];
  const titled = Object.fromEntries(declared.map((t) => [t.as, t.title]));
  const texts = [...declared.map((t) => t.as), ...Object.keys(TEXTS)].filter((key, i, all) => f[key] && all.indexOf(key) === i);
  const titleOf = (key) => titled[key] || TEXTS[key] || key;
  const tables = Object.entries(f).filter(([, value]) => Array.isArray(value) && value.length && typeof value[0] === "object" && !value[0].answer);
  const plain = Object.entries(f).filter(([key, value]) => key !== "name" && key !== "actions" && !texts.includes(key) && !Array.isArray(value));
  const up = n.parent
    ? h("a", { href: nodeHref(n.parent.id) }, `${n.parent.id} ${n.parent.name || ""}`)
    : n.kind === "document" ? h("a", { href: "#/" }, "Overview")
    : h("a", { href: `#/list/${n.kind}` }, PLURAL[n.kind] || n.kind);
  const parts = [
    h("div", { class: "crumbs" }, up),
    h("div", { class: `kind-label kind-${n.kind}` }, n.kind),
    h("h1", {}, n.kind === "document" ? (n.name || "The document") : n.name ? `${n.id} ${n.name}` : n.id),
    h("div", { class: "meta" }, `${n.file}:${n.line} · fingerprint ${n.fingerprint}`),
    h("div", { class: "actions-row node-ways" },
      waysOf([...pictureWays(n.id), ["matrix", "Matrix: all its links", mxNode(n.id)]]),
      n.kind === "screen" ? waysOf([["prototype", "Prototype: open it", `#/prototype/${encodeURIComponent(n.id)}`]]) : null,
      h("span", { class: "live-seg" }, h("button", { type: "button", class: "mx-tool", title: "Request a change", "aria-label": "Request a change",
                                                     onclick: () => requestChange(n.id, n.name) }, icon("request")))),
  ];
  if (n.stale && n.stale.length) {
    parts.push(h("aside", { class: "stale" },
      h("strong", {}, `Stale: ${n.id} stands on ${n.stale.length === 1 ? "something" : n.stale.length + " things"} that changed since it was last reviewed.`),
      n.stale.map((s) => h("div", { class: "owed" },
        h("div", {}, chip(s.on), ` changed (${s.link}):`),
        h("dl", { class: "fields moved" }, Object.keys({ ...s.was, ...s.now }).filter((k) =>
          JSON.stringify(s.was[k]) !== JSON.stringify(s.now[k])).map((k) =>
          [h("dt", {}, k), h("dd", {}, moved(s.was[k], s.now[k]))])))),
      h("p", { class: "meta" }, `Read it against what changed, then: spec.py do confirm ${n.id}`)));
  }
  if (n.unsettled && n.unsettled.length) {
    parts.push(h("aside", { class: "unsettled" },
      h("strong", {}, `Not settled: ${counted(n.unsettled.length, "question or addition", "questions and additions")} stand on ${n.id}.`),
      h("ul", {}, n.unsettled.map((u) => h("li", {}, chip(u.id), ` ${u.kind === "addition" ? "added" : "asks"}`,
        u.on.some((o) => o !== n.id) ? [" on ", u.on.map((o) => chip(o))] : "", ": ", u.name || "")))));
  }
  if (n.opens) {
    parts.push(h("p", { class: "actions-row" }, h("a", { class: "button", href: "#/evidence/" + encodeURIComponent(n.opens) },
      `Open ${n.opens.split("/").pop()}, where it was read`)));
  }
  if (n.kind === "component") {
    parts.push(h("h2", {}, "Drawn"), frame(`/prototype/components/${encodeURIComponent(n.id)}.html`, "drawings",
      `The variants of ${n.id}, drawn`));
  }
  let diagram = n.kind === "flow";                // a flow's diagram, drawn where its Diagram or its Steps come first
  if (n.kind === "flow") parts.push(...await flowStory(n));   // its story and what it carries, first
  for (const key of texts) {
    if (diagram && (key === "diagram" || key === "steps")) {
      const drawn = flowMap(n);
      if (drawn) parts.push(h("h2", {}, "Diagram"), drawn);
      diagram = false;
    }
    if (n.kind === "flow" && key === "diagram") continue;
    if (n.kind === "foundation" && key === texts[0]) {   // its tables, with what each row looks like
      parts.push(h("h2", {}, titleOf(key)), ...foundationBody(f[key]));
      continue;
    }
    parts.push(h("h2", {}, titleOf(key)), h("div", { class: "panel text" }, paragraphs(f[key])));
  }
  for (const [key, rows] of tables) {
    const columns = Object.keys(rows[0]).filter((c) => c !== "line");
    parts.push(h("h2", {}, key[0].toUpperCase() + key.slice(1)), h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, columns.map((c) => h("th", {}, c)))),
      h("tbody", {}, rows.map((r) => h("tr", {}, columns.map((c) => h("td", {}, linkify(String(r[c] || ""))))))))));
  }
  if (plain.length) {
    parts.push(h("h2", {}, "Fields"), h("div", { class: "panel" },
      h("dl", { class: "fields" }, plain.map(([key, value]) => [h("dt", {}, key), h("dd", {}, linkify(String(value)))]))));
  }
  if (n.parts.length && (n.kind === "screen" || n.kind === "component")) {
    const body = rowsTable(n.parts, n.kind === "screen" ? "Element" : "Part");
    parts.push(h("h2", {}, n.kind === "screen" ? "Elements" : "Parts"), body.table);
    if (n.kind === "screen") {
      const preview = frame(`/prototype/${encodeURIComponent(n.id)}.html`, "preview", `The prototype of ${n.id}`);
      body.onHover((number) => mark(preview.querySelector("iframe"), number));
      parts.push(h("h2", {}, "Prototype"), preview);
    }
  } else if (n.parts.length) {
    parts.push(h("h2", {}, n.kind === "requirement" ? "Accepted when" : "Parts"),
      h("div", { class: "panel" }, h("ol", { class: "parts" },
        n.parts.map((p) => h("li", { id: p.id }, chip(p.id), h("div", {}, linkify(p.says)))))));
  }
  if (f.actions) {
    const word = { yes: "may", no: "may not", "?": "not known" };
    parts.push(h("h2", {}, "What they may do"), h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Answer"), h("th", {}, "About"), h("th", {}, "Action"))),
      h("tbody", {}, f.actions.map((a) => h("tr", {},
        h("td", {}, h("span", { class: `answer ${a.answer === "?" ? "maybe" : a.answer}` }, word[a.answer])),
        h("td", {}, chip(a.about)),
        h("td", {}, a.action)))))));
  }
  parts.push(h("div", { class: "two" },
    h("div", {}, h("h2", {}, "Links"), h("div", { class: "panel" }, grouped(n.links))),
    h("div", {}, h("h2", {}, "Linked from"), h("div", { class: "panel" }, grouped(n.back)))));
  return parts.concat(await changesOf(n));
}

// What changed in a node, newest first: from the change log.
async function changesOf(n) {
  const parts = [];
  const told = await get(`history?id=${encodeURIComponent(n.id)}`);
  parts.push(h("h2", {}, "History"), told.length ? h("ol", { class: "history" }, told.slice().reverse().map((entry) =>
    h("li", {},
      h("div", { class: "when" }, `${entry.at.replace("T", " ").replace("Z", "")} · ${entry.who}`,
        entry.because ? h("span", { class: "why" }, ` -- because ${entry.because}`) : null),
      h("ul", {}, entry.changes.map((c) => h("li", {}, chip(c.id), " ", c.change,
        c.change === "changed" && c.fields ? h("dl", { class: "fields moved" }, Object.entries(c.fields).map(([k, [was, now]]) =>
          [h("dt", {}, k), h("dd", {}, moved(was, now))])) : null,
        c.tied ? h("div", { class: "meta" }, "tied: " + c.tied.join(", ")) : null,
        c.untied ? h("div", { class: "meta" }, "untied: " + c.untied.join(", ")) : null))))))
    : h("p", { class: "empty" }, "No change is logged for it yet."));
  return parts;
}

// A frame for a page the server draws in the product's look: as tall as what it holds, once it has loaded.
// A frame shows what it holds whole, with no scrollbar of its own: the page scrolls. A sheet sizes its frames itself.
function frame(src, kind, title) {
  const whole = kind === "preview" && !SHEET;
  const iframe = h("iframe", { src, title, class: `frame ${kind}`, loading: "lazy", scrolling: whole ? "no" : null });
  iframe.addEventListener("load", () => {
    try {
      const page = iframe.contentDocument.documentElement;
      if (kind === "drawings") iframe.style.height = `${page.scrollHeight + 4}px`;
      if (!whole) return;
      const fit = () => { iframe.style.height = `${page.scrollHeight}px`; };
      fit();
      new ResizeObserver(fit).observe(iframe.contentDocument.body);   // what comes later, a picture or a font, makes it taller
    } catch (error) { /* a frame it cannot read keeps its height */ }
  });
  return h("div", { class: `frame-box ${kind}` }, iframe);
}

// Each element of a screen, or part of a component, as a row: its number, what it is, and its links by column.
function rowsTable(rows, label) {
  const hovers = [];
  const table = h("div", { class: "table-frame" }, h("table", { class: "rows" },
    h("thead", {}, h("tr", {}, h("th", {}, "#"), h("th", {}, label), h("th", { class: "wide" }, "Kind"),
      h("th", {}, "Component"), h("th", {}, "Shows"), h("th", { class: "wide" }, "About"), h("th", { class: "wide" }, "Leads to"))),
    h("tbody", {}, rows.map((p) => {
      const by = (rel) => p.links.filter((l) => l.rel === rel).map((l) => chip(l.id));
      const number = p.id.split(".").pop();
      return h("tr", { onmouseenter: () => hovers.forEach((f) => f(number)), onmouseleave: () => hovers.forEach((f) => f(null)) },
        h("td", {}, chip(p.id, number)),
        h("td", {}, h("a", { href: nodeHref(p.id) }, p.fields.name || p.id)),
        h("td", { class: "wide" }, p.fields.is || ""),
        h("td", {}, by("is")), h("td", {}, by("shows")), h("td", { class: "wide" }, by("about")),
        h("td", { class: "wide" }, by("leads to")));
    }))));
  return { table, onHover: (f) => hovers.push(f) };
}

// Mark one element in a prototype's frame, or none: what the reader points at in a table, outlined in the page.
function mark(iframe, number) {
  try {
    const page = iframe.contentDocument;
    for (const el of page.querySelectorAll(".spec-marked")) el.classList.remove("spec-marked");
    if (!page.getElementById("spec-mark-style")) {
      page.head.append(Object.assign(page.createElement("style"), { id: "spec-mark-style",
        textContent: ".spec-marked { outline: 3px solid #2f5bd3 !important; outline-offset: 3px; }" }));
    }
    if (number === null) return;
    const found = page.querySelectorAll(`[data-el="${number}"]`);
    found.forEach((el) => el.classList.add("spec-marked"));
    if (found[0]) {                               // into sight inside the frame only: scrollIntoView would move the
      const win = iframe.contentWindow;           // page around the frame too, away from the row under the pointer
      const at = found[0].getBoundingClientRect();
      if (at.top < 0 || at.bottom > win.innerHeight) win.scrollTo({ top: win.scrollY + at.top - win.innerHeight / 3 });
    }
  } catch (error) { /* not loaded yet */ }
}

// ---- the prototype, as a tool: a toolbar, the screen running full size, and an inspector on the element picked
// The toolbar picks the view -- the look, or the wireframe with every element marked -- whether the look marks what
// is under the pointer, the screen, what it shows (a state, or a variant), and its width. Each is sent to the frame,
// which runtime/live.js reads, and kept in the address; a link followed inside the prototype moves the toolbar with
// it. A mark clicked opens the inspector: the element's row and what it stands on, each a link, and its box and its
// text as measured, beside the token that says each value. Escape or × closes it; ↑ and ↓ step out to the element
// around it and in to the first inside it.
const tool = { current: null, nodes: new Map(), tokens: null, wired: false };
const PROTO_FOLDED = "specs-builder-2.proto-folded";             // "1" while the prototype has its bars folded away
const FOLDED = "specs-builder-2.inspector";              // the inspector's sections this browser folded

const held = (id) => tool.nodes.has(id) ? Promise.resolve(tool.nodes.get(id))
  : get(`node/${encodeURIComponent(id)}`).then((n) => { tool.nodes.set(id, n); return n; });

function wireTool() {
  tool.wired = true;
  window.addEventListener("message", (e) => {
    const t = tool.current;
    if (t && t.frame.isConnected && e.source === t.frame.contentWindow) t.message(e.data || {});
  });
  document.addEventListener("keydown", (e) => {
    const t = tool.current;
    if (t && t.frame.isConnected) t.key(e);
  });
}

// Every screen drawn, flow by flow as the prototype is walked, then the screens no flow passes.
async function gallery() {
  const p = await get("prototypes");
  const thumb = (sc) => h("a", { class: "thumb", href: `#/prototype/${encodeURIComponent(sc.id)}` },
    h("div", { class: "thumb-frame" }, sc.drawn
      ? h("iframe", { src: `/prototype/${encodeURIComponent(sc.id)}.html`, title: `The prototype of ${sc.id}`, loading: "lazy", tabindex: "-1" })
      : h("p", { class: "empty" }, "Not drawn yet")),
    h("div", { class: "thumb-label" }, `${sc.id} ${sc.name}`));
  const row = (screens) => h("div", { class: "gallery" }, screens.map(thumb));
  if (!p.flows.length && !p.elsewhere.length) return [h("h1", {}, "Every screen drawn"), h("p", { class: "empty" }, "No screen is drawn yet.")];
  return [h("h1", {}, "Every screen drawn"),
    p.flows.filter((f) => f.screens.length).map((f) => [h("h2", {}, `${f.id} ${f.name}`),
      f.user ? h("p", { class: "flow-user" }, f.user) : null, row(f.screens)]),
    p.elsewhere.length ? [h("h2", {}, "In no flow"), row(p.elsewhere)] : null];
}

async function prototype(id) {
  if (!tool.wired) wireTool();
  const screens = Object.entries(state.names).filter(([, n]) => n.kind === "screen")
    .map(([sid, n]) => ({ id: sid, name: n.name || "" }))
    .sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
  if (!screens.length) return [h("h1", {}, "Prototype"), h("p", { class: "empty" }, "No screen is drawn yet.")];
  if (!screens.some((sc) => sc.id === id)) id = screens[0].id;
  const asked = new URLSearchParams(location.hash.split("?")[1] || "");
  if (!tool.tokens) tool.tokens = get("design").then((d) => d.tokens).catch(() => []);
  const [first, tokens] = await Promise.all([held(id), tool.tokens]);
  const folded = new Set((() => { try { return (localStorage.getItem(FOLDED) || "").split(",").filter(Boolean); } catch (e) { return []; } })());

  const t = { screen: { id, name: first.name || "" }, node: first, picked: null, loading: id, kept: false };
  tool.current = t;
  const select = (options, value, onchange) => h("select", { onchange },
    options.map(([v, text]) => h("option", { value: v, selected: v === value ? true : null }, text)));
  const group = (label, control) => h("label", { class: "live-group" }, h("span", { class: "live-label" }, label), control);
  const viewPick = select([["look", "look"], ["wireframe", "wireframe"]], asked.get("view") === "wireframe" ? "wireframe" : "look", changed);
  const marksPick = select([["hover", "on hover"], ["off", "off"]], asked.get("marks") === "off" ? "off" : "hover", changed);
  const screenPick = select(screens.map((sc) => [sc.id, `${sc.id} · ${sc.name}`]), id, () => go(screenPick.value));
  const showPick = h("select", { onchange: changed });
  let width = WIDTHS[asked.get("width")] !== undefined ? asked.get("width") : "desktop";
  const widths = h("span", { class: "live-seg" });
  const reset = h("button", { type: "button", class: "live-button", hidden: true, onclick: () => say({ reset: true }) }, "Reset the sample data");
  const docLink = h("a", {}, "Its specification");
  const alone = h("a", { target: "_blank", rel: "noopener" }, "Open alone");
  const frame = h("iframe", { class: "live-frame", title: "The prototype" });
  t.frame = frame;
  const facts = h("div", { class: "live-facts" });
  const inspector = h("aside", { class: "live-inspector", hidden: true, "aria-label": "The inspector" },
    h("div", { class: "live-inspector-head" }, h("span", { class: "live-label" }, "Inspector"),
      h("button", { type: "button", "aria-label": "Close the inspector", onclick: close }, "×")), facts);
  const body = h("div", { class: "live-body" }, h("div", { class: "live-frame-box" }, frame), inspector);

  // what Show says: "state:failing" is a state, "as:draft" a variant in the normal state
  function shown() {
    const [kind, word] = (showPick.value || "state:normal").split(":");
    return kind === "as" ? { state: "normal", as: word } : { state: word || "normal", as: "" };
  }
  function said() {
    marksPick.disabled = viewPick.value === "wireframe";           // the wireframe marks every element
    return { ...shown(), view: viewPick.value, marks: marksPick.value };
  }
  function say(what) { if (frame.contentWindow) frame.contentWindow.postMessage({ ...what, live: true }, "*"); }
  function query(extra) {
    const was = shown(), q = new URLSearchParams();
    if (was.state !== "normal") q.set("state", was.state);
    if (was.as) q.set("as", was.as);
    if (viewPick.value === "wireframe") q.set("view", "wireframe");
    if (marksPick.value === "hover") q.set("marks", "hover");
    for (const [k, v] of Object.entries(extra || {})) if (v) q.set(k, v);
    return q.toString();
  }
  // the address says what is shown: #/prototype/SC2?show=failing&view=wireframe&el=3, without drawing the view again
  function remember() {
    const q = new URLSearchParams();
    const was = shown();
    if (was.state !== "normal" || was.as) q.set("show", was.as || was.state);
    if (viewPick.value === "wireframe") q.set("view", "wireframe");
    if (marksPick.value === "off") q.set("marks", "off");
    if (width !== "desktop") q.set("width", width);
    if (t.picked) q.set("el", t.picked.el);
    const hash = `#/prototype/${encodeURIComponent(t.screen.id)}${q.toString() ? "?" + q : ""}`;
    if (location.hash !== hash) history.replaceState(null, "", hash);
    docLink.href = nodeHref(t.screen.id);
    alone.href = `/prototype/${encodeURIComponent(t.screen.id)}.html${query() ? "?" + query() : ""}`;
    tool.shown = query();
  }
  function changed() { say(said()); remember(); }
  function drawWidths() {
    widths.replaceChildren(...Object.keys(WIDTHS).map((w) => h("button", { type: "button", class: `live-button${w === width ? " on" : ""}`,
      "aria-pressed": String(w === width), onclick: () => { width = w; drawWidths(); remember(); } }, w)));
    frame.style.width = WIDTHS[width] ? `${WIDTHS[width]}px` : "";
    body.classList.toggle("narrow", !!WIDTHS[width]);
  }
  function load(sid, extra) {
    t.loading = sid;
    frame.src = `/prototype/${encodeURIComponent(sid)}.html${query(extra) ? "?" + query(extra) : ""}`;
  }
  function go(sid) {
    t.picked = null;
    showInspector();
    showPick.value = "state:normal";
    load(sid);
  }
  // Show holds the states and the variants this screen's markup has, and no other's
  function offer(want) {
    let page;
    try { page = frame.contentDocument; } catch (e) { return; }
    const words = (...attrs) => [...new Set(attrs.flatMap((a) => [...page.querySelectorAll(`[${a}]`)].flatMap((el) =>
      el.getAttribute(a).split(/[\s,]+/))).filter(Boolean))].sort();
    const main = page.querySelector("[data-prototype]");
    const own = (a) => (main && main.getAttribute(a) || "").split(/\s+/).filter(Boolean);
    const states = [...new Set([...words("data-when", "data-unless"), ...own("data-states")])].filter((w) => w !== "normal");
    const variants = [...new Set([...words("data-as", "data-unless-as"), ...own("data-variants")])];
    showPick.replaceChildren(h("optgroup", { label: "State" }, h("option", { value: "state:normal" }, "normal"),
      states.map((w) => h("option", { value: `state:${w}` }, w))),
      variants.length ? h("optgroup", { label: "As" }, variants.map((w) => h("option", { value: `as:${w}` }, w.replace(/-/g, " ")))) : null);
    const value = want.word ? (states.includes(want.word) ? `state:${want.word}` : `as:${want.word}`)
      : want.as ? `as:${want.as}` : `state:${want.state || "normal"}`;
    showPick.value = [...showPick.options].some((o) => o.value === value) ? value : "state:normal";
  }
  // the names the frame puts beside its marks: this screen's elements, and the parts of the components on it
  async function names() {
    const out = {};
    for (const p of t.node.parts || []) out[p.id.split(".").pop()] = p.fields.name || "";
    let page;
    try { page = frame.contentDocument; } catch (e) { return out; }
    const components = [...new Set([...page.querySelectorAll("[data-part]")].map((el) => el.getAttribute("data-part").split(".")[0]))];
    for (const c of await Promise.all(components.map((cid) => held(cid).catch(() => null)))) {
      for (const p of (c && c.parts) || []) out[p.id] = p.fields.name || "";
    }
    t.names = out;
    return out;
  }
  // the frame is on a screen: the toolbar, the links and the address follow it
  async function at(what) {
    const page = (what.page || "").split("?")[0];
    if (t.loading && page !== `${t.loading}.html`) return;      // a frame on its way out, not the page asked for
    t.loading = "";
    if (what.screen !== t.screen.id) {
      t.node = await held(what.screen);
      t.screen = { id: what.screen, name: t.node.name || "" };
      if (t.picked && t.picked.screen !== what.screen) t.picked = null;
    }
    screenPick.value = t.screen.id;
    named();                                      // the folded strip's name follows the screen too
    const q = new URLSearchParams((what.page || "").split("?")[1] || "");
    offer(t.word ? { word: t.word } : { state: q.get("state") || shown().state, as: q.get("as") || (q.get("state") ? "" : shown().as) });
    t.word = "";
    reset.hidden = !what.kept;
    say({ ...said(), names: await names() });
    showInspector();
    remember();
  }
  function rowOf(ref) {
    if (/^C\d+\.\d+$/.test(ref)) {
      const c = tool.nodes.get(ref.split(".")[0]);
      return c ? (c.parts || []).find((p) => p.id === ref) : null;
    }
    return (t.node.parts || []).find((p) => p.id === `${t.screen.id}.${ref}`);
  }
  const nameOf = (ref) => (t.names && t.names[ref]) || "";

  // ---- the inspector
  function section(key, title, content) {
    if (!content) return null;
    const open = !folded.has(key);
    const inner = h("div", { class: "live-sec-body", hidden: open ? null : true }, content);
    const button = h("button", { type: "button", "aria-expanded": String(open), onclick: () => {
      const now = button.getAttribute("aria-expanded") !== "true";
      button.setAttribute("aria-expanded", String(now));
      inner.hidden = !now;
      if (now) folded.delete(key); else folded.add(key);
      try { localStorage.setItem(FOLDED, [...folded].join(",")); } catch (e) { /* kept for this page alone */ }
    } }, title);
    return h("section", { class: "live-sec" }, h("h3", {}, button), inner);
  }
  function pairs(list) {
    const shown = list.filter(([, v]) => v !== null && v !== undefined && v !== "" && !(Array.isArray(v) && !v.length));
    return shown.length ? h("dl", {}, shown.map(([k, v]) => [h("dt", {}, k), h("dd", {}, v)])) : null;
  }
  const num = (text) => h("span", { class: "num" }, text);
  function tokenOf(type, word, value) {
    const same = tokens.filter((tk) => tk.type === type);
    const own = same.filter((tk) => `${tk.group || ""} ${tk.name}`.toLowerCase().includes(word));
    if (!own.length || !value) return null;
    const found = [...own, ...same].find((tk) => String(tk.value).toLowerCase() === String(value).toLowerCase());
    return found ? h("span", { class: "token", title: String(found.value) }, found.name) : h("span", { class: "token off" }, "no token");
  }
  function hex(value) {
    const m = /^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)$/.exec(value || "");
    if (!m) return "";
    if (m[4] !== undefined && parseFloat(m[4]) === 0) return "none";
    return "#" + [m[1], m[2], m[3]].map((n) => (+n).toString(16).padStart(2, "0")).join("");
  }
  function colour(value) {
    const said = hex(value);
    if (!said) return value || "";
    if (said === "none") return "none";
    return [h("span", { class: "swatch-dot", style: `background:${said}` }), num(said), tokenOf("color", "colo", said)];
  }
  function dim(value, word) {
    const said = /^0(px)?$/.test(value) ? "0" : value;
    return [num(said), said === "0" ? null : tokenOf("dimension", word, value)];
  }
  function boxModel(b) {
    const on = (list) => ["t", "r", "b", "l"].map((side, i) => h("i", { class: `bm-${side}` }, String(list[i])));
    return h("div", { class: "bm bm-margin" }, h("b", {}, "margin"), on(b.margin),
      h("div", { class: "bm bm-border" }, h("b", {}, "border"), on(b.border),
        h("div", { class: "bm bm-padding" }, h("b", {}, "padding"), on(b.padding),
          h("div", { class: "bm-content" }, `${Math.round(b.content.width)} × ${Math.round(b.content.height)}`))));
  }
  function inspect(what) {
    const ref = what.el;
    const piece = /^(C\d+)\.(\d+)$/.exec(ref);
    const row = rowOf(ref);
    const f = row ? row.fields : {};
    const name = f.name || nameOf(ref);
    const component = piece ? piece[1] : row && (row.links.find((l) => l.rel === "is") || {}).id;
    const around = what.around || [];
    const linked = (rel) => row ? row.links.filter((l) => l.rel === rel).map((l) => chip(l.id)) : [];
    const b = what.box;
    const keep = facts.scrollTop;
    facts.replaceChildren(
      h("nav", { class: "live-path", "aria-label": "Where it sits" },
        around.map((r, i) => [h("button", { type: "button", title: r, onclick: () => say({ step: "out", by: around.length - i }) },
          nameOf(r) || r), h("span", {}, "›")]),
        h("b", {}, name || ref),
        h("span", { class: "live-path-ways" },
          h("button", { type: "button", disabled: around.length ? null : true, title: "The element around it (↑)",
                        onclick: () => say({ step: "out", by: 1 }) }, "Out"),
          h("button", { type: "button", disabled: what.inner ? null : true, title: `${nameOf(what.inner) || what.inner || ""} (↓)`,
                        onclick: () => say({ step: "in" }) }, "In"))),
      h("header", { class: "live-el" }, h("span", { class: "live-el-no" }, ref),
        h("div", { class: "live-el-text" },
          h("div", { class: "live-el-name" }, row ? h("a", { href: nodeHref(row.id) }, name || `Element ${ref}`) : name || `Element ${ref}`),
          h("div", { class: "live-el-kind" }, [f.is, `${t.screen.id} · ${t.screen.name}`].filter(Boolean).join(" · ")),
          h("nav", { class: "live-el-acts" }, row ? h("a", { href: nodeHref(row.id) }, "Its row") : null,
            component ? h("a", { href: nodeHref(component) }, "Its component") : null,
            h("button", { type: "button", onclick: (e) => copyAddress(e.currentTarget) }, "Copy address")))),
      section("stands", "Stands on", pairs([["Part of", piece ? chip(piece[1]) : null], ["Component", piece ? [] : linked("is")],
        ["Shows", linked("shows")], ["About", linked("about")], ["Leads to", linked("leads to")]])),
      section("says", "Says", pairs([["Shows & does", f.does ? linkify(String(f.does)) : null], ["States", f.states ? linkify(String(f.states)) : null],
        ["Heard as", f["heard as"] || null], ["From", f.from ? linkify(String(f.from)) : null]])),
      b ? section("box", "Box", [boxModel(b), pairs([["Size", num(`${Math.round(b.width)} × ${Math.round(b.height)} px`)],
        ["At", num(`${Math.round(b.left)}, ${Math.round(b.top)} px`)], ["Display", b.display],
        ["Border", b.border.some((n) => n > 0) ? colour(b.borderColor) : null],
        ["Radius", b.radius && b.radius !== "0px" ? dim(b.radius, "radius") : null]])]) : null,
      b ? section("text", "Text", pairs([["Font", (b.font || "").split(",")[0].replace(/["']/g, "").trim()],
        ["Size", [dim(b.size, "font"), " / ", num(b.lineHeight)]], ["Weight", num(b.weight)],
        ["Colour", colour(b.color)], ["Background", colour(b.background)]])) : null,
      h("p", { class: "hint" }, "Click another mark to see that element; ↑ and ↓ move out and in. Rest the pointer on an " +
        "ID to light what it names on the screen. Escape, or ×, closes the inspector."));
    facts.scrollTop = t.shownEl === ref ? keep : 0;    // another element starts at its header; a re-measure stays put
    t.shownEl = ref;
  }
  function showInspector() {
    inspector.hidden = !t.picked;
    if (t.picked) inspect(t.picked);
  }
  function close() {
    t.picked = null;
    say({ el: "" });
    showInspector();
    remember();
  }
  function copyAddress(button) {
    const was = button.textContent;
    navigator.clipboard.writeText(location.href).then(() => {
      button.textContent = "Copied";
      setTimeout(() => { button.textContent = was; }, 1200);
    }).catch(() => { /* the address bar has it */ });
  }
  // an ID in the inspector, under the pointer: the elements on the screen whose rows name it are lit
  let lit = "";
  function light(ref) {
    if (ref === lit) return;
    lit = ref;
    const handles = [];
    if (ref) {
      for (const p of t.node.parts || []) if (p.links.some((l) => l.id === ref)) handles.push(p.id.split(".").pop());
      for (const [cid, c] of tool.nodes) {
        if (/^C\d+$/.test(cid)) for (const p of c.parts || []) if (p.links.some((l) => l.id === ref)) handles.push(p.id);
      }
    }
    say({ light: ref ? { ref, handles } : null });
  }
  facts.addEventListener("mouseover", (e) => { const c = e.target.closest(".chip"); light(c ? c.textContent.trim() : ""); });
  facts.addEventListener("mouseleave", () => light(""));

  t.message = (what) => {
    if (what.live === "at") at(what);
    if (what.live === "pick") {
      t.picked = what.el ? { ...what, screen: t.screen.id } : null;
      showInspector();
      remember();
    }
  };
  t.key = (e) => {
    if (e.key === "Escape" && t.picked) { close(); return; }
    const typing = /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName || "") || e.target.closest(".bar");
    if (t.picked && !typing && !e.altKey && !e.ctrlKey && !e.metaKey && (e.key === "ArrowUp" || e.key === "ArrowDown")) {
      e.preventDefault();
      say({ step: e.key === "ArrowUp" ? "out" : "in" });
    }
  };

  // the first screen: what the address asked for -- a word Show resolves once the page says its states and
  // variants -- and the element it named, picked once the frame is there
  t.word = asked.get("show") || "";
  showPick.replaceChildren(h("option", { value: "state:normal" }, "normal"));
  drawWidths();
  load(id, { el: asked.get("el") || "" });
  remember();
  // Folded: the application's bar and this toolbar out of the way, the screen nearly full height; a strip left with
  // the screen's name and the way back. Kept in the browser, for every screen, until unfolded.
  const stripName = h("span", { class: "live-strip-name" });
  const named = () => { const sc = screens.find((s) => s.id === screenPick.value); stripName.textContent = sc ? `${sc.id} · ${sc.name}` : ""; };
  screenPick.addEventListener("change", named);
  named();
  const fold = (on) => {
    document.documentElement.classList.toggle("proto-folded", on);
    try { localStorage.setItem(PROTO_FOLDED, on ? "1" : ""); } catch (e) { /* kept for this page alone */ }
    (on ? strip : bar).querySelector(".live-fold").focus({ preventScroll: true });
  };
  const bar = h("div", { class: "live-bar" },
    group("View", viewPick), group("Marks", marksPick), h("span", { class: "live-rule" }),
    group("Screen", screenPick), group("Show", showPick), h("span", { class: "live-rule" }),
    group("Width", widths), reset,
    h("span", { class: "live-links" }, docLink, alone),
    h("button", { type: "button", class: "live-fold", title: "Fold the bars away: the screen full height",
                  "aria-label": "Fold the bars away", onclick: () => fold(true) }, icon("chevron")));
  const strip = h("div", { class: "live-strip" }, stripName,
    h("button", { type: "button", class: "live-fold", title: "Show the bars again", "aria-label": "Show the bars again",
                  onclick: () => fold(false) }, icon("chevron")));
  document.documentElement.classList.toggle("proto-folded", (() => { try { return localStorage.getItem(PROTO_FOLDED) === "1"; } catch (e) { return false; } })());
  return h("section", { class: "live-tool", "aria-label": "The prototype" },
    h("h1", { class: "sr-only" }, `The prototype of ${id}`), strip, bar, body);
}

// Every node owing a review: what it stands on that changed, and how.
async function staleList() {
  const owed = await get("stale");
  const by = new Map();
  for (const s of owed) { if (!by.has(s.node)) by.set(s.node, []); by.get(s.node).push(s); }
  return [
    h("h1", {}, "Stale"),
    h("p", { class: "lead" }, by.size ? `${by.size} nodes stand on something that changed since they were last reviewed.`
      : "Nothing is stale: every node was reviewed against what it stands on as it is now."),
    h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Node"), h("th", {}, "Stands on, changed"), h("th", { class: "wide" }, "By"))),
      h("tbody", {}, [...by].map(([node, items]) => h("tr", {},
        h("td", {}, chip(node)), h("td", {}, items.map((s) => chip(s.on))),
        h("td", { class: "wide meta" }, items.map((s) => s.link).join("; "))))))),
  ];
}

// All that is not settled: what the user answers, confirms or decides before the specification is agreed.
// What of the specification the code carries, read from the code: the criteria its tests name, the files that name each.
async function builtView() {
  const b = await get("built");
  if (b.none) return [h("h1", {}, "What is built"),
    h("p", { class: "empty" }, "No code is known to be built from this specification yet. Once there is some, " +
      "spec.py snapshot --target <code> records what it is built from, and where it is.")];
  const shown = b.requirements.filter((r) => r.priority !== "wont");
  const named = shown.reduce((sum, r) => sum + r.criteria.length - r.untested.length, 0);
  const all = shown.reduce((sum, r) => sum + r.criteria.length, 0);
  return [h("h1", {}, "What is built"),
    h("p", { class: "lead" }, `${named} of ${all} criteria are named by a test. Read from ${b.target}: ` +
      `${counted(b["tests read"], "file of tests", "files of tests")} and ${counted(b["code read"], "other file", "other files")} of code.`),
    h("p", { class: "meta" }, "A test counts by naming the criterion it proves, R4.2 or R4_2. This says what the code " +
      "names, not that a test passes."),
    b.whole ? null : h("aside", { class: "unsettled" }, h("strong", {}, counted(b.untested.length, "criterion", "criteria")),
      " no test names yet."),
    h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "ID"), h("th", {}, "Name"), h("th", {}, "Priority"), h("th", {}, "Criteria"),
        h("th", {}, "Tests"), h("th", { class: "wide" }, "Other code"))),
      h("tbody", {}, b.requirements.map((r) => h("tr", {},
        h("td", {}, chip(r.id)), h("td", {}, r.name),
        h("td", {}, r.priority ? h("span", { class: `badge ${r.priority}` }, r.priority) : ""),
        h("td", {}, `${r.criteria.length - r.untested.length} of ${r.criteria.length}`,
          r.priority !== "wont" && r.untested.length ? h("div", { class: "meta built-not" }, "not", r.untested.map((i) => chip(i))) : null),
        h("td", { class: "meta built-files" }, r.tests.join(", ")),
        h("td", { class: "meta built-files wide" }, r.code.join(", "))))))),
    b.unknown.length ? [h("h2", {}, `The code names what the specification has not (${b.unknown.length})`),
      h("div", { class: "table-frame" }, h("table", {},
        h("thead", {}, h("tr", {}, h("th", {}, "ID"), h("th", {}, "Files"))),
        h("tbody", {}, b.unknown.map((u) => h("tr", {}, h("td", {}, u.id), h("td", { class: "meta built-files" }, u.files.join(", "))))))),
    ] : null];
}

async function openList() {
  const o = await get("open");
  if (!o.questions) return [h("h1", {}, "Open"), h("p", { class: "error" }, "The data has problems: they come first.")];
  const plain = (items) => items.length ? h("div", { class: "ids" }, items.map((n) => chip(n.id))) : h("p", { class: "empty" }, "None.");
  return [
    h("h1", {}, "Open"),
    h("p", { class: "lead" }, "All that is not settled yet, the most deciding first. Nothing here stops a build, " +
      "but the specification is agreed only once the questions left are for engineering and nothing else is listed."),
    o.asked.length ? [h("h2", {}, `Waiting in the inbox (${o.asked.length})`),
      h("p", { class: "meta" }, "Changes requested here, and questions sent back by whoever builds from the specification -- " +
        "never part of the data. Claude Code takes each up, and closes it."),
      h("div", { class: "table-frame" }, h("table", {},
        h("thead", {}, h("tr", {}, h("th", {}, "No"), h("th", {}, "From"), h("th", {}, "About"), h("th", {}, "What it asks"))),
        h("tbody", {}, o.asked.map((a) => h("tr", {},
          h("td", { class: "num" }, `#${a.no}`), h("td", {}, a.by, h("div", { class: "meta" }, a.asked)),
          h("td", {}, a.about.map((i) => chip(i))), h("td", {}, a.question))))))] : null,
    h("h2", {}, `Questions (${o.questions.length})`),
    o.questions.length ? h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "ID"), h("th", {}, "Answered by"), h("th", {}, "Question"), h("th", { class: "wide" }, "Touches"))),
      h("tbody", {}, o.questions.map((q) => h("tr", {},
        h("td", {}, chip(q.id)), h("td", {}, q.answers || "nobody named"), h("td", {}, linkify(q.question)),
        h("td", { class: "wide" }, [...q.about, ...q["asked by"].filter((a) => !q.about.includes(a))].map((i) => chip(i)))))))) : h("p", { class: "empty" }, "None."),
    h("h2", {}, `Added, not confirmed (${o.additions.length})`),
    o.additions.length ? h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "ID"), h("th", {}, "Added to"), h("th", {}, "What was added"))),
      h("tbody", {}, o.additions.map((a) => h("tr", {},
        h("td", {}, chip(a.id)),
        h("td", {}, a["added to"].map((i) => chip(i))), h("td", {}, linkify(a.says)))))))
      : h("p", { class: "empty" }, "None."),
    h("h2", {}, "Qualities open"), plain(o["qualities open"]),
    o["qualities missing"].length ? h("p", {}, "Nothing says anything yet of " + o["qualities missing"].join(", ") +
      ": each is a quality to write, with its requirement, none and why, or open.") : null,
    h("h2", {}, "Risks with no mitigation"), plain(o["risks open"]),
    h("h2", {}, "Contradictions unsettled"), plain(o.contradictions),
    h("h2", {}, "Findings that became nothing"), plain(o["findings open"]),
    h("h2", {}, "Requirements and rules on weak ground"), plain(o.weak),
    h("h2", {}, `Documented only (${o.documented.length})`),
    h("p", { class: "meta" }, "Only documents stand behind these -- a help page, a ticket, an older specification -- and " +
      "the product itself was not looked at for them. Each is a claim to check against the product."),
    plain(o.documented),
    h("h2", {}, `To investigate (${o["to investigate"].length})`),
    h("p", { class: "meta" }, "What the skill finds out itself before anyone is asked, the heaviest first: " +
      "3 for each must that leans on it, 1 for each other requirement, 2 more where who may do what is in it."),
    o["to investigate"].length ? h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", { class: "num" }, "Weight"), h("th", {}, "What"), h("th", {}, "Of"),
        h("th", {}, "Says"), h("th", { class: "wide" }, "How"))),
      h("tbody", {}, o["to investigate"].map((r) => h("tr", {}, h("td", { class: "num" }, r.weight), h("td", {}, r.what),
        h("td", {}, chip(r.id)), h("td", {}, linkify(r.says)), h("td", { class: "wide meta" }, r.how))))))
      : h("p", { class: "empty" }, "None."),
    h("h2", {}, "Stale"), o.stale.length ? h("p", {}, h("a", { href: "#/stale" }, counted(o.stale.length, "node", "nodes") + " to read again"))
      : h("p", { class: "empty" }, "None."),
    h("h2", {}, `Notes for a review (${o.words.length})`),
    h("p", { class: "meta" }, "Words a review reads for: a vague word, a technology word that may say how rather than what, " +
      "a statement that opens with none of The, When, While, Where, If. Notes, never refusals."),
    o.words.length ? h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Node"), h("th", {}, "Note"), h("th", {}, "Words"))),
      h("tbody", {}, o.words.map((w) => h("tr", {}, h("td", {}, chip(w.id)), h("td", {}, w.note),
        h("td", {}, w.words.join(", "))))))) : h("p", { class: "empty" }, "None."),
  ];
}

// The design system: the foundations from the tokens, and the components.
async function design() {
  const d = await get("design");
  const colours = d.tokens.filter((t) => t.type === "color" && /^#[0-9a-f]{3,8}$/i.test(String(t.value)));
  const others = d.tokens.filter((t) => !colours.includes(t));
  return [
    h("h1", {}, "Design system"),
    h("p", { class: "lead" }, `${d.tokens.length} tokens and ${d.components.length} components.`),
    h("h2", {}, "Colours"),
    colours.length ? h("div", { class: "swatches" }, colours.map((t) =>
      h("div", { class: "swatch", title: t.about || "" },
        h("span", { class: "chip-colour", style: `background:${t.value}` }),
        h("div", {}, h("div", { class: "swatch-name" }, t.name), h("div", { class: "meta" }, t.value))))) : h("p", { class: "empty" }, "None."),
    h("h2", {}, "Other tokens"),
    others.length ? h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Group"), h("th", {}, "Name"), h("th", {}, "Type"), h("th", {}, "Value"))),
      h("tbody", {}, others.map((t) => h("tr", { title: t.about || "" }, h("td", {}, t.group), h("td", {}, t.name),
        h("td", {}, t.type || ""), h("td", { class: "meta" }, String(t.value))))))) : h("p", { class: "empty" }, "None."),
    h("h2", {}, "Components"),
    h("div", { class: "cards" }, d.components.map((c) =>
      h("a", { class: "card kind-component", href: nodeHref(c.id) },
        h("div", { class: "kind-label" }, c.id),
        h("div", { class: "swatch-name" }, c.name),
        h("div", { class: "what" }, `${counted(c.variants, "variant", "variants")} · ${counted(c.parts, "part", "parts")} · ` +
          `used by ${counted(c.used, "element", "elements")}`)))),
  ];
}

// A view is built whole, away from the page, and only then put in place with the bar and the tree, all in one frame: what is on
// the screen does not move while the next view's data is asked for. A view overtaken by another is never shown.
let routed = 0;

// A node's page: what it is linked to, what stands on it, what connects to it, and all its links; each beside its twin for another tab
const pictureWays = (id) => { const [around, layers, impact] = graphWays(id); return [around, impact, layers]; };
const waysOf = (ways) => h("span", { class: "live-seg" }, ways.map((way) => [wayHere(...way), wayAway(...way)]));

async function route() {
  const [, where, arg, extra] = (location.hash.slice(1).split("?")[0] || "/").split("/");
  const decoded = arg ? decodeURIComponent(arg) : "";
  const turn = ++routed;
  if (where === "matrix" && matrixShowing()) {            // the page stays: only what the address changed is asked for
    await matrixGo(decoded, extra);
    return;
  }
  const parentKind = { criterion: "requirement", element: "screen", part: "component", state: "entity" };
  let active = null;
  try {
    state.summary = await get("summary");
    const { version } = state.summary;
    if (version !== state.namesOf) {                      // every node's name is a large answer: asked when the data has changed
      const names = get("names").then((found) => { state.names = found; state.namesOf = version; });
      if (where === "matrix") names.catch(() => { /* the page has its own names */ });   // it asks for what it shows: they can follow
      else await names;
    }
    if (!state.grammar) state.grammar = await get("grammar");
    const kind = where === "list" ? decoded : where === "group" ? decoded : where === "evidence" ? "Evidence"
      : where === "design" ? "design" : where === "prototype" || where === "prototypes" ? "prototype"
      : where === "help" ? "help"
      : where === "graph" ? "graph"
      : where === "matrix" ? "matrix"
      : where === "node" ? (state.names[decoded] || {}).kind : null;
    active = parentKind[kind] || kind;
    if (!view.firstChild) { nav(active); problems(); }     // the first view of all: nothing to keep, and the bar need not wait
    let content;
    if (!where) content = await overview();
    else if (where === "group") content = await partView(decoded);
    else if (where === "evidence") content = decoded ? await evidenceFile(decoded) : await evidenceIndex();
    else if (where === "help") content = helpView();
    else if (where === "list") content = await list(decoded);
    else if (where === "node") content = await node(decoded);
    else if (where === "graph") content = await graphPage(decoded);
    else if (where === "matrix") content = await matrixPage(decoded, extra);
    else if (where === "prototype") content = await (SHEET ? screenOnSheet(decoded) : prototype(decoded));
    else if (where === "prototypes") content = await gallery();
    else if (where === "design") content = await design();
    else if (where === "stale") content = await staleList();
    else if (where === "open") content = await openList();
    else if (where === "built") content = await builtView();
    else throw new Error(`${location.hash}: no such view`);
    if (turn !== routed) return;
    nav(active);
    drawSide(where, decoded);
    problems();
    view.classList.toggle("fills", (where === "prototype" || where === "matrix" || where === "graph") && !SHEET);
    if (where !== "prototype") document.documentElement.classList.remove("proto-folded");   // folded on its own page only
    forgetCards();
    view.replaceChildren(...withAids(view, where, decoded, content));
    window.scrollTo(0, 0);
  } catch (error) {
    if (turn !== routed) return;
    if (state.summary) { nav(active); drawSide(where, decoded); problems(); }
    view.classList.remove("fills");
    view.replaceChildren(h("h1", {}, "Not found"), h("p", { class: "error" }, error.message),
      h("p", {}, h("a", { href: "#/" }, "Back to the overview")));
  } finally {
    fetchMenu();                                          // after the view: its checks would share the server's time with it
  }
}

window.addEventListener("hashchange", route);
route();
