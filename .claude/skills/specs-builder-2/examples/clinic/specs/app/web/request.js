// Asking for a change from a page. The application reads: a change is made in Claude Code, which goes through all that stands on
// what moves, the screens too. A request waits in inbox.md, beside the data and never in it, with the name asked once and kept in
// this browser. Loaded before engine.js; it draws with engine.js's h().
"use strict";

const REQUEST_WHO = "specs-builder-2.who";

function requestChange(id, name) {
  const remembered = (() => { try { return localStorage.getItem(REQUEST_WHO) || ""; } catch { return ""; } })();
  const says = h("textarea", { rows: 5, placeholder: "What should change, and why?", "aria-label": "What should change, and why" });
  const who = h("input", { type: "text", placeholder: "Your name", "aria-label": "Your name", value: remembered });
  const status = h("p", { class: "status", role: "status", "aria-live": "polite" });
  const sendButton = h("button", { type: "button", class: "button primary", onclick: () => send() }, "Send");
  const close = () => dialog.close();
  const body = h("div", { class: "request-body" }, says, who, status,
    h("div", { class: "actions-row" }, sendButton, h("button", { type: "button", class: "button", onclick: close }, "Cancel")));
  const dialog = h("dialog", { class: "request", "aria-label": `Request a change to ${id}` },
    h("h2", {}, "Request a change"),
    h("p", { class: "meta" }, `${id}${name ? ` ${name}` : ""}. It waits under What is open until Claude Code takes it up.`), body);

  async function send() {
    const asked = says.value.trim(), by = who.value.trim();
    status.className = "status bad";
    if (!asked) { status.textContent = "Say what should change."; says.focus(); return; }
    if (!by) { status.textContent = "Say who is asking."; who.focus(); return; }
    status.className = "status";
    status.textContent = "Sending...";
    sendButton.disabled = true;
    try {
      const r = await fetch("/api/inbox", { method: "POST", headers: { "Content-Type": "application/json" },
                                            body: JSON.stringify({ says: asked, about: [id], by }) });
      const said = await r.json();
      if (!r.ok) throw new Error(said.error || r.statusText);
      try { localStorage.setItem(REQUEST_WHO, by); } catch { /* asked again next time */ }
      body.replaceChildren(h("p", {}, `Sent. Request #${said.no} waits under What is open.`),
        h("div", { class: "actions-row" }, h("button", { type: "button", class: "button primary", onclick: close }, "Close")));
    } catch (error) {
      status.className = "status bad";
      status.textContent = `Not sent: ${error.message}`;
      sendButton.disabled = false;
    }
  }

  dialog.addEventListener("close", () => dialog.remove());
  document.body.append(dialog);
  dialog.showModal();
  says.focus();
}
