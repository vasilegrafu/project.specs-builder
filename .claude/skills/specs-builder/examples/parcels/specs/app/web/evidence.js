// The evidence: what was read, by folder and by file, and the Markdown it is kept in, drawn.
"use strict";

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
