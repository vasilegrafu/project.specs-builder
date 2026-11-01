// The Matrix, #/matrix: the specification read as a table and walked link by link. It opens on a grid, a row and a column
// for each kind, each cell counting the links from one to the other; an empty cell is a gap. Beside it a tree of every
// node, by part and kind. Every label there shows something in the middle, and only a chevron folds: a part says its kinds, a
// kind what it is, how it is linked and its nodes. Choose a node, and its links are listed by sort, both ways; choose a link, and it is told: both
// ends, how it reads, where it is written, what goes stale, whether it is stale now. The far end is one click on, and the
// trail keeps the way walked. The tree narrows to what has a problem; the links narrow to a few words, and group by the kind
// at their far end; the grid marks where links are stale; and a path says how two nodes are joined.
//
// Nothing here holds the whole specification. The server answers in small parts (app/matrix.py): the tree asks for a kind's
// nodes a page at a time as they are scrolled to, and draws only the rows in view, measuring each, for a name wraps; so a
// kind of any size scrolls as one of ten. The tree reads as the other trees do, its width dragged at its edge and kept.
// A node's links come with the first few of each sort, the rest when asked; a link when it is chosen. It needs no
// library, so it works without a connection. On a sheet it draws what is in view, flat. Loaded before engine.js; it draws
// with engine.js's h(), get(), state, GROUPS, PLURAL, counted(), moved() and nodeHref(), menu.js's icon(), PARTS and
// lettersOf(), and side.js's kept(), keep(), words(), widen(), wireGrip(), wireTips() and SIDE_WIDE.
"use strict";

const MX_KEEP = "specs-builder-2.matrix-open";                  // what is open in the tree, kept in the browser
const MX_ROW = 30;                                              // px: a row of the tree holding one line
const MX_GUESS = 43;                                            // px: a node's row until it has been drawn: most names take two lines
const MX_PAGE = 200;                                            // the rows of the tree in one answer, as the server pages them
const MX_MORE = 200;                                            // the links one "Show more" asks for
const MX_SPARE = 12;                                            // rows drawn past each edge of the tree, for a smooth scroll
const MX_TRAIL = 12;                                            // the steps the trail keeps
const MX_FAR = { least: 240, most: 640, usual: 340 };           // px: the right side's width
const MX_QUIET = 180;                                           // ms: Find waits for the typing to pause
const MX_BY = "specs-builder-2.matrix-by";                      // how a node's links are grouped, kept in the browser
const MX_FILTERS = { stale: ["Stale", "Nothing is stale."], unlinked: ["No links", "Every node has a link."], open: ["Open questions", "No question is open."] };
const mx = { filter: "", folded: new Set(), q: "", by: kept(MX_BY, "sort"), path: null, been: [], here: -1, stepping: 0, grid: null, lists: new Map(), open: null, rows: [], at: new Float64Array(1), wide: 0, shelf: null, node: null, groups: [], cell: null, link: null, trail: [],
             active: 0, top: 0, turn: 0, pane: "links", root: null };

const mxNode = (id) => `#/matrix/${encodeURIComponent(id)}`;
const mxPlace = () => (mx.path ? `path:${mx.path.from}:${mx.path.to}` : mx.cell ? `cell:${mx.cell.from}:${mx.cell.to}` : mx.node ? mx.node.id : mx.shelf ? mx.shelf.key : "");
const mxKindHref = (kind) => mxNode(kind === "document" ? "document" : `kind:${kind}`);
const mxKindKey = (kind) => `kind=${encodeURIComponent(kind)}${mx.filter ? `&problem=${mx.filter}` : ""}`;
const mxIsOpen = (key) => (mx.filter && !key.startsWith("n:") ? !mx.folded.has(key) : mx.open.has(key));
const mxMatching = () => (mx.q ? `&q=${encodeURIComponent(mx.q)}` : "");
const mxLink = (said) => `#/matrix/${encodeURIComponent(mxPlace())}/${encodeURIComponent(said)}`;
const mxChip = (n) => h("span", { class: `chip kind-${n.kind}`, "data-card": n.id }, n.id);
const mxKind = (kind) => PLURAL[kind] || kind;
const matrixShowing = () => !!(mx.root && mx.root.isConnected);

// The right side's width, as the tree's is set: the grip on its left edge
function mxFarWide(px) {
  const wide = Math.round(Math.min(MX_FAR.most, Math.max(MX_FAR.least, px)));
  document.documentElement.style.setProperty("--mx-far-w", `${wide}px`);
  document.querySelectorAll(".side-grip.far").forEach((grip) => grip.setAttribute("aria-valuenow", wide));
  mx.far = wide;
  return wide;
}

// The tree

function mxGroups() {
  const count = new Map(mx.filter ? Object.entries(mx.grid.problems[mx.filter]) : mx.grid.kinds.map((k) => [k.kind, k.count]));
  const named = GROUPS.flatMap(([, kinds]) => kinds);
  const others = mx.grid.kinds.map((k) => k.kind).filter((k) => k !== "document" && !named.includes(k));
  return [["Document", ["document"]], ...GROUPS, ["Other", others]]
    .map(([name, kinds]) => ({ name, kinds: kinds.filter((k) => count.get(k)).map((k) => ({ kind: k, count: count.get(k) })) }))
    .filter((group) => group.kinds.length);
}

const mxList = (key, total) => {
  if (!mx.lists.has(key)) mx.lists.set(key, { key, total, rows: [], asked: new Set() });
  return mx.lists.get(key);
};

// Every row the tree has now, as a plain list: a node not fetched yet is a place in its list, filled when it comes
function mxFlatten() {
  const rows = [];
  for (const group of mxGroups()) {
    const shut = !mxIsOpen(`g:${group.name}`);
    rows.push({ t: "group", key: `g:${group.name}`, level: 1, name: group.name, count: group.kinds.reduce((sum, k) => sum + k.count, 0), shut,
                place: group.name === "Document" ? "document" : `part:${group.name}` });
    if (shut) continue;
    for (const { kind, count } of group.kinds) {
      const held = kind !== "document" && !mxIsOpen(`k:${kind}`);     // the document is one node: no kind stands between
      if (kind !== "document") rows.push({ t: "kind", key: `k:${kind}`, level: 2, kind, name: mxKind(kind), count, shut: held, place: `kind:${kind}` });
      if (held) continue;
      const list = mxList(mxKindKey(kind), count);
      for (let i = 0; i < count; i++) {
        rows.push({ t: "node", level: 3, list, i });
        const n = list.rows[i];
        if (n && n.parts && mx.open.has(`n:${n.id}`)) {
          const inner = mxList(`parent=${encodeURIComponent(n.id)}`, n.parts);
          for (let j = 0; j < n.parts; j++) rows.push({ t: "node", level: 4, list: inner, i: j });
        }
      }
    }
  }
  mx.rows = rows;
  mx.active = Math.min(mx.active, Math.max(0, rows.length - 1));
  mxPlaces();
}

// Where each row starts: a node's row by what it measured when it was drawn
function mxPlaces() {
  const rows = mx.rows;
  if (mx.at.length !== rows.length + 1) mx.at = new Float64Array(rows.length + 1);
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const high = row.t !== "node" ? MX_ROW : (row.list.rows[row.i] || {}).high || MX_GUESS;
    mx.at[i + 1] = mx.at[i] + high;
  }
}

// The row at a height down the tree
function mxRowAt(y) {
  let low = 0, high = mx.rows.length - 1;
  while (low < high) {
    const middle = Math.ceil((low + high) / 2);
    if (mx.at[middle] <= y) low = middle; else high = middle - 1;
  }
  return low;
}

function mxStore(list, found) {
  found.rows.forEach((n, i) => { list.rows[found.offset + i] = n; });
  list.total = found.total;
  list.asked.add(Math.floor(found.offset / MX_PAGE));
  return found.rows.some((n) => n.parts && mx.open.has(`n:${n.id}`));
}

function mxAsk(list, i) {
  const page = Math.floor(i / MX_PAGE);
  if (list.asked.has(page)) return;
  list.asked.add(page);
  get(`matrix/tree?${list.key}&offset=${page * MX_PAGE}`).then((found) => {
    if (mxStore(list, found)) mxFlatten();
    mxDraw();
  }).catch(() => list.asked.delete(page));
}

function mxRow(row, index) {
  const where = { id: `mx-row-${index}`, role: "treeitem", "aria-level": row.level, "data-row": index, style: `top:${mx.at[index]}px;--level:${row.level}` };
  const chosen = index === mx.active ? " active" : "";
  if (row.t !== "node") {
    const fold = (e) => { e.preventDefault(); e.stopPropagation(); mx.active = index; mxToggle(row.key); };
    const here = mxPlace() === row.place;
    return h("a", { ...where, class: `mx-row mx-${row.t}${chosen}${here ? " on" : ""}`, href: mxNode(row.place), tabindex: "-1",
                    "aria-expanded": row.shut ? "false" : "true", "aria-selected": String(here) },
      h("span", { class: `mx-turn${row.shut ? " shut" : ""}`, onclick: fold, title: row.shut ? "Open" : "Fold" }, icon("chevron")), row.t === "group" && PARTS[row.name] ? h("span", { class: "mx-part-icon" }, icon(PARTS[row.name].icon)) : null,
      row.t === "kind" ? h("span", { class: `drop-dot kind-${row.kind}` }) : null,
      h("span", { class: "mx-name" }, row.name, row.t === "kind" && lettersOf(row.kind) ? h("span", { class: "drop-letters" }, ` (${lettersOf(row.kind)})`) : null),
      h("span", { class: "side-count" }, row.count));
  }
  const n = row.list.rows[row.i];
  if (!n) {
    mxAsk(row.list, row.i);
    return h("div", { ...where, class: `mx-row mx-waiting side-node${chosen}` }, h("span", { class: "side-name" }, "..."));
  }
  const shut = !mx.open.has(`n:${n.id}`);
  const fold = (e) => { e.preventDefault(); e.stopPropagation(); mx.active = index; mxToggle(`n:${n.id}`); };
  const name = words(n.name || "");
  const holds = row.level === 3 && ((state.grammar.kinds[n.kind] || {}).form || {}).rows;
  return h("a", { ...where, class: `mx-row side-node${holds ? " mx-holds" : ""}${chosen}${mx.node && mx.node.id === n.id ? " on" : ""}`, href: mxNode(n.id), tabindex: "-1",
                  "aria-selected": mx.node && mx.node.id === n.id ? "true" : "false", "aria-expanded": n.parts ? String(!shut) : null,
                  "data-cut": name.cut ? "1" : null, "data-card": n.id, "aria-label": `${n.id} ${n.name || ""}`.trim() },
    n.parts ? h("span", { class: `mx-turn${shut ? " shut" : ""}`, onclick: fold }, icon("chevron")) : null,
    h("span", { class: "side-id" }, n.id), h("span", { class: "side-name" }, name.text), n.links ? h("span", { class: "side-count" }, n.links) : null);
}

function mxDraw() {
  const box = mx.root && mx.root.querySelector(".mx-tree");
  if (!box) return;
  const inner = box.firstChild;
  if (!mx.rows.length) {
    inner.style.height = "auto";
    inner.replaceChildren(h("p", { class: "empty mx-none" }, MX_FILTERS[mx.filter] ? MX_FILTERS[mx.filter][1] : "Nothing here."));
    return;
  }
  mxPlaces();
  inner.style.height = `${mx.at[mx.rows.length]}px`;
  const seen = mxRowAt(box.scrollTop);
  const first = Math.max(0, seen - MX_SPARE);
  const last = Math.min(mx.rows.length, mxRowAt(box.scrollTop + box.clientHeight) + MX_SPARE + 1);
  const shown = [];
  for (let i = first; i < last; i++) shown.push(mxRow(mx.rows[i], i));
  inner.replaceChildren(...shown);
  // Each row now measured: what moved above the view is taken from the scroll, so that what is read stays where it is
  let above = 0, moved = false;
  for (const el of shown) {
    const row = mx.rows[Number(el.dataset.row)];
    const n = row.t === "node" ? row.list.rows[row.i] : null;
    if (!n || n.high === el.offsetHeight) continue;
    if (Number(el.dataset.row) < seen) above += el.offsetHeight - (n.high || MX_GUESS);
    n.high = el.offsetHeight;
    moved = true;
  }
  if (moved) {
    mxPlaces();
    inner.style.height = `${mx.at[mx.rows.length]}px`;
    for (const el of shown) el.style.top = `${mx.at[Number(el.dataset.row)]}px`;
    if (above) box.scrollTop += above;
  }
  if (shown.some((el) => el.id === `mx-row-${mx.active}`)) box.setAttribute("aria-activedescendant", `mx-row-${mx.active}`);
  else box.removeAttribute("aria-activedescendant");
}

function mxToggle(key) {
  if (mx.filter && !key.startsWith("n:")) {                     // a filter opens all it finds, and forgets its folds with it
    if (mx.folded.has(key)) mx.folded.delete(key); else mx.folded.add(key);
  } else {
    if (mx.open.has(key)) mx.open.delete(key); else mx.open.add(key);
    keep(MX_KEEP, [...mx.open].filter((k) => !k.startsWith("n:")).join(","));
  }
  mxFlatten();
  mxDraw();
}

// The tree narrowed to what has a problem
function mxFilter(what) {
  mx.filter = what;
  mx.folded = new Set();
  mx.active = 0;
  mxFlatten();
  mx.root.querySelector(".mx-tree").scrollTop = 0;
  mxDraw();
}

function mxFilterBox() {
  const total = (what) => Object.values(mx.grid.problems[what]).reduce((sum, n) => sum + n, 0);
  return h("select", { class: "mx-filter", "aria-label": "Show in the tree", onchange: (e) => mxFilter(e.target.value) },
    h("option", { value: "" }, "Every node"),
    Object.entries(MX_FILTERS).map(([what, [word]]) => h("option", { value: what }, `${word} (${total(what)})`)));
}

// The whole tree folded to its parts, and kept so
function mxCollapse() {
  mx.open = new Set();
  keep(MX_KEEP, "");
  mx.folded = new Set(mxGroups().map((g) => `g:${g.name}`));
  mx.active = 0;
  mx.top = 0;
  mxFlatten();
  mx.root.querySelector(".mx-tree").scrollTop = 0;
  mxDraw();
}

function mxShowRow(index) {
  const box = mx.root.querySelector(".mx-tree");
  if (mx.at[index] < box.scrollTop) box.scrollTop = mx.at[index];
  else if (mx.at[index + 1] > box.scrollTop + box.clientHeight) box.scrollTop = mx.at[index + 1] - box.clientHeight;
}

function mxTreeKey(e) {
  const row = mx.rows[mx.active];
  const jump = { ArrowDown: 1, ArrowUp: -1, PageDown: 15, PageUp: -15 }[e.key];
  if (jump) mx.active = Math.max(0, Math.min(mx.rows.length - 1, mx.active + jump));
  else if (e.key === "Home") mx.active = 0;
  else if (e.key === "End") mx.active = mx.rows.length - 1;
  else if (!row) return;
  else if (e.key === "Enter" || e.key === " " || e.key === "ArrowRight" || e.key === "ArrowLeft") {
    const n = row.t === "node" ? row.list.rows[row.i] : null;
    const key = n ? (n.parts ? `n:${n.id}` : null) : row.key;
    const open = key && mxIsOpen(key);
    if (e.key === "Enter" || e.key === " ") {
      if (n || row.place) location.hash = mxNode(n ? n.id : row.place);
    } else if (e.key === "ArrowRight" ? key && !open : open) mxToggle(key);
    else if (e.key === "ArrowLeft") {                           // shut already: the row above it, that holds it
      for (let i = mx.active - 1; i >= 0; i--) if (mx.rows[i].level < row.level) { mx.active = i; break; }
    }
  } else return;
  e.preventDefault();
  mxShowRow(mx.active);
  mxDraw();
}

// The chosen node shown in the tree: its kind opened, and the page it is on fetched, however far down that is
async function mxReveal(node) {
  const group = mxGroups().find((g) => g.kinds.some((k) => k.kind === node.top.kind));
  if (!group) return;
  mx.open.add(`g:${group.name}`);
  mx.open.add(`k:${node.top.kind}`);
  const count = group.kinds.find((k) => k.kind === node.top.kind).count;
  const list = mxList(mxKindKey(node.top.kind), count);
  const found = await get(`matrix/tree?${list.key}&at=${encodeURIComponent(node.top.id)}`);
  mxStore(list, found);
  if (found.position === null) { mxFlatten(); mxDraw(); return; }  // a filter that leaves it out
  let target = list, position = found.position;
  if (node.parent) {
    mx.open.add(`n:${node.parent}`);
    const holder = list.rows[found.position];
    const inner = mxList(`parent=${encodeURIComponent(node.parent)}`, holder ? holder.parts : 0);
    const within = await get(`matrix/tree?${inner.key}&at=${encodeURIComponent(node.id)}`);
    mxStore(inner, within);
    target = inner;
    position = within.position;
  }
  mxFlatten();
  const index = mx.rows.findIndex((row) => row.list === target && row.i === position);
  if (index >= 0) { mx.active = index; mxBring(index); }
  mxDraw();
}

// A row out of view brought to the upper part of the tree
function mxBring(index) {
  const box = mx.root.querySelector(".mx-tree");
  if (mx.at[index] < box.scrollTop || mx.at[index + 1] > box.scrollTop + box.clientHeight) box.scrollTop = mx.at[index] - box.clientHeight / 3;
}

// The grid

function mxGrid() {
  const kinds = mx.grid.kinds.slice().sort((a, b) => {
    const order = ["document", ...GROUPS.flatMap(([, held]) => held)];
    return order.indexOf(a.kind) - order.indexOf(b.kind);
  });
  const cells = new Map(mx.grid.cells.map((c) => [`${c.from}|${c.to}`, c]));
  const most = Math.max(1, ...mx.grid.cells.map((c) => c.count));
  const said = (c) => `${mxKind(c.from)} to ${mxKind(c.to)}: ${counted(c.count, "link", "links")}${c.stale ? `, ${c.stale} stale` : ""} -- ` +
    Object.entries(c.rels).sort(([, x], [, y]) => y - x).map(([rel, n]) => `${rel} ${n}`).join(", ");
  return h("div", { class: "mx-grid-frame" }, h("table", { class: "mx-grid" },
    h("caption", { class: "sr-only" }, "How many links go from the kind of each row to the kind of each column"),
    h("thead", {}, h("tr", {}, h("td", { class: "mx-corner" }, "From \\ to"),
      kinds.map((k) => h("th", { scope: "col", class: `kind-${k.kind}` }, h("a", { href: mxKindHref(k.kind) }, h("span", {}, mxKind(k.kind))))))),
    h("tbody", {}, kinds.map((row) => h("tr", {},
      h("th", { scope: "row", class: `kind-${row.kind}` }, h("a", { href: mxKindHref(row.kind) }, mxKind(row.kind)), " ", h("span", { class: "mx-count" }, row.count)),
      kinds.map((col) => {
        const c = cells.get(`${row.kind}|${col.kind}`);
        if (!c) return h("td", { class: "mx-gap", title: `No link from ${mxKind(row.kind)} to ${mxKind(col.kind)}` }, h("span", { "aria-label": "None" }, "·"));
        const heat = Math.round(8 + 34 * Math.log1p(c.count) / Math.log1p(most));
        return h("td", { class: c.stale ? "mx-owed" : null, style: `--heat:${heat}%` }, h("a", { href: mxNode(`cell:${c.from}:${c.to}`), title: said(c), "aria-label": said(c) }, c.count));
      })))))) ;
}

// The middle: the grid, the links of a cell, or the links of a node

const mxOwed = (l) => (l.stale ? h("span", { class: "mx-owed-mark", title: "Stale: choose it to see what moved", "aria-label": "Stale" }) : null);

function mxRowOfLink(l) {
  const said = `${l.src} ${l.rel} ${l.dst}`;
  return h("li", { class: "mx-link", "data-link": said, "data-card": l.far.id },
    h("a", { class: "mx-link-main", href: mxLink(said) }, mxOwed(l), mxChip(l.far), mx.by === "kind" ? h("span", { class: "mx-rel" }, l.word) : null,
      h("span", { class: "mx-name" }, l.far.name),
      l.count > 1 ? h("span", { class: "mx-from" }, `${l.count} links`) : l.from ? h("span", { class: "mx-from" }, `from ${l.from}`) : null),
    h("a", { class: "mx-walk", href: mxNode(l.far.id), title: `Go to ${l.far.id}`, "aria-label": `Go to ${l.far.id}` }, icon("arrow")));
}

function mxRowOfCell(l) {
  const said = l.said;
  return h("li", { class: "mx-link", "data-link": said, "data-card": l.dst.id },
    h("a", { class: "mx-link-main", href: mxLink(said) }, mxOwed(l), mxChip(l.src), h("span", { class: "mx-rel" }, l.rel), mxChip(l.dst),
      h("span", { class: "mx-name" }, l.dst.name), l.count > 1 ? h("span", { class: "mx-from" }, `${l.count} links`) : null),
    h("a", { class: "mx-walk", href: mxNode(l.dst.id), title: `Go to ${l.dst.id}`, "aria-label": `Go to ${l.dst.id}` }, icon("arrow")));
}

function mxMore(list, have, total, ask, draw) {
  const left = total - have();
  if (left <= 0) return null;
  const button = h("button", { type: "button", class: "button small mx-more", onclick: async () => {
    button.disabled = true;
    const rows = await ask(have()).catch(() => []);
    list.append(...rows.map(draw));
    const next = mxMore(list, have, total, ask, draw);
    button.replaceWith(next || "");
  } }, `Show more, ${left} left`);
  return button;
}

// The box that narrows the links in view, and asks the server, for it may hold more than the page does
function mxNarrow(again) {
  let wait = 0;
  const input = h("input", { class: "graph-find mx-narrow", type: "search", placeholder: "Filter these links", "aria-label": "Filter these links by what is at their far end",
    value: mx.q, oninput: () => {
      clearTimeout(wait);
      wait = setTimeout(() => { mx.q = input.value.trim(); again(); }, MX_QUIET);
    } });
  return input;
}

function mxLinkBody() {
  const n = mx.node;
  if (!mx.groups.length) return h("p", { class: "empty" }, mx.q ? "No link here matches that." : "Nothing is linked to it.");
  return mx.groups.map((group) => {
    const list = h("ul", { class: "mx-links" }, group.links.map(mxRowOfLink));
    const which = group.kind ? `of=${encodeURIComponent(group.kind)}` : `way=${group.way}&rel=${encodeURIComponent(group.rel)}`;
    const ask = (from) => get(`matrix/links/${encodeURIComponent(n.id)}?${which}&offset=${from}&limit=${MX_MORE}${mxMatching()}`)
      .then((found) => { group.links.push(...found.links); return found.links; });
    return [h("h3", {}, group.kind ? mxKindNamed(group.kind) : group.label, " ", h("span", { class: "mx-count" }, group.count)), list,
      mxMore(list, () => group.links.length, group.count, ask, mxRowOfLink)];
  });
}

function mxFill(box, body) {
  box.replaceChildren(...[body].flat(Infinity).filter(Boolean));
  mxMark();
}

async function mxNodeAgain(box) {
  const turn = ++mx.turn;
  const found = await get(`matrix/links/${encodeURIComponent(mx.node.id)}?by=${mx.by}${mxMatching()}`);
  if (turn !== mx.turn) return;
  mx.groups = found.groups;
  mxFill(box, mxLinkBody());
}

function mxNodeLinks() {
  const n = mx.node;
  const body = h("div", { class: "mx-link-body" });
  mxFill(body, mxLinkBody());
  const way = (by, word) => h("button", { type: "button", class: `live-button${mx.by === by ? " on" : ""}`, "aria-pressed": String(mx.by === by), onclick: (e) => {
    mx.by = by;
    keep(MX_BY, by);
    e.currentTarget.parentNode.querySelectorAll("button").forEach((b) => { b.classList.toggle("on", b === e.currentTarget); b.setAttribute("aria-pressed", String(b === e.currentTarget)); });
    mxNodeAgain(body);
  } }, word);
  return [h("div", { class: "mx-head" }, h("h2", {}, mxChip(n), " ", n.name),
    h("p", { class: "meta" }, n.kind, n.parent ? ` in ${n.parent}` : "", n.parts ? `, ${counted(n.parts, "row", "rows")} counted with it` : ""),
    h("div", { class: "actions-row node-ways" }, waysOf(pictureWays(n.parent || n.id)))),
  h("div", { class: "mx-link-tools" }, mxNarrow(() => mxNodeAgain(body)), h("span", { class: "live-seg" }, way("sort", "By sort"), way("kind", "By kind"))), body];
}

function mxCellBody() {
  const c = mx.cell;
  const list = h("ul", { class: "mx-links" }, c.links.map(mxRowOfCell));
  const ask = (from) => get(`matrix/cell?from=${encodeURIComponent(c.from)}&to=${encodeURIComponent(c.to)}&offset=${from}&limit=${MX_MORE}${mxMatching()}`)
    .then((found) => { c.links.push(...found.links); return found.links; });
  return [h("p", { class: "meta" }, counted(c["links count"], "link", "links")),
    c.total ? [list, mxMore(list, () => c.links.length, c.total, ask, mxRowOfCell)]
      : h("p", { class: "empty" }, mx.q ? "No link here matches that." : "No link goes from the one to the other.")];
}

function mxCellLinks() {
  const c = mx.cell;
  const body = h("div", { class: "mx-link-body" });
  mxFill(body, mxCellBody());
  const again = async () => {
    const turn = ++mx.turn;
    const found = await get(`matrix/cell?from=${encodeURIComponent(c.from)}&to=${encodeURIComponent(c.to)}${mxMatching()}`);
    if (turn !== mx.turn) return;
    mx.cell = found;
    mxFill(body, mxCellBody());
  };
  return [h("div", { class: "mx-head" }, h("h2", {}, `${mxKind(c.from)} to ${mxKind(c.to)}`)),
    h("div", { class: "mx-link-tools" }, mxNarrow(again)), body];
}

// A path: two nodes chosen, and the shortest chain of links between them
function mxPathBody() {
  const p = mx.path;
  if (!p.found) return h("p", { class: "empty" }, p.from && p.to ? "" : "Choose both ends.");
  const { found } = p;
  if (!found.found) return h("p", { class: "empty" }, `No chain of links joins ${p.from} and ${p.to}.`);
  if (!found.steps.length) return h("p", { class: "empty" }, `${p.from} and ${p.to} are the same node, or one holds the other.`);
  return [h("p", { class: "mx-note" }, `${counted(found.steps.length, "step", "steps")} from ${p.from} to ${p.to}. ` +
    (found.changing ? "A change passes along each of these links, in one direction or the other." : "No change passes along all of these links: they only show how the two are joined.")),
  h("ul", { class: "mx-links mx-chain" }, found.steps.map(mxRowOfCell))];
}

function mxPathView() {
  const p = mx.path;
  const pick = (side) => (hit) => { location.hash = mxNode(`path:${side === "from" ? hit.id : p.from}:${side === "to" ? hit.id : p.to}`); };
  const picked = (id, side) => mxFinder(pick(side), side === "from" ? "From a node" : "To a node", id);
  return [h("div", { class: "mx-head" }, h("h2", {}, "Path between two nodes"),
    h("p", { class: "mx-note" }, "Choose two nodes to see the shortest chain of links that joins them. What a node holds counts as that node.")),
  h("div", { class: "mx-path-ends" }, picked(p.from, "from"), picked(p.to, "to")), mxPathBody()];
}

// A part: its kinds, each with its letters and its count
function mxPartView(name) {
  const group = mxGroups().find((g) => g.name === name);
  if (!group) throw new Error(`${name}: no such part`);
  return [h("div", { class: "mx-head" }, h("h2", { class: "mx-part-head" }, PARTS[name] ? h("span", { class: "mx-part-icon" }, icon(PARTS[name].icon)) : null, name),
    PARTS[name] ? h("p", { class: "mx-note" }, `${PARTS[name].lead}.`) : null),
  h("ul", { class: "mx-links" }, group.kinds.map(({ kind, count }) => h("li", { class: "mx-link" },
    h("a", { class: "mx-link-main", href: mxNode(`kind:${kind}`) }, h("span", { class: `drop-dot mx-dot kind-${kind}` }),
      h("span", { class: "mx-name" }, mxKindNamed(kind), state.grammar.kinds[kind] ? h("span", { class: "mx-is" }, ` -- ${state.grammar.kinds[kind].is}`) : null),
      h("span", { class: "side-count mx-line-count" }, count)))))];
}

const mxKindNamed = (kind) => [mxKind(kind), lettersOf(kind) ? h("span", { class: "drop-letters" }, ` (${lettersOf(kind)})`) : null];

// A kind: what it is, the kinds it is linked to and from, each a cell of the grid, and its nodes a page at a time
function mxKindView(shelf) {
  const { kind, list, total } = shelf;
  const near = (cells, end, word) => (cells.length ? [h("h3", {}, word),
    h("ul", { class: "mx-links" }, cells.sort((a, b) => b.count - a.count).map((c) => h("li", { class: "mx-link" },
      h("a", { class: "mx-link-main", href: mxNode(`cell:${c.from}:${c.to}`) }, h("span", { class: `drop-dot mx-dot kind-${c[end]}` }),
        h("span", { class: "mx-name" }, mxKindNamed(c[end]), h("span", { class: "mx-is" }, ` -- ${Object.keys(c.rels).join(", ")}`)),
        h("span", { class: "side-count mx-line-count" }, c.count)))))] : null);
  const row = (n) => h("li", { class: "mx-link" }, h("a", { class: "mx-link-main", href: mxNode(n.id) }, mxChip(n), h("span", { class: "mx-name" }, n.name),
    n.links ? h("span", { class: "side-count mx-line-count" }, n.links) : null));
  const nodes = h("ul", { class: "mx-links" }, list.map(row));
  const ask = (from) => get(`matrix/tree?kind=${encodeURIComponent(kind)}&offset=${from}`).then((found) => { list.push(...found.rows); return found.rows; });
  return [h("div", { class: "mx-head" }, h("h2", { class: "mx-part-head" }, h("span", { class: `drop-dot mx-dot kind-${kind}` }), h("span", {}, mxKindNamed(kind))),
    state.grammar.kinds[kind] ? h("p", { class: "mx-note" }, `${state.grammar.kinds[kind].is}.`) : null),
  near(mx.grid.cells.filter((c) => c.from === kind), "to", "Links to"),
  near(mx.grid.cells.filter((c) => c.to === kind), "from", "Linked from"),
  h("h3", {}, "Nodes ", h("span", { class: "mx-count" }, total)), nodes, mxMore(nodes, () => list.length, total, ask, row)];
}

async function mxOpenShelf(place) {
  const [type, name] = place.split(":");
  if (type === "part") return { key: place, part: name };
  const found = await get(`matrix/tree?kind=${encodeURIComponent(name)}`);
  return { key: place, kind: name, list: found.rows, total: found.total };
}

function mxMiddle() {
  const box = mx.root.querySelector(".mx-middle");
  const panes = mx.root.querySelector(".mx-panes");
  const wide = !mx.node && !mx.cell && !mx.path;
  panes.classList.toggle("wide", wide);
  box.replaceChildren(...[mx.path ? mxPathView() : mx.shelf ? (mx.shelf.part ? mxPartView(mx.shelf.part) : mxKindView(mx.shelf)) : wide ? [h("div", { class: "mx-head" }, h("h2", {}, "Links between kinds"),
    h("p", { class: "mx-note" }, `${counted(mx.grid.nodes, "node", "nodes")}, ${counted(mx.grid.links, "link", "links")}. Each number counts the links going from the row's kind to the column's. Choose one to see them, or a kind's name to open it. A dot is a gap: no link at all.${mx.grid.stale ? ` A number marked amber holds stale links: ${mx.grid.stale} in all.` : ""}`)), mxGrid()]
    : mx.cell ? mxCellLinks() : mxNodeLinks()].flat(Infinity).filter(Boolean));
  box.scrollTop = 0;
  mxMark();
}

function mxMark() {
  const said = mx.link ? mx.link.reads : "";
  mx.root.querySelectorAll(".mx-link").forEach((row) => row.classList.toggle("on", row.dataset.link === said));
}

// The right: a link told, or what the chosen node is

function mxEnd(n) {
  return h("a", { class: "mx-end", href: mxNode(n.id) }, mxChip(n), h("span", { class: "mx-name" }, n.name), h("span", { class: "meta" }, n.kind));
}

function mxStale(s) {
  const keys = Object.keys({ ...s.was, ...s.now }).filter((k) => JSON.stringify((s.was || {})[k]) !== JSON.stringify((s.now || {})[k]));
  return h("div", { class: "mx-stale" }, h("strong", {}, `${s.node} is stale`), `: ${s.on} changed since it was reviewed.`,
    keys.map((k) => h("div", { class: "mx-moved" }, h("span", { class: "meta" }, k), " ", moved((s.was || {})[k] ?? "", (s.now || {})[k] ?? ""))));
}

function mxTold(l) {
  const here = mx.node ? mx.node.id : "";
  const far = [l.src, l.dst].find((n) => n.id !== here) || l.dst;
  const stands = l.stands.length ? l.stands.map((s) => h("div", {}, `If ${s.on} changes, ${s.node} goes stale.`))
    : h("div", {}, "Neither end goes stale when the other changes.");
  return [h("h2", {}, l.reads),
    h("p", { class: "meta" }, `${l.src.kind} to ${l.dst.kind}`),
    h("div", { class: "mx-ends" }, mxEnd(l.src), h("div", { class: "mx-joined" }, l.rel), mxEnd(l.dst)),
    h("dl", { class: "mx-facts" },
      h("dt", {}, "Read from the other end"), h("dd", {}, l["reads back"]),
      h("dt", {}, "If one end changes"), h("dd", {}, stands),
      h("dt", {}, "Now"), h("dd", {}, l.stale.length ? l.stale.map(mxStale) : "Reviewed: nothing has changed since."),
      h("dt", {}, "Written in"), h("dd", {}, h("code", {}, l.file), `, line ${l.line}`)),
    h("p", { class: "mx-ways" }, h("a", { class: "button small", href: mxNode(far.id) }, `Go to ${far.id}`),
      h("a", { class: "button small", href: nodeHref(far.id) }, `Open ${far.id}'s page`))];
}

async function mxRight(turn) {
  const box = mx.root.querySelector(".mx-right");
  if (mx.link) { box.replaceChildren(...mxTold(mx.link).flat(Infinity).filter(Boolean)); return; }
  if (!mx.node) { box.replaceChildren(h("p", { class: "empty" }, "Choose a link to see what joins its two ends.")); return; }
  const n = mx.node;
  const card = await get(`card/${encodeURIComponent(n.id)}`).catch(() => null);
  if (turn !== mx.turn) return;
  box.replaceChildren(...[h("h2", {}, mxChip(n), " ", n.name), h("p", { class: "meta" }, n.kind),
    card && card.said ? h("p", {}, card.said) : null,
    h("p", { class: "empty" }, "Choose a link to see what joins its two ends."),
    h("p", { class: "mx-ways" }, h("a", { class: "button small", href: nodeHref(n.id) }, `Open ${n.id}'s page`),
      h("a", { class: "button small", href: `#/graph/${encodeURIComponent(n.id)}` }, `Graph around ${n.id}`),
      h("a", { class: "button small", href: mxNode(`path:${n.id}:`) }, `Path from ${n.id}`))].filter(Boolean));
}

// Back and forward: the places of the Matrix in the order they were reached. A step keeps what lies ahead, and going anywhere else
// drops it, as a browser does. It stays inside the Matrix, and the browser's own Back goes on working beside it.
function mxRemember() {
  const hash = location.hash;
  if (mx.stepping) { mx.here += mx.stepping; mx.stepping = 0; }
  else if (mx.been[mx.here] === hash) { /* the same place, asked again */ }
  else if (mx.been[mx.here - 1] === hash) mx.here -= 1;           // the browser's own Back
  else if (mx.been[mx.here + 1] === hash) mx.here += 1;           // and its Forward
  else {
    mx.been = [...mx.been.slice(0, mx.here + 1), hash];
    mx.here = mx.been.length - 1;
  }
  mxSteps();
}

function mxTravel(by) {
  const to = mx.been[mx.here + by];
  if (to === undefined) return;
  mx.stepping = by;
  location.hash = to;
}

function mxSteps() {
  if (!mx.root) return;
  mx.root.querySelector(".mx-back").disabled = mx.here <= 0;
  mx.root.querySelector(".mx-forward").disabled = mx.here >= mx.been.length - 1;
}

// The way walked

function mxTrail() {
  const box = mx.root.querySelector(".mx-trail");
  box.hidden = mx.trail.length < 2;
  box.replaceChildren(...[h("span", { class: "mx-note" }, "Walked:"),
    mx.trail.map((n, i) => [i ? h("span", { class: "mx-step" }, icon("chevron")) : null,
      h("a", { class: "mx-trail-step", href: mxNode(n.id), title: n.name, "aria-current": i === mx.trail.length - 1 ? "step" : null }, mxChip(n))]),
    h("button", { type: "button", class: "live-button mx-trail-clear", onclick: () => { mx.trail = mx.node ? [mx.node] : []; mxTrail(); } }, "Clear")]
    .flat(Infinity).filter(Boolean));
}

function mxStep(node) {
  const at = mx.trail.findIndex((n) => n.id === node.id);
  if (at >= 0) mx.trail = mx.trail.slice(0, at + 1);
  else mx.trail = [...mx.trail, node].slice(-MX_TRAIL);
}

// Going somewhere: only what the address changed is asked for

function mxPane(name) {
  mx.pane = name;
  mx.root.querySelector(".mx-panes").dataset.pane = name;
  mx.root.querySelectorAll(".mx-tab").forEach((tab) => tab.setAttribute("aria-selected", String(tab.dataset.pane === name)));
}

async function matrixGo(arg, extra) {
  mxRemember();
  const turn = ++mx.turn;
  const said = extra ? decodeURIComponent(extra) : "";
  const middle = mx.root.querySelector(".mx-middle");
  try {
    const place = arg || "";
    const moved = place !== mxPlace();
    if (moved) {
      mx.q = "";
      if (!place) { mx.node = null; mx.cell = null; mx.shelf = null; mx.path = null; mx.groups = []; }
      else if (place.startsWith("path:")) {
        const [, from, to] = place.split(":");
        const found = from && to ? await get(`matrix/path?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`) : null;
        if (turn !== mx.turn) return;
        mx.path = { from: from || "", to: to || "", found };
        mx.node = null;
        mx.cell = null;
        mx.shelf = null;
      } else if (/^(part|kind):/.test(place)) {
        const found = await mxOpenShelf(place);
        if (turn !== mx.turn) return;
        mx.shelf = found;
        mx.node = null;
        mx.cell = null;
        mx.path = null;
      } else if (place.startsWith("cell:")) {
        const [, from, to] = place.split(":");
        const found = await get(`matrix/cell?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`);
        if (turn !== mx.turn) return;
        mx.cell = found;
        mx.node = null;
        mx.shelf = null;
        mx.path = null;
      } else {
        const found = await get(`matrix/links/${encodeURIComponent(place)}?by=${mx.by}`);
        if (turn !== mx.turn) return;
        mx.node = found.node;
        mx.groups = found.groups;
        mx.cell = null;
        mx.shelf = null;
        mx.path = null;
        mxStep(found.node);
      }
    }
    mx.link = null;
    if (said) {
      const words = said.split(" ");
      const found = await get(`matrix/link?src=${encodeURIComponent(words[0])}&rel=${encodeURIComponent(words.slice(1, -1).join(" "))}&dst=${encodeURIComponent(words[words.length - 1])}`);
      if (turn !== mx.turn) return;
      mx.link = found;
    }
    if (moved) { mxMiddle(); mxTrail(); mxDraw(); if (mx.node) await mxReveal(mx.node); } else mxMark();
    mx.root.querySelector(".mx-kinds").classList.toggle("on", !mx.node && !mx.cell && !mx.shelf && !mx.path);
    mx.root.querySelector(".mx-path").classList.toggle("on", !!mx.path);
    mxPane(said ? "told" : mx.node || mx.cell || mx.shelf || mx.path ? "links" : mx.pane === "nodes" ? "nodes" : "links");
    await mxRight(turn);
  } catch (error) {
    if (turn === mx.turn) middle.replaceChildren(h("p", { class: "error" }, error.message), h("p", {}, h("a", { href: "#/matrix" }, "Back to the kinds")));
  }
}

// Find: each hit a place to go

function mxFinder(pick, word = "Find a node", value = "") {
  let wait = 0;
  let asked = 0;
  let hits = [];
  let hit = -1;
  const list = h("div", { class: "mx-hits", role: "listbox", hidden: true });
  const shut = () => { list.hidden = true; hit = -1; };
  const go = (one) => {
    shut();
    input.value = pick ? one.id : "";
    (pick || ((n) => { location.hash = mxNode(n.id); }))(one);
  };
  const draw = () => {
    list.hidden = false;
    list.replaceChildren(...(hits.length ? hits.map((one, i) =>
      h("button", { type: "button", class: `mx-hit${i === hit ? " on" : ""}`, role: "option", "aria-selected": String(i === hit), onmousedown: (e) => { e.preventDefault(); go(one); } },
        mxChip(one), h("span", { class: "mx-name" }, words(one.name || "").text))) : [h("div", { class: "empty mx-none" }, "None found")]));
  };
  const input = h("input", { class: "graph-find", type: "search", placeholder: word, "aria-label": `${word}, by its ID or name`, value,
    oninput: () => {
      clearTimeout(wait);
      const text = input.value.trim();
      if (!text) { shut(); return; }
      wait = setTimeout(async () => {
        const turn = ++asked;
        const found = await get(`matrix/find?q=${encodeURIComponent(text)}`).catch(() => []);
        if (turn !== asked) return;
        hits = found;
        hit = found.length ? 0 : -1;
        draw();
      }, MX_QUIET);
    },
    onkeydown: (e) => {
      if (e.key === "Escape") shut();
      else if (list.hidden) return;
      else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (hits.length) { hit = (hit + (e.key === "ArrowDown" ? 1 : -1) + hits.length) % hits.length; draw(); }
      } else if (e.key === "Enter" && hit >= 0) go(hits[hit]);
    },
    onblur: () => setTimeout(shut, 120) });
  return h("span", { class: "mx-find" }, input, list);
}

// The page

async function matrixPage(arg, extra) {
  mx.grid = await get("matrix");
  mx.lists = new Map();
  if (SHEET) return matrixSheet(arg, extra);
  mx.node = null; mx.cell = null; mx.shelf = null; mx.path = null; mx.link = null; mx.groups = []; mx.filter = ""; mx.q = "";
  const stored = kept(MX_KEEP, null);
  mx.open ??= new Set(stored === null ? mxGroups().map((g) => `g:${g.name}`) : stored.split(",").filter(Boolean));
  mxFlatten();
  const tree = h("div", { class: "mx-tree", role: "tree", tabindex: "0", "aria-label": "Every node, by part and kind", onkeydown: mxTreeKey,
                          onscroll: () => { if (tree.isConnected && tree.clientHeight) mx.top = tree.scrollTop; requestAnimationFrame(mxDraw); } }, h("div", { class: "mx-rows", role: "presentation" }));
  const tab = (pane, word) => h("button", { type: "button", role: "tab", class: "mx-tab", "data-pane": pane, onclick: () => mxPane(pane) }, word);
  mx.root = h("div", { class: "live-tool matrix" },
    h("h1", { class: "sr-only" }, "Matrix"),
    h("div", { class: "mx-tabs", role: "tablist", "aria-label": "Parts of the Matrix" }, tab("nodes", "Nodes"), tab("links", "Links"), tab("told", "Connection")),
    h("div", { class: "mx-panes wide", "data-pane": "links" }, h("nav", { class: "mx-left", "aria-label": "Every node" },
        h("div", { class: "mx-tree-head" },
          h("div", { class: "mx-tools" },
            h("a", { class: "mx-tool mx-kinds", href: "#/matrix", title: "Kinds: the grid of links between kinds", "aria-label": "Kinds: the grid of links between kinds" }, icon("matrix")),
            h("button", { type: "button", class: "mx-tool", onclick: mxCollapse, title: "Collapse all", "aria-label": "Collapse all" }, icon("collapse")),
            h("button", { type: "button", class: "mx-tool mx-back", onclick: () => mxTravel(-1), title: "Back", "aria-label": "Back" }, icon("back")),
            h("button", { type: "button", class: "mx-tool mx-forward", onclick: () => mxTravel(1), title: "Forward", "aria-label": "Forward" }, icon("arrow")),
            h("a", { class: "mx-tool mx-path", href: mxNode("path::"), title: "Path between two nodes", "aria-label": "Path between two nodes" }, icon("path"))),
          mxFinder(), mxFilterBox()),
        tree,
        h("div", { class: "side-grip", role: "separator", "aria-orientation": "vertical", tabindex: "0",
                   "aria-label": "The tree's width: drag, or the arrow keys; a double click puts it back",
                   "aria-valuemin": SIDE_WIDE.least, "aria-valuemax": SIDE_WIDE.most })),
      h("section", { class: "mx-middle", "aria-label": "Links" }),
      h("aside", { class: "mx-far", "aria-label": "The connection" }, h("div", { class: "mx-right" }),
        h("div", { class: "side-grip far", role: "separator", "aria-orientation": "vertical", tabindex: "0",
                   "aria-label": "This side's width: drag, or the arrow keys; a double click puts it back",
                   "aria-valuemin": MX_FAR.least, "aria-valuemax": MX_FAR.most }))),
    h("nav", { class: "mx-trail", "aria-label": "The way walked", hidden: true }));
  wireGrip(mx.root.querySelector(".mx-left"), "Matrix");
  wireTips(mx.root.querySelector(".mx-left"));
  wireGrip(mx.root.querySelector(".mx-far"), "Matrix's right side", { set: mxFarWide, usual: MX_FAR.usual, now: () => mx.far });
  widen(sideState.widths.Matrix || SIDE_WIDE.usual);
  mxFarWide(sideState.widths["Matrix's right side"] || MX_FAR.usual);
  let placed = false;
  const sizes = new ResizeObserver(() => {
    if (!tree.isConnected || !tree.clientHeight) {              // told before the page is in place: it is told again when it is
      if (placed) sizes.disconnect();
      return;
    }
    if (tree.clientWidth !== mx.wide) {                         // a name wraps where it will now: every row is measured again
      mx.wide = tree.clientWidth;
      for (const list of mx.lists.values()) list.rows.forEach((n) => { delete n.high; });
    }
    mxDraw();
    if (placed) return;
    placed = true;                                              // it has a height now: back where it was, or at the node asked for
    tree.scrollTop = mx.top;
    if (mx.node) mxBring(mx.active);
    mxDraw();
  });
  sizes.observe(tree);
  mxMiddle();
  await matrixGo(arg, extra);
  return mx.root;
}

// On a sheet: what is in view, flat. A list too long for paper says how much it leaves out.
async function matrixSheet(arg, extra) {
  const out = [];
  const said = extra ? decodeURIComponent(extra) : "";
  if (arg && arg.startsWith("path:")) {
    const [, from, to] = arg.split(":");
    const found = from && to ? await get(`matrix/path?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`) : null;
    out.push(h("h1", {}, `Matrix: path from ${from} to ${to}`), found && found.steps.length
      ? h("ul", { class: "mx-links" }, found.steps.map((l) => h("li", {}, `${l.src.id} ${l.rel} ${l.dst.id}`))) : h("p", { class: "empty" }, "No chain of links joins them."));
  } else if (arg && /^(part|kind):/.test(arg)) {
    const shelf = await mxOpenShelf(arg);
    out.push(h("h1", {}, `Matrix: ${shelf.part || mxKind(shelf.kind)}`), shelf.part ? mxPartView(shelf.part) : mxKindView(shelf));
  } else if (arg && arg.startsWith("cell:")) {
    const [, from, to] = arg.split(":");
    mx.cell = await get(`matrix/cell?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}&limit=500`);
    out.push(h("h1", {}, `Matrix: ${mxKind(from)} to ${mxKind(to)}`), h("p", { class: "lead" }, counted(mx.cell.total, "link", "links")),
      h("ul", { class: "mx-links" }, mx.cell.links.map((l) => h("li", {}, `${l.src.id} ${l.rel} ${l.dst.id}  ${l.dst.name}`))),
      mx.cell.total > mx.cell.links.length ? h("p", { class: "meta" }, `The first ${mx.cell.links.length} are shown.`) : null);
  } else if (arg) {
    const found = await get(`matrix/links/${encodeURIComponent(arg)}?limit=500`);
    out.push(h("h1", {}, `Matrix: ${found.node.id} ${found.node.name}`.trim()),
      found.groups.map((group) => [h("h2", {}, `${group.label} (${group.count})`),
        h("ul", { class: "mx-links" }, group.links.map((l) => h("li", {}, `${l.far.id}  ${l.far.name}${l.from ? ` (from ${l.from})` : ""}`))),
        group.count > group.links.length ? h("p", { class: "meta" }, `The first ${group.links.length} are shown.`) : null]));
  } else {
    out.push(h("h1", {}, "Matrix"), h("p", { class: "lead" }, `${counted(mx.grid.nodes, "node", "nodes")}, ${counted(mx.grid.links, "link", "links")}. ` +
      "Each number counts the links from the row's kind to the column's."), mxGrid());
  }
  if (said) {
    const words = said.split(" ");
    const link = await get(`matrix/link?src=${encodeURIComponent(words[0])}&rel=${encodeURIComponent(words.slice(1, -1).join(" "))}&dst=${encodeURIComponent(words[words.length - 1])}`);
    mx.node = arg.startsWith("cell:") ? null : { id: arg };
    out.push(mxTold(link).slice(0, -1));
  }
  return out.flat(Infinity).filter(Boolean);
}
