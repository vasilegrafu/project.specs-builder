// Drives a real Chrome with real input over the Chrome DevTools Protocol. Node 22 or later, and Chrome: nothing to install.
//
//   import { start, walk } from "./drive.mjs";
//   const page = await start({ headless: true });
//   await page.open("http://127.0.0.1:8080/");
//   const t = walk(page);
//   await t.step("a click opens the menu", async () => { await page.click(".menu"); return page.run(`!!document.querySelector(".open")`); });
//   await t.finish();                                      // prints the result, stops Chrome, exits 1 on any problem
//
// Input goes through the browser as a person's does, so hit testing, hover, focus and click counts are real: a click lands on what
// is at that point at that moment, not on the element a script named. That is what a page's own el.click() cannot find out.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const KEYS = { Enter: 13, Escape: 27, Tab: 9, Backspace: 8, Delete: 46, " ": 32, Home: 36, End: 35, PageUp: 33, PageDown: 34, ArrowLeft: 37, ArrowUp: 38, ArrowRight: 39, ArrowDown: 40 };

export function findChrome() {
  const local = process.env.LOCALAPPDATA ? join(process.env.LOCALAPPDATA, "Google/Chrome/Application/chrome.exe") : "";
  const known = {
    win32: ["C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe", local],
    darwin: ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
    linux: ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser"],
  }[process.platform] || [];
  const found = [process.env.CHROME, ...known].find((p) => p && existsSync(p));
  if (!found) throw new Error("no Chrome found: set CHROME to its path");
  return found;
}

const freePort = () => new Promise((resolve, reject) => {
  const probe = createServer();
  probe.on("error", reject);
  probe.listen(0, "127.0.0.1", () => { const { port } = probe.address(); probe.close(() => resolve(port)); });
});

// Chrome in a profile of its own, so that it touches nothing of the user's, and goes when `stop` is called.
export async function start({ headless = true, width = 1440, height = 900, touch = false, mobile = false } = {}) {
  const port = await freePort();
  const profile = mkdtempSync(join(tmpdir(), "real-input-"));
  const chrome = spawn(findChrome(), [...(headless ? ["--headless=new"] : []), `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", `--window-size=${width + 60},${height + 120}`,
    // a window behind others is throttled otherwise: timers slow to a second and frames stop, and a real test fails for no reason
    "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding", "--disable-background-timer-throttling", "about:blank"], { stdio: "ignore" });
  let target;
  for (let i = 0; i < 80 && !target; i++) {
    try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === "page"); } catch { /* not up yet */ }
    if (!target) await wait(150);
  }
  if (!target) { chrome.kill(); throw new Error("Chrome did not start"); }
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => { ws.onopen = r; });
  let id = 0;
  const pending = new Map();
  const loaded = [];
  const errors = [];
  ws.onmessage = (message) => {
    const d = JSON.parse(message.data);
    if (d.id && pending.has(d.id)) { const { resolve, reject } = pending.get(d.id); pending.delete(d.id); if (d.error) reject(new Error(`${d.error.message}`)); else resolve(d.result); }
    if (d.method === "Page.loadEventFired") loaded.splice(0).forEach((r) => r());
    if (d.method === "Runtime.exceptionThrown") errors.push((d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text).split("\n").slice(0, 2).join(" "));
    if (d.method === "Log.entryAdded" && d.params.entry.level === "error") errors.push(`${d.params.entry.text} ${d.params.entry.url || ""}`.trim());
  };
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const n = ++id;
    pending.set(n, { resolve, reject });
    ws.send(JSON.stringify({ id: n, method, params }));
  });
  for (const domain of ["Page", "Runtime", "Log"]) await send(`${domain}.enable`);
  await send("Page.bringToFront");
  await send("Emulation.setFocusEmulationEnabled", { enabled: true });
  await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
  if (touch) await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });

  let mx = 0, my = 0;
  const page = {
    errors, send, wait,

    // about:blank first: a change of hash alone would not load the page again
    async open(url, settle = 800) {
      await send("Page.navigate", { url: "about:blank" });
      const done = new Promise((r) => loaded.push(r));
      await send("Page.navigate", { url });
      await Promise.race([done, wait(15000)]);
      await wait(settle);
    },

    async run(expression) {
      const r = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description?.split("\n")[0] || r.exceptionDetails.text);
      return r.result.value;
    },

    // Wait for a condition instead of a guess of how long something takes
    async until(expression, ms = 5000) {
      const end = Date.now() + ms;
      while (Date.now() < end) { if (await page.run(`!!(${expression})`)) return true; await wait(30); }
      return false;
    },

    // Where a thing is now, once it has stopped moving: a picture still settling, or one a click just redrew, moves what was found a
    // moment ago. `text` narrows it to the first that holds those words; only what can be seen in the window is found.
    async find(selector, { text = "", ms = 3000 } = {}) {
      const where = `(() => { const el = [...document.querySelectorAll(${JSON.stringify(selector)})].find((e) => { const b = e.getBoundingClientRect();
        return b.width > 1 && b.height > 1 && b.bottom > 0 && b.right > 0 && b.top < innerHeight && b.left < innerWidth && e.textContent.includes(${JSON.stringify(text)}); });
        if (!el) return null; const b = el.getBoundingClientRect();
        const moving = document.getAnimations().some((a) => a.playState === "running" && a.effect.getTiming().iterations !== Infinity && a.effect.target && (a.effect.target === el || a.effect.target.contains(el)));
        return { x: Math.round(b.left + b.width / 2), y: Math.round(b.top + b.height / 2), w: Math.round(b.width), h: Math.round(b.height), moving }; })()`;
      const end = Date.now() + ms;
      let last = null, still = 0;
      while (Date.now() < end) {
        const now = await page.run(where);
        // the same four times over 150 ms, and no animation running on it: a busy browser stalls a move, and a stall is not stillness
        still = now && last && !now.moving && now.x === last.x && now.y === last.y ? still + 1 : 0;
        if (still >= 3) return now;
        last = now;
        await wait(50);
      }
      if (!last) throw new Error(`nothing to see at ${selector}${text ? ` holding "${text}"` : ""}`);
      return last;
    },

    at: async (target) => (typeof target === "string" ? page.find(target) : target),

    async hover(target) {
      const { x, y } = await page.at(target);
      for (let i = 1; i <= 6; i++) { await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: mx + (x - mx) * i / 6, y: my + (y - my) * i / 6 }); await wait(10); }
      mx = x; my = y;
      return { x, y };
    },

    async press({ x, y }, count = 1, button = "left") {
      await send("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button, buttons: button === "right" ? 2 : 1, clickCount: count });
      await send("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button, clickCount: count });
    },

    async click(target) { await page.press(await page.hover(target)); },
    async rightClick(target) { await page.press(await page.hover(target), 1, "right"); },

    // Two presses at the same point, as a person's: if the first redraws, the second lands on whatever is there by then
    async dblclick(target, gap = 90) {
      const at = await page.hover(target);
      await page.press(at, 1);
      await wait(gap);
      await page.press(at, 2);
    },

    async drag(target, dx, dy) {
      const { x, y } = await page.hover(target);
      await send("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", buttons: 1, clickCount: 1 });
      for (let i = 1; i <= 10; i++) { await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: x + dx * i / 10, y: y + dy * i / 10, button: "left", buttons: 1 }); await wait(12); }
      await send("Input.dispatchMouseEvent", { type: "mouseReleased", x: x + dx, y: y + dy, button: "left", clickCount: 1 });
      mx = x + dx; my = y + dy;
    },

    async wheel(target, deltaY) {
      const { x, y } = await page.hover(target);
      await send("Input.dispatchMouseEvent", { type: "mouseWheel", x, y, deltaX: 0, deltaY });
    },

    async key(name) {
      const code = KEYS[name] || name.toUpperCase().charCodeAt(0);
      const label = name.length === 1 ? (name === " " ? "Space" : `Key${name.toUpperCase()}`) : name;
      await send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: name, code: label, windowsVirtualKeyCode: code });
      if (name === "Enter") await send("Input.dispatchKeyEvent", { type: "char", text: "\r" });
      await send("Input.dispatchKeyEvent", { type: "keyUp", key: name, code: label, windowsVirtualKeyCode: code });
    },

    type: (text) => send("Input.insertText", { text }),

    // Needs start({ touch: true })
    async hold(target, ms = 800) {
      const { x, y } = await page.at(target);
      await send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y }] });
      await wait(ms);
      await send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    },
    tap: (target) => page.hold(target, 40),
    async swipe(target, dx, dy) {
      const { x, y } = await page.at(target);
      await send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y }] });
      for (let i = 1; i <= 12; i++) { await send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: x + dx * i / 12, y: y + dy * i / 12 }] }); await wait(16); }
      await send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    },

    // A line along the bottom of the page, for whoever is watching a visible run
    caption: (text) => page.run(`(() => { let c = document.getElementById("real-input-caption"); if (!c) { c = document.createElement("div"); c.id = "real-input-caption"; c.style.cssText = "position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:2147483647;max-width:90vw;padding:8px 16px;border-radius:8px;background:#ffd24a;color:#111;font:600 16px system-ui;box-shadow:0 2px 10px #0008;pointer-events:none"; document.body.append(c); } c.textContent = ${JSON.stringify(text)}; })()`),

    async shot(path) {
      mkdirSync(dirname(path), { recursive: true });
      const webp = path.toLowerCase().endsWith(".webp");       // a picture to keep is lighter so; PNG otherwise, for reading
      const wanted = webp ? { format: "webp", quality: 86 } : { format: "png" };
      writeFileSync(path, Buffer.from((await send("Page.captureScreenshot", wanted)).data, "base64"));
      return path;
    },

    async stop() {
      try { ws.close(); } catch { /* it has gone */ }
      chrome.kill();
      await wait(400);
      try { rmSync(profile, { recursive: true, force: true }); } catch { /* Chrome may hold it a moment: the system's temp folder clears it */ }
    },
  };
  return page;
}

// Steps, each told as it ends. A step fails on false, on a string, which is the reason, or on anything it throws; with `shots`, a
// failed step leaves a picture. `pace` slows a visible run so that it can be followed, and shows each step in a caption.
export function walk(page, { pace = 0, shots = "" } = {}) {
  const done = [];
  return {
    async step(name, run) {
      let said;
      if (pace) { await page.caption(`${done.length + 1}. ${name}`).catch(() => {}); await wait(pace); }
      try { said = await run(); } catch (error) { said = String(error.message || error).slice(0, 160); }
      const ok = said === true || said === undefined;
      done.push({ name, ok });
      console.log(`${ok ? "OK     " : "PROBLEM"} ${name}${ok || said === false ? "" : `: ${said}`}`);
      if (!ok && shots) await page.shot(join(shots, `step-${done.length}.png`)).catch(() => {});
      if (pace) { await page.caption(`${done.length}. ${name}: ${ok ? "OK" : "PROBLEM"}`).catch(() => {}); await wait(pace / 2); }
      return ok;
    },
    // With `more`, the run goes on with another page: it says whether all was well here, for the last finish to take in
    async finish({ more = false, before = true } = {}) {
      const passed = done.filter((d) => d.ok).length;
      const errors = [...new Set(page.errors)];
      console.log(`${passed} of ${done.length} OK`);
      if (errors.length) console.log(`page errors:\n  ${errors.join("\n  ")}`);
      if (pace) { await page.caption(`Finished: ${passed} of ${done.length} OK`).catch(() => {}); await wait(2500); }
      await page.stop();
      const well = before && passed === done.length && !errors.length;
      if (more) return well;
      process.exit(well ? 0 : 1);
    },
  };
}
