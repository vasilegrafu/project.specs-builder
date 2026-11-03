// What an ID is, without leaving the view. A right click on an ID, or the menu key on its link, opens a card:
// its kind, its name, a sentence or two of its text and the facts that place it, from /api/card, which takes them
// from the grammar's `card` for that kind, and the node's links by kind. A right click on an ID inside a card opens another beside
// it, so that a chain of cards walks the graph from any page, and a pin keeps a card open from page to page. Its x, Escape for
// the newest, or a click elsewhere for all but the pinned, close them. Its Preview opens the node's own view in a popup over this one -- the application in a
// frame, ?peek=1, without its bar, where a link followed stays -- and Escape, × or a click outside closes that.
// Anything may ask for its card by saying `data-card`. Loaded before engine.js; it draws
// with engine.js's h(), chip() and get(), and menu.js's icon(). The export runs this same file over the cards it holds,
// window.cards, with no server to ask, no application to preview and no icons: its one way out is the word Open.
"use strict";

const peeked = document.documentElement.classList.contains("peeked");
const inExport = "cards" in window;
const CARD_MOST = 6, CARD_GAP = 8;                  // the cards open at once before the oldest folds to the strip, and px between them
const CARD_PRESS = 500, CARD_SLIP = 10;             // ms a finger is held on an ID for its card, and px it may slip and still be held
const TIP_AFTER = 120;                              // ms a pointer rests on an ID before the tip says what it is
const TIP_ON = ".chip, a.ref, a.id, .side-id, .map-tag, .map-node";   // what shows an ID, here and in the export
const idCards = { held: new Map(), open: [], strip: null, peek: null, from: null };

// The cards fetched are kept until the view is drawn again: what a change moved is asked again then.
function forgetCards() {
  idCards.held.clear();
  closeCard();                                       // all but the pinned
}

// What says an ID: anything marked `data-card`, a chip, or an ID in a text, on the page or in a card. The menu and search do not.
function idLink(node) {
  if (!node || !node.closest) return null;
  if (inExport) return node.closest("main a.id, .id-card a.id");
  const said = node.closest("[data-card]");
  if (said) return said;
  const link = node.closest("a.chip, a.ref");
  return link && link.closest("#view, .id-card") && /^#\/(node|graph)\/[A-Za-z]/.test(link.getAttribute("href") || "") ? link : null;
}
const idOf = (link) => inExport ? link.getAttribute("href").slice(1)
  : link.dataset.card || decodeURIComponent(link.getAttribute("href").replace(/^#\/(node|graph)\//, ""));

function cardFor(id) {
  if (inExport) return Promise.resolve(window.cards[id] || null);
  if (!idCards.held.has(id)) idCards.held.set(id, get(`card/${encodeURIComponent(id)}`).catch(() => null));
  return idCards.held.get(id);
}

// The ways on to a node, here and in another tab: a card's foot and a node's page hold the same ones
const graphWays = (id) => [["focus", "Around: what it is linked to", mapHref(id)], ["layers", "Layers: what connects to it", mapHref(`layers:${id}`)],
                           ["impact", "Impact: what stands on it", mapHref(`impact:${id}`)]];
const wayHere = (name, word, href) => h("a", { class: "mx-tool", href, title: word, "aria-label": word.split(":")[0] }, icon(name));
// from the page's own address: a preview's would open a preview
const wayAway = (name, word, href) => h("a", { class: "mx-tool away", href: location.pathname + href, target: "_blank", rel: "noopener",
                                               title: `${word}, in another tab`, "aria-label": `${word.split(":")[0]} in another tab` }, icon(name), icon("newtab"));

function drawCard(c, entry) {
  const ids = (list, more) => [list.map((id) => chip(id)), more ? h("span", { class: "id-card-more" }, `and ${more} more`) : null];
  const mark = (name, word) => (inExport ? word : icon(name));
  const top = c.parent ? c.parent.id : c.id;         // the Graph and the Matrix hold what a row belongs to
  const ways = inExport ? [] : [...graphWays(top), ["matrix", "Matrix: all its links", mxNode(top)]];
  const pin = h("button", { type: "button", class: "id-card-tool", title: "Pin it: it stays open, on other pages too", "aria-label": "Pin", "aria-pressed": String(entry.pinned),
                            onclick: () => pinCard(entry, pin) }, mark("pin", "Pin"));
  return [
    h("div", { class: "id-card-head" }, h("span", { class: `chip kind-${c.kind}` }, c.id),
      h("span", { class: "id-card-kind" }, c.kind),
      c.parent ? h("span", { class: "id-card-of" }, "of ", chip(c.parent.id)) : null,
      h("span", { class: "id-card-tools" }, pin,
        h("button", { type: "button", class: "id-card-tool", title: "Close", "aria-label": "Close", onclick: () => shutCard(entry) }, mark("close", "×")))),
    c.name ? h("p", { class: "id-card-name" }, c.name) : null,
    c.said ? h("p", { class: c.name ? "id-card-said" : "id-card-name" }, c.said) : null,
    c.facts.length ? h("dl", {}, c.facts.map((f) => [h("dt", {}, f.label),
      h("dd", {}, f.ids ? ids(f.ids, f.more) : linkify(f.text))])) : null,
    c.unsettled.length ? h("p", { class: "id-card-warn" }, "Not settled: ", ids(c.unsettled.map((u) => u.id), 0)) : null,
    c.stale ? h("p", { class: "id-card-warn" }, c.stale === 1 ? "Stale: it stands on something that changed since it was read"
      : `Stale: it stands on ${c.stale} things that changed since it was read`) : null,
    c.linked && c.linked.kinds.length ? h("div", { class: "id-card-links" }, c.linked.kinds.map((k) => h("div", { class: "id-card-linked" },
      h("div", { class: "id-card-link-kind" }, h("span", { class: `drop-dot kind-${k.kind}` }), PLURAL[k.kind] || k.kind, " ", h("span", { class: "id-card-more" }, k.count)),
      h("div", { class: "id-card-link-ids" }, k.nodes.map((n) => h("a", { class: `chip kind-${k.kind}`, href: nodeHref(n.id), title: n.name || "" }, n.id)),
        k.count > k.nodes.length ? h("a", { class: "id-card-more", href: `#/matrix/${encodeURIComponent(c.id)}`, title: "All of them, in the Matrix" }, `+${k.count - k.nodes.length}`) : null)))) : null,
    h("div", { class: "id-card-ways" }, inExport ? h("a", { href: nodeHref(c.id) }, "Open") : [
      h("div", { class: "id-card-way-row" }, wayHere("document", "Open", nodeHref(c.id)),
        peeked ? null : h("button", { type: "button", class: "mx-tool", title: "Preview", "aria-label": "Preview", onclick: () => openPeek(c.id, entry.link) }, icon("preview")),
        h("button", { type: "button", class: "mx-tool", title: "Request a change", "aria-label": "Request a change", onclick: () => requestChange(c.id, c.name) }, icon("request")),
        h("span", { class: "id-card-graph" }, ways.map((way) => wayHere(...way)))),
      h("div", { class: "id-card-way-row" }, wayAway("document", "Open", nodeHref(c.id)),
        h("span", { class: "id-card-graph" }, ways.map((way) => wayAway(...way))))]),
  ];
}

// A card never covers what opened it: below it, above it, or beside it, whichever it fits, and in a window too narrow for any of
// those it takes the larger room and scrolls inside itself. One opened from a card stands beside that one where there is room.
function placeCard(entry) {
  const card = entry.el;
  card.style.maxHeight = `${window.innerHeight - 16}px`;
  const wide = card.offsetWidth;
  let high = card.offsetHeight;
  const at = entry.link.getBoundingClientRect();
  const room = { below: window.innerHeight - at.bottom - 14, above: at.top - 14 };
  const sideOf = (box) => [box.right + CARD_GAP, box.left - CARD_GAP - wide].find((x) => x >= 8 && x + wide <= window.innerWidth - 8);
  const chained = entry.parent ? sideOf(entry.parent.rect) : undefined;
  const beside = sideOf(at);
  let left, top;
  if (chained !== undefined) {
    left = chained;
    top = entry.parent.rect.top;
  } else if (high <= room.below) {
    left = at.left;
    top = at.bottom + 6;
  } else if (high <= room.above) {
    left = at.left;
    top = at.top - high - 6;
  } else if (beside !== undefined) {
    left = beside;
    top = at.top;
  } else {
    const under = room.below >= room.above;
    high = under ? room.below : room.above;
    card.style.maxHeight = `${high}px`;
    left = at.left;
    top = under ? at.bottom + 6 : at.top - high - 6;
  }
  left = Math.max(8, Math.min(left, window.innerWidth - wide - 8));
  top = Math.max(8, Math.min(top, window.innerHeight - high - 8));
  card.style.left = `${left}px`;
  card.style.top = `${top}px`;
  entry.rect = { left, top, right: left + wide, bottom: top + high };
}

const cardsOf = (node) => idCards.open.find((e) => e.el.contains(node));

// A card opened from the page starts a new chain; from a card, it goes on from that card, in place of what came after it. A
// node already open says so and opens no second card, so that a chain cannot go round. Pinned cards are never taken away.
async function openCard(link) {
  const id = idOf(link);
  const c = await cardFor(id);
  if (!c || !link.isConnected) return;               // a view drawn again since: its link is gone
  const open = idCards.open.find((e) => e.id === id);
  if (open) { unfoldCard(open); flashCard(open); return; }
  const parent = cardsOf(link) || null;
  const keep = parent ? idCards.open.indexOf(parent) : -1;
  for (const e of idCards.open.slice(keep + 1)) if (!e.pinned) dropCard(e);
  const entry = { id, link, parent, pinned: false, folded: false, rect: null, el: h("div", { class: "id-card", role: "group", "aria-label": `${c.id} ${c.name || ""}`.trim() }) };
  entry.el.replaceChildren(...drawCard(c, entry).flat(Infinity).filter(Boolean));
  document.body.append(entry.el);
  idCards.open.push(entry);
  placeCard(entry);
  while (idCards.open.filter((e) => !e.folded).length > CARD_MOST) {
    const oldest = idCards.open.find((e) => !e.folded && !e.pinned && e !== entry);
    if (!oldest) break;
    oldest.folded = true;
    oldest.el.hidden = true;
  }
  drawStrip();
}

function flashCard(entry) {
  entry.el.classList.remove("flash");
  void entry.el.offsetWidth;                         // so that it starts again
  entry.el.classList.add("flash");
}

function unfoldCard(entry) {
  if (!entry.folded) return;
  entry.folded = false;
  entry.el.hidden = false;
  const oldest = idCards.open.find((e) => !e.folded && !e.pinned && e !== entry);
  if (oldest && idCards.open.filter((e) => !e.folded).length > CARD_MOST) { oldest.folded = true; oldest.el.hidden = true; }
  drawStrip();
}

function pinCard(entry, button) {
  entry.pinned = !entry.pinned;
  entry.el.classList.toggle("pinned", entry.pinned);
  button.setAttribute("aria-pressed", String(entry.pinned));
}

function dropCard(entry) {
  entry.el.remove();
  idCards.open = idCards.open.filter((e) => e !== entry);
  for (const e of idCards.open) if (e.parent === entry) e.parent = null;
}

// A card closed takes with it what was opened from it, pinned cards apart
function shutCard(entry) {
  const gone = [entry];
  for (const e of idCards.open) if (!e.pinned && gone.includes(e.parent)) gone.push(e);
  gone.forEach(dropCard);
  drawStrip();
}

function closeCard() {
  for (const e of [...idCards.open]) if (!e.pinned) dropCard(e);
  drawStrip();
}

// The cards folded away for want of room, each a button to bring it back
function drawStrip() {
  if (!idCards.strip) {
    idCards.strip = h("div", { class: "id-card-strip", hidden: true });
    document.body.append(idCards.strip);
  }
  const folded = idCards.open.filter((e) => e.folded);
  idCards.strip.hidden = !folded.length;
  idCards.strip.replaceChildren(...folded.map((e) => h("button", { type: "button", class: "id-card-tool id-card-folded", title: `Bring back ${e.id}`, onclick: () => unfoldCard(e) }, e.id)));
}

// What a pause on an ID says: its kind, so that R4 reads as a requirement and F2 as a flow, in the small tip that wireCards shows
function idKind(el) {
  const id = el.dataset.id || el.dataset.card || (el.hasAttribute("href") ? idOf(el) : el.textContent.trim());
  const kind = inExport ? (window.cards[id] || {}).kind : (state.names[id] || {}).kind;
  return kind ? kind[0].toUpperCase() + kind.slice(1) : "";
}

function wireTips() {
  let tip = null, timer = 0, over = null;                 // made when first shown: this runs before engine.js gives it h()
  const hide = () => { clearTimeout(timer); over = null; if (tip) tip.hidden = true; };
  const show = (el) => {
    const word = idKind(el);
    if (!word || !el.isConnected) return;
    if (!tip) document.body.append(tip = h("div", { class: "id-tip", role: "tooltip", hidden: true }));
    tip.textContent = word;
    tip.hidden = false;
    const at = el.getBoundingClientRect();
    const above = at.top - tip.offsetHeight - 6;
    tip.style.top = `${above >= 8 ? above : at.bottom + 6}px`;
    tip.style.left = `${Math.max(8, Math.min(at.left + at.width / 2 - tip.offsetWidth / 2, window.innerWidth - tip.offsetWidth - 8))}px`;
  };
  document.addEventListener("mouseover", (e) => {
    const el = e.target.closest ? e.target.closest(TIP_ON) : null;
    if (el === over) return;
    hide();
    if (!el || !window.matchMedia("(hover: hover)").matches) return;
    over = el;
    timer = setTimeout(() => show(el), TIP_AFTER);
  });
  for (const name of ["click", "contextmenu", "hashchange", "keydown"]) window.addEventListener(name, hide, true);
  window.addEventListener("scroll", hide, true);
  document.addEventListener("mouseleave", hide);
}

function wireCards() {
  wireTips();
  // by the path the event took, for the button clicked may be gone by the time it arrives here
  const held = (e) => e.composedPath().some((n) => n === idCards.strip || n === idCards.peek || n.tagName === "DIALOG" || (n.classList && n.classList.contains("id-card")));
  document.addEventListener("click", (e) => {
    if (idCards.open.length && !held(e)) closeCard();
  });
  // A card moves by its head, within the window
  document.addEventListener("pointerdown", (e) => {
    const entry = e.button === 0 ? cardsOf(e.target) : null;
    if (!entry || !e.target.closest(".id-card-head") || e.target.closest("button, a")) return;
    e.preventDefault();
    const card = entry.el;
    const grip = { x: e.clientX - entry.rect.left, y: e.clientY - entry.rect.top };
    card.setPointerCapture(e.pointerId);
    card.classList.add("moving");
    const move = (m) => {
      const wide = card.offsetWidth, high = card.offsetHeight;
      const left = Math.max(8, Math.min(m.clientX - grip.x, window.innerWidth - wide - 8));
      const top = Math.max(8, Math.min(m.clientY - grip.y, window.innerHeight - high - 8));
      card.style.left = `${left}px`;
      card.style.top = `${top}px`;
      entry.rect = { left, top, right: left + wide, bottom: top + high };
    };
    const done = () => {
      card.removeEventListener("pointermove", move);
      card.removeEventListener("pointerup", done);
      card.removeEventListener("pointercancel", done);
      card.classList.remove("moving");
    };
    card.addEventListener("pointermove", move);
    card.addEventListener("pointerup", done);
    card.addEventListener("pointercancel", done);
  });
  // A finger held on an ID opens its card: an iPhone or iPad says no contextmenu, and Android's comes as well, so `done` keeps
  // the one press from opening twice, and from following the link when the finger lifts. A finger that moves is scrolling.
  const press = { timer: 0, done: false, x: 0, y: 0 };
  const letGo = () => clearTimeout(press.timer);
  document.addEventListener("pointerdown", (e) => {
    letGo();
    press.done = false;
    const link = e.pointerType === "mouse" ? null : idLink(e.target);
    if (!link) return;
    press.x = e.clientX;
    press.y = e.clientY;
    press.timer = setTimeout(() => { press.done = true; openCard(link); }, CARD_PRESS);
  });
  document.addEventListener("pointermove", (e) => {
    if (Math.hypot(e.clientX - press.x, e.clientY - press.y) > CARD_SLIP) letGo();
  });
  document.addEventListener("pointerup", letGo);
  document.addEventListener("pointercancel", letGo);
  document.addEventListener("click", (e) => {
    if (!press.done) return;
    press.done = false;
    e.preventDefault();
    e.stopPropagation();
  }, true);
  document.addEventListener("contextmenu", (e) => {
    letGo();
    const link = idLink(e.target);
    if (link) { e.preventDefault(); if (!press.done) openCard(link); return; }
    if (held(e)) return;
    closeCard();
    if (e.target.closest && e.target.closest(".graph-map")) e.preventDefault();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || document.querySelector("dialog[open]")) return;
    const newest = [...idCards.open].reverse().find((c) => !c.pinned);
    if (idCards.peek && !idCards.peek.hidden) closePeek();
    else if (newest) shutCard(newest);
    else if (peeked && window.parent !== window) window.parent.postMessage("id-peek:close", "*");
  });
  // the preview's page says when Escape is pressed in it, since a key pressed there is its own
  window.addEventListener("message", (e) => {
    const frame = idCards.peek && idCards.peek.querySelector("iframe");
    if (frame && e.source === frame.contentWindow && e.data === "id-peek:close") closePeek();
  });
}

// ---- the preview: the node's own view, in the application drawn again in a frame without its bar

function openPeek(id, back) {
  if (!idCards.peek) {
    const close = h("button", { type: "button", class: "id-peek-close", "aria-label": "Close the preview", onclick: closePeek }, "×");
    idCards.peek = h("div", { class: "id-peek", hidden: true },
      h("div", { class: "id-peek-panel", role: "dialog", "aria-modal": "true", "aria-labelledby": "id-peek-title" },
        h("div", { class: "id-peek-head" }, h("p", { id: "id-peek-title" }),
          h("a", { class: "id-peek-open", onclick: closePeek }, "Open the page"), close),
        h("iframe", { class: "id-peek-frame", title: "The node, previewed" })));
    idCards.peek.addEventListener("click", (e) => { if (e.target === idCards.peek) closePeek(); });
    document.body.append(idCards.peek);
  }
  const known = state.names[id] || {};
  idCards.from = back || document.activeElement;           // focus goes back to the ID, the card being gone
  idCards.peek.querySelector("#id-peek-title").replaceChildren(h("span", { class: `chip kind-${known.kind || "unknown"}` }, id),
    " ", known.name || "");
  idCards.peek.querySelector(".id-peek-open").href = nodeHref(id);
  idCards.peek.querySelector("iframe").src = `/?peek=1${nodeHref(id)}`;
  idCards.peek.hidden = false;
  document.documentElement.classList.add("id-peeking");
  idCards.peek.querySelector(".id-peek-close").focus();
}

function closePeek() {
  if (!idCards.peek || idCards.peek.hidden) return;
  idCards.peek.hidden = true;
  idCards.peek.querySelector("iframe").src = "about:blank";
  document.documentElement.classList.remove("id-peeking");
  if (idCards.from && idCards.from.isConnected && idCards.from.focus) idCards.from.focus();
}

wireCards();
