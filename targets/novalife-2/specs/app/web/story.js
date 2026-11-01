// A flow as a user story, at the head of its page: "As the visitor, I want to buy a product, so that ..." -- its
// user, its name and the goals it serves; a job with no user, "Started by the timer: the nightly run, so that ..." --
// and the table of what it carries: every requirement its steps and what goes wrong name, with its priority, how
// well it is backed, and its criteria. What a team plans from. The story is told by finish.story, which the export
// and `spec.py story` tell too; this draws /api/story/<id>. Loaded before engine.js; it draws with engine.js's h(),
// chip(), get() and nodeHref().
"use strict";

async function flowStory(n) {
  const s = await get(`story/${encodeURIComponent(n.id)}`).catch(() => null);
  if (!s) return [];
  const out = [h("h2", {}, "Story"), h("p", { class: "story" }, s.story)];
  if (s.untold.length) out.push(h("p", { class: "meta" }, `Not told whole: ${s.untold.join("; ")}.`));
  if (!s.requirements.length) return out;
  const n_ = s.requirements.length;
  out.push(h("h2", {}, "What it carries"),
    h("p", { class: "lead" }, `${n_} requirement${n_ === 1 ? "" : "s"} named in its steps, ` +
      `${s.must === n_ ? (n_ === 1 ? "a must" : "all must") : `${s.must} must`}, ` +
      `with ${s.criteria} criteri${s.criteria === 1 ? "on" : "a"} to pass.`),
    h("div", { class: "table-frame" }, h("table", { class: "story-table" },
      h("thead", {}, h("tr", {}, h("th", {}, "Requirement"), h("th", {}, "Priority"), h("th", {}, "Backed"), h("th", {}, "Accepted when"))),
      h("tbody", {}, s.requirements.map((r) => h("tr", {},
        h("td", { class: "story-req" }, chip(r.id), " ", h("a", { href: nodeHref(r.id) }, r.name)),
        h("td", {}, r.priority ? h("span", { class: `badge ${r.priority}` }, r.priority) : ""),
        h("td", { class: "story-backed" }, r.backed || "—"),
        h("td", {}, h("ul", { class: "story-criteria" }, r.criteria.map((c) => h("li", {}, chip(c.id), " ", c.says))))))))));
  return out;
}
