// The Graph walked with a real mouse in a real Chrome: each picture's clicks, double clicks and drags, on a specification of its own
// server. It finds what reading the code cannot: a click that redraws moves a node from under the pointer, and the second click of
// a double one then lands on what was behind it.
//
//   node tests/graph_walk.mjs [a specification's folder]     the shop example, if none is named
//
// It needs Node 22 or later, Chrome, and the real-input-tester skill beside this one. tests/selftest.py runs it where it can.
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { createServer } from "node:net";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const DRIVE = join(HERE, "..", "..", "real-input-tester", "scripts", "drive.mjs");
if (!existsSync(DRIVE)) {
  console.log("left out: this needs the real-input-tester skill beside this one");
  process.exit(0);
}
const { start, walk } = await import(pathToFileURL(DRIVE).href);

const spec = resolve(process.argv[2] || join(HERE, "..", "examples", "shop", "specs"));
const python = process.env.PYTHON || (process.platform === "win32" ? "python" : "python3");
const port = await new Promise((done) => { const probe = createServer(); probe.listen(0, "127.0.0.1", () => { const free = probe.address().port; probe.close(() => done(free)); }); });
const server = spawn(python, ["-B", "app/serve.py", "--port", String(port)], { cwd: spec, stdio: "ignore", env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" } });
process.on("exit", () => server.kill());
const base = `http://127.0.0.1:${port}`;
for (let i = 0; i < 150; i++) {
  try { await fetch(`${base}/api/summary`); break; } catch { await new Promise((r) => setTimeout(r, 200)); }
}

const page = await start({ headless: process.env.WALK_VISIBLE !== "1" });
const t = walk(page, { pace: process.env.WALK_VISIBLE === "1" ? 500 : 0 });
const OTHER = ".map-tag:not(.centre):not(.looped)";
const tag = (id) => `.map-tag[data-id="${id}"]`;
const open = (hash) => page.open(`${base}/${hash}`, 500);
const hash = () => page.run("decodeURIComponent(location.hash)");
const count = (selector) => page.run(`document.querySelectorAll(${JSON.stringify(selector)}).length`);
const goes = (to) => page.until(`decodeURIComponent(location.hash) === ${JSON.stringify(to)}`, 2500);
const selected = (id) => page.until(`mapState.last === ${JSON.stringify(id)}`, 2500);
const middle = (id) => page.until(`document.querySelector(".map-tag.centre")?.dataset.id === ${JSON.stringify(id)}`, 2500);
const spread = (n) => page.until(`document.querySelectorAll(".map-tag.spread").length === ${n}`, 2500);
const first = async (selector) => { await page.find(selector); return page.run(`document.querySelector(${JSON.stringify(selector)}).dataset.id`); };
const stays = async (what) => { await page.wait(750); return (await hash()) === what; };   // longer than a click waits for a second one

await open("#/graph/R4");
const around = await first(OTHER);
await t.step("Around: a click spreads a node's links", async () => { const was = await count(".map-tag"); await page.click(tag(around)); return (await spread(1)) && (await count(".map-tag")) > was; });
await t.step("Around: a second click takes them back", async () => { await page.click(tag(around)); return spread(0); });
await open("#/graph/R4");
await t.step("Around: a double click puts a node in the middle", async () => { const id = await first(OTHER); await page.dblclick(tag(id)); return (await goes(`#/graph/${id}`)) && (await middle(id)) && selected(id); });
await open("#/graph/R4");
await t.step("Around: so does a slow one", async () => { const id = await first(OTHER); await page.dblclick(tag(id), 230); return (await goes(`#/graph/${id}`)) && middle(id); });
await open("#/graph/R4");
await t.step("Around: a double click on the middle changes nothing", async () => { await page.dblclick(".map-tag.centre"); return (await stays("#/graph/R4")) && (await count(".map-tag.spread")) === 0; });
await open("#/graph/R4");
await t.step("Around: a node dragged stays, and nothing spreads", async () => {
  const id = await first(OTHER);
  const was = await page.find(tag(id));
  await page.drag(tag(id), 60, 40);
  const now = await page.find(tag(id));
  return (await stays("#/graph/R4")) && (await count(".map-tag.spread")) === 0 && now.x !== was.x;
});
await open("#/graph/R4");
await t.step("Around: Back returns from a double click", async () => { const id = await first(OTHER); await page.dblclick(tag(id)); await goes(`#/graph/${id}`); await page.run("history.back()"); return (await goes("#/graph/R4")) && middle("R4"); });

await open("#/graph/impact:R4");
const impact = await first(OTHER);
await t.step("Impact: a click goes a step further", async () => { const was = await count(".map-tag"); await page.click(tag(impact)); return (await spread(1)) && (await count(".map-tag")) > was; });
await t.step("Impact: a second click folds it back", async () => { await page.click(tag(impact)); return spread(0); });
await open("#/graph/impact:R4");
await t.step("Impact: a double click makes a node the root", async () => { const id = await first(OTHER); await page.dblclick(tag(id)); return (await goes(`#/graph/impact:${id}`)) && (await middle(id)) && selected(id); });

await open("#/graph/layers:R4");
await t.step("Layers: a click selects a node", async () => { const id = await first(OTHER); await page.click(tag(id)); return (await goes(`#/graph/layers:${id}`)) && (await middle(id)) && selected(id); });
await open("#/graph/layers:R4");
await t.step("Layers: a double click opens Around", async () => { const id = await first(OTHER); await page.dblclick(tag(id)); return (await goes(`#/graph/${id}`)) && middle(id); });
await open("#/graph/layers:R4");
await t.step("Layers: a click on the selected node leaves it", async () => { await page.click(".map-tag.centre"); return (await stays("#/graph/layers:R4")) && middle("R4"); });
await open("#/graph/layers:R4");
await t.step("Layers: a double click on the selected node opens Around", async () => { await page.dblclick(".map-tag.centre"); return goes("#/graph/R4"); });
await open("#/graph/layers:R4");
await t.step("Layers: two steps show more", async () => { await page.find(".map-tag.centre"); const was = await count(".map-tag"); await page.click('[data-steps="2"]'); await page.until(`document.querySelectorAll(".map-tag").length > ${was}`, 2500); return (await count(".map-tag")) > was; });

await open("#/graph/layers");
await t.step("All Layers: a click selects a node", async () => { const id = await first(".map-tag"); await page.click(tag(id)); return (await goes(`#/graph/layers:${id}`)) && selected(id); });
await open("#/graph/layers");
await t.step("All Layers: a double click opens Around", async () => { const id = await first(".map-tag"); await page.dblclick(tag(id)); return goes(`#/graph/${id}`); });
await open("#/graph/layers");
await page.click('[aria-label="Fold every kind to bands"]');
await page.until(`document.querySelectorAll(".map-tag").length === 0`, 2500);
await t.step("All Layers: a click opens a kind", async () => { await page.click(".map-block"); return page.until(`document.querySelectorAll(".map-tag").length > 0`, 2500); });
await t.step("All Layers: a second click folds it", async () => { await page.click(".map-block.open"); return page.until(`document.querySelectorAll(".map-tag").length === 0`, 2500); });
await t.step("All Layers: a double click on a band breaks nothing", async () => { await page.dblclick(".map-band"); return stays("#/graph/layers"); });

await open("#/graph");
await t.step("Map: a click opens a kind", async () => { const was = await count(".map-bubble"); await page.click(".map-bubble"); return page.until(`document.querySelectorAll(".map-bubble").length < ${was}`, 2500); });
await open("#/graph");
await t.step("Map: a double click on a kind breaks nothing", async () => { await page.dblclick(".map-bubble"); return stays("#/graph"); });
await open("#/graph");
await t.step("Map: a burst of fast clicks on a kind leaves it whole", async () => {
  const place = await page.hover(await page.find(".map-bubble", { text: "Requirements" }));   // the map moves under the pointer: the clicks stay where they began
  for (let i = 0; i < 8; i++) await page.press(place);
  await page.wait(1200);
  return page.run(`[...document.querySelectorAll(".graph-map line")].every((l) => !Number.isNaN(l.x1.baseVal.value))`);
});
await open("#/graph");
if (!(await count(".map-node"))) await page.click(".map-bubble");
await t.step("Map: a click selects a node", async () => { const id = await first(".map-node"); await page.click(`.map-node[data-id="${id}"]`); return selected(id); });
await open("#/graph");
if (!(await count(".map-node"))) await page.click(".map-bubble");
await t.step("Map: a double click opens it", async () => { const id = await first(".map-node"); await page.dblclick(`.map-node[data-id="${id}"]`); return goes(`#/graph/${id}`); });
await t.finish();
