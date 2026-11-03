// The bar, in two rows. Above: the specification's name, then search, help and the appearance. Below:
// the document and each part of the specification, each a button opening a short menu of the kinds it holds with
// their counts -- on hover where there is a pointer, on a click, from the keyboard -- and the prototype, the matrix and
// the graph, links straight to them. Where the row is too narrow for every part, a drawer, each part opening in place. Loaded before
// engine.js; it draws with engine.js's h(), svg() and state once the first view asks for the bar.
"use strict";

const PARTS = {
  Document: { icon: "document", lead: "What the product is, and where the specification stands" },
  Evidence: { icon: "evidence", lead: "What was read, where, and what it showed" },
  Decisions: { icon: "decisions", lead: "What was decided, what is still asked, and what was added" },
  Requirements: { icon: "requirements", lead: "What the product is for, and what it shall do" },
  Domain: { icon: "domain", lead: "The product's words, rules, roles and things" },
  API: { icon: "api", lead: "What programs call" },
  UX: { icon: "ux", lead: "How the product is used, and how it looks" },
  Prototype: { icon: "prototype", lead: "Every screen drawn, flow by flow" },
  Matrix: { icon: "matrix", lead: "Every node and link, walked one at a time" },
  Graph: { icon: "graph", lead: "The whole specification, and how it is linked" },
};
const DIRECT = { Prototype: "#/prototype", Matrix: "#/matrix", Graph: "#/graph" };   // no menu: a link straight to the page
const LOOKS = [["system", "As the system"], ["light", "Light"], ["dark", "Dark"]];
const ICONS = {
  brand: [["path", { d: "M12 3l9 5-9 5-9-5z" }], ["path", { d: "M3 13l9 5 9-5" }], ["path", { d: "M3 17.5l9 5 9-5" }]],
  document: [["path", { d: "M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" }], ["path", { d: "M14 3v5h5M9 13h6M9 17h6" }]],
  evidence: [["rect", { x: 6, y: 4, width: 12, height: 17, rx: 2 }], ["path", { d: "M9 4V2.5h6V4M9 10h6M9 14h6M9 18h3" }]],
  decisions: [["circle", { cx: 6, cy: 18, r: 2.5 }], ["circle", { cx: 6, cy: 6, r: 2.5 }], ["circle", { cx: 18, cy: 8, r: 2.5 }],
              ["path", { d: "M6 8.5v7M18 10.5c0 4-4 5.5-9.5 6.5" }]],
  requirements: [["path", { d: "M10 6h10M10 12h10M10 18h10M3.5 6l1.5 1.5L8 4.5M3.5 12l1.5 1.5L8 10.5M3.5 18l1.5 1.5L8 16.5" }]],
  domain: [["path", { d: "M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z" }], ["path", { d: "M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5" }]],
  api: [["path", { d: "M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16" }]],
  ux: [["rect", { x: 3, y: 3, width: 18, height: 18, rx: 2 }], ["path", { d: "M3 9h18M9 21V9" }]],
  prototype: [["rect", { x: 2.5, y: 4, width: 13, height: 10, rx: 1.5 }], ["path", { d: "M6.5 18h5M9 14v4" }],
              ["rect", { x: 17.5, y: 8, width: 4, height: 11, rx: 1 }]],
  matrix: [["rect", { x: 3, y: 3, width: 18, height: 18, rx: 2 }], ["path", { d: "M3 9h18M3 15h18M9 3v18M15 3v18" }]],
  graph: [["circle", { cx: 6, cy: 6, r: 2.5 }], ["circle", { cx: 18, cy: 7.5, r: 2.5 }], ["circle", { cx: 11, cy: 18, r: 2.5 }],
          ["path", { d: "M8.5 6.3l7 1M7.2 8.2l2.6 7.6M16.6 9.6l-4.3 6.3" }]],
  search: [["circle", { cx: 11, cy: 11, r: 7 }], ["path", { d: "M20 20l-3.5-3.5" }]],
  help: [["circle", { cx: 12, cy: 12, r: 9 }], ["path", { d: "M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17h.01" }]],
  request: [["path", { d: "M4 5h16v11H10l-4 4v-4H4z" }], ["path", { d: "M8 9h8M8 12h5" }]],
  export: [["path", { d: "M12 3.5V15" }], ["path", { d: "M7.5 10.5 12 15l4.5-4.5" }], ["path", { d: "M4 16v3.5h16V16" }]],
  print: [["path", { d: "M7 8V3.5h10V8" }], ["path", { d: "M7 17H4.5A1.5 1.5 0 0 1 3 15.5v-6A1.5 1.5 0 0 1 4.5 8h15A1.5 1.5 0 0 1 21 9.5v6a1.5 1.5 0 0 1-1.5 1.5H17" }],
    ["rect", { x: 7, y: 14, width: 10, height: 6.5, rx: .75 }], ["path", { d: "M17.5 11h.01" }]],
  arrow: [["path", { d: "M5 12h14M13 6l6 6-6 6" }]],
  back: [["path", { d: "M19 12H5M11 6l-6 6 6 6" }]],
  path: [["circle", { cx: 6, cy: 19, r: 2.5 }], ["circle", { cx: 18, cy: 5, r: 2.5 }], ["path", { d: "M8.5 19H15a3.5 3.5 0 0 0 0-7H9a3.5 3.5 0 0 1 0-7h6.5" }]],
  system: [["rect", { x: 3, y: 4, width: 18, height: 12, rx: 2 }], ["path", { d: "M8 20h8M12 16v4" }]],
  light: [["circle", { cx: 12, cy: 12, r: 4 }], ["path", { d: "M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" }]],
  dark: [["path", { d: "M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" }]],
  chevron: [["path", { d: "M6 9l6 6 6-6" }]],
  collapse: [["path", { d: "M7 4l5 5 5-5M7 20l5-5 5 5" }]],
  expand: [["path", { d: "M7 9l5-5 5 5M7 15l5 5 5-5" }]],
  preview: [["path", { d: "M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7z" }], ["circle", { cx: 12, cy: 12, r: 3 }]],
  newtab: [["path", { d: "M14 4h6v6M20 4l-9 9M18 14v6H4V6h6" }]],
  pin: [["path", { d: "M9 3h6l-1 7 3.5 3.5h-11L10 10zM12 13.5V21" }]],
  fit: [["path", { d: "M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" }]],
  focus: [["circle", { cx: 12, cy: 12, r: 3 }], ["circle", { cx: 12, cy: 12, r: 8 }], ["path", { d: "M12 1.5V4M12 20v2.5M1.5 12H4M20 12h2.5" }]],
  impact: [["circle", { cx: 4.5, cy: 12, r: 2 }], ["circle", { cx: 19.5, cy: 5, r: 2 }], ["circle", { cx: 19.5, cy: 12, r: 2 }], ["circle", { cx: 19.5, cy: 19, r: 2 }],
           ["path", { d: "M6.5 12h11M9 12c3 0 3-7 8.5-7M9 12c3 0 3 7 8.5 7" }]],
  layers: [["rect", { x: 3, y: 8, width: 5, height: 8, rx: 1 }], ["rect", { x: 10, y: 4, width: 5, height: 16, rx: 1 }], ["rect", { x: 17, y: 6, width: 4.5, height: 12, rx: 1 }]],
  both: [["path", { d: "M4 8h15M15 4l4 4-4 4M20 16H5M9 12l-4 4 4 4" }]],
  hop1: [["circle", { cx: 6, cy: 12, r: 2.5 }], ["circle", { cx: 18, cy: 12, r: 2.5 }], ["path", { d: "M8.5 12h7" }]],
  hop2: [["circle", { cx: 4, cy: 12, r: 2 }], ["circle", { cx: 12, cy: 12, r: 2 }], ["circle", { cx: 20, cy: 12, r: 2 }], ["path", { d: "M6 12h4M14 12h4" }]],
  menu: [["path", { d: "M4 7h16M4 12h16M4 17h16" }]],
  close: [["path", { d: "M6 6l12 12M18 6L6 18" }]],
};
const bar = { open: null, drawn: false };

function icon(name) {
  return svg("svg", { viewBox: "0 0 24 24", class: "icon", "aria-hidden": "true", focusable: "false" },
    ICONS[name].map(([tag, attrs]) => svg(tag, attrs)));
}

const header = () => document.querySelector("header.bar");
const compact = () => header().classList.contains("compact");
const kindCount = () => Object.fromEntries(state.summary.kinds.map((k) => [k.kind, k.count]));

function menuItems() {
  const count = kindCount();
  return [count.document ? "Document" : null,
          ...GROUPS.filter(([, kinds]) => kinds.some((k) => count[k])).map(([group]) => group),
          count.screen ? "Prototype" : null, "Matrix", "Graph"].filter(Boolean);
}

function partOf(active) {
  if (active === "document") return "Document";
  if (active === "design") return "UX";
  if (active === "prototype") return "Prototype";
  if (active === "matrix") return "Matrix";
  if (active === "graph") return "Graph";
  if (GROUPS.some(([g]) => g === active)) return active;
  return (GROUPS.find(([, kinds]) => kinds.includes(active)) || [null])[0];
}

// The parts, drawn again on every view: the one you are in marked, every menu closed.
function nav(active) {
  if (!bar.drawn) wireBar();
  const on = partOf(active);
  bar.active = active;
  closeMenu();
  closeDrawer();
  document.getElementById("nav").replaceChildren(...menuItems().map((key) => {
    if (DIRECT[key]) {
      return h("div", { class: `nav-item${on === key ? " on" : ""}`, "data-key": key },
        h("a", { class: "nav-button", href: DIRECT[key], "aria-current": on === key ? "page" : null,
                 onkeydown: (e) => keyOnPart(e, key) }, icon(PARTS[key].icon), h("span", { class: "nav-label" }, key)));
    }
    // The word is its page, and the arrow its menu: the two never share a press, on any device
    return h("div", { class: `nav-item${on === key ? " on" : ""}`, "data-key": key },
      h("a", { class: "nav-button", href: partPage(key), "aria-current": on === key ? "true" : null, onclick: () => { closeMenu(); closeDrawer(); },
               onkeydown: (e) => keyOnPart(e, key) }, icon(PARTS[key].icon), h("span", { class: "nav-label" }, key)),
      h("button", { type: "button", class: "nav-arrow", "aria-label": `The menu of ${key}`, "aria-expanded": "false", "aria-controls": `sub-${key}`,
                    onclick: () => (bar.open === key ? closeMenu() : openMenu(key)), onkeydown: (e) => keyOnPart(e, key) },
        h("span", { class: "nav-chevron" }, icon("chevron"))),
      h("div", { class: "nav-sub", id: `sub-${key}`, hidden: true }));
  }));
  document.getElementById("brand").textContent = state.summary.title;
  document.getElementById("brand-link").title = state.summary.title;
  document.title = state.summary.title;
  const help = document.getElementById("help-link");
  help.classList.toggle("on", active === "help");
  if (active === "help") help.setAttribute("aria-current", "page"); else help.removeAttribute("aria-current");
  fit();
}

// What is open and the evidence's files come after the view, from the server's one answer for the data as it stands.
function fetchMenu() {
  get("menu").then((found) => {
    state.menu = found;
    if (bar.open === "Document" || bar.open === "Evidence") openMenu(bar.open);
  }).catch(() => { /* the menus show the counts the view already has */ });
}

// A row too narrow for every part becomes a drawer: measured, not guessed, so a long name is allowed for.
function fit() {
  const top = header(), list = document.getElementById("nav");
  top.classList.remove("compact");
  if (list.scrollWidth > list.clientWidth + 1) top.classList.add("compact");
}

function wireBar() {
  bar.drawn = true;
  const top = header();
  document.getElementById("nav").addEventListener("keydown", (e) => {
    const sub = e.target.closest(".nav-sub");
    if (sub) moveIn(sub, e);
  });
  const button = document.getElementById("menu-button");
  button.replaceChildren(icon("menu"));
  button.addEventListener("click", () => (top.classList.contains("drawer-open") ? closeDrawer() : openDrawer()));
  document.getElementById("brand-mark").replaceChildren(icon("brand"));
  document.getElementById("print-link").replaceChildren(icon("print"));
  document.getElementById("export-button").prepend(icon("export"));
  document.getElementById("help-link").replaceChildren(icon("help"));
  document.addEventListener("keydown", (e) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable;
    if ((e.key === "k" && (e.ctrlKey || e.metaKey)) || (e.key === "/" && !typing)) {
      e.preventDefault();
      openSearch();
      return;
    }
    if (e.key !== "Escape") return;
    if (bar.open) {
      const key = bar.open;
      closeMenu();
      const part = document.querySelector(`.nav-item[data-key="${key}"] .nav-arrow`);
      if (part) part.focus();
    } else if (top.classList.contains("drawer-open")) closeDrawer();
    closeTheme();
  });
  document.addEventListener("click", (e) => {
    if (e.target.isConnected && !top.contains(e.target)) {      // a choice that redrew its list is not outside
      closeMenu();
      closeTheme();
      closeDrawer();
      closeResults();
    } else if (e.target.isConnected && !e.target.closest(".nav-item.open")) closeMenu();   // elsewhere in the bar
  });
  window.addEventListener("blur", () => {           // a click in a frame -- the prototype -- is outside too
    if (document.activeElement && document.activeElement.tagName === "IFRAME") {
      closeMenu();
      closeTheme();
      closeResults();
    }
  });
  let pending = 0;
  window.addEventListener("resize", () => {
    cancelAnimationFrame(pending);
    pending = requestAnimationFrame(() => {
      const was = compact();
      fit();
      if (was !== compact()) closeMenu();
      else if (bar.open) placeMenu(document.getElementById(`sub-${bar.open}`), document.querySelector(`.nav-item[data-key="${bar.open}"]`));
    });
  });
  themeSwitch();
  wireSearch();
}

function openDrawer() {
  header().classList.add("drawer-open");
  const button = document.getElementById("menu-button");
  button.setAttribute("aria-expanded", "true");
  button.replaceChildren(icon("close"));
}

function closeDrawer() {
  if (!header().classList.contains("drawer-open")) return;
  header().classList.remove("drawer-open");
  const button = document.getElementById("menu-button");
  button.setAttribute("aria-expanded", "false");
  button.replaceChildren(icon("menu"));
  closeMenu();
}

// A part's page, its whole list of what it holds -- the document's, the whole document
const partPage = (key) => key === "Document" ? "#/node/document" : `#/group/${key}`;

function keyOnPart(e, key) {
  const parts = [...document.querySelectorAll(".nav-button")];
  const at = parts.indexOf(e.currentTarget.closest(".nav-item").querySelector(".nav-button"));
  if (e.key === "ArrowDown" && !DIRECT[key]) { e.preventDefault(); openMenu(key, true); }
  else if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
    e.preventDefault();
    const next = parts[(at + (e.key === "ArrowRight" ? 1 : -1) + parts.length) % parts.length];
    next.focus();
    const to = next.parentElement.dataset.key;
    if (bar.open) { if (DIRECT[to]) closeMenu(); else openMenu(to); }
  } else if (e.key === "Home" || e.key === "End") {
    e.preventDefault();
    parts[e.key === "Home" ? 0 : parts.length - 1].focus();
  }
}

// One menu open at a time: dropping down under its part where the row is wide, in place in the drawer where it is not.
function openMenu(key, focusFirst) {
  for (const entry of document.querySelectorAll(".nav-item")) {
    const sub = entry.querySelector(".nav-sub");
    if (!sub) continue;
    const here = entry.dataset.key === key;
    entry.classList.toggle("open", here);
    entry.querySelector(".nav-arrow").setAttribute("aria-expanded", String(here));
    sub.replaceChildren(...(here ? [panel(key)] : []));
    sub.hidden = !here;
    if (here) placeMenu(sub, entry);
  }
  bar.open = key;
  if (focusFirst) {
    const first = document.querySelector(`#sub-${key} a`);
    if (first) first.focus();
  }
}

// The row hides what overflows it, so that it can be measured; a menu is fixed under its part instead, kept on screen.
function placeMenu(sub, entry) {
  if (compact()) { sub.style.left = sub.style.top = ""; return; }
  const at = entry.getBoundingClientRect();
  sub.style.top = `${at.bottom}px`;
  sub.style.left = `${Math.max(8, Math.min(at.left, window.innerWidth - sub.offsetWidth - 8))}px`;
}

function closeMenu() {
  bar.open = null;
  for (const entry of document.querySelectorAll(".nav-item")) {
    const sub = entry.querySelector(".nav-sub");
    if (!sub) continue;
    entry.classList.remove("open");
    entry.querySelector(".nav-arrow").setAttribute("aria-expanded", "false");
    sub.hidden = true;
    sub.replaceChildren();
  }
}

// Up and down through a menu's entries; up from the first goes back to the part it belongs to.
function moveIn(place, e) {
  if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
  const links = [...place.querySelectorAll("a, button")];
  const at = links.indexOf(document.activeElement);
  if (at < 0) return;
  e.preventDefault();
  if (e.key === "ArrowDown") links[Math.min(at + 1, links.length - 1)].focus();
  else if (at > 0) links[at - 1].focus();
  else {
    const part = document.querySelector(`.nav-item[data-key="${bar.open}"] .nav-arrow`);
    if (part) part.focus();
  }
}

// ---- what a part's menu holds: each kind in it with its count, then the part's own pages

function panel(key) {
  const count = kindCount();
  const m = state.menu;
  const kinds = key === "Document" ? [] : ((GROUPS.find(([g]) => g === key) || [null, []])[1]).filter((k) => count[k]);
  const pages = [];
  if (key === "Document") {
    const stale = state.summary.stale && state.summary.stale.nodes;
    pages.push(menuEntry("#/node/document", "The whole document"),
      menuEntry("#/open", "What is open", m && m.open !== null ? m.open : "…"),
      stale ? menuEntry("#/stale", "Stale", stale) : null, menuEntry("#/built", "What is built"),
      menuEntry("#/", "The overview"));
  }
  if (key === "Evidence") pages.push(menuEntry("#/evidence", "Files", m ? m.evidence.reduce((sum, f) => sum + f.files, 0) : null));
  if (key === "UX") pages.push(menuEntry("#/design", "Design system"), count.screen ? menuEntry("#/prototypes", "Every screen drawn", count.screen) : null);
  const rows = kinds.map((k) => menuEntry(`#/list/${k}`, PLURAL[k] || k, count[k], k, lettersOf(k)));
  const others = pages.filter(Boolean);
  return h("ul", { class: "drop" }, rows, rows.length && others.length ? h("li", { class: "drop-sep", role: "separator" }) : null, others);
}

// The letters a kind's IDs begin with, from the grammar: G for goals, SC for screens; none for a row's kind,
// whose IDs are its holder's and a number, nor for the document.
function lettersOf(kind) {
  const id = ((state.grammar || {}).kinds || {})[kind]?.id || "";
  return /^[A-Z]+$/.test(id) ? id : null;
}

function menuEntry(href, label, count, kind, letters) {
  const here = (kind && kind === bar.active) || (!kind && location.hash === href);
  return h("li", {}, h("a", { href, class: `drop-item${here ? " on" : ""}`, "aria-current": here ? "page" : null },
    h("span", { class: `drop-dot${kind ? ` kind-${kind}` : ""}` }),
    h("span", { class: "drop-label" }, label, letters ? h("span", { class: "drop-letters" }, ` (${letters})`) : null),
    count === null || count === undefined ? null : h("span", { class: "drop-count" }, count)));
}

// ---- search: a field above, the nodes it finds dropping down as it is typed

function wireSearch() {
  const box = document.getElementById("search");
  const input = h("input", { type: "search", id: "search-input", class: "search-input", placeholder: "Search",
                             autocomplete: "off", spellcheck: "false", role: "combobox", "aria-expanded": "false",
                             "aria-controls": "search-results", "aria-autocomplete": "list",
                             "aria-label": "Search the specification" });
  const results = h("div", { class: "search-results", id: "search-results", role: "listbox", hidden: true });
  results.addEventListener("mousedown", (e) => e.preventDefault());       // a pick is not a blur
  box.replaceChildren(
    h("button", { type: "button", class: "tool icon-only search-open", "aria-label": "Search", onclick: openSearch }, icon("search")),
    h("label", { class: "search-field" }, icon("search"), input, h("kbd", { class: "search-key" }, "Ctrl K")),
    results);
  let timer = 0, asked = 0, hits = [], at = -1;
  const pick = (i) => {
    at = i;
    hits.forEach((el, n) => el.setAttribute("aria-selected", String(n === i)));
    if (hits[i]) { input.setAttribute("aria-activedescendant", hits[i].id); hits[i].scrollIntoView({ block: "nearest" }); }
    else input.removeAttribute("aria-activedescendant");
  };
  const run = async () => {
    const query = input.value.trim();
    const ticket = ++asked;
    if (!query) { closeResults(); return; }
    let found = [];
    try { found = await get(`search?q=${encodeURIComponent(query)}`); } catch (error) { found = []; }
    if (ticket !== asked) return;                               // a later search answered first
    const words = query.toLowerCase().split(/\s+/).filter(Boolean);
    const kinds = [];
    for (const f of found) if (!kinds.includes(f.kind)) kinds.push(f.kind);
    hits = [];
    results.replaceChildren(...[
      ...(found.length ? kinds.map((kind) => [
        h("div", { class: "search-group", role: "presentation" }, PLURAL[kind] || kind),
        found.filter((f) => f.kind === kind).map((f) => {
          const hit = h("a", { class: "search-hit", role: "option", id: `hit-${hits.length}`, href: nodeHref(f.id),
                               "aria-selected": "false", onclick: () => done() },
            h("span", { class: `chip kind-${f.kind}` }, f.id),
            h("span", { class: "hit-name" }, marked(f.name, words)),
            f.snippet ? h("span", { class: "hit-snip" }, marked(f.snippet, words))
              : f.parent ? h("span", { class: "hit-snip" }, `in ${f.parent}`) : null);
          hits.push(hit);
          return hit;
        })]) : [h("p", { class: "search-none" }, `Nothing found for “${query}”.`)]),
      h("p", { class: "search-hint" }, "↑ ↓ to move · Enter to open · Esc to close")].flat(Infinity));
    results.hidden = false;
    input.setAttribute("aria-expanded", "true");
    pick(hits.length ? 0 : -1);
  };
  const done = () => {
    closeResults();
    input.value = "";
    input.blur();
    header().classList.remove("searching");
  };
  input.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(run, 120); });
  input.addEventListener("focus", () => { if (input.value.trim()) run(); });
  input.addEventListener("blur", () => { closeResults(); if (!input.value) header().classList.remove("searching"); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" && hits.length) { e.preventDefault(); pick(Math.min(at + 1, hits.length - 1)); }
    else if (e.key === "ArrowUp" && hits.length) { e.preventDefault(); pick(Math.max(at - 1, 0)); }
    else if (e.key === "Enter" && hits[at]) { e.preventDefault(); location.hash = hits[at].getAttribute("href"); done(); }
    else if (e.key === "Escape") { e.stopPropagation(); if (input.value) { input.value = ""; closeResults(); } else done(); }
  });
}

function openSearch() {
  closeMenu();
  header().classList.add("searching");
  const input = document.getElementById("search-input");
  input.focus();
  input.select();
}

function closeResults() {
  const results = document.getElementById("search-results");
  if (!results || results.hidden) return;
  results.hidden = true;
  document.getElementById("search-input").setAttribute("aria-expanded", "false");
}

// The words searched for, marked where they are in a text; the text is set as text, never as markup.
function marked(text, words) {
  if (!words.length) return text;
  const pattern = new RegExp(`(${words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`, "gi");
  return String(text).split(pattern).map((piece, i) => (i % 2 ? h("mark", {}, piece) : piece));
}

// ---- the appearance: a button showing the choice, opening the three

function themeSwitch() {
  const place = document.getElementById("theme");
  if (!window.theme) { place.hidden = true; return; }
  const now = window.theme.choice();
  const name = (LOOKS.find(([k]) => k === now) || LOOKS[0])[1];
  const list = h("div", { class: "theme-list", role: "menu", hidden: true },
    LOOKS.map(([k, label]) => h("button", { type: "button", role: "menuitemradio", "aria-checked": String(k === now),
      onclick: () => { window.theme.set(k); themeSwitch(); place.querySelector(".tool").focus(); } }, icon(k), label)));
  list.addEventListener("keydown", (e) => moveAround(list, e));
  const button = h("button", { type: "button", class: "tool icon-only", "aria-haspopup": "menu", "aria-expanded": "false",
                               "aria-label": `Appearance: ${name}`, title: `Appearance: ${name}`,
                               onclick: () => {
                                 const opening = list.hidden;
                                 list.hidden = !opening;
                                 button.setAttribute("aria-expanded", String(opening));
                                 if (opening) (list.querySelector('[aria-checked="true"]') || list.firstChild).focus();
                               } }, icon(now));
  place.replaceChildren(button, list);
}

function moveAround(list, e) {
  const items = [...list.querySelectorAll("button")];
  const at = items.indexOf(document.activeElement);
  if (e.key === "ArrowDown") { e.preventDefault(); items[(at + 1) % items.length].focus(); }
  if (e.key === "ArrowUp") { e.preventDefault(); items[(at - 1 + items.length) % items.length].focus(); }
}

function closeTheme() {
  const place = document.getElementById("theme");
  const list = place && place.querySelector(".theme-list");
  if (list && !list.hidden) {
    list.hidden = true;
    place.querySelector(".tool").setAttribute("aria-expanded", "false");
  }
}
