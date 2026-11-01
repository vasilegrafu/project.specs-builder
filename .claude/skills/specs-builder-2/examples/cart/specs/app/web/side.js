// The tree of a part, down the left of its pages, as specs-builder had: the part's name, leading to a page of
// everything it holds; under it each kind with its letters and count, folding open to its nodes; then the part's
// own pages. The kind and the node open are marked, and the page beside it takes the rest of the width. An entry
// too long is cut with dots -- a name after eight words -- and a pause over it shows it whole. Its edge drags to another width,
// kept for each part's tree; its « folds it to a rail, kept so for every part. Under 1024px it folds into a
// button above the page that opens it as a drawer. No tree on the overview, Help, the document's pages or the
// prototype tool. Loaded before engine.js; it draws with engine.js's h(), state and GROUPS, and menu.js's icon(),
// PARTS and lettersOf().
"use strict";

const SIDE_FOLDS = "specs-builder-2.side";                   // the kinds unfolded, kept in the browser
const SIDE_WIDTHS = "specs-builder-2.side-widths";           // each part's tree's width, as {part: px}
const SIDE_RAIL = "specs-builder-2.side-folded";             // "1" when the tree is folded to its rail
const SIDE_WIDE = { least: 200, most: 520, usual: 288 };
const SIDE_TIP_PAUSE = 300;
const SIDE_WORDS = 8;                                          // a node's name in the tree, at most, before the dots
const SIDE_PAGES = {                                           // a part's own pages, as its menu has them
  Evidence: [["#/evidence", "Files"]],
  UX: [["#/design", "Design system"], ["#/prototypes", "Every screen drawn"]],
};
const ROW_OF = { criterion: "requirement", element: "screen", part: "component", state: "entity" };
const kept = (key, fallback) => { try { return localStorage.getItem(key) ?? fallback; } catch (e) { return fallback; } };
const keep = (key, value) => { try { localStorage.setItem(key, value); } catch (e) { /* kept for this page alone */ } };
const sideState = {
  part: null,
  open: new Set(kept(SIDE_FOLDS, "").split(",").filter(Boolean)),
  widths: (() => { try { return JSON.parse(kept(SIDE_WIDTHS, "{}")) || {}; } catch (e) { return {}; } })(),
  tip: null,
  tipping: 0,
};
document.documentElement.classList.toggle("side-folded", kept(SIDE_RAIL, "") === "1");

const kindsOf = (part) => (GROUPS.find(([g]) => g === part) || [null, null])[1];
const byId = (a, b) => a.localeCompare(b, undefined, { numeric: true });
const nodesOf = (kind) => Object.keys(state.names).filter((id) => state.names[id].kind === kind).sort(byId);

// A name cut at whole words, and whether it was cut: a name the server cut already ends with dots of its own
function words(name) {
  const bare = name.replace(/\s*(\.\.\.|…)$/, "");
  const all = bare.split(/\s+/).filter(Boolean);
  const cut = all.length > SIDE_WORDS || bare !== name;
  return { text: all.slice(0, SIDE_WORDS).join(" ") + (cut ? "…" : ""), cut };
}

// Where a view stands: its part, the kind and the node to mark, or the page of the part's own
function sideFor(where, arg) {
  if (document.documentElement.classList.contains("peeked")) return null;
  if (where === "group") return kindsOf(arg) ? { part: arg, here: "group" } : null;
  if (where === "list") return kindsOf(partOf(arg)) ? { part: partOf(arg), kind: arg } : null;
  if (where === "node") {
    const known = state.names[arg];
    if (!known) return null;
    const kind = ROW_OF[known.kind] || known.kind;
    const id = ROW_OF[known.kind] ? arg.split(".")[0] : arg;
    return kindsOf(partOf(kind)) ? { part: partOf(kind), kind, id } : null;
  }
  if (where === "evidence") return { part: "Evidence", page: "#/evidence" };
  if (where === "design" || where === "prototypes") return { part: "UX", page: `#/${where}` };
  return null;
}

function drawSide(where, arg) {
  const at = sideFor(where, arg);
  const side = document.getElementById("side");
  const root = document.documentElement;
  closeSide();
  root.classList.toggle("has-side", !!at);
  side.hidden = !at;
  document.getElementById("side-button").hidden = !at;
  if (!at) { sideState.part = null; return; }
  if (at.kind && !sideState.open.has(at.kind)) { sideState.open.add(at.kind); keepFolds(); }
  const was = side.querySelector(".side-body");
  const scrolled = sideState.part === at.part && was ? was.scrollTop : 0;
  const kinds = kindsOf(at.part).filter((k) => nodesOf(k).length);
  hideTip();
  side.replaceChildren(
    h("div", { class: "side-head" },
      h("a", { class: `side-title${at.here === "group" ? " on" : ""}`, href: `#/group/${at.part}`, "aria-label": at.part,
               "aria-current": at.here === "group" ? "page" : null }, icon(PARTS[at.part].icon), h("span", { class: "side-title-text" }, at.part)),
      h("button", { type: "button", class: "side-rail-button", onclick: () => fold(!railed()) }, icon("chevron"))),
    h("div", { class: "side-body" },
      h("ul", { class: "side-kinds" }, kinds.map((k) => sideKind(k, at))),
      SIDE_PAGES[at.part] ? h("ul", { class: "side-pages" }, SIDE_PAGES[at.part].map(([href, label]) =>
        h("li", {}, h("a", { href, class: `side-page${at.page === href ? " on" : ""}`, "aria-current": at.page === href ? "page" : null },
          h("span", { class: "side-page-name" }, label))))) : null),
    h("div", { class: "side-grip", role: "separator", "aria-orientation": "vertical", tabindex: "0",
               "aria-label": "The tree's width: drag, or the arrow keys; a double click puts it back",
               "aria-valuemin": SIDE_WIDE.least, "aria-valuemax": SIDE_WIDE.most }));
  document.getElementById("side-button").replaceChildren(icon(PARTS[at.part].icon), h("span", {}, at.part), icon("chevron"));
  sideState.part = at.part;
  widen(sideState.widths[at.part] || SIDE_WIDE.usual);
  fold(railed());
  side.querySelector(".side-body").scrollTop = scrolled;
  reveal();
}

// what is open, brought into the tree's sight a third of the way down when it is out of it
function reveal() {
  const body = document.querySelector("#side .side-body");
  const on = body && (body.querySelector(".side-node.on") || body.querySelector(".side-kind-link.on"));
  if (on && (on.offsetTop < body.scrollTop || on.offsetTop + on.offsetHeight > body.scrollTop + body.clientHeight)) {
    body.scrollTop = on.offsetTop - body.clientHeight / 3;
  }
  return on;
}

// ---- the width, dragged at the tree's edge and kept for its part; the rail, the tree folded, kept for all

const railed = () => document.documentElement.classList.contains("side-folded");

function widen(px) {
  const wide = Math.round(Math.min(SIDE_WIDE.most, Math.max(SIDE_WIDE.least, px)));
  document.documentElement.style.setProperty("--side-w", `${wide}px`);
  document.querySelectorAll(".side-grip:not(.far)").forEach((grip) => grip.setAttribute("aria-valuenow", wide));
  return wide;
}

function keepWidth(px, part = sideState.part) {
  if (px === null) delete sideState.widths[part];
  else sideState.widths[part] = px;
  keep(SIDE_WIDTHS, JSON.stringify(sideState.widths));
}

function fold(rail) {
  document.documentElement.classList.toggle("side-folded", rail);
  keep(SIDE_RAIL, rail ? "1" : "");
  const button = document.querySelector("#side .side-rail-button");
  if (!button) return;
  button.setAttribute("aria-expanded", String(!rail));
  button.setAttribute("aria-label", rail ? "Open the tree" : "Fold the tree");
  hideTip();
}

// A side's edge, dragged, double clicked or moved with the arrows: `part` is whose width is kept, the side tree's own by
// default. A side on the right of the page says so in `far`, with how to set its width, its usual width and its width now.
function wireGrip(side, part, far) {
  const save = (px) => keepWidth(px, part || sideState.part);
  const set = far ? far.set : widen;
  const usual = far ? far.usual : SIDE_WIDE.usual;
  const across = (x, box) => (far ? box.right - x : x - box.left);
  side.addEventListener("pointerdown", (e) => {
    const grip = e.target.closest(".side-grip");
    if (!grip || e.button !== 0) return;
    e.preventDefault();
    grip.setPointerCapture(e.pointerId);
    document.documentElement.classList.add("side-resizing");
    const box = side.getBoundingClientRect();
    const move = (m) => set(across(m.clientX, box));
    const done = (u) => {
      grip.removeEventListener("pointermove", move);
      grip.removeEventListener("pointerup", done);
      grip.removeEventListener("pointercancel", done);
      document.documentElement.classList.remove("side-resizing");
      save(set(across(u.clientX, box)));
    };
    grip.addEventListener("pointermove", move);
    grip.addEventListener("pointerup", done);
    grip.addEventListener("pointercancel", done);
  });
  side.addEventListener("dblclick", (e) => {
    if (!e.target.closest(".side-grip")) return;
    set(usual);
    save(null);
  });
  side.addEventListener("keydown", (e) => {
    if (!e.target.closest(".side-grip") || (e.key !== "ArrowLeft" && e.key !== "ArrowRight")) return;
    e.preventDefault();
    const now = far ? far.now() : parseInt(getComputedStyle(document.documentElement).getPropertyValue("--side-w"), 10) || SIDE_WIDE.usual;
    save(set(now + ((e.key === "ArrowRight") === !far ? 16 : -16)));
  });
}

// ---- an entry cut with dots, shown whole after a pause over it or on its focus

function wireTips(side) {
  const entry = (target) => target.closest && target.closest(".side-node, .side-kind-link, .side-page, .side-title");
  const show = (a) => {
    clearTimeout(sideState.tipping);
    sideState.tipping = setTimeout(() => tipFor(a), SIDE_TIP_PAUSE);
  };
  side.addEventListener("pointerover", (e) => { const a = entry(e.target); if (a) show(a); });
  side.addEventListener("pointerout", (e) => { const a = entry(e.target); if (a && !a.contains(e.relatedTarget)) hideTip(); });
  side.addEventListener("focusin", (e) => { const a = entry(e.target); if (a) show(a); });
  side.addEventListener("focusout", hideTip);
  side.addEventListener("scroll", hideTip, { capture: true, passive: true });
}

function tipFor(a) {
  if (!a.isConnected || document.documentElement.classList.contains("side-resizing")) return;
  const cut = a.dataset.cut === "1" || [...a.querySelectorAll(".side-kind-name, .side-page-name, .side-title-text")]
    .some((t) => t.scrollWidth > t.clientWidth + 1 || (railed() && t.classList.contains("side-title-text")));
  if (!cut) return;
  const text = a.classList.contains("side-node") ? a.getAttribute("aria-label")
    : (a.querySelector(".side-kind-name, .side-page-name, .side-title-text") || a).textContent;
  if (!sideState.tip) {
    sideState.tip = h("div", { class: "side-tip", role: "tooltip", hidden: true });
    document.body.append(sideState.tip);
  }
  const tip = sideState.tip;
  tip.textContent = text;
  tip.hidden = false;
  const at = a.getBoundingClientRect(), wide = tip.offsetWidth, high = tip.offsetHeight;
  const beside = at.right + 8 + wide <= window.innerWidth - 8;
  tip.style.left = `${beside ? at.right + 8 : Math.max(8, Math.min(at.left, window.innerWidth - wide - 8))}px`;
  tip.style.top = `${beside ? at.top + (at.height - high) / 2 : at.bottom + 4}px`;
}

function hideTip() {
  clearTimeout(sideState.tipping);
  if (sideState.tip) sideState.tip.hidden = true;
}

function sideKind(kind, at) {
  const ids = nodesOf(kind);
  const open = sideState.open.has(kind);
  const letters = lettersOf(kind);
  const list = h("ul", { class: "side-nodes", id: `side-${kind}`, hidden: !open }, ids.map((id) => {
    const on = id === at.id;
    const name = words(state.names[id].name || "");
    return h("li", {}, h("a", { href: nodeHref(id), class: `side-node${on ? " on" : ""}`, "aria-current": on ? "page" : null,
                                "data-cut": name.cut ? "1" : null, "data-card": id, "aria-label": `${id} ${state.names[id].name || ""}` },
      h("span", { class: "side-id" }, id), h("span", { class: "side-name" }, name.text)));
  }));
  const fold = h("button", { type: "button", class: "side-fold", "aria-expanded": String(open), "aria-controls": `side-${kind}`,
                             "aria-label": `${open ? "Fold" : "Unfold"} ${PLURAL[kind] || kind}` }, icon("chevron"));
  fold.addEventListener("click", () => {
    const now = list.hidden;
    list.hidden = !now;
    fold.setAttribute("aria-expanded", String(now));
    fold.setAttribute("aria-label", `${now ? "Fold" : "Unfold"} ${PLURAL[kind] || kind}`);
    if (now) sideState.open.add(kind); else sideState.open.delete(kind);
    keepFolds();
  });
  const here = at.kind === kind && !at.id;
  return h("li", { class: "side-kind" },
    h("div", { class: "side-kind-head" }, fold,
      h("a", { href: `#/list/${kind}`, class: `side-kind-link${here ? " on" : ""}`, "aria-current": here ? "page" : null },
        h("span", { class: `drop-dot kind-${kind}` }), h("span", { class: "side-kind-name" }, PLURAL[kind] || kind,
          letters ? h("span", { class: "drop-letters" }, ` (${letters})`) : null),
        h("span", { class: "side-count" }, ids.length))),
    list);
}

function keepFolds() {
  keep(SIDE_FOLDS, [...sideState.open].join(","));
}

// Under 1024px: the button above the page opens the tree as a drawer; a link followed, Escape or a click beside
// it closes it
function openSide() {
  document.documentElement.classList.add("side-open");
  document.getElementById("side-button").setAttribute("aria-expanded", "true");
  const on = reveal() || document.querySelector("#side .on") || document.querySelector("#side a");
  if (on) on.focus({ preventScroll: true });
}

function closeSide() {
  const root = document.documentElement;
  if (!root.classList.contains("side-open")) return;
  root.classList.remove("side-open");
  document.getElementById("side-button").setAttribute("aria-expanded", "false");
}

document.getElementById("side-button").addEventListener("click", () =>
  document.documentElement.classList.contains("side-open") ? closeSide() : openSide());
document.getElementById("side-shade").addEventListener("click", closeSide);
wireGrip(document.getElementById("side"));
wireTips(document.getElementById("side"));
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && document.documentElement.classList.contains("side-open")) {
    closeSide();
    document.getElementById("side-button").focus();
  }
});
// the bar's height, which the tree stays below as the page scrolls
new ResizeObserver(([entry]) => document.documentElement.style.setProperty("--bar-h", `${entry.target.offsetHeight}px`))
  .observe(document.querySelector(".bar"));

// A part's page: every kind it holds, with what each kind is, and its nodes, each named whole
async function partView(part) {
  const kinds = kindsOf(part);
  if (!kinds) throw new Error(`${part}: no such part`);
  const held = kinds.filter((k) => nodesOf(k).length);
  const lists = await Promise.all(held.map((k) => get(`nodes?kind=${encodeURIComponent(k)}`)));
  return [
    h("h1", {}, part),
    h("p", { class: "lead" }, `${PARTS[part].lead}.`),
    held.map((k, i) => {
      const letters = lettersOf(k);
      return h("section", { class: "part-kind" },
        h("h2", {}, h("a", { href: `#/list/${k}` }, PLURAL[k] || k, letters ? h("span", { class: "drop-letters" }, ` (${letters})`) : null),
          h("span", { class: "part-count" }, lists[i].length)),
        h("p", { class: "part-is" }, `${state.grammar.kinds[k].is}.`),
        h("ul", { class: "part-nodes" }, lists[i].map((r) => h("li", {}, chip(r.id), h("a", { href: nodeHref(r.id) }, r.whole || r.name || "")))));
    }),
  ];
}
