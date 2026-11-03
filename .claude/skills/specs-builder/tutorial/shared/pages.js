document.documentElement.classList.add("js");
function chapters() {
  var list = window.CHAPTERS, nav = document.querySelector("nav.toc");
  if (!list || !nav) return;
  var here = (location.pathname.split("/").pop() || "index.html").replace(/\.html$/, "");
  var heads = [].slice.call(document.querySelectorAll("main h2[id]"));
  var sections = heads.map(function (h) { return '<li><a href="#' + h.id + '">' + h.textContent + "</a></li>"; }).join("");
  function item(page, tag) {
    var on = page[0] === here;
    return "<" + tag + (on ? ' class="current"' : "") + '><a href="' + page[0] + '.html"' + (on ? ' aria-current="page"' : "") + ">" + page[1] + "</a>"
      + (on && sections ? '<ol class="sections">' + sections + "</ol>" : "") + "</" + tag + ">";
  }
  var flat = [], n = 0, html = "";
  list.forEach(function (part, k) {
    flat = flat.concat(part.pages);
    if (k === 0) { html += '<div class="home-link">' + item(part.pages[0], "div") + "</div>"; return; }
    var open = part.pages.some(function (page) { return page[0] === here; });
    html += '<details class="part"' + (open ? " open" : "") + "><summary>" + part.name + '</summary><ol class="chapters" start="' + (n + 1) + '">'
      + part.pages.map(function (page) { return item(page, "li"); }).join("") + "</ol></details>";
    n += part.pages.length;
  });
  nav.innerHTML = '<div class="card"><details open><summary>Steps</summary>' + html + "</details></div>";
  if (window.innerWidth < 1220) nav.querySelector("details").open = false;
  var at = flat.findIndex(function (page) { return page[0] === here; }), pager = document.querySelector("nav.pager");
  if (pager && at >= 0) {
    var prev = flat[at - 1], next = flat[at + 1];
    pager.innerHTML = (prev ? '<a class="prev" href="' + prev[0] + '.html">\u2190 Previous<strong>' + prev[1] + "</strong></a>" : "")
      + (next ? '<a class="next" href="' + next[0] + '.html">Next \u2192<strong>' + next[1] + "</strong></a>" : "");
  }
}
function explain() {
  var words = window.WORDS, seen = {};
  if (!words) return;
  var names = Object.keys(words).sort(function (a, b) { return b.length - a.length; });
  var find = new RegExp("\\b(" + names.join("|") + ")\\b", "i");
  var key = {};
  names.forEach(function (n) { key[n.toLowerCase()] = n; });
  [].forEach.call(document.querySelectorAll("main p, main li"), function (box) {
    if (box.closest("nav, pre, figcaption, .pins, .strip, .chat, .asks, .say")) return;
    [].slice.call(box.childNodes).forEach(function walk(node) {
      if (node.nodeType === 1 && !/^(a|code|pre|svg|span)$/i.test(node.tagName)) { [].slice.call(node.childNodes).forEach(walk); return; }
      if (node.nodeType !== 3) return;
      var hit = find.exec(node.nodeValue);
      while (hit && seen[key[hit[1].toLowerCase()]]) {
        var rest = node.nodeValue.slice(hit.index + hit[0].length), next = find.exec(rest);
        if (!next) return;
        next.index += hit.index + hit[0].length; hit = next;
      }
      if (!hit) return;
      var name = key[hit[1].toLowerCase()], term = document.createElement("span");
      seen[name] = true;
      term.className = "term"; term.tabIndex = 0; term.dataset.say = words[name]; term.textContent = hit[1];
      var after = node.splitText(hit.index);
      after.nodeValue = after.nodeValue.slice(hit[1].length);
      node.parentNode.insertBefore(term, after);
      walk(after);
    });
  });
}
function copies() {
  [].forEach.call(document.querySelectorAll("button.copy"), function (button) {
    button.addEventListener("click", function () {
      var text = button.parentNode.querySelector("p").textContent;
      function said() { button.textContent = "Copied"; setTimeout(function () { button.textContent = "Copy"; }, 1500); }
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(said, function () {});
    });
  });
}
function ticks() {
  var KEY = "specs-builder.tutorial.done", done = {};
  try { done = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { done = {}; }
  var here = (location.pathname.split("/").pop() || "").replace(/\.html$/, ""), button = document.querySelector("button.done");
  function show() {
    [].forEach.call(document.querySelectorAll("nav.toc a[href$='.html']"), function (a) { a.classList.toggle("ticked", !!done[a.getAttribute("href").replace(/\.html$/, "")]); });
    if (button) { button.setAttribute("aria-pressed", done[here] ? "true" : "false"); button.textContent = done[here] ? "Done" : "Mark this step as done"; }
  }
  if (button) button.addEventListener("click", function () {
    if (done[here]) delete done[here]; else done[here] = true;
    try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) { /* kept for this page alone */ }
    show();
  });
  show();
}
function zoom() {
  var box = document.createElement("dialog"), big = document.createElement("img");
  box.className = "zoom"; box.appendChild(big); document.body.appendChild(box);
  box.addEventListener("click", function () { box.close(); });
  document.querySelectorAll("main img").forEach(function (img) {
    img.addEventListener("click", function (e) { e.preventDefault(); big.src = img.src; big.alt = img.alt; box.showModal(); });
  });
}
document.addEventListener("DOMContentLoaded", function () {
chapters();
ticks();
explain();
copies();
zoom();
(function(){
document.querySelectorAll(".steps").forEach(function(box){
  var steps=box.querySelectorAll(".step"),dots=box.querySelectorAll(".steps-dots button"),
      prev=box.querySelector("[data-step=prev]"),next=box.querySelector("[data-step=next]"),i=0;
  function show(n){
    i=Math.max(0,Math.min(steps.length-1,n));
    steps.forEach(function(s,k){s.classList.toggle("on",k===i);});
    dots.forEach(function(d,k){if(k===i){d.setAttribute("aria-current","step");}else{d.removeAttribute("aria-current");}});
    prev.disabled=i===0;next.disabled=i===steps.length-1;
  }
  prev.addEventListener("click",function(){show(i-1);});
  next.addEventListener("click",function(){show(i+1);});
  dots.forEach(function(d,k){d.addEventListener("click",function(){show(k);});});
  box.addEventListener("keydown",function(e){
    if(e.key==="ArrowRight"){show(i+1);e.preventDefault();}
    if(e.key==="ArrowLeft"){show(i-1);e.preventDefault();}
  });
  show(0);
});
var links=document.querySelectorAll('nav.toc a[href^="#"]');
document.querySelectorAll("nav.toc .card>details").forEach(function(d){if(window.innerWidth>=1220){d.open=true;}});
if(links.length&&"IntersectionObserver" in window){
  var heads=Array.prototype.map.call(links,function(a){return document.getElementById(a.hash.slice(1));});
  function mark(){
    var at=0;
    heads.forEach(function(h,k){if(h&&h.getBoundingClientRect().top<window.innerHeight*0.35){at=k;}});
    links.forEach(function(a,k){a.classList.toggle("here",k===at);});
  }
  var watch=new IntersectionObserver(mark,{rootMargin:"0px 0px -60% 0px"});
  heads.forEach(function(h){if(h){watch.observe(h);}});
  window.addEventListener("scroll",mark,{passive:true});
  mark();
}
})();
});
