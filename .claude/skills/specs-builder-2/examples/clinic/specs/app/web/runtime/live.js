// Copied from specs-builder's prototype engine. In specs-builder-2 the application serves it at /runtime/ to every prototype it draws; where the comments below say how specs-builder copies it, read that.
// Two changes for specs-builder-2: an element's anchor, data-el, and a part's, data-part, are handles as data-spec-element
// and data-spec-part are; and nothing is marked under the pointer unless ?marks=hover or the Prototype view asks, so that
// a screen's preview and the export show the product undisturbed.
// The engine of a prototype page: prototype/SC1-the-name.html, the working face of a screen.
// The skill's file: `spec.py --write` copies it into site/assets/js/ of a specification. Change it in the skill.
//
// A prototype page is the screen built in the product's look, on sample data, with no server. It holds no
// behaviour of its own that this file can give it:
//
//   ?state=empty|loading|failing   which state to show. An element with data-when="empty" shows only in that
//                                  state; one with data-unless="empty" shows in every state but that one. With no
//                                  state given, the state is "normal".
//   ?as=signed-in                  which variant, read the same way by data-as="signed-in" and data-unless-as.
//   ?view=wireframe                the wireframe view: the look taken out, each element with a handle -- data-spec-element
//                                  or data-spec-part -- outlined, with a marker at its corner. `?spec=1` is read as
//                                  this view. In the look, the product as it looks, only the element under the
//                                  pointer and each element around it with a handle of its own are outlined and
//                                  carry their markers. A marker, clicked, in either view, opens its element in
//                                  the Prototype page's inspector: its component (data-spec-component), its requirements
//                                  (data-spec-req), what it is about (data-spec-about), what is unsettled about it
//                                  (data-spec-question), and its box -- size, padding, border, margin, position, font and
//                                  colours -- measured from the page as it is. Alone, a tooltip says the
//                                  attributes.
//   ?el=3                          open element 3 in the inspector, in either view.
//   ?marks=hover                   in the look, mark the element under the pointer and those around it; without
//                                  it, nothing is marked: the product, undisturbed.
//   ?reset=1                       forget what the prototype kept in the browser: the sample data starts again.
//
//   data-open="id" / data-close    open, or close, the <dialog> with that id.
//   data-states, data-variants     on <main>: the states and variants that site/assets/js/prototype.js shows itself,
//                                  so that the toolbar offers them.
//
// The Prototype page of the specification, prototype/index.html, frames each prototype page and sends the same
// as messages, so that its toolbar changes what is shown and the view without reloading; each page tells it
// which screen it is, and whether it keeps data, so that the toolbar follows a link from one screen to another
// and offers a reset only where there is something to forget. What the product does beyond this -- a cart that adds, a list that
// pages -- is the product's own script, site/assets/js/prototype.js, which keeps what it changes with live.keep() and
// reads it with live.kept().
(function () {
  "use strict";
  var params = new URLSearchParams(location.search);
  var KEY = "specs-builder-prototype:";
  var memory = {};

  function storage() {
    try { localStorage.setItem(KEY + "probe", "1"); localStorage.removeItem(KEY + "probe"); return localStorage; }
    catch (e) { return null; }
  }
  var store = storage();

  var live = window.live = {
    state: params.get("state") || "normal",
    as: params.get("as") || "",
    view: params.get("view") === "wireframe" || params.get("spec") === "1" ? "wireframe" : "look",
    marks: params.get("marks") === "hover" ? "hover" : "off",
    // what the prototype keeps between its pages: in the browser's storage where it may, else for this page alone
    kept: function (name, fallback) {
      var raw = store ? store.getItem(KEY + name) : memory[name];
      if (raw === null || raw === undefined) { return fallback; }
      try { return JSON.parse(raw); } catch (e) { return fallback; }
    },
    keep: function (name, value) {
      var raw = JSON.stringify(value);
      if (store) { store.setItem(KEY + name, raw); } else { memory[name] = raw; }
    },
    forget: function () {
      if (store) {
        Object.keys(store).forEach(function (k) { if (k.indexOf(KEY) === 0) { store.removeItem(k); } });
      }
      memory = {};
    },
    // a link to another prototype page keeps the state, the variant and the overlay; a link that names a variant
    // of its own -- ?as=reset -- opens that one, and a link to the page itself that names none opens it as it is
    carry: function (href) {
      var parts = href.split("?");
      var keep = new URLSearchParams(parts[1] || "");      // what the link asks for itself, as a product's id
      var own = keep.get("as");
      var here = parts[0].split("/").pop() === location.pathname.split("/").pop();
      ["state", "as", "spec", "view", "reset", "marks"].forEach(function (name) { keep.delete(name); });
      if (live.state !== "normal") { keep.set("state", live.state); }
      if (own || (live.as && !here)) { keep.set("as", own || live.as); }
      if (live.view === "wireframe") { keep.set("view", "wireframe"); }
      if (live.marks === "hover") { keep.set("marks", "hover"); }
      var query = keep.toString();
      return query ? parts[0] + "?" + query : parts[0];
    }
  };
  if (params.get("reset")) { live.forget(); }

  function words(list) {
    return (list || "").split(/[\s,]+/).filter(function (w) { return w; });
  }

  function apply() {
    var body = document.body;
    body.setAttribute("data-live-state", live.state);
    body.setAttribute("data-live-as", live.as || "none");
    Array.prototype.forEach.call(document.querySelectorAll("[data-when], [data-unless], [data-as], [data-unless-as]"),
      function (el) {
        var when = words(el.getAttribute("data-when")), unless = words(el.getAttribute("data-unless"));
        var as = words(el.getAttribute("data-as")), unlessAs = words(el.getAttribute("data-unless-as"));
        var shown = (!when.length || when.indexOf(live.state) >= 0) && unless.indexOf(live.state) < 0 &&
                    (!as.length || as.indexOf(live.as) >= 0) && unlessAs.indexOf(live.as) < 0;
        el.hidden = !shown;
      });
    document.dispatchEvent(new CustomEvent("live:change", { detail: { state: live.state, as: live.as } }));
    remeasure();
  }
  // whether the prototype keeps anything in the browser that a reset would forget
  function kept() {
    if (store) {
      return Object.keys(store).some(function (k) { return k.indexOf(KEY) === 0; });
    }
    return Object.keys(memory).length > 0;
  }

  // --- the specification on the page ---------------------------------------------------------------------------
  // an element's handle: its number among its screen's Elements, data-spec-element, or the part of a component it is,
  // data-spec-part, C9.2; the same number or part may stand on many elements, one for each card or row it repeats in
  var HANDLED = "[data-spec-element], [data-spec-part], [data-el], [data-part]";
  function handle(el) {
    return el.getAttribute("data-spec-element") || el.getAttribute("data-el") || el.getAttribute("data-spec-part") ||
           el.getAttribute("data-part") || "";
  }
  function isPart(el) { return !!(el.getAttribute("data-spec-part") || el.getAttribute("data-part")); }
  function withHandle(ref) {
    var said = (ref || "").replace(/"/g, "");
    return said ? document.querySelector('[data-spec-element="' + said + '"], [data-spec-part="' + said + '"], [data-el="' + said +
                                   '"], [data-part="' + said + '"]') : null;
  }
  var tip = null;
  function tipFor(el) {
    var lines = ["#" + handle(el)];
    if (el.getAttribute("data-spec-component")) { lines.push(el.getAttribute("data-spec-component")); }
    if (el.getAttribute("data-spec-req")) { lines.push(words(el.getAttribute("data-spec-req")).join(" ")); }
    if (el.getAttribute("data-spec-about")) { lines.push("about " + words(el.getAttribute("data-spec-about")).join(" ")); }
    var head = lines.join(" · ");
    var q = el.getAttribute("data-spec-question");
    return (q ? head + "\nUnsettled: " + words(q).join(" ") : head)
           + "\nClick its marker to open it in the specification";
  }
  function showTip(event) {
    var el = elementOf(event.target);
    if (!el || framed()) { hideTip(); return; }        // framed, the Prototype page's inspector says it
    if (!tip) {
      tip = document.createElement("div");
      tip.className = "live-tip";
      tip.setAttribute("role", "tooltip");
      document.body.appendChild(tip);
    }
    tip.textContent = tipFor(el);
    var r = el.getBoundingClientRect();
    tip.style.left = Math.max(4, Math.min(window.innerWidth - 260, r.left)) + "px";
    tip.style.top = (r.bottom + 6 + window.scrollY) + "px";
    tip.hidden = false;
  }
  function hideTip() { if (tip) { tip.hidden = true; } }

  // --- the element picked by its marker, said to the Prototype page, whose inspector shows it, every fact a link
  var picked_el = null;                                // the element whose marker was clicked, until the next, or Escape
  // the numbered element an event is on: the element itself, or the one a marker stands for
  function elementOf(target) {
    if (!target || !target.closest) { return null; }
    var mark = target.closest(".live-mark");
    if (mark) { return mark.liveEl || withHandle(mark.getAttribute("data-for")); }
    return target.closest(HANDLED);
  }
  // the screen an element leads to, by a link of its own to that screen's prototype: SC2-the-name.html
  function leadsTo(el) {
    var links = el.tagName === "A" ? [el] : Array.prototype.filter.call(el.querySelectorAll("a[href]"), function (a) {
      return a.closest(HANDLED) === el;                     // a link inside an element of its own is that one's
    });
    var to = "";
    links.some(function (a) {
      var found = /^(SC\d+)-/.exec(a.getAttribute("href") || "");
      if (found) { to = found[1]; }
      return !!found;
    });
    return to;
  }
  // the element's box as the page lays it out, read from the element itself: the border box and its position,
  // the content inside the padding and the border, the margin around, and what the text is set in
  function px(value) { return Math.round(parseFloat(value) || 0); }
  function box(el) {
    var r = el.getBoundingClientRect(), s = window.getComputedStyle(el);
    var padding = [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft].map(px);
    var border = [s.borderTopWidth, s.borderRightWidth, s.borderBottomWidth, s.borderLeftWidth].map(px);
    var margin = [s.marginTop, s.marginRight, s.marginBottom, s.marginLeft].map(px);
    return { left: r.left + window.scrollX, top: r.top + window.scrollY, width: r.width, height: r.height,
             content: { width: r.width - padding[1] - padding[3] - border[1] - border[3],
                        height: r.height - padding[0] - padding[2] - border[0] - border[2] },
             padding: padding, border: border, margin: margin, display: s.display, radius: s.borderRadius,
             borderColor: s.borderTopColor,
             font: s.fontFamily, size: s.fontSize, weight: s.fontWeight, lineHeight: s.lineHeight,
             color: s.color, background: s.backgroundColor };
  }
  function facts(el) {
    var inner = innerOf(el);
    return { live: "pick", el: handle(el), c: el.getAttribute("data-spec-component") || "",
             req: el.getAttribute("data-spec-req") || "", q: el.getAttribute("data-spec-question") || "",
             about: el.getAttribute("data-spec-about") || "", to: leadsTo(el), box: box(el),
             around: chainOf(el).slice(1).reverse().map(handle), inner: inner ? handle(inner) : "" };
  }
  // the first element inside one, in the order the page reads, whose nearest element with a handle is that one
  function innerOf(el) {
    return Array.prototype.filter.call(el.querySelectorAll(HANDLED), function (e) {
      var r = e.getBoundingClientRect();
      return (r.width || r.height) && e.parentElement.closest(HANDLED) === el;
    })[0] || null;
  }
  // out to the element around the one picked, so many steps out, or in to the first inside it
  function step(way, by) {
    if (!picked_el) { return; }
    var to = way === "in" ? innerOf(picked_el) : chainOf(picked_el)[by || 1];
    if (to) { pick(to); remeasure(); }
  }
  // the elements an ID names, lit while the pointer is on that ID in the inspector: those that carry it -- its
  // requirement, what it is about, its component, its question, a part of that component -- and those whose rows
  // name it, as the Prototype page says
  function light(what) {
    Array.prototype.forEach.call(document.querySelectorAll(".is-lit"), function (e) { e.classList.remove("is-lit"); });
    if (!what || !what.ref) { return; }
    var rows = what.handles || [];
    Array.prototype.forEach.call(document.querySelectorAll(HANDLED), function (el) {
      var carried = ["data-spec-req", "data-spec-about", "data-spec-component", "data-spec-question"].some(function (a) {
        return words(el.getAttribute(a)).indexOf(what.ref) >= 0;
      });
      var part = isPart(el) && handle(el).indexOf(what.ref + ".") === 0;
      if (carried || part || rows.indexOf(handle(el)) >= 0) { el.classList.add("is-lit"); }
    });
  }
  function framed() { return window.parent !== window; }
  function pick(el) {
    var was = picked_el;
    picked_el = el;
    Array.prototype.forEach.call(document.querySelectorAll(".is-picked"), function (e) { e.classList.remove("is-picked"); });
    if (el) {
      if (el.liveUnpick) { el.liveUnpick.cancel(); el.liveUnpick = null; el.classList.remove("is-unpicking"); }
      el.classList.add("is-picked");
    }
    // the same number or part, wherever else it repeats: a card's price on every card
    Array.prototype.forEach.call(document.querySelectorAll(".is-repeat"), function (e) { e.classList.remove("is-repeat"); });
    if (el) {
      Array.prototype.forEach.call(document.querySelectorAll(HANDLED), function (e) {
        if (e !== el && handle(e) === handle(el)) { e.classList.add("is-repeat"); }
      });
    }
    Array.prototype.forEach.call(document.querySelectorAll(".live-mark"), function (m) {
      m.classList.toggle("is-picked", !!el && m.liveEl === el);
    });
    if (was && was !== el) { unpick(was); }
    if (framed()) { window.parent.postMessage(el ? facts(el) : { live: "pick", el: "" }, "*"); }
  }
  // the element a pick has left: its picked outline held while it fades out -- to nothing, or to the wireframe's
  // grey -- and then what it is outlined as now, a repeat's dashes or the wireframe's line, fades in. An element
  // still under the pointer keeps its outline, and needs none of this.
  function unpick(e) {
    if (!e.animate || e.classList.contains("is-hover") || e.classList.contains("is-chain")) { return; }
    var wire = live.view === "wireframe";
    e.classList.add("is-unpicking");
    var going = e.animate([{ outlineColor: BLUE }, { outlineColor: wire ? GREY : CLEAR }],
                          { duration: fade(), easing: "cubic-bezier(0.4, 0, 1, 1)", fill: "forwards" });
    e.liveUnpick = going;
    going.onfinish = function () {
      if (e.liveUnpick !== going) { return; }
      e.liveUnpick = null;
      e.classList.remove("is-unpicking");
      going.cancel();
      var now = window.getComputedStyle(e);
      if (now.outlineStyle !== "none") {
        e.animate([{ outlineColor: wire ? GREY : CLEAR }, { outlineColor: now.outlineColor }],
                  { duration: fade(), easing: "cubic-bezier(0.2, 0, 0, 1)" });
      }
    };
  }
  function keep(ref) {
    pick(withHandle(ref));
  }
  // under the pointer, in the wireframe, an element is outlined, and no more: the inner one where elements nest.
  // Its outline fades from the wireframe's grey to blue and back, and its marker brightens and grows a little.
  var GREY = "#444444";
  function hover(el) {
    var wire = live.view === "wireframe";
    Array.prototype.forEach.call(document.querySelectorAll(".is-hover"), function (e) {
      if (e === el) { return; }
      e.classList.remove("is-hover");
      if (wire && e.animate && e !== picked_el) {
        e.animate([{ outlineColor: BLUE, outlineWidth: "2px" }, { outlineColor: GREY, outlineWidth: "1px" }],
                  { duration: fade(), easing: "cubic-bezier(0.4, 0, 1, 1)" });
      }
    });
    if (el && wire && !el.classList.contains("is-hover")) {
      el.classList.add("is-hover");
      if (el.animate && el !== picked_el) {
        el.animate([{ outlineColor: GREY, outlineWidth: "1px" }, { outlineColor: BLUE, outlineWidth: "2px" }],
                   { duration: fade(), easing: "cubic-bezier(0.2, 0, 0, 1)" });
      }
    }
    if (layer) {
      Array.prototype.forEach.call(layer.children, function (b) { b.classList.toggle("is-hot", wire && !!el && b.liveEl === el); });
    }
  }
  // In the look, the element under the pointer and each element around it with a handle of its own -- the chain,
  // the inner one first -- are outlined and carry their markers, and no other element does. The chain follows the
  // pointer at once, wherever it goes. The chain the pointer left stays a moment, its markers faint and still
  // clicked, for as long as the pointer keeps moving and a moment after: the pointer on one of them brings that
  // chain back. So the pointer crosses whatever lies between and reaches any marker of the chain it came from,
  // the outer ones too. Where the pointer leaves for no element, the chain stays as it is for half a second. A
  // marker under the pointer outlines its element more strongly, and says its number and its name beside it.
  var chain = [], fading = [], letGo = 0, LINGER = 600, held = 0, HOLD = 500;
  function chainOf(el) {
    var out = [];
    for (var at = el; at; at = at.parentElement ? at.parentElement.closest(HANDLED) : null) { out.push(at); }
    return out;
  }
  function same(a, b) { return a.length === b.length && a.every(function (e, i) { return e === b[i]; }); }
  // An outline comes and goes softly: its colour faded in and out by an animation of its own, never by a
  // transition, which would take the place of the product's own. A fade moves nothing, so it runs where a reader
  // asks for less motion too; there the markers only lose their growing and sliding (live.css).
  // One duration for every fade, in and out, in both views: --live-fade, set once in live.css, which its
  // transitions use too, so that a marker, an outline and a label always come and go at the same pace.
  var BLUE = "#0b57d0", CLEAR = "rgba(11, 87, 208, 0)", fadeMs = 0;
  function fade() {
    if (!fadeMs) {
      fadeMs = parseFloat(window.getComputedStyle(document.documentElement).getPropertyValue("--live-fade")) || 350;
    }
    return fadeMs;
  }
  function fadeIn(e) {
    if (e.liveFade) { e.liveFade.cancel(); e.liveFade = null; }
    if (e.liveSwap) { e.liveSwap.cancel(); e.liveSwap = null; }
    if (e.animate) { e.animate([{ outlineColor: CLEAR }, { outlineColor: BLUE }], { duration: fade(), easing: "cubic-bezier(0.2, 0, 0, 1)" }); }
  }
  function fadeOut(e) {
    if (e.liveSwap) { e.liveSwap.cancel(); e.liveSwap = null; }
    if (!e.animate || e === picked_el) { e.classList.remove("is-chain", "is-hover"); return; }
    if (e.liveFade) { return; }
    e.liveFade = e.animate([{ outlineColor: BLUE }, { outlineColor: CLEAR }], { duration: fade(), easing: "cubic-bezier(0.4, 0, 1, 1)", fill: "forwards" });
    e.liveFade.onfinish = function () {
      if (chain.indexOf(e) < 0) { e.classList.remove("is-chain", "is-hover"); }
      if (e.liveFade) { e.liveFade.cancel(); e.liveFade = null; }
    };
  }
  // the part an element has in the chain now: the one under the pointer, one around it, or none
  function role(e) {
    var i = chain.indexOf(e);
    return i < 0 ? "" : i ? "is-chain" : "is-hover";
  }
  function cast(e, cls) {
    e.classList.remove("is-chain", "is-hover");
    if (cls) { e.classList.add(cls); }
  }
  // an element whose part changes -- around the one under the pointer, then under it itself -- changes its
  // outline softly: a dashed line cannot become a solid one, so the old one fades out and then the new one in
  function swap(e) {
    if (e.liveFade) { e.liveFade.cancel(); e.liveFade = null; }
    if (!e.animate || e === picked_el) { cast(e, role(e)); return; }
    if (e.liveSwap) { return; }                                // on its way already: it takes the part it has then
    var going = e.animate([{ outlineColor: BLUE }, { outlineColor: CLEAR }],
                          { duration: fade(), easing: "cubic-bezier(0.4, 0, 1, 1)", fill: "forwards" });
    e.liveSwap = going;
    going.onfinish = function () {
      if (e.liveSwap !== going) { return; }
      e.liveSwap = null;
      cast(e, role(e));
      going.cancel();
      if (role(e)) { fadeIn(e); }
    };
  }
  function show(next) {
    var before = chain;
    chain = next;
    before.forEach(function (e) { if (next.indexOf(e) < 0) { fadeOut(e); } });
    next.forEach(function (e, i) {
      var had = before.indexOf(e) >= 0 && !e.liveFade, now = i ? "is-chain" : "is-hover";
      if (had && !e.classList.contains(now) && !e.liveSwap) { swap(e); return; }   // its part changed
      if (e.liveSwap) { return; }                              // it takes its part when the old outline is out
      cast(e, now);
      if (!had && e !== picked_el) { fadeIn(e); }            // the picked one is blue already
    });
    remeasure();
  }
  // the pointer moved to another element, or off every one: its chain at once; the chain it came from stays
  // faint while the pointer moves on, the first one it left, and goes once the pointer rests
  function lookAt(el) {
    clearTimeout(held);
    var next = el ? chainOf(el) : [];
    if (same(next, chain)) { return; }
    if (!fading.length && chain.length && !(el && chain[0].contains(el))) { fading = chain; }
    if (same(fading, next)) { fading = []; }
    clearTimeout(letGo);
    if (fading.length) { letGo = setTimeout(function () { fading = []; remeasure(); }, LINGER); }
    show(next);
  }
  function leave() {                                // off every element: the chain as it is, half a second
    clearTimeout(held);
    if (chain.length || fading.length) {
      held = setTimeout(function () { clearTimeout(letGo); fading = []; show([]); }, HOLD);   // then nothing at all
    }
  }
  function lookBack() {                             // the pointer on a faint marker: that chain is back
    clearTimeout(letGo);
    var back = fading;
    fading = [];
    show(back);
  }
  document.addEventListener("mouseover", function (event) {
    if (live.view === "wireframe") { hover(elementOf(event.target)); return; }
    if (live.marks === "off") { return; }                     // the product, undisturbed
    var mark = event.target.closest ? event.target.closest(".live-mark") : null;
    if (mark) {                                                // on a marker: its chain stays, or comes back
      clearTimeout(held);
      if (fading.indexOf(mark.liveEl) >= 0 && chain.indexOf(mark.liveEl) < 0) { lookBack(); } else { clearTimeout(letGo); }
      return;
    }
    var el = elementOf(event.target);
    if (el) { lookAt(el); } else { leave(); }
  });
  document.documentElement.addEventListener("mouseleave", function () {
    if (live.view === "wireframe") { hover(null); } else { leave(); }
  });
  document.addEventListener("focusin", function (event) {
    var el = elementOf(event.target);
    if (live.view !== "wireframe" && live.marks !== "off" && el &&
        !(event.target.closest && event.target.closest(".live-mark"))) {
      lookAt(el);
    }
  });
  // the marker under the pointer, or with the focus, says whose it is: its element outlined more strongly, and
  // beside it its number or part and its name, which the Prototype page sends from the specification
  var names = {}, label = null;
  function nameMark(mark) {
    if (!mark || !mark.liveEl) { return; }
    mark.liveEl.classList.add("is-marked");
    if (!label) {
      label = document.createElement("div");
      label.className = "live-label";
      label.setAttribute("aria-hidden", "true");
    }
    var ref = mark.getAttribute("data-for");
    label.textContent = ref + (names[ref] ? " · " + names[ref] : "");
    var r = mark.getBoundingClientRect();
    label.style.left = Math.round(r.right + 4) + "px";
    label.style.top = Math.round(r.top - 3) + "px";
    document.body.appendChild(label);
  }
  function unnameMark(mark) {
    if (mark && mark.liveEl) { mark.liveEl.classList.remove("is-marked"); }
    if (label && label.parentNode) { label.parentNode.removeChild(label); }
  }
  document.addEventListener("mouseover", function (event) {
    nameMark(event.target.closest ? event.target.closest(".live-mark") : null);
  });
  document.addEventListener("mouseout", function (event) {
    unnameMark(event.target.closest ? event.target.closest(".live-mark") : null);
  });
  document.addEventListener("focusin", function (event) {
    if (event.target.classList && event.target.classList.contains("live-mark")) { nameMark(event.target); }
  });
  document.addEventListener("focusout", function (event) {
    if (event.target.classList && event.target.classList.contains("live-mark")) { unnameMark(event.target); }
  });
  // the marker, clicked: framed, the inspector shows its element; alone, the Prototype page opens on it
  document.addEventListener("click", function (event) {
    var mark = event.target.closest ? event.target.closest(".live-mark") : null;
    var el = mark ? elementOf(mark) : null;
    if (!el) { return; }
    event.preventDefault();
    if (!framed()) {                                   // alone: the Prototype page has the inspector
      var main = document.querySelector("[data-prototype]");
      var q = new URLSearchParams();
      if (live.view === "wireframe") { q.set("view", "wireframe"); }
      q.set("el", handle(el));
      if (live.state !== "normal") { q.set("show", live.state); } else if (live.as) { q.set("show", live.as); }
      location.href = "/#/prototype/" + encodeURIComponent(main ? main.getAttribute("data-prototype") : "") + "?" + q.toString();
      return;
    }
    pick(el);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && picked_el) { pick(null); }
    var typing = /^(INPUT|SELECT|TEXTAREA)$/.test(event.target.tagName || "") || event.target.isContentEditable;
    if (picked_el && !typing && !event.altKey && !event.ctrlKey && !event.metaKey &&
        (event.key === "ArrowUp" || event.key === "ArrowDown")) {
      event.preventDefault();                       // out to the element around, or in to the first inside it
      step(event.key === "ArrowUp" ? "out" : "in");
    }
  });

  // --- the view: the look, or the wireframe with its markers ----------------------------------------------------
  // In the wireframe each element with a handle is outlined (live.css), and this layer draws its marker at its
  // corner, where the page lays the element out; in the look, the chain under the pointer and the picked element
  // alone, each marker a step to the right of one already at that corner. Drawn again when the window, the state
  // or a picture changes, and the picked element's box said again, as it is then.
  // The layer is fixed to the window, and each marker is placed from its element as the window shows it now:
  // again whenever the page or a part of it scrolls, so that an element that stays put while the rest scrolls --
  // a sticky header -- keeps its markers, and the rest move with theirs. A marker whose corner something else
  // covers -- that header, over what scrolls beneath it -- goes down its element's edge to where the element is
  // first seen, and is hidden only where none of that edge is.
  // A marker is kept from one drawing to the next while its element is still marked, so that it never blinks; a
  // new one fades in, and one no longer wanted fades out before it goes.
  var layer = null, pending = 0, placing = 0;
  function mark(el) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "live-mark is-new";
    b.liveEl = el;                                  // the marker's own element, though its number repeats
    b.setAttribute("data-for", handle(el));
    b.setAttribute("aria-label", (isPart(el) ? "Part " : "Element ") + handle(el));
    layer.appendChild(b);
    return b;
  }
  function unmark(b) {
    if (b.liveGoing) { return; }
    b.liveGoing = true;
    b.classList.add("is-going");
    if (label && label.parentNode && document.activeElement !== b) { unnameMark(b); }
    setTimeout(function () { if (b.parentNode) { b.parentNode.removeChild(b); } }, fade() + 40);
  }
  // whether what the window shows at a point is the element, inside it, or around it: not something over it
  function seen(el, x, y) {
    if (x < 0 || y < 0 || x >= window.innerWidth || y >= window.innerHeight) { return true; }   // off the window
    var hit = document.elementFromPoint(x, y);
    return !hit || el === hit || el.contains(hit) || hit.contains(el);
  }
  function place() {
    placing = 0;
    if (!layer) { return; }
    layer.classList.add("is-probing");              // so that the point finds the page, not a marker; hiding the
                                                    // layer instead would cut short every marker's fade
    var spots = Array.prototype.map.call(layer.children, function (b) {
      if (!document.contains(b.liveEl)) { return { left: 0, top: 0, shown: false }; }
      var r = b.liveEl.getBoundingClientRect(), y = r.top + 2;
      // a corner covered: the marker goes down the element's edge, to where the element is first seen
      var end = Math.min(r.bottom - 2, window.innerHeight);
      while (y < end && !seen(b.liveEl, r.left + 2, y)) { y += 6; }
      return { left: r.left - 7 + 15 * (b.liveShift || 0), top: y - 9,
               shown: !!(r.width || r.height) && (y < end || seen(b.liveEl, r.left + 2, r.top + 2)) };
    });
    layer.classList.remove("is-probing");
    Array.prototype.forEach.call(layer.children, function (b, i) {
      b.style.left = Math.round(spots[i].left) + "px";
      b.style.top = Math.round(spots[i].top) + "px";
      b.hidden = !spots[i].shown;
    });
  }
  function replace() {
    if (!placing) { placing = (window.requestAnimationFrame || setTimeout)(place) || 1; }
  }
  function measure() {
    pending = 0;
    var all = live.view === "wireframe";
    var those = all ? Array.prototype.slice.call(document.querySelectorAll(HANDLED))
                    : chain.concat(fading, picked_el ? [picked_el] : []).filter(function (e, i, list) {
                      return list.indexOf(e) === i;
                    });
    if (!layer || !layer.parentNode) {
      layer = document.createElement("div");
      layer.className = "live-measure";
      document.body.appendChild(layer);
    }
    var had = Array.prototype.filter.call(layer.children, function (b) { return !b.liveGoing; });
    var kept = [], fresh = [], shown = false, taken = [];
    those.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (!r.width && !r.height) { return; }                    // hidden in this state
      var left = r.left - 7, top = r.top - 7, shift = 0;
      while (!all && taken.some(function (t) { return Math.abs(t[0] - left) < 13 && Math.abs(t[1] - top) < 13; })) {
        left += 15;                                             // a corner shared with an element already marked
        shift += 1;
      }
      taken.push([left, top]);
      var b = had.filter(function (o) { return o.liveEl === el && kept.indexOf(o) < 0; })[0];
      if (!b) { b = mark(el); fresh.push(b); }
      b.liveShift = shift;                                      // steps to the right of a marker at that corner
      b.classList.toggle("is-picked", el === picked_el);
      b.classList.toggle("is-left", !all && el !== picked_el && chain.indexOf(el) < 0 && fading.indexOf(el) >= 0);
      kept.push(b);
      if (el === picked_el) { shown = true; }
    });
    had.forEach(function (b) { if (kept.indexOf(b) < 0) { unmark(b); } });
    place();
    fresh.forEach(function (b) { void b.offsetWidth; b.classList.remove("is-new"); });   // placed, then faded in
    if (picked_el && !shown) { pick(null); }                    // the state hid it: nothing to inspect
    else if (picked_el && framed()) { window.parent.postMessage(facts(picked_el), "*"); }   // its box, as it is now
  }
  function remeasure() {
    if (pending) { return; }
    pending = setTimeout(measure, 0) || 1;          // after the change has laid out; a timer runs in a hidden tab too
  }
  function view(name) {
    live.view = name === "wireframe" ? "wireframe" : "look";
    document.body.classList.toggle("wire-on", live.view === "wireframe");
    document.body.classList.toggle("spec-on", live.view === "wireframe");
    hideTip();
    hover(null);
    clearTimeout(held);
    fading = [];
    show([]);                                       // the picked element stays picked, in either view
    remeasure();
  }
  window.addEventListener("resize", remeasure);
  window.addEventListener("scroll", replace, { passive: true, capture: true });   // the page, or a part of it
  document.addEventListener("load", remeasure, true);                 // a picture that arrives moves the rest
  // what the product's own script changes -- a message shown, a field marked, rows drawn -- moves the rest too;
  // the classes the hover and the pick set are this file's own, and move nothing
  var OWN = /^(is-hover|is-picked|is-chain|is-marked|is-lit|is-repeat|is-unpicking)$/;
  function moved(records) {
    return records.some(function (r) {
      if (r.type !== "attributes" || r.attributeName !== "class") { return true; }
      function rest(said) { return said.split(/\s+/).filter(function (c) { return c && !OWN.test(c); }).sort().join(" "); }
      return rest(r.oldValue || "") !== rest(r.target.getAttribute("class") || "");
    });
  }
  function follow() {
    var main = document.querySelector("[data-prototype]");
    if (!main) { return; }
    if (window.MutationObserver) {
      new MutationObserver(function (records) { if (moved(records)) { remeasure(); } })
        .observe(main, { attributes: true, attributeOldValue: true, childList: true, characterData: true, subtree: true });
    }
    if (window.ResizeObserver) { new ResizeObserver(remeasure).observe(main); }
  }

  // --- dialogs ----------------------------------------------------------------------------------------------------
  document.addEventListener("click", function (event) {
    var opener = event.target.closest ? event.target.closest("[data-open]") : null;
    if (opener) {
      var dialog = document.getElementById(opener.getAttribute("data-open"));
      if (dialog && dialog.showModal) { event.preventDefault(); dialog.showModal(); }
      return;
    }
    var closer = event.target.closest ? event.target.closest("[data-close]") : null;
    if (closer) {
      var open = closer.closest("dialog");
      if (open) { event.preventDefault(); open.close(); }
      return;
    }
    var link = event.target.closest ? event.target.closest("a[href]") : null;
    if (link && /\.html(\?|$)/.test(link.getAttribute("href")) && !/^[a-z]+:/i.test(link.getAttribute("href"))) {
      link.setAttribute("href", live.carry(link.getAttribute("href")));
    }
  });
  document.addEventListener("mouseover", showTip);
  document.addEventListener("focusin", showTip);

  // --- what the Prototype page's toolbar says -----------------------------------------------------------------------
  window.addEventListener("message", function (event) {
    var said = event.data || {};
    if (said.live !== true) { return; }
    if (said.names) { names = said.names; }
    if (said.marks !== undefined) {
      live.marks = said.marks === "off" ? "off" : "hover";
      if (live.marks === "off") { clearTimeout(held); fading = []; show([]); }
    }
    if (said.step) { step(said.step, said.by); }
    if (said.light !== undefined) { light(said.light); }
    if (said.view !== undefined) { view(said.view); }
    if (said.spec !== undefined) { view(said.spec ? "wireframe" : "look"); }
    if (said.reset) { live.forget(); location.reload(); return; }
    if (said.state !== undefined || said.as !== undefined) {
      if (said.state !== undefined) { live.state = said.state || "normal"; }
      if (said.as !== undefined) { live.as = said.as || ""; }
      apply();
    }
    if (said.el !== undefined) { keep(said.el); }        // once the state shows it, so that it has a size
  });

  function start() {
    view(live.view);
    apply();
    follow();
    var main = document.querySelector("[data-prototype]");
    if (main && window.parent !== window) {
      window.parent.postMessage({ live: "at", screen: main.getAttribute("data-prototype"),
                                  page: location.pathname.split("/").pop() + location.search, kept: kept() }, "*");
    }
    if (params.get("el")) { keep(params.get("el")); }
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", start); } else { start(); }
})();
