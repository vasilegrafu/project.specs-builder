// What helps along a page: an outline of its headings where it has several, small links to the node before and after
// it in the order of the tree, at the top of its page and at the foot, and the page alone on a sheet of A4, in a tab of its own, ?print=1: the Print button of the bar opens it,
// shown first, with what it holds as the paper will. A screen goes across the sheet's whole width, in the state it is
// shown in, and runs on from sheet to sheet. On paper, from there or by the browser's own print, every page is A4 with
// margins of its own and a foot saying what it is, ink on white whatever the theme on screen. No aid in a preview or on the prototype, which is a tool, not a page.
// Loaded before engine.js; it draws with engine.js's h(), state and nodeHref(), and side.js's nodesOf().
"use strict";

const OUTLINE_LEAST = 3;                                       // fewer headings than this are seen at a glance
const SHEET = document.documentElement.classList.contains("sheet");
const SCREEN_WIDE = 1200;                                      // px: a screen on a sheet is drawn as on a desktop
const SHEET_WIDE = 657;                                        // px: 174mm, A4's width inside its margins, whatever the window
const SHEET_TALL = 950;                                        // px: what a sheet of A4 holds inside its margins

function outline(body) {
  const heads = [...body.querySelectorAll("h2")].filter((head) => !head.closest(".panel, .card"));
  if (heads.length < OUTLINE_LEAST) return null;
  const go = (head) => {
    head.tabIndex = -1;
    head.scrollIntoView();
    head.focus({ preventScroll: true });
  };
  return h("nav", { class: "outline", "aria-label": "On this page" },
    h("p", { class: "outline-title" }, "On this page"),
    h("ul", {}, heads.map((head) => h("li", {},
      h("button", { type: "button", class: "outline-link", onclick: () => go(head) }, head.textContent.trim())))));
}

function pager(id) {
  const known = state.names[id];
  if (!known || known.kind === "document") return null;
  const row = nodesOf(known.kind);
  const at = row.indexOf(id);
  const link = (other, word, side) => {
    if (!other) return null;
    const said = `${word}: ${other} ${state.names[other].name || ""}`.trim();
    return h("a", { class: `pager-link ${side}`, href: nodeHref(other), title: said, "aria-label": said },
      side === "pager-before" ? [icon("chevron"), other] : [other, icon("chevron")]);
  };
  const before = link(row[at - 1], "Previous", "pager-before");
  const after = link(row[at + 1], "Next", "pager-after");
  return before || after ? h("nav", { class: "pager", "aria-label": `Beside ${id}` }, before, after) : null;
}

// What the page's foot says on paper: what it is, and which sheet of how many. Paper is the page's own, so it is said
// on a view in the application too, for the browser's own print.
function paperFoot(name) {
  let style = document.getElementById("paper-foot");
  if (!style) document.head.append(style = h("style", { id: "paper-foot" }));
  const small = 'font: 9pt system-ui, "Segoe UI", sans-serif; color: #5f6878;';
  style.textContent = `@page { @bottom-left { content: ${JSON.stringify(name)}; ${small} }
    @bottom-right { content: "Page " counter(page) " of " counter(pages); ${small} } }`;
}

// A screen across the whole width of the sheet, running on from sheet to sheet. A frame is one solid block to a printer,
// cut off where the sheet ends, so a screen taller than a sheet is drawn as one frame to a sheet, each holding the part
// that falls there in a box no taller than the sheet: still the screen at its own width, in its own state. The page in
// a frame is moved, never scrolled, so that what sticks to the top of a screen does not come again on every sheet.
function wholeOnSheet(iframe) {
  // what a cut must not go through: each thing that holds words or is a picture, by where it starts and ends
  const leaves = (page) => [...page.body.querySelectorAll("*")]
    .filter((el) => !el.closest("svg svg, svg *") && (el.matches("img, svg, input, button, select, textarea") ||
      !el.children.length || [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())))
    .map((el) => el.getBoundingClientRect()).filter((r) => r.height > 0).map((r) => [r.top, r.bottom]);
  const cutAt = (held, at, most) => {                           // as far down as a sheet reaches, above what it would cut
    let cut = at + most;
    for (let moved = true; moved;) {
      moved = false;
      for (const [top, bottom] of held) {
        if (at < top && top < cut && cut < bottom) { cut = top; moved = true; }
      }
    }
    return cut;
  };
  iframe.setAttribute("loading", "eager");                      // a lazy frame below the sheet's fold is printed empty
  iframe.addEventListener("load", () => {
    const box = iframe.parentElement;
    const wide = Number(iframe.dataset.width) || SCREEN_WIDE;
    const scale = SHEET_WIDE / wide;
    iframe.style.width = `${wide}px`;
    const tall = iframe.contentDocument.documentElement.scrollHeight;
    let head = box.previousElementSibling;
    while (head && !/^H[12]$/.test(head.tagName)) head = head.previousElementSibling;
    const above = head ? box.getBoundingClientRect().top - head.getBoundingClientRect().top : 0;
    const held = leaves(iframe.contentDocument);
    const parts = [];
    for (let at = 0; at < tall - 1;) {
      const room = (SHEET_TALL - (at ? 0 : above)) / scale;
      const end = at + room >= tall ? tall : cutAt(held, at, room);
      parts.push({ at, high: end - at });
      at = held.some(([, bottom]) => bottom > end) ? end : tall;  // nothing but the page's own end is left for another sheet
    }
    if (parts.length > 1 && head && head.tagName === "H2") head.classList.add("sheet-start");
    box.replaceChildren(...parts.map(({ at, high }) => {
      const part = h("iframe", { src: iframe.src, title: iframe.title, class: "frame preview", scrolling: "no" });
      part.style.cssText = `width: ${wide}px; height: ${high}px; transform: scale(${scale});`;
      part.addEventListener("load", () => { part.contentDocument.body.style.transform = `translateY(${-at}px)`; });
      const clip = h("div", { class: "sheet-part" }, part);
      clip.style.height = `${high * scale}px`;
      return clip;
    }));
  }, { once: true });
}

// The prototype on a sheet: the screen alone, in the state the address it came from says.
async function screenOnSheet(arg) {
  const id = arg || nodesOf("screen")[0];
  if (!id) return [h("h1", {}, "Prototype"), h("p", { class: "empty" }, "No screen is drawn yet.")];
  const asked = new URLSearchParams(location.hash.split("?")[1] || "");
  const shown = new URLSearchParams(location.search).get("screen");
  const box = frame(`/prototype/${encodeURIComponent(id)}.html${shown ? `?${shown}` : ""}`, "preview", `The prototype of ${id}`);
  box.querySelector("iframe").dataset.width = WIDTHS[asked.get("width")] || "";
  return [h("h1", {}, `${id} ${(state.names[id] || {}).name || ""}`.trim()),
    asked.get("show") ? h("p", { class: "meta" }, `As it shows ${asked.get("show")}.`) : null, box];
}

function onSheet(content) {
  const body = h("div", { class: "view-body" }, content);
  body.querySelectorAll("iframe.preview").forEach(wholeOnSheet);
  body.querySelectorAll(".thumb-frame iframe").forEach((iframe) => iframe.setAttribute("loading", "eager"));
  const name = `${state.summary.title} - ${(body.querySelector("h1") || { textContent: "" }).textContent}`;
  document.title = name;
  paperFoot(name);
  const close = () => {
    window.close();                                             // a tab that has gone on from where it opened stays open
    setTimeout(() => { location.href = `/${location.hash}`; }, 200);
  };
  return [h("div", { class: "sheet-bar" }, h("span", { class: "sheet-title" }, name),
    h("button", { type: "button", class: "button small primary", onclick: () => window.print() }, icon("print"), "Print"),
    h("button", { type: "button", class: "button small", onclick: close }, "Close")), body];
}

// A view's content with what helps along it: the view is told whether an outline stands beside it.
function withAids(view, where, arg, content) {
  if (SHEET) return onSheet(content);
  const plain = where === "prototype" || where === "matrix" || document.documentElement.classList.contains("peeked");
  const body = h("div", { class: "view-body" }, content);
  const crumbs = body.querySelector(".crumbs");
  const above = !plain && where === "node" && crumbs ? pager(arg) : null;
  if (above) {
    crumbs.classList.add("with-pager");
    crumbs.append(above);
    body.append(h("footer", { class: "page-foot" }, pager(arg)));
  }
  const heads = plain ? null : outline(body);
  view.classList.toggle("outlined", heads !== null);
  paperFoot(`${state.summary.title} - ${(body.querySelector("h1") || { textContent: "" }).textContent}`);
  return [heads, body].filter(Boolean);
}

// The sheet of the page in view: asked as it is opened, since the prototype keeps what it shows in the address unsaid.
function printAddress(link) {
  const shown = location.hash.startsWith("#/prototype") && tool.current ? `&screen=${encodeURIComponent(tool.shown)}` : "";
  link.href = `/?print=1${shown}${location.hash}`;
}

// The whole specification as one file, as `spec.py export` writes it, kept where the browser keeps what it fetches.
async function exportWhole(button) {
  const word = button.querySelector(".tool-word");
  const usual = button.title;
  button.disabled = true;
  word.textContent = "Exporting...";
  try {
    const answer = await fetch("/api/export", { method: "POST" });
    if (!answer.ok) throw new Error((await answer.json()).refused || answer.statusText);
    const name = (answer.headers.get("Content-Disposition").match(/filename="(.+)"/) || [])[1];
    const file = URL.createObjectURL(await answer.blob());
    h("a", { href: file, download: name || "specification.html" }).click();
    setTimeout(() => URL.revokeObjectURL(file), 60000);
    word.textContent = "Export";
  } catch (error) {
    word.textContent = "Not exported";
    button.title = `Not exported: ${error.message}`;
    setTimeout(() => { word.textContent = "Export"; button.title = usual; }, 8000);
  }
  button.disabled = false;
}

const exportButton = document.getElementById("export-button");
if (exportButton) exportButton.addEventListener("click", () => exportWhole(exportButton));
const printLink = document.getElementById("print-link");
if (printLink) ["click", "auxclick", "contextmenu"].forEach((e) => printLink.addEventListener(e, () => printAddress(printLink)));
window.addEventListener("beforeprint", () => document.documentElement.setAttribute("data-theme", "light"));
window.addEventListener("afterprint", () => window.theme.set(window.theme.choice()));
