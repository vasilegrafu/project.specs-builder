// A flow's diagram, above its steps, drawn by Mermaid: the one written in the flow's Diagram section where it has
// one, else one made from its steps -- each step in order, a step beginning "If" leaving the line from the one before
// it, another flow it hands over to, and each row of "When it goes wrong" beside the step whose IDs it stands on.
// Drawn in the application's look, light or dark, again when the appearance changes; a box named by an ID opens it.
// Mermaid (MIT) is fetched from the CDN at one exact version, the first time a diagram is shown, so that a diagram
// drawn today is drawn the same next year; it is not kept in the repository. Without a connection the diagram's
// text is shown instead, and the steps under it say the same. Loaded before engine.js; it draws with engine.js's h()
// and state.
"use strict";

const MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11.9.0/dist/mermaid.min.js";
const FLOW_SAYS = 60;                                          // a step's words in a made diagram, at most
const FLOW_ID = /\b([A-Z]+\d+(?:\.\d+)*)\b/g;
const flowDiagrams = { loading: null, drawn: 0 };

const idsIn = (text) => [...String(text).matchAll(FLOW_ID)].map((m) => m[1]).filter((id) => state.names[id]);
const kindOf = (id) => (state.names[id] || {}).kind;

// Words cut at a whole word, the IDs a step ends on left off
function shortly(text, most = FLOW_SAYS) {
  const bare = String(text).replace(/(\s*,?\s*\b[A-Z]+\d+(?:\.\d+)*\b)+\s*\.?\s*$/, "").trim();
  if (bare.length <= most) return bare;
  const clause = bare.lastIndexOf(";", most);
  if (clause > most / 2) return bare.slice(0, clause) + "…";
  return bare.slice(0, most).replace(/[\s,;:]+\S*$/, "") + "…";
}

function stepsOf(text) {
  return String(text || "").split("\n").map((line) => line.match(/^\s*(\d+)\.\s+(.*)$/)).filter(Boolean)
    .map(([, no, said]) => ({ no, said, ids: idsIn(said), side: [] }));
}

function failuresOf(text) {
  const rows = String(text || "").split("\n").filter((l) => l.trim().startsWith("|"))
    .map((l) => l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
  return rows.slice(1).filter((r) => !r.every((c) => /^:?-+:?$/.test(c)))
    .map((r) => ({ what: r[0] || "", then: r[1] || "", ids: idsIn(r.join(" ")) }));
}

// The diagram a flow holds: the text of its Diagram section, fenced or not
function written(f) {
  const said = String(f.diagram || "").trim();
  const fenced = said.match(/```(?:mermaid)?\s*\n([\s\S]*?)\n```/);
  return fenced ? fenced[1].trim() : said;
}

// A diagram made from the steps, for a flow that holds none
function made(n) {
  const f = n.fields;
  const label = (text) => `"${String(text).replace(/"/g, "'")}"`;
  const steps = stepsOf(f.steps);
  if (!steps.length) return "";
  const main = [];
  for (const s of steps) {
    if (/^if\b/i.test(s.said) && main.length) main[main.length - 1].side.push({ kind: "if", step: s });
    else main.push(s);
  }
  for (const fail of failuresOf(f["goes wrong"])) {
    const wanted = fail.ids.filter((id) => kindOf(id) !== "flow");
    let best = null, most = 0;
    for (const s of main) {
      const shared = s.ids.filter((id) => wanted.includes(id)).length;
      if (shared > most) { best = s; most = shared; }
    }
    (best || main[main.length - 1]).side.push({ kind: "fails", fail });
  }
  const lines = ["flowchart TD", `  start([${label(shortly(f.trigger || f.user || "It starts"))}])`];
  let before = "start", k = 0;
  for (const s of main) {
    const id = `s${s.no}`;
    lines.push(`  ${before} --> ${id}[${label(`${s.no} · ${shortly(s.said)}`)}]`);
    for (const to of new Set(s.ids.filter((x) => kindOf(x) === "flow" && x !== n.id))) {
      lines.push(`  ${id} -.-> ${to}([${label(`${to} ${state.names[to].name || ""}`)}])`);
    }
    for (const b of s.side) {
      if (b.kind === "if") lines.push(`  ${id} -.->|if| s${b.step.no}[${label(`${b.step.no} · ${shortly(b.step.said)}`)}]`);
      else lines.push(`  ${id} -.->|fails| x${++k}[${label(`${shortly(b.fail.what, 48)}: ${shortly(b.fail.then, 48)}`)}]`);
    }
    before = id;
  }
  lines.push(`  ${before} --> done([${label("Done")}])`);
  if (k) lines.push("  classDef fails stroke-dasharray: 4 3", `  class ${Array.from({ length: k }, (_, i) => `x${i + 1}`).join(",")} fails`);
  return lines.join("\n");
}

function loadMermaid() {
  if (window.mermaid) return Promise.resolve(window.mermaid);
  flowDiagrams.loading ??= new Promise((done, failed) => {
    const script = h("script", { src: MERMAID, crossorigin: "anonymous" });
    script.onload = () => done(window.mermaid);
    script.onerror = () => { flowDiagrams.loading = null; failed(new Error("Mermaid could not be fetched -- is there a connection?")); };
    document.head.append(script);
  });
  return flowDiagrams.loading;
}

// The application's tokens, as Mermaid's theme
function look() {
  const css = getComputedStyle(document.documentElement);
  const t = (name) => css.getPropertyValue(name).trim();
  return {
    startOnLoad: false, securityLevel: "strict", theme: "base",
    flowchart: { wrappingWidth: 170, htmlLabels: true, nodeSpacing: 28, rankSpacing: 34, padding: 10, curve: "basis" },
    themeVariables: {
      fontFamily: getComputedStyle(document.body).fontFamily, fontSize: "14px", background: t("--panel"),
      primaryColor: t("--panel"), primaryTextColor: t("--ink"), primaryBorderColor: t("--line-strong"),
      secondaryColor: t("--accent-soft"), tertiaryColor: t("--sunken"), lineColor: t("--ink-3"),
      textColor: t("--ink"), edgeLabelBackground: t("--panel"), clusterBkg: t("--sunken"), clusterBorder: t("--line"),
    },
  };
}

async function draw(box) {
  const mermaid = await loadMermaid();
  mermaid.initialize(look());
  const { svg } = await mermaid.render(`flow-diagram-${++flowDiagrams.drawn}`, box.dataset.source);
  box.querySelector(".flow-diagram-canvas").innerHTML = svg;
  for (const node of box.querySelectorAll("g.node")) {      // a box named by an ID opens it
    const id = (node.textContent.match(FLOW_ID) || [])[0];
    if (id && state.names[id] && node.textContent.trim().startsWith(id)) {
      node.classList.add("flow-diagram-link");
      node.addEventListener("click", () => { location.hash = nodeHref(id); });
    }
  }
}

function flowMap(n) {
  const own = written(n.fields);
  const source = own || made(n);
  if (!source) return null;
  const box = h("figure", { class: "flow-diagram", "data-source": source },
    h("div", { class: "flow-diagram-canvas" }, h("p", { class: "empty" }, "Drawing the diagram…")),
    h("figcaption", { class: "meta" }, own ? "Written in its Diagram section." : "Made from its steps: it has no Diagram section."));
  draw(box).catch((error) => box.querySelector(".flow-diagram-canvas").replaceChildren(
    h("p", { class: "meta" }, `The diagram is not drawn: ${error.message} Its text:`), h("pre", { class: "flow-diagram-text" }, source)));
  return box;
}

document.addEventListener("specs-builder-2:theme", () => {
  for (const box of document.querySelectorAll(".flow-diagram")) draw(box).catch(() => {});
});
