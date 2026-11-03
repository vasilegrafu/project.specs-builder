// A foundation's page: what it says, its tables with a column of what each row looks like, drawn from the row's own
// values where they can be -- a colour's swatch and its contrast on white, a text style's sample at its size, weight
// and line height in the typeface the foundation names, the spacing scale as bars, the padding inside a control,
// corners, borders and shadows on small cards, a contrast pair as words on their ground, the focus ring, the signs
// of an icon set. A row that is a rule in words is left as it is. Loaded before engine.js; it draws with engine.js's
// h(), linkify() and paragraphs().
"use strict";

const FD_HEX = /#[0-9a-fA-F]{6}\b/g;
const FD_WEIGHTS = { thin: 100, light: 300, regular: 400, normal: 400, medium: 500, semibold: 600, bold: 700,
                     extrabold: 800, black: 900 };

// A colour a row gives: its first hex, else a word CSS knows as a colour ("teal"); null where it gives none
function fdColour(row) {
  const hex = row.match(FD_HEX);
  if (hex) return hex[0];
  if (typeof CSS === "undefined") return null;
  for (const word of row.toLowerCase().match(/[a-z]+/g) || []) {
    if (word.length > 2 && !FD_WEIGHTS[word] && CSS.supports("color", word) && !["transparent", "currentcolor", "inherit"].includes(word)) return word;
  }
  return null;
}

function fdLum(hex) {
  const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((x) => (x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4));
  return .2126 * c[0] + .7152 * c[1] + .0722 * c[2];
}
const fdRatio = (a, b) => { const x = fdLum(a), y = fdLum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
const fdPx = (text) => [...String(text).matchAll(/(\d+(?:\.\d+)?)\s*px/g)].map((m) => Number(m[1]));

// "0 1px 2px and 0 4px 12px of #111827 at 6%" -> a box-shadow
function fdShadow(text) {
  const colour = (text.match(FD_HEX) || ["#000000"])[0];
  const alpha = Number((text.match(/(\d+(?:\.\d+)?)\s*%/) || [0, 10])[1]) / 100;
  const rgb = [1, 3, 5].map((i) => parseInt(colour.slice(i, i + 2), 16)).join(", ");
  const layers = [...text.matchAll(/(-?\d+(?:px)?)\s+(-?\d+px)\s+(\d+px)(?:\s+(\d+px))?/g)]
    .map((m) => `${m[1].endsWith("px") ? m[1] : m[1] + "px"} ${m[2]} ${m[3]}${m[4] ? " " + m[4] : ""} rgba(${rgb}, ${alpha})`);
  if (layers.length) return layers.join(", ");
  const depths = fdPx(text);
  return depths.map((d) => `0 ${d}px ${d * 3}px rgba(${rgb}, ${alpha})`).join(", ");
}

// A cell as written, each token it names followed by its value, so that a reader sees both
function fdCell(text, tokens) {
  const parts = String(text).split(/((?<![\w-])--[A-Za-z][\w-]*)/);
  return parts.map((part, i) => (i % 2 ? h("span", { class: "fd-token", title: tokens[part] ? `${part}: ${tokens[part]}` : part },
    part, tokens[part] ? h("small", { class: "meta" }, ` ${tokens[part]}`) : null) : linkify(part)));
}

// A row's cells with each token it names replaced by its value, for the example drawn from it
const fdResolved = (cells, tokens) => cells.map((c) => c.replace(/(?<![\w-])--[A-Za-z][\w-]*/g, (name) => (name in tokens ? tokens[name] : name)));

// What one row looks like, from its cells; null where it is a rule in words
function fdExample(cells, heads, font) {
  const row = cells.join(" | ");
  const first = cells[0].toLowerCase();
  const hexes = row.match(FD_HEX) || [];
  const pair = row.match(/(#[0-9a-fA-F]{6})\s+on\s+(#[0-9a-fA-F]{6})/);
  if (/focus/.test(first) && fdColour(row)) {
    const [width = 2, off = 2] = fdPx(row);
    return h("span", { class: "fd-focus", style: `outline: ${width}px solid ${fdColour(row)}; outline-offset: ${off}px` }, "Focused");
  }
  if (pair) {
    return [...row.matchAll(/(#[0-9a-fA-F]{6})\s+on\s+(#[0-9a-fA-F]{6})/g)].map(([, ink, ground]) =>
      h("span", { class: "fd-pair", style: `color: ${ink}; background: ${ground}` }, "Aa",
        h("small", {}, `${fdRatio(ink, ground).toFixed(1)}:1`)));
  }
  const words = Object.keys(FD_WEIGHTS).join("|");
  const size = row.match(new RegExp(`(\\d+)px,\\s*(\\d{3}|${words})\\b(?:,\\s*(?:on\\s*(\\d+)px|(\\d(?:\\.\\d+)?)\\b))?`, "i"));
  if (size) {
    const sample = cells[heads.findIndex((t) => /sample/i.test(t))] || cells[0];
    const weight = FD_WEIGHTS[size[2].toLowerCase()] || size[2];
    const height = size[3] ? `${size[3]}px` : size[4] || "normal";
    const family = (row.match(/\|\s*([A-Z][\w ]+?),\s*\d+px/) || [])[1];
    const tint = fdColour(row.replace(/^[^|]*\|/, ""));
    const extra = (/capitals/i.test(row) ? "text-transform: uppercase;" : "") + (/spaced/i.test(row) ? "letter-spacing: .06em;" : "")
      + (tint && !/^#?(fff|ffffff|white)$/i.test(tint) ? `color: ${tint};` : "");
    return h("span", { class: "fd-type", style: `font: ${weight} ${size[1]}px/${height} ${family ? `"${family}", ` : ""}${font}; ${extra}` }, sample);
  }
  const steps = row.match(/(\d+(?:(?:,\s*|\s+and\s+)\d+)+)\s*px/);   // "4, 8, 12, 16px", "... 48 and 64px"
  if (/scale/.test(first) && (steps || fdPx(row).length > 1)) {
    const values = steps ? steps[1].split(/,\s*|\s+and\s+/).map(Number) : fdPx(row);
    return h("span", { class: "fd-scale" }, values.map((v) => h("span", { class: "fd-step" },
      h("i", { style: `width: ${v}px` }), h("small", {}, v))));
  }
  const padding = row.match(/(\d+)px above and below,\s*(\d+)(?:\s*to\s*\d+)?px at the sides/);
  if (padding) {
    return h("span", { class: "fd-pad", style: `padding: ${padding[1]}px ${padding[2]}px` }, cells[0].replace(/^inside an? /i, ""));
  }
  if (/corner/.test(first)) {
    const corners = [...cells[1].matchAll(/(\d+)px(?:\s+(?:on|for)\s+([^;|]+))?/g)]
      .map(([, r, what]) => [Number(r), (what || "").split(/ and |,/)[0].trim()]);
    if (/round/.test(row)) corners.push([999, "round"]);
    return h("span", { class: "fd-shapes" }, corners.map(([r, what]) =>
      h("span", { class: "fd-shape", style: `border-radius: ${r}px` }, r === 999 ? "round" : `${r}px`,
        r === 999 ? null : h("small", {}, what))));
  }
  if (/border/.test(first) && fdColour(row)) {
    const [width = 1] = fdPx(row);
    return h("span", { class: "fd-shape", style: `border: ${width}px solid ${fdColour(row)}` }, `${width}px`);
  }
  if (/height/.test(first) && fdPx(cells[1]).length) {
    const tall = [...cells[1].matchAll(/(\d+)px(?:\s+for\s+([^,;|]+))?/g)].map(([, px, what]) => [Number(px), (what || "").trim()]);
    return h("span", { class: "fd-heights" }, tall.map(([px, what]) =>
      h("span", { class: "fd-height", style: `height: ${px}px` }, `${px}`, what ? h("small", {}, what) : null)));
  }
  if (/shadow/.test(first)) {
    const shadow = fdShadow(row);
    return shadow ? h("span", { class: "fd-shape fd-raised", style: `box-shadow: ${shadow}` }, "raised") : null;
  }
  if (hexes.length && (/^swatch\b/.test(first) || heads.some((t) => /colou?r/i.test(t)))) {
    const colour = hexes[0];
    return h("span", { class: "fd-swatch" }, h("i", { style: `background: ${colour}` }),
      h("span", { class: "fd-pair", style: `color: ${colour}; background: #ffffff` }, "Aa",
        h("small", {}, `${fdRatio(colour, "#ffffff").toFixed(1)}:1`)));
  }
  const signs = [...new Set(row.match(/[★☆✓✔✗✕×−+›‹→←↑↓•…♥]/g) || [])];
  if (signs.length >= 2) return h("span", { class: "fd-signs", style: `font-family: ${font}` }, signs.join(" "));
  return null;
}

// The families a "Typeface:" line names, a list or a sentence: "system-ui, then Segoe UI, Roboto" or "the reader's
// own system font -- Segoe UI on Windows, ... Helvetica Neue, Arial" -- each a name in capitals, or a CSS keyword;
// the application's own font last, so the shorthand always holds
function fdFamilies(said) {
  const names = said.split(/,|;|\.\s|\s--\s|\bthen\b|:/).map((seg) => seg.trim().replace(/\s+on\s+.*$/, ""))
    .filter((seg) => /^[A-Z][\w-]*(?: [A-Z][\w-]*){0,3}$/.test(seg) || /^(?:system-ui|ui-[a-z]+|sans-serif|serif|monospace)$/.test(seg));
  if (/\bsystem\b/i.test(said) && !names.includes("system-ui")) names.unshift("system-ui");
  return [...new Set(names)].map((n) => (/\s/.test(n) ? `"${n}"` : n)).concat("var(--font)").join(", ");
}

function fdTable(lines, font, tokens) {
  const rows = lines.map((l) => l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
  const heads = rows[0];
  const body = rows.slice(1).filter((r) => !r.every((c) => /^:?-+:?$/.test(c)));
  const examples = body.map((r) => fdExample(fdResolved(r, tokens), heads, font));
  const drawn = examples.some(Boolean);
  const label = (cell, i) => (i === 0 ? cell.replace(/^swatch\s+/i, "") : cell);
  return h("div", { class: "table-frame" }, h("table", { class: "fd-table" },
    h("thead", {}, h("tr", {}, heads.map((t) => h("th", {}, t)), drawn ? h("th", {}, "Looks like") : null)),
    h("tbody", {}, body.map((r, i) => h("tr", {}, r.map((c, j) => h("td", {}, fdCell(label(c, j), tokens))),
      drawn ? h("td", { class: "fd-example" }, examples[i] || "") : null)))));
}

// The foundation's text, its tables drawn with their examples; the typeface a line names, for the samples; the tokens it
// names, each shown with its value and resolved for the examples
function foundationBody(text, tokens = {}) {
  const said = String(text || "");
  const named = said.match(/^typeface:\s*(.+)$/im);
  const font = named ? fdFamilies(fdResolved([named[1]], tokens)[0]) : "var(--font)";
  const out = [];
  let prose = [], table = [];
  const flush = () => {
    if (prose.length) out.push(h("div", { class: "panel text" }, paragraphs(prose.join("\n"))));
    if (table.length) out.push(fdTable(table, font, tokens));
    prose = []; table = [];
  };
  for (const line of said.split("\n")) {
    if (line.trim().startsWith("|")) { if (prose.length) { const p = prose; prose = []; out.push(h("div", { class: "panel text" }, paragraphs(p.join("\n")))); } table.push(line); }
    else { if (table.length) { out.push(fdTable(table, font, tokens)); table = []; } prose.push(line); }
  }
  flush();
  return out;
}
