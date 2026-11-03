// The specification as pictures, #/graph, and none of them holds all of it. The server answers what is in view, from what it
// keeps of how the nodes join (app/matrix.py), so a specification of any size opens from its counts.
//
// Two scopes, the whole specification and one selected node, each with its own pictures. The bar holds both, and a node stays
// selected from one picture to the next.
//
// The map, #/graph: each kind folded, a bubble with its count, the lines between bubbles saying how many links join two kinds.
// A bubble clicked opens to a box of that kind's most linked nodes, and a tile there shows more; the box's title folds it.
// Around, #/graph/R4: one node in the middle, what it is linked to around it by kind, nothing else. A click spreads a node's
// own links, a double click puts it in the middle, a node dragged stays where it is put.
// Impact, #/graph/impact:R4: what stands on a node, then what stands on those, each step asked as it is opened.
// Layers, #/graph/layers: the specification left to right in the top menu's order, in bands that hold all of it, each kind
// opening to its nodes; #/graph/layers:R4 holds only what connects to one node, one step out, two, or all the way.
//
// What is held inside a node -- a criterion, an element -- is counted as that node. Everything is SVG in the application's own
// colours, so the appearance needs nothing from here, and on a sheet each picture is drawn flat, as it stands. The kinds open
// are kept in the browser. D3 (ISC) is fetched from the CDN at one exact version, the first time the page opens; it is not kept
// in the repository. Without a connection the page says so. Loaded before engine.js; it draws with engine.js's h(), svg(),
// get(), state, GROUPS, PLURAL and counted(), side.js's kept(), keep(), byId() and words(), matrix.js's mxFinder() and
// card.js's closeCard().
"use strict";

const D3_SCRIPT = "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js";
const MAP_OPEN = "specs-builder.graph-open";                  // the kinds open, kept in the browser
const MAP_MOVE = 260;                                           // ms: the picture moving to where it now stands
const MAP_TICKS = 280;                                          // steps of the forces, each time the kinds are laid out
const MAP_CAP = 60;                                             // the nodes a kind opens to; its tile doubles it
const MAP_LAYER_CAP = 24;                                       // the nodes of a kind a layer shows at a time
const MAP_LAYER_SMALL = 150;                                    // nodes in all: as few as this open from the start
const MAP_LAYER_HIDDEN = "specs-builder.layers-hidden";       // the columns hidden, kept in the browser
const MAP_LAYER = { wide: 240, gap: 150, row: 34, head: 34, strip: 34, tallest: 170, step: 6, quiet: 120, dense: 80 };   // px, rows and ms for the wheel, and the links past which they lighten
const MAP_BOX = { high: 26, gap: 6, pad: 10, head: 30, apart: 40 };   // px: a node in a box, the box, and between kinds
const MAP_GLYPH = { id: 7.6, name: 7.4, head: 8 };              // px: a character's width, for sizes known before drawing
const MAP_TAG = { high: 28, pad: 22, words: 4 };                // a node in the other pictures
const MAP_TWICE = 320;                                          // ms a click waits for a second, where a double click means something else
const mapState = { loading: null, open: new Set(kept(MAP_OPEN, "").split(",").filter(Boolean)), more: new Map(), at: new Map(), seen: null, moved: false, last: "", picked: null, steps: 1 };
const layerState = { open: null, at: new Map(), hidden: new Set(kept(MAP_LAYER_HIDDEN, "").split(",").filter(Boolean)) };
const mapHref = (id) => `#/graph/${encodeURIComponent(id)}`;
// How far the wheel zooms: D3's own step, a third as long, so that a picture can be brought to just the size wanted
const mapWheel = (e) => -e.deltaY * (e.deltaMode === 1 ? .05 : e.deltaMode ? 1 : .002) * (e.ctrlKey ? 10 : 1) / 3;

function loadD3() {
  if (window.d3) return Promise.resolve(window.d3);
  mapState.loading ??= new Promise((done, failed) => {
    const script = h("script", { src: D3_SCRIPT, crossorigin: "anonymous" });
    script.onload = () => done(window.d3);
    script.onerror = () => {
      mapState.loading = null;
      failed(Object.assign(new Error("D3 could not be fetched -- is there a connection?"), { offline: true }));
    };
    document.head.append(script);
  });
  return mapState.loading;
}

// Which picture an address asks for
async function graphPage(id) {
  try {
    if (!id) return await wholeGraph();
    if (id === "layers") return await layersGraph();
    if (id.startsWith("layers:")) return await layersGraph(id.slice("layers:".length));
    if (id.startsWith("impact:")) return await impactGraph(id.slice("impact:".length));
    return await focusGraph(id);
  } catch (error) {
    if (!error.offline) throw error;
    return h("div", { class: "graph-none" }, h("h1", {}, "Graph"), h("p", { class: "error" }, `The graph is not drawn: ${error.message}`),
      h("p", {}, "Every link it would show is on the page of the node at each end, and in the Matrix."));
  }
}

// The bar every picture shares: the whole specification on the left, the selected node on the right, and Find. A node stays
// selected from one picture to the next, until its x.
function mapPick(n) {
  mapState.last = n.id;
  mapState.picked = n;
}

function mapBar(here, title, ...tools) {
  const n = mapState.picked;
  const view = (name, word, picture, href) => (href
    ? h("a", { class: `mx-tool${here === name ? " on" : ""}`, href, title: word, "aria-label": word, "aria-current": here === name ? "page" : null }, icon(picture))
    : h("span", { class: "mx-tool graph-off", title: `${word}: select a node first`, "aria-label": word }, icon(picture)));
  const clear = () => { mapState.last = ""; mapState.picked = null; location.hash = "#/graph"; };
  const lead = { layers: "layers:", trace: "layers:", impact: "impact:" }[here] || "";
  return h("div", { class: "live-bar graph-bar" }, h("h1", { class: "sr-only" }, title),
    h("span", { class: "graph-scope" }, "All"),
    h("span", { class: "live-seg" }, view("map", "Map: every kind", "graph", "#/graph"), view("layers", "Layers: every kind, in the menu's order", "layers", "#/graph/layers")),
    h("span", { class: "graph-scope graph-picked" }, "Selected"),
    n ? h("span", { class: `graph-selected kind-${n.kind}`, title: `${n.id} ${n.name || ""}`.trim() }, h("span", { class: `chip kind-${n.kind}`, "data-card": n.id }, n.id),
      h("span", { class: "graph-selected-name" }, mapShort(n)),
      h("button", { type: "button", class: "graph-clear", title: "Clear the selection", "aria-label": "Clear the selection", onclick: clear }, icon("close"))) : null,
    mxFinder((hit) => { location.hash = mapHref(`${lead}${hit.parent || hit.id}`); }, "Find a node"),
    h("span", { class: "live-seg" }, view("focus", "Around: what it is linked to", "focus", n ? mapHref(n.id) : null),
      view("trace", "Layers: what connects to it", "layers", n ? mapHref(`layers:${n.id}`) : null),
      view("impact", "Impact: what stands on it", "impact", n ? mapHref(`impact:${n.id}`) : null)), tools);
}

// A node's page, here and in another tab
const mapOpen = (id) => [wayHere("document", `Open ${id}'s page`, nodeHref(id)), wayAway("document", `Open ${id}'s page`, nodeHref(id))];
const mapButton = (word, picture, did, on) => h("button", { type: "button", class: `mx-tool${on ? " on" : ""}`, onclick: did, title: word, "aria-label": word,
                                                           "aria-pressed": on === undefined ? null : String(on) }, icon(picture));
const mapShort = (n) => {
  const all = String(n.name || "").split(/\s+/).filter(Boolean);
  return all.slice(0, MAP_TAG.words).join(" ") + (all.length > MAP_TAG.words ? "…" : "");
};
const mapWide = (n) => MAP_TAG.pad + n.id.length * MAP_GLYPH.id + mapShort(n).length * (MAP_GLYPH.name - .9);

// A click that redraws the picture moves the node from under the pointer, so that the second click of a double one lands on what
// was behind it. A node with something else to do on a double click waits for it before it does anything.
//
// A node in a picture: its ID and the start of its name in a box, centred on where it stands. A right click opens its card,
// fetched only then; a picture that does something else with a click says so in `on`.
function mapTag(n, more) {
  const wide = mapWide(n), high = MAP_TAG.high;
  const { onclick: once, ondblclick: twice, ...on } = more.on || {};
  const first = once || (() => { location.hash = mapHref(n.id); });
  let waiting = 0;
  const clicked = (e) => {
    e.preventDefault();
    closeCard();
    if (!twice) { first(e); return; }
    clearTimeout(waiting);
    if (waiting) { waiting = 0; twice(e); return; }
    waiting = setTimeout(() => { waiting = 0; first(e); }, MAP_TWICE);
  };
  return svg("a", { class: `ref map-tag kind-${n.kind}${more.class ? ` ${more.class}` : ""}`, href: mapHref(n.id), "data-id": n.id, "aria-label": `${n.id} ${n.name || ""}${more.says ? ` -- ${more.says}` : ""}`,
                    ...on, onclick: clicked },
    svg("rect", { x: -wide / 2, y: -high / 2, width: wide, height: high, rx: 6 }),
    svg("text", { class: "map-tag-id", x: -wide / 2 + 9 }, n.id),
    svg("text", { class: "map-tag-name", x: -wide / 2 + 13 + n.id.length * MAP_GLYPH.id }, mapShort(n)));
}

// What a picture sits on: pan and zoom, fitted to what it holds until the reader moves it; on a sheet, flat
function mapStage(d3, label) {
  const picture = svg("svg", { class: `graph-map${SHEET ? " flat" : ""}`, "aria-label": label });
  const layer = svg("g", {});
  picture.append(layer);
  const stage = d3.select(picture);
  const quiet = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let moved = false;
  let box = null;
  const zoom = d3.zoom().scaleExtent([.05, 3]).wheelDelta(mapWheel).on("zoom", (e) => {
    layer.setAttribute("transform", e.transform);
    if (e.sourceEvent) moved = true;
  });
  const fit = (moving) => {
    if (!box || !picture.clientWidth) return;
    const scale = Math.min(1.25, .94 * Math.min(picture.clientWidth / box.wide, picture.clientHeight / box.tall));
    const view = d3.zoomIdentity.translate(picture.clientWidth / 2 - scale * (box.left + box.wide / 2), picture.clientHeight / 2 - scale * (box.top + box.tall / 2)).scale(scale);
    (moving && !quiet() ? stage.transition().duration(MAP_MOVE) : stage).call(zoom.transform, view);
  };
  const hold = (now, moving) => {
    box = now;
    if (SHEET) picture.setAttribute("viewBox", `${now.left - 8} ${now.top - 8} ${now.wide + 16} ${now.tall + 16}`);
    else if (!moved) fit(moving);
  };
  if (!SHEET) {
    stage.call(zoom).on("dblclick.zoom", null);
    requestAnimationFrame(() => {
      if (!picture.isConnected) return;
      fit(false);
      const sizes = new ResizeObserver(() => {
        if (!picture.isConnected) sizes.disconnect();
        else if (!moved) fit(false);
      });
      sizes.observe(picture);
    });
  }
  return { picture, layer, hold, refit: () => { moved = false; fit(true); } };
}

const mapMark = (id) => (id === mapState.last ? " selected" : "");
const mapSheet = (title, lead, picture) => [h("h1", {}, title), lead ? h("p", { class: "lead" }, lead) : null, picture];
const mapTool = (bar, stage) => h("div", { class: "live-tool" }, bar, h("div", { class: "graph-stage" }, stage));

// ---- the map

function mapAsk() {
  const open = [...mapState.open].map((k) => `${k}:${mapState.more.get(k) || MAP_CAP}`).join(",");
  return get(`map?open=${encodeURIComponent(open)}`);
}

// The kinds there are, in the order the menu has them
function mapKinds(data) {
  const order = ["document", ...GROUPS.flatMap(([, kinds]) => kinds)];
  const rank = (k) => (order.includes(k) ? order.indexOf(k) : order.length);
  return data.kinds.slice().sort((a, b) => rank(a.kind) - rank(b.kind) || a.kind.localeCompare(b.kind)).map(({ kind }, i, all) => {
    const place = mapState.at.get(kind) || { x: 300 * Math.cos((2 * Math.PI * i) / all.length), y: 300 * Math.sin((2 * Math.PI * i) / all.length) };
    return { kind, name: PLURAL[kind] || kind, count: 0, held: [], ...place };
  });
}

// What the server answered, laid over the kinds as they stand
function mapHeld(kinds, data) {
  const asked = new Map(data.kinds.map((k) => [k.kind, k]));
  for (const g of kinds) {
    g.count = asked.get(g.kind).count;
    g.held = asked.get(g.kind).nodes.slice().sort((a, b) => byId(a.id, b.id));
  }
}

// A kind's size, folded or open
function measure(g) {
  g.left = g.count - g.held.length;
  g.open = mapState.open.has(g.kind);
  g.r = 24 + 4.5 * Math.sqrt(Math.min(g.count, 900));
  if (!g.open) {
    g.w = Math.max(2 * g.r, g.name.length * MAP_GLYPH.name + 12);
    g.h = 2 * g.r + 44;                                         // its name is under it, and a kind's centre stays the bubble's
    return;
  }
  const many = g.held.length + (g.left > 0 ? 1 : 0);
  const { high, gap, pad, head } = MAP_BOX;
  g.cell = 16 + MAP_GLYPH.id * Math.max(5, ...g.held.map((n) => n.id.length));
  g.cols = Math.ceil(Math.sqrt(many * 1.6));
  const rows = Math.ceil(many / g.cols);
  g.w = Math.max(g.cols * (g.cell + gap) - gap + 2 * pad, (g.name.length + String(g.count).length) * MAP_GLYPH.head + 90);
  g.h = head + rows * (high + gap) - gap + pad + gap;
}

// Kinds side by side, not on top of each other: forceCollide holds circles, and a box is no circle
function keepApart(room) {
  let kinds = [];
  const force = () => {
    for (let i = 0; i < kinds.length; i++) {
      for (let j = i + 1; j < kinds.length; j++) {
        const a = kinds[i], b = kinds[j];
        const dx = b.x - a.x || 0.01, dy = b.y - a.y || 0.01;
        const over = { x: (a.w + b.w) / 2 + room - Math.abs(dx), y: (a.h + b.h) / 2 + room - Math.abs(dy) };
        if (over.x <= 0 || over.y <= 0) continue;
        const along = over.x / a.w < over.y / a.h ? "x" : "y";
        const shift = (over[along] / 2) * Math.sign(along === "x" ? dx : dy);
        a[along] -= a.fx === undefined ? shift : 0;
        b[along] += b.fx === undefined ? shift : 0;
      }
    }
  };
  force.initialize = (rows) => { kinds = rows; };
  return force;
}

// What the server says joins what is showing, each pair with how to say it
function mapLinks(data) {
  const label = (it) => (it.startsWith("kind:") ? PLURAL[it.slice(5)] || it.slice(5) : it);
  return data.links.map((l) => ({ ...l, key: `${l.a}|${l.b}`, says: l.count === 1 ? `${label(l.a)} ${Object.keys(l.rels)[0]} ${label(l.b)}` : `${label(l.a)} and ${label(l.b)}: ${l.count} links -- ` +
    Object.entries(l.rels).sort(([, x], [, y]) => y - x).map(([rel, n]) => `${rel} ${n}`).join(", ") }));
}

function mapBubble(g, toggle) {
  const said = `${g.name}, ${g.count}: open`;
  return svg("g", { class: `map-bubble map-toggle kind-${g.kind}`, tabindex: "0", role: "button", "aria-expanded": "false", "aria-label": said,
                    "data-item": `kind:${g.kind}`, "data-kind": g.kind, onclick: () => toggle(g),
                    onkeydown: (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(g, true); } } },
    svg("circle", { r: g.r }), svg("text", { class: "map-many" }, g.count), svg("text", { class: "map-name", y: g.r + 7 }, g.name));
}

function mapBox(g, toggle) {
  const { head } = MAP_BOX;
  const left = -g.w / 2, top = -g.h / 2;
  return svg("g", { class: `map-box kind-${g.kind}` },
    svg("rect", { class: "map-frame", x: left, y: top, width: g.w, height: g.h, rx: 8 }),
    svg("g", { class: "map-head map-toggle", tabindex: "0", role: "button", "aria-expanded": "true", "aria-label": `${g.name}, ${g.count}: fold`,
               "data-kind": g.kind, "data-item": `kind:${g.kind}`, onclick: () => toggle(g),
               onkeydown: (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(g, true); } } },
      svg("rect", { x: left + .7, y: top + .7, width: g.w - 1.4, height: head - .7, rx: 7 }),
      svg("text", { x: left + 12, y: top + head / 2 }, `${g.name} ${g.count}`),
      svg("text", { class: "map-fold", x: left + g.w - 12, y: top + head / 2 }, "Fold")));
}

// A node in its box: a right click shows its card, a click puts it in focus
function mapNode(n, g) {
  const { high } = MAP_BOX;
  return svg("a", { class: `ref map-node kind-${g.kind}${mapMark(n.id)}`, href: mapHref(n.id), "aria-label": `${n.id} ${n.name || ""}`.trim(), "data-item": n.id, "data-id": n.id },
    svg("rect", { x: -g.cell / 2, y: -high / 2, width: g.cell, height: high, rx: 5 }), svg("text", {}, n.id));
}

// The tile that holds the rest of a kind: it says how many, and shows more
function mapMore(g, more) {
  const { high } = MAP_BOX;
  return svg("g", { class: "map-more map-toggle", tabindex: "0", role: "button", "aria-label": `Show more of ${g.count} ${g.name}`, onclick: () => more(g),
                    onkeydown: (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); more(g); } } },
    svg("title", {}, `The most linked ${g.held.length} of ${g.count} show. Click for more, or see them all in the Matrix.`),
    svg("rect", { x: -g.cell / 2, y: -high / 2, width: g.cell, height: high, rx: 5 }), svg("text", {}, `+${g.left}`));
}

async function wholeGraph() {
  const d3 = await loadD3();
  let data = await mapAsk();
  const kinds = mapKinds(data);
  mapHeld(kinds, data);
  const home = new Map();
  const rehome = () => { home.clear(); for (const g of kinds) for (const n of g.held) home.set(n.id, g); };
  rehome();
  // Only the newest answer counts: a double click asks twice, and an older answer that came late would draw a state already left
  let asked = 0;
  const refresh = async () => {
    const turn = ++asked;
    const answer = await mapAsk();
    if (turn !== asked) return false;
    data = answer;
    mapHeld(kinds, data);
    rehome();
    return true;
  };

  const picture = svg("svg", { class: `graph-map${SHEET ? " flat" : ""}`, "aria-label": "Every kind of the specification and how they are linked" });
  const [lines, boxes, tallies, items] = [0, 1, 2, 3].map(() => svg("g", {}));   // a box over the lines, so that its title reads
  const layer = svg("g", {}, lines, boxes, tallies, items);
  picture.append(layer);
  const stage = d3.select(picture);
  const quiet = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // The kinds laid out: the more two are linked, the closer they stand; a kind dragged stays where it was put
  const arrange = (heat) => {
    kinds.forEach(measure);
    const reach = (g) => Math.max(g.w, g.h) / 2;
    const apart = keepApart(MAP_BOX.apart);
    const kindOf = (item) => (item.startsWith("kind:") ? item.slice(5) : home.get(item).kind);
    const joined = new Map();
    for (const l of data.links) {
      const [a, b] = [kindOf(l.a), kindOf(l.b)].sort();
      if (a !== b) joined.set(`${a}|${b}`, { source: a, target: b, count: (joined.get(`${a}|${b}`) || { count: 0 }).count + l.count });
    }
    const forces = d3.forceSimulation(kinds).stop().alpha(heat)
      .force("linked", d3.forceLink([...joined.values()]).id((g) => g.kind).distance((p) => reach(p.source) + reach(p.target) + 50)
        .strength((p) => Math.min(.5, .05 + Math.log1p(p.count) / 16)))
      .force("spread", d3.forceManyBody().strength((g) => -500 - reach(g) * 9).distanceMax(800))
      .force("x", d3.forceX(0).strength(.07)).force("y", d3.forceY(0).strength(.13))
      .force("apart", apart);
    forces.tick(MAP_TICKS);
    for (let i = 0; i < 60; i++) apart();                       // the forces end with no two kinds touching
    kinds.forEach((g) => mapState.at.set(g.kind, { x: g.x, y: g.y, ...(g.fx === undefined ? {} : { fx: g.fx, fy: g.fy }) }));
  };

  // Where each thing shown stands
  const spot = (key) => {
    if (key.startsWith("kind:")) return kinds.find((g) => g.kind === key.slice(5));
    const g = key.startsWith("more:") ? kinds.find((k) => k.kind === key.slice(5)) : home.get(key);
    const i = key.startsWith("more:") ? g.held.length : g.held.findIndex((n) => n.id === key);
    const { high, gap, pad, head } = MAP_BOX;
    return { x: g.x - g.w / 2 + pad + (i % g.cols + .5) * (g.cell + gap) - gap / 2,
             y: g.y - g.h / 2 + head + gap + (Math.floor(i / g.cols) + .5) * (high + gap) - gap / 2 };
  };
  let spots = new Map();
  const at = (key) => {
    if (!spots.has(key)) spots.set(key, spot(key));
    return spots.get(key);
  };
  const setBox = (s) => s.attr("transform", (g) => `translate(${g.x},${g.y})`);
  const setItem = (s) => s.attr("transform", (d) => `translate(${at(d.key).x},${at(d.key).y})`);
  const setLine = (s) => s.attr("x1", (l) => at(l.a).x).attr("y1", (l) => at(l.a).y).attr("x2", (l) => at(l.b).x).attr("y2", (l) => at(l.b).y);
  const setTally = (s) => s.attr("x", (l) => (at(l.a).x + at(l.b).x) / 2).attr("y", (l) => (at(l.a).y + at(l.b).y) / 2);
  const everything = () => [[d3.select(boxes).selectChildren(), setBox], [d3.select(items).selectChildren(), setItem],
    [d3.select(lines).selectChildren(), setLine], [d3.select(tallies).selectChildren(), setTally]];
  const place = (moving) => {
    spots = new Map();
    for (const [chosen, set] of everything()) (moving ? chosen.transition().duration(MAP_MOVE) : chosen).call(set);
  };

  // A kind dragged moves with what it holds, and only the lines that reach it are drawn again
  const dragged = d3.drag().clickDistance(4).on("drag", (e, d) => {
    const g = d.group || d;
    g.x = g.fx = g.x + e.dx;
    g.y = g.fy = g.y + e.dy;
    mapState.at.set(g.kind, { x: g.x, y: g.y, fx: g.fx, fy: g.fy });
    spots = new Map();
    d3.select(boxes).selectChildren().filter((b) => b === g).call(setBox);
    d3.select(items).selectChildren().filter((i) => i.group === g).call(setItem);
    const moved = (l) => [l.a, l.b].some((key) => (key.startsWith("kind:") ? key.slice(5) === g.kind : home.get(key) === g));
    d3.select(lines).selectChildren().filter(moved).call(setLine);
    d3.select(tallies).selectChildren().filter(moved).call(setTally);
  });

  let shown = [];

  // What shows, drawn: a thing that stays moves to where it now stands, one that is new is simply there
  const draw = (moving) => {
    spots = new Map();
    shown = mapLinks(data);
    const list = kinds.flatMap((g) => (g.open
      ? [...g.held.map((n) => ({ key: n.id, n, group: g })), ...(g.left > 0 ? [{ key: `more:${g.kind}`, group: g, tile: true }] : [])]
      : [{ key: `kind:${g.kind}`, group: g, bubble: true }]));
    d3.select(boxes).selectChildren().data(kinds.filter((g) => g.open), (g) => g.kind)
      .join((enter) => enter.append((g) => mapBox(g, toggle)).call(setBox));
    d3.select(boxes).selectChildren().select(".map-frame").attr("x", (g) => -g.w / 2).attr("y", (g) => -g.h / 2).attr("width", (g) => g.w).attr("height", (g) => g.h);
    d3.select(boxes).selectChildren().select(".map-head").call(SHEET ? () => {} : dragged);
    d3.select(items).selectChildren().data(list, (d) => d.key)
      .join((enter) => enter.append((d) => (d.bubble ? mapBubble(d.group, toggle) : d.tile ? mapMore(d.group, more) : mapNode(d.n, d.group))).call(setItem));
    if (!SHEET) d3.select(items).selectChildren().filter((d) => d.bubble).call(dragged);
    d3.select(lines).selectChildren().data(shown, (l) => l.key)
      .join((enter) => enter.append((l) => svg("line", { class: "map-link", "stroke-width": Math.min(1 + Math.log2(l.count), 6) }, svg("title", {}, l.says))).call(setLine));
    d3.select(tallies).selectChildren().data(shown.filter((l) => l.count > 1), (l) => l.key)
      .join((enter) => enter.append((l) => svg("text", { class: `map-tally${l.a.startsWith("kind:") && l.b.startsWith("kind:") ? "" : " only-lit"}` }, l.count)).call(setTally));
    place(moving && !quiet());
  };

  const bounds = () => {
    const edge = (side) => kinds.map(side);
    const left = Math.min(...edge((g) => g.x - g.w / 2)), right = Math.max(...edge((g) => g.x + g.w / 2));
    const top = Math.min(...edge((g) => g.y - g.h / 2)), bottom = Math.max(...edge((g) => g.y + g.h / 2));
    return { left, top, wide: right - left, tall: bottom - top };
  };

  const zoom = d3.zoom().scaleExtent([.05, 3]).wheelDelta(mapWheel).on("zoom", (e) => {
    layer.setAttribute("transform", e.transform);
    mapState.seen = e.transform;
    if (e.sourceEvent) mapState.moved = true;                   // the reader's own view: nothing refits it but Fit
  });
  const fit = (moving) => {
    const { left, top, wide, tall } = bounds();
    const room = { wide: picture.clientWidth, tall: picture.clientHeight };
    const scale = Math.min(1.5, .95 * Math.min(room.wide / wide, room.tall / tall));
    const view = d3.zoomIdentity.translate(room.wide / 2 - scale * (left + wide / 2), room.tall / 2 - scale * (top + tall / 2)).scale(scale);
    (moving && !quiet() ? stage.transition().duration(MAP_MOVE) : stage).call(zoom.transform, view);
  };

  const refit = () => { mapState.moved = false; fit(true); };

  // Opened or folded: only what that changes is asked for, the kinds laid out again from where they stand, and all of it
  // fitted, unless the reader has moved the view to look at something
  async function toggle(g, byKey) {
    if (mapState.open.has(g.kind)) mapState.open.delete(g.kind); else mapState.open.add(g.kind);
    keep(MAP_OPEN, [...mapState.open].join(","));
    if (!(await refresh())) return;
    arrange(.4);
    draw(true);
    if (!mapState.moved) fit(true);
    if (byKey) items.parentNode.querySelector(`.map-toggle[data-kind="${CSS.escape(g.kind)}"]`).focus({ preventScroll: true });
  }

  // More of a kind: twice what it shows
  async function more(g) {
    mapState.more.set(g.kind, (mapState.more.get(g.kind) || MAP_CAP) * 2);
    if (!(await refresh())) return;
    arrange(.2);
    draw(true);
  }

  const all = async (open) => {
    for (const g of kinds) { delete g.fx; delete g.fy; if (open) mapState.open.add(g.kind); else mapState.open.delete(g.kind); }
    keep(MAP_OPEN, [...mapState.open].join(","));
    if (!(await refresh())) return;
    arrange(1);
    draw(true);
    refit();
  };

  // What is pointed at, or focused, lights what it is linked to and fades the rest
  const light = (key) => {
    const near = new Set([key]);
    for (const l of shown) { if (l.a === key) near.add(l.b); if (l.b === key) near.add(l.a); }
    const touches = (l) => l.a === key || l.b === key;
    d3.select(lines).selectChildren().classed("lit", touches);
    d3.select(tallies).selectChildren().classed("lit", touches);
    d3.select(items).selectChildren().classed("lit", (d) => near.has(d.key));
    picture.classList.add("focusing");
  };
  const unlit = () => picture.classList.remove("focusing");
  const pointed = (e) => (e.target.closest ? e.target.closest("[data-item]") : null);
  for (const [on, off] of [["pointerover", "pointerout"], ["focusin", "focusout"]]) {
    items.addEventListener(on, (e) => { const it = pointed(e); if (it) light(it.dataset.item); });
    items.addEventListener(off, unlit);
  }

  arrange(mapState.at.size === kinds.length ? .02 : 1);
  draw(false);

  if (SHEET) {
    const { left, top, wide, tall } = bounds();
    picture.setAttribute("viewBox", `${left - 8} ${top - 8} ${wide + 16} ${tall + 16}`);
    return mapSheet("Graph", `${counted(data.nodes, "node", "nodes")} in ${counted(kinds.length, "kind", "kinds")}, joined by ${counted(data.total, "link", "links")}.`, picture);
  }

  stage.call(zoom).on("dblclick.zoom", null);
  requestAnimationFrame(() => {
    if (!picture.isConnected) return;
    if (mapState.seen) stage.call(zoom.transform, mapState.seen); else fit(false);
    const sizes = new ResizeObserver(() => {
      if (!picture.isConnected) sizes.disconnect();
      else if (!mapState.moved) fit(false);
    });
    sizes.observe(picture);
  });

  return mapTool(mapBar("map", "Graph",
    h("span", { class: "live-seg" }, mapButton("Open every kind", "expand", () => all(true)), mapButton("Fold every kind", "collapse", () => all(false)), mapButton("Fit it to the window", "fit", refit)),
    h("span", { class: "graph-count" }, `${counted(data.nodes, "node", "nodes")}, ${counted(data.total, "link", "links")}`)), picture);
}

// ---- focus: one node and what it is linked to, and nothing else

async function focusGraph(asked) {
  const d3 = await loadD3();
  const first = await get(`map/around?id=${encodeURIComponent(asked)}`);
  const id = first.centre.id;
  mapPick(first.centre);
  const nodes = new Map([[id, { ...first.centre, x: 0, y: 0, fx: 0, fy: 0, centre: true }]]);
  const links = new Map();
  const spread = new Set();
  const left = new Map();                                       // how many more each spread node has than it shows
  let way = "both";

  const add = (found) => {
    const at = nodes.get(found.centre.id);
    const kinds = [...new Set(found.neighbours.map((n) => n.kind))];
    for (const n of found.neighbours) {
      const angle = (2 * Math.PI * kinds.indexOf(n.kind)) / Math.max(kinds.length, 1) + (at.centre ? 0 : Math.atan2(at.y, at.x));
      if (!nodes.has(n.id)) nodes.set(n.id, { ...n, x: at.x + 40 * Math.cos(angle) + Math.random(), y: at.y + 40 * Math.sin(angle) + Math.random(), tx: at.x + 300 * Math.cos(angle), ty: at.y + 300 * Math.sin(angle) });
      const key = [found.centre.id, n.id].sort().join("|");
      const was = links.get(key);
      const towards = found.centre.id === key.split("|")[0];    // said from the end that sorts first
      links.set(key, { key, a: key.split("|")[0], b: key.split("|")[1], rels: { ...(was || {}).rels, ...n.rels }, forth: (was || {}).forth || (towards ? n.out : n.in), back: (was || {}).back || (towards ? n.in : n.out) });
    }
    spread.add(found.centre.id);
    left.set(found.centre.id, found.left);
  };
  add(first);

  const { picture, layer, hold, refit } = mapStage(d3, `${id} and what it is linked to`);
  const said = h("span", { class: "graph-count", "aria-live": "polite" });

  // What the direction chosen reaches from the middle
  const reached = () => {
    const seen = new Set([id]);
    const kept = [];
    const next = [id];
    while (next.length) {
      const at = next.shift();
      for (const l of links.values()) {
        if (l.a !== at && l.b !== at) continue;
        const other = l.a === at ? l.b : l.a;
        const out = l.a === at ? l.forth : l.back, into = l.a === at ? l.back : l.forth;
        if (way === "out" ? !out : way === "in" ? !into : false) continue;
        if (!kept.includes(l)) kept.push(l);
        if (!seen.has(other)) { seen.add(other); next.push(other); }
      }
    }
    return { seen, kept };
  };

  const lay = () => {
    const { seen, kept } = reached();
    const list = [...nodes.values()].filter((n) => seen.has(n.id));
    for (const n of list) { n.w = mapWide(n) + 8; n.h = MAP_TAG.high + 8; }
    const lines = kept.map((l) => ({ ...l, source: l.a, target: l.b }));
    const forces = d3.forceSimulation(list).stop().alpha(.9)
      .force("linked", d3.forceLink(lines).id((n) => n.id).distance(190).strength(.5))
      .force("spread", d3.forceManyBody().strength(-700).distanceMax(600))
      .force("x", d3.forceX((n) => n.tx ?? n.x).strength(.12)).force("y", d3.forceY((n) => n.ty ?? n.y).strength(.12))
      .force("apart", keepApart(10));
    forces.tick(220);
    const apart = keepApart(10);
    apart.initialize(list);
    for (let i = 0; i < 40; i++) apart();
    return { list, lines };
  };

  let shown = { list: [], lines: [] };
  const lit = (at, on) => {
    picture.classList.toggle("focusing", on);
    const near = new Set([at]);
    for (const line of layer.querySelectorAll(".map-link")) {
      const hit = on && line.dataset.a === at || on && line.dataset.b === at;
      line.classList.toggle("lit", hit);
      if (hit) { near.add(line.dataset.a); near.add(line.dataset.b); }
    }
    for (const tag of layer.querySelectorAll(".map-tag")) tag.classList.toggle("lit", on && near.has(tag.dataset.id));
    for (const word of layer.querySelectorAll(".map-rel")) word.classList.toggle("lit", on && (word.dataset.a === at || word.dataset.b === at));
  };

  const draw = () => {
    picture.classList.remove("focusing");                       // what was pointed at is drawn anew, and no pointer leaves it
    const words = shown.lines.length <= 40;
    const lines = shown.lines.map((l) => {
      const rels = Object.entries(l.rels).map(([rel, n]) => (n > 1 ? `${rel} ${n}` : rel)).join(", ");
      return [svg("line", { class: "map-link", "data-a": l.source.id, "data-b": l.target.id, x1: l.source.x, y1: l.source.y, x2: l.target.x, y2: l.target.y }, svg("title", {}, `${l.source.id} ${rels} ${l.target.id}`)),
        svg("text", { class: `map-rel${words ? "" : " only-lit"}`, "data-a": l.source.id, "data-b": l.target.id, x: (l.source.x + l.target.x) / 2, y: (l.source.y + l.target.y) / 2 }, rels)];
    });
    const tags = shown.list.map((n) => {
      const tag = mapTag(n, { class: `${n.centre ? "centre" : ""}${spread.has(n.id) && !n.centre ? " spread" : ""}${n.fx !== undefined && !n.centre ? " pinned" : ""}`,
                              says: n.centre ? "the middle" : spread.has(n.id) ? "click to take back what it spreads, double click to put it in the middle" : "click to spread its links, double click to put it in the middle",
                              on: { onclick: () => toggle(n), ondblclick: () => { location.hash = mapHref(n.id); },
                                    onmouseenter: () => lit(n.id, true), onmouseleave: () => lit(n.id, false), onfocus: () => lit(n.id, true), onblur: () => lit(n.id, false),
                                    onkeydown: (e) => { if (e.key === "Enter") location.hash = mapHref(n.id); else if (e.key === " ") { e.preventDefault(); toggle(n); } } } });
      tag.setAttribute("transform", `translate(${n.x},${n.y})`);
      return tag;
    });
    layer.replaceChildren(...lines.flat(), ...tags);
    if (!SHEET) d3.select(layer).selectAll(".map-tag").data(shown.list).call(drag);
    const edge = (side) => shown.list.map(side);
    const x0 = Math.min(...edge((n) => n.x - n.w / 2)), x1 = Math.max(...edge((n) => n.x + n.w / 2));
    const y0 = Math.min(...edge((n) => n.y - n.h / 2)), y1 = Math.max(...edge((n) => n.y + n.h / 2));
    hold({ left: x0, top: y0, wide: x1 - x0, tall: y1 - y0 }, true);
    const hidden = [...left.values()].reduce((sum, n) => sum + n, 0);
    said.textContent = `${counted(shown.list.length - 1, "node", "nodes")} around ${id}${hidden ? `, ${hidden} more in the Matrix` : ""}`;
  };

  // A node dragged stays where it is put
  const drag = d3.drag().clickDistance(4).on("drag", (e, n) => {
    if (n.centre) return;
    n.x = n.fx = n.x + e.dx;
    n.y = n.fy = n.y + e.dy;
    draw();
  });

  const again = () => { shown = lay(); draw(); };

  async function toggle(n) {
    if (n.centre) return;
    if (spread.has(n.id)) {                                     // what it brought in, and nothing else reaches, goes
      spread.delete(n.id);
      left.delete(n.id);
      for (const l of [...links.values()]) {
        const other = l.a === n.id ? l.b : l.b === n.id ? l.a : null;
        if (other && !spread.has(other)) links.delete(l.key);
      }
      for (const m of [...nodes.keys()]) if (![...links.values()].some((l) => l.a === m || l.b === m) && m !== id) nodes.delete(m);
    } else add(await get(`map/around?id=${encodeURIComponent(n.id)}`));
    again();
  }

  async function steps(two) {
    if (two) {
      const near = first.neighbours.filter((n) => !spread.has(n.id)).slice(0, 30);
      (await Promise.all(near.map((n) => get(`map/around?id=${encodeURIComponent(n.id)}`)))).forEach(add);
    } else {
      for (const m of [...spread]) if (m !== id) await toggle(nodes.get(m));
    }
    again();
    refit();
  }

  again();
  if (SHEET) return mapSheet(`${id} ${first.centre.name || ""}`.trim(), said.textContent, picture);

  const ways = (word, picture, name) => mapButton(word, picture, (e) => {
    way = name;
    e.currentTarget.parentNode.querySelectorAll("button").forEach((b) => { b.classList.toggle("on", b === e.currentTarget); b.setAttribute("aria-pressed", String(b === e.currentTarget)); });
    again();
    refit();
  }, way === name);
  const counts = (word, picture, two) => mapButton(word, picture, () => steps(two));
  return mapTool(mapBar("focus", `The graph around ${id}`,
    h("span", { class: "live-seg" }, ways("Links both ways", "both", "both"), ways("Links out of it", "arrow", "out"), ways("Links into it", "back", "in")),
    h("span", { class: "live-seg" }, counts("One step from the middle", "hop1", false), counts("Two steps from the middle", "hop2", true), mapButton("Fit it to the window", "fit", refit),
      mapOpen(id)), said), picture);
}

// ---- impact: what stands on a node, and what stands on those

async function impactGraph(asked) {
  const d3 = await loadD3();
  const ask = (id) => get(`map/stands?id=${encodeURIComponent(id)}`);
  const first = await ask(asked);
  const id = first.node.id;
  mapPick(first.node);
  const root = { ...first.node, next: first.stands.length + first.more, kids: first.stands.map((n) => ({ ...n })), more: first.more, opened: true };
  const { picture, layer, hold, refit } = mapStage(d3, `What stands on ${id}`);
  const said = h("span", { class: "graph-count", "aria-live": "polite" });
  const STEP = 300;

  const draw = () => {
    const tree = d3.hierarchy(root, (d) => (d.opened ? d.kids : null));
    d3.tree().nodeSize([MAP_TAG.high + 12, STEP])(tree);
    const seen = tree.descendants();
    const line = d3.linkHorizontal().x((d) => d.y).y((d) => d.x);
    const lines = tree.links().map((l) => svg("path", { class: "map-link", d: line(l) },
      svg("title", {}, `${l.target.data.id} ${Object.keys(l.target.data.rels || {}).join(", ")} ${l.source.data.id}`)));
    const tags = seen.flatMap((d) => {
      const n = d.data;
      const looped = d.ancestors().slice(1).some((a) => a.data.id === n.id);
      const tag = mapTag(n, { class: `${d.depth ? "" : "centre"}${n.opened && d.depth ? " spread" : ""}${looped ? " looped" : ""}`,
                              says: looped ? "already on this branch" : n.next ? `${n.next} stand on it: click to open` : "nothing stands on it",
                              on: { onclick: () => toggle(n, looped), ondblclick: () => { location.hash = mapHref(`impact:${n.id}`); },
                                    onkeydown: (e) => { if (e.key === "Enter") toggle(n, looped); } } });
      tag.setAttribute("transform", `translate(${d.y},${d.x})`);
      const count = n.next && !n.opened && !looped
        ? svg("text", { class: "map-next", x: d.y + mapWide(n) / 2 + 8, y: d.x }, `+${n.next}`) : null;
      const rest = n.opened && n.more ? svg("text", { class: "map-next", x: d.y + mapWide(n) / 2 + 8, y: d.x + 16 }, `${n.more} more in the Matrix`) : null;
      return [tag, count, rest].filter(Boolean);
    });
    layer.replaceChildren(...lines, ...tags);
    const y0 = Math.min(...seen.map((d) => d.x)) - 24, y1 = Math.max(...seen.map((d) => d.x)) + 24;
    const x1 = Math.max(...seen.map((d) => d.y + mapWide(d.data))) + 60;
    hold({ left: -mapWide(root), top: y0, wide: x1 + mapWide(root), tall: y1 - y0 }, true);
    said.textContent = first.stands.length + first.more
      ? `${counted(first.stands.length + first.more, "node stands", "nodes stand")} on ${id}`
      : `Nothing stands on ${id}`;
  };

  async function toggle(n, looped) {
    if (looped || !n.next) return;
    if (n.opened) n.opened = false;
    else {
      if (!n.kids) {
        const found = await ask(n.id);
        n.kids = found.stands.map((m) => ({ ...m }));
        n.more = found.more;
      }
      n.opened = true;
    }
    draw();
  }

  draw();
  if (SHEET) return mapSheet(`What stands on ${id}`, said.textContent, picture);
  return mapTool(mapBar("impact", `What stands on ${id}`,
    h("span", { class: "live-seg" }, mapButton("Fit it to the window", "fit", refit),
      mapOpen(id)), said), picture);
}

// ---- layers: the kinds left to right in the top menu's order

// One picture at any size. A kind is a block, and bands between blocks say how many links join them, so the whole specification
// is there however large it is. A block or a band clicked opens to that kind's most linked nodes, and the wheel over them goes on
// down the kind, asking only for the rows it shows; a column can be hidden. On a small specification the nodes are open from the
// start. With a node, #/graph/layers:R4, it holds only what connects to that node, column by column, and the links come first:
// the rows stand beside what they link to, the links the trace walked are drawn strong, that node's own the strongest, and the
// rest wait for a pause on a node that has them.
function mapLayerNodes(kinds) { return kinds.reduce((sum, k) => sum + k.count, 0); }

async function layersGraph(asked) {
  const d3 = await loadD3();
  const windows = () => [...layerState.open].map((k) => `${k}:${MAP_LAYER_CAP}@${layerState.at.get(k) || 0}`).join(",");
  const ask = () => (asked ? get(`map/layers?id=${encodeURIComponent(asked)}&steps=${mapState.steps}`) : get(`map?open=${encodeURIComponent(windows())}`));
  if (!asked && !layerState.open) {
    const first = await get("map");
    const held = new Set(first.layers.flat());
    const small = mapLayerNodes(first.kinds.filter((k) => held.has(k.kind))) <= MAP_LAYER_SMALL;
    layerState.open = new Set(small ? held : []);
  }
  let data = await ask();
  const anchor = asked ? data.node.id : "";
  if (anchor) mapPick(data.node);
  const { picture, layer, hold, refit } = mapStage(d3, anchor ? `What connects to ${anchor}, layer by layer` : "The specification in layers");
  const { wide: WIDE, gap: GAP, row: ROW, head: HEAD, strip: STRIP } = MAP_LAYER;
  const opened = (kind) => !!anchor || layerState.open.has(kind);

  const lit = (at, on) => {
    picture.classList.toggle("focusing", on);
    const near = new Set([at]);
    for (const line of layer.querySelectorAll(".map-link")) {
      const hit = on && (line.dataset.a === at || line.dataset.b === at);
      line.classList.toggle("lit", hit);
      if (hit) { near.add(line.dataset.a); near.add(line.dataset.b); }
    }
    for (const tag of layer.querySelectorAll(".map-tag")) tag.classList.toggle("lit", on && near.has(tag.dataset.id));
  };

  const again = async () => { data = await ask(); draw(false); };
  const toggle = async (...kinds) => {
    const shut = kinds.every((k) => layerState.open.has(k));
    for (const k of kinds) { if (shut) layerState.open.delete(k); else layerState.open.add(k); }
    await again();
  };
  const everything = async (open) => {
    layerState.open = new Set(open ? data.layers.flat() : []);
    await again();
  };
  const hide = (key) => {
    if (layerState.hidden.has(key)) layerState.hidden.delete(key); else layerState.hidden.add(key);
    keep(MAP_LAYER_HIDDEN, [...layerState.hidden].join(","));
    draw(true);
  };

  // The wheel over an open kind goes on down it: the rows it shows are asked for when the wheel pauses
  let waiting = 0;
  const scroll = (e, kind, count) => {
    e.preventDefault();
    e.stopPropagation();
    const now = layerState.at.get(kind) || 0;
    const next = Math.max(0, Math.min(Math.max(0, count - MAP_LAYER_CAP), now + Math.sign(e.deltaY) * MAP_LAYER.step));
    if (next === now) return;
    layerState.at.set(kind, next);
    const range = layer.querySelector(`[data-range="${CSS.escape(kind)}"]`);
    if (range) range.textContent = `${next + 1}-${Math.min(count, next + MAP_LAYER_CAP)} of ${count}`;
    clearTimeout(waiting);
    waiting = setTimeout(again, MAP_LAYER.quiet);
  };

  function draw(moving) {
    picture.classList.remove("focusing");
    const kinds = new Map(data.kinds.map((k) => [k.kind, k]));
    const columns = data.layers.map((held) => held.filter((k) => kinds.has(k) && kinds.get(k).count)).filter((held) => held.length);
    const place = new Map();
    const sections = [];
    let x = 0, tallest = 0;
    for (const held of columns) {
      const key = held[0];
      const hidden = layerState.hidden.has(key);
      const named = held.map((k) => PLURAL[k] || k).join(", ");
      if (hidden) {
        sections.push({ strip: true, key, x, named });
        x += STRIP + 40;
        continue;
      }
      let y = 0;
      const column = [];
      for (const kind of held) {
        const k = kinds.get(kind);
        const open = opened(kind) && k.nodes.length > 0;
        const block = open ? HEAD : Math.max(HEAD, Math.min(MAP_LAYER.tallest, 14 * Math.sqrt(k.count)));
        const part = { kind, k, open, x, y, block, rows: open ? k.nodes.length : 0 };
        column.push(part);
        y += block + part.rows * ROW + 14;
      }
      sections.push({ key, x, column, named, tall: y - 14 });
      tallest = Math.max(tallest, y - 14);
      x += WIDE + GAP;
    }
    const left = x - GAP;

    // Where each thing stands, the columns centred on the tallest
    for (const s of sections) {
      if (s.strip) continue;
      const shift = (tallest - s.tall) / 2;
      for (const part of s.column) {
        part.y += shift;
        place.set(`kind:${part.kind}`, { x: part.x + WIDE / 2, y: part.y + part.block / 2, half: WIDE / 2, col: s.key });
        part.k.nodes.forEach((n, i) => {
          if (part.open) place.set(n.id, { x: part.x + WIDE / 2, y: part.y + HEAD + ROW * (i + .5), half: mapWide(n) / 2, col: s.key, n });
        });
      }
    }

    const most = Math.max(1, ...data.links.filter((l) => l.a.startsWith("kind:") && l.b.startsWith("kind:")).map((l) => l.count));
    picture.classList.toggle("dense", !!anchor && data.links.filter((l) => l.walked !== false).length > MAP_LAYER.dense);
    const own = (l) => l.a === anchor || l.b === anchor;
    const weight = (l) => (l.walked === false ? 0 : own(l) ? 2 : 1);     // the strongest on top
    const lines = [...data.links].sort((l, m) => weight(l) - weight(m)).flatMap((l) => {
      const p = place.get(l.a), q = place.get(l.b);
      if (!p || !q || p.col === q.col) return [];
      const [a, b] = p.x < q.x ? [p, q] : [q, p];
      const middle = (a.x + a.half + b.x - b.half) / 2;
      const d = `M${a.x + a.half} ${a.y} C${middle} ${a.y} ${middle} ${b.y} ${b.x - b.half} ${b.y}`;
      const says = `${Object.entries(l.rels).map(([rel, n]) => `${rel} ${n}`).join(", ")}`;
      const both = l.a.startsWith("kind:") && l.b.startsWith("kind:");
      const name = (item) => (item.startsWith("kind:") ? PLURAL[item.slice(5)] || item.slice(5) : item);
      const sort = !anchor ? "" : l.walked === false ? " aside" : own(l) ? " trace own" : " trace";
      if (!both) return [svg("path", { class: `map-link${sort}`, "data-a": l.a, "data-b": l.b, d }, svg("title", {}, `${name(l.a)} and ${name(l.b)}: ${says}`))];
      const kindsOf = [l.a.slice(5), l.b.slice(5)];
      return [svg("path", { class: `map-band kind-${p.x < q.x ? kindsOf[0] : kindsOf[1]}`, d, "stroke-width": 1.5 + 22 * Math.log1p(l.count) / Math.log1p(most),
                            onclick: anchor ? null : () => toggle(...kindsOf) },
        svg("title", {}, `${name(l.a)} and ${name(l.b)}: ${counted(l.count, "link", "links")}, ${says}. ${anchor ? "" : "Click to see their nodes."}`))];
    });

    const drawn = sections.flatMap((s) => {
      if (s.strip) {
        return [svg("g", { class: "map-strip map-toggle", tabindex: "0", role: "button", "aria-label": `Show ${s.named}`, onclick: () => hide(s.key),
                           onkeydown: (e) => { if (e.key === "Enter") hide(s.key); } },
          svg("rect", { x: s.x, y: 0, width: STRIP, height: tallest, rx: 6 }),
          svg("title", {}, `${s.named}: click to show`),
          svg("text", { transform: `translate(${s.x + STRIP / 2},${tallest / 2}) rotate(-90)` }, s.named))];
      }
      const hider = svg("g", { class: "map-hide map-toggle", tabindex: "0", role: "button", "aria-label": `Hide ${s.named}`, onclick: () => hide(s.key),
                               onkeydown: (e) => { if (e.key === "Enter") hide(s.key); } },
        svg("title", {}, `Hide ${s.named}`), svg("text", { x: s.x + WIDE, y: -14 }, "Hide"));
      return [hider, ...s.column.flatMap((part) => {
        const { kind, k, open, x: px, y: py, block } = part;
        const from = layerState.at.get(kind) || 0;
        const range = anchor ? `${k.nodes.length} of ${k.count}` : open ? `${from + 1}-${from + k.nodes.length} of ${k.count}` : `${k.count}`;
        const head = svg("g", { class: `map-block map-toggle kind-${kind}${open ? " open" : ""}`, tabindex: "0", role: "button", "aria-expanded": String(open),
                                "aria-label": `${PLURAL[kind] || kind}, ${k.count}`, onclick: anchor ? null : () => toggle(kind),
                                onkeydown: (e) => { if (e.key === "Enter" && !anchor) toggle(kind); } },
          svg("rect", { x: px, y: py, width: WIDE, height: block, rx: 7 }),
          svg("text", { class: "map-block-name", x: px + 12, y: py + (open ? HEAD / 2 : block / 2) }, PLURAL[kind] || kind),
          svg("text", { class: "map-block-range", x: px + WIDE - 12, y: py + (open ? HEAD / 2 : block / 2), "data-range": kind }, range));
        if (!open) return [head];
        const body = svg("rect", { class: "map-section", x: px, y: py + HEAD, width: WIDE, height: part.rows * ROW });
        const wheel = !anchor && k.count > MAP_LAYER_CAP ? (e) => scroll(e, kind, k.count) : null;
        const tags = k.nodes.map((n) => {
          const at = place.get(n.id);
          const tag = mapTag(n, { class: n.id === anchor ? "centre" : mapMark(n.id).trim(), says: "click to see what connects to it, double click to focus on it",
                                  on: { onclick: () => { location.hash = mapHref(`layers:${n.id}`); }, ondblclick: () => { location.hash = mapHref(n.id); },
                                        onmouseenter: () => lit(n.id, true), onmouseleave: () => lit(n.id, false), onfocus: () => lit(n.id, true), onblur: () => lit(n.id, false) } });
          tag.setAttribute("transform", `translate(${at.x},${at.y})`);
          return tag;
        });
        return [svg("g", wheel ? { onwheel: wheel } : {}, body, ...tags), head];
      })];
    });
    const heads = sections.filter((s) => !s.strip).map((s) => svg("text", { class: "map-layer", x: s.x, y: -14 }, s.named));
    layer.replaceChildren(...lines, ...drawn, ...heads);
    hold({ left: -12, top: -40, wide: left + 24, tall: tallest + 60 }, moving);
  }

  draw(false);
  if (SHEET) return mapSheet(anchor ? `Layers of ${anchor}` : "Layers", "", picture);
  const step = (word, picture, steps) => mapButton(word, picture, async (e) => {
    const button = e.currentTarget;
    mapState.steps = steps;
    button.parentNode.querySelectorAll("[data-steps]").forEach((b) => { b.classList.toggle("on", b === button); b.setAttribute("aria-pressed", String(b === button)); });
    await again();
    refit();
  }, mapState.steps === steps);
  const stepping = (word, picture, steps) => { const b = step(word, picture, steps); b.dataset.steps = steps; return b; };
  return mapTool(mapBar(anchor ? "trace" : "layers", anchor ? `Layers of ${anchor}` : "Layers",
    anchor ? h("span", { class: "live-seg" }, stepping("One step: what it joins directly", "hop1", 1), stepping("Two steps", "hop2", 2), stepping("All the way", "expand", 0)) : null,
    h("span", { class: "live-seg" }, anchor ? null : mapButton("Open every kind", "expand", () => everything(true)), anchor ? null : mapButton("Fold every kind to bands", "collapse", () => everything(false)),
      mapButton("Fit it to the window", "fit", refit),
      anchor ? mapOpen(anchor) : null)), picture);
}
