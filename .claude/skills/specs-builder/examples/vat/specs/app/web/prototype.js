"use strict";

// ---- the prototype, as a tool: a toolbar, the screen running full size, and an inspector on the element picked
// The toolbar picks the view -- the look, or the wireframe with every element marked -- whether the look marks what
// is under the pointer, the screen, what it shows (a state, or a variant), and its width. Each is sent to the frame,
// which runtime/live.js reads, and kept in the address; a link followed inside the prototype moves the toolbar with
// it. A mark clicked opens the inspector: the element's row and what it stands on, each a link, and its box and its
// text as measured, beside the token that says each value. Escape or × closes it; ↑ and ↓ step out to the element
// around it and in to the first inside it.
const tool = { current: null, nodes: new Map(), tokens: null, wired: false };
const PROTO_FOLDED = "specs-builder.proto-folded";             // "1" while the prototype has its bars folded away
const FOLDED = "specs-builder.inspector";              // the inspector's sections this browser folded

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
