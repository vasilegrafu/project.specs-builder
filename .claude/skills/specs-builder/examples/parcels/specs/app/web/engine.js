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
// Text as it is written: a block fenced with three backticks stands as it is, blank lines and all.
function paragraphs(text) {
  return String(text).split(/^(```[^\n]*\n[\s\S]*?^```[ \t]*)$/m).flatMap((piece, i) =>
    (i % 2 ? [h("pre", { class: "code" }, h("code", {}, piece.replace(/^```[^\n]*\n/, "").replace(/\n?```[ \t]*$/, "")))] : prose(piece)));
}

function prose(text) {
  return String(text).split(/\n\s*\n/).filter((part) => part.trim()).map((part) => {
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

// words with code in backticks and IDs as links
function spoken(text) {
  return String(text).split("`").map((piece, i) => (i % 2 ? h("code", {}, piece) : linkify(piece)));
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
  const able = await get("capabilities");
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
    able.length ? [h("h2", {}, "What it lets people do"), h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Outcome"), h("th", {}, "Who"), h("th", {}, "Rules"), h("th", {}, "Requirements"), h("th", { class: "wide" }, "Through"))),
      h("tbody", {}, able.map((c) => h("tr", {},
        h("td", {}, c.flow ? chip(c.flow) : null, " ", c.outcome), h("td", {}, c.who.map((i) => chip(i))), h("td", {}, c.rules.map((i) => chip(i))),
        h("td", {}, c.requirements.map((i) => chip(i))), h("td", { class: "wide" }, c.through.map((i) => chip(i))))))))] : null,
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
      h("p", { class: "meta" }, `Read it against what changed, then: spec.py do confirm ${n.id} ${n["owed print"] || ""}`)));
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
    if (n.kind === "foundation" && key === texts[0]) {   // its tables, with what each row looks like, the tokens it names resolved
      parts.push(h("h2", {}, titleOf(key)), ...foundationBody(f[key], n.tokens || {}));
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

// Every node owing a review: what it stands on that changed, and how.
// The print a stale node is confirmed against: the server says it beside each of its stale links
const owedPrint = (items) => (items.find((s) => s["owed print"]) || {})["owed print"] || "";

async function staleList() {
  const owed = await get("stale");
  const by = new Map();
  for (const s of owed) { if (!by.has(s.node)) by.set(s.node, []); by.get(s.node).push(s); }
  return [
    h("h1", {}, "Stale"),
    h("p", { class: "lead" }, by.size ? `${by.size} nodes stand on something that changed since they were last reviewed.`
      : "Nothing is stale: every node was reviewed against what it stands on as it is now."),
    h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Node"), h("th", {}, "Stands on, changed"), h("th", { class: "wide" }, "By"), h("th", {}, "Confirm with"))),
      h("tbody", {}, [...by].map(([node, items]) => h("tr", {},
        h("td", {}, chip(node)), h("td", {}, items.map((s) => chip(s.on))),
        h("td", { class: "wide meta" }, items.map((s) => s.link).join("; ")),
        h("td", { class: "meta" }, h("code", {}, `do confirm ${node} ${owedPrint(items)}`))))))),
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

function gapList(title, items) {
  return items.length ? [h("h3", {}, `${title} (${items.length})`), h("div", { class: "ids" }, items.map((n) => chip(n.id)))] : null;
}

async function openList() {
  const o = await get("open");
  if (!o.questions) return [h("h1", {}, "Open"), h("p", { class: "error" }, "The data has problems: they come first.")];
  const plain = (items) => items.length ? h("div", { class: "ids" }, items.map((n) => chip(n.id))) : h("p", { class: "empty" }, "None.");
  return [
    h("h1", {}, "Open"),
    h("p", { class: "lead" }, "All that is not settled yet, the most deciding first. Nothing here stops a build. " +
      "Most of it holds an agreement, and spec.py ready says which."),
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
    h("h2", {}, `Where the content falls short (${o.faults.length})`),
    h("p", { class: "meta" }, "A claim with nothing under it, a state nobody accounted for, a prototype that draws what the data does not " +
      "hold. Any of it can stand while the work goes on, and all of it goes before the specification is agreed."),
    o.faults.length ? h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Of"), h("th", {}, "What falls short"), h("th", { class: "wide" }, "Where"))),
      h("tbody", {}, o.faults.map((f) => h("tr", {}, h("td", {}, chip(f.id)), h("td", {}, spoken(f.says)),
        h("td", { class: "wide meta" }, `${f.file}${f.line ? ":" + f.line : ""}`.replaceAll("/", "/\u200b")))))))
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
    h("h2", {}, `Prototypes to look at (${o.undrawn.length})`),
    h("p", { class: "meta" }, "What these screens show has changed and their prototypes have not, so a word or a number in them may no " +
      "longer be so; or a value of the look they are drawn with moved in tokens.json. Redraw each, or confirm that it still holds."),
    plain(o.undrawn),
    o.undrawn.some((n) => n["look moved"] && n["look moved"].length) ? h("ul", {}, o.undrawn.filter((n) => n["look moved"] && n["look moved"].length)
      .map((n) => h("li", {}, chip(n.id), " the look moved: ", n["look moved"].map(([name, was, now]) => `${name} ${was} → ${now}`).join("; ")))) : null,
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
    h("h2", {}, "Gaps a review reads"),
    h("p", { class: "meta" }, "Each may be right as it stands: a rule the specification leaves to what exists, a must that lives behind the " +
      "scenes. None of them holds an agreement."),
    gapList("Rules enforced by nothing", o.gaps["rules unenforced"]),
    gapList("Musts nothing shows", o.gaps["musts unshown"]),
    gapList("Musts that show nowhere and enforce no rule", o.gaps["musts tied to nothing"]),
    gapList("Requirements in no flow's story", o.gaps["in no story"]),
    gapList("Endpoints that do not say how they fail", o.gaps["endpoints with no fails"]),
    gapList("Foundations nothing follows", o.gaps["foundations unfollowed"]),
    o.gaps["read in part"].length ? [h("h3", {}, `Material read in part, or not at all (${o.gaps["read in part"].length})`), h("ul", {},
      o.gaps["read in part"].map((m) => h("li", {}, chip(m.id), ` ${m.part}, ${m.read || "not said"}${m.note ? ": " + m.note : ""}`)))] : null,
    o.gaps["not captured"].length ? [h("h3", {}, `Views the walk did not capture (${o.gaps["not captured"].length})`), h("ul", {},
      o.gaps["not captured"].map((v) => h("li", {}, `${v.site} ${v.view} ${v.address}${v.why ? ": " + v.why : ""}`)))] : null,
    h("h2", {}, `Notes for a review (${o.words.length})`),
    h("p", { class: "meta" }, "Words a review reads for: a vague word, a technology word that may say how rather than what, " +
      "a statement that opens with none of The, When, While, Where, If. Notes, never refusals."),
    o.words.length ? h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Node"), h("th", {}, "Note"), h("th", {}, "Words"))),
      h("tbody", {}, o.words.map((w) => h("tr", {}, h("td", {}, chip(w.id)), h("td", {}, w.note),
        h("td", {}, w.words.join(", "))))))) : h("p", { class: "empty" }, "None."),
  ];
}

// Where a token is: the foundations that name it, and the prototypes its value reaches
function tokenPlaces(t) {
  const named = (t["named by"] || []).map((id) => chip(id));
  const reach = t.reaches || [];
  return [named.length ? ["named by ", named] : "named by no foundation",
    reach.length ? [`; reaches ${reach.length}: `, reach.slice(0, 6).map((id) => chip(id)), reach.length > 6 ? ` … ${reach.length - 6} more` : ""] : "; reaches no prototype"];
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
    h("p", { class: "meta" }, "Each value lives in tokens.json alone; a foundation names it, and every prototype it reaches is listed to be looked at when it moves."),
    colours.length ? h("div", { class: "swatches" }, colours.map((t) =>
      h("div", { class: "swatch", title: `${t.variable}${t.about ? ": " + t.about : ""}` },
        h("span", { class: "chip-colour", style: `background:${t.value}` }),
        h("div", {}, h("div", { class: "swatch-name" }, t.name), h("div", { class: "meta" }, t.value),
          h("div", { class: "meta" }, tokenPlaces(t)))))) : h("p", { class: "empty" }, "None."),
    h("h2", {}, "Other tokens"),
    others.length ? h("div", { class: "table-frame" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Group"), h("th", {}, "Name"), h("th", {}, "Type"), h("th", {}, "Value"), h("th", {}, "Named by, reaches"))),
      h("tbody", {}, others.map((t) => h("tr", { title: t.about || "" }, h("td", {}, t.group), h("td", {}, t.name),
        h("td", {}, t.type || ""), h("td", { class: "meta" }, String(t.value)), h("td", { class: "meta" }, tokenPlaces(t))))))) : h("p", { class: "empty" }, "None."),
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
