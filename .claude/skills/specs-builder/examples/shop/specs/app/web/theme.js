// The appearance -- as the system prefers, light or dark -- as this person chose it in the bar, kept in this
// browser. Loaded first in the head, without defer, so that a dark reader never sees a light flash; the bar's
// switch, drawn by menu.js, calls theme.set(). It marks a page opened in a preview, ?peek=1, here too, so that
// its bar is never drawn; and a page opened on its sheet, ?print=1, which has no bar either and is always light.
(function () {
  "use strict";
  var KEY = "specs-builder.theme";
  var system = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  var sheet = /(?:^|[?&])print=1(?:&|$)/.test(location.search.slice(1));
  function choice() {
    try { return localStorage.getItem(KEY) || "system"; } catch (e) { return "system"; }
  }
  function apply() {
    var want = choice();
    var theme = sheet ? "light" : want === "system" ? (system && system.matches ? "dark" : "light") : want;
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.setAttribute("data-theme-wanted", want);
    document.dispatchEvent(new CustomEvent("specs-builder:theme", { detail: { theme: theme, choice: want } }));
  }
  window.theme = {
    choice: choice,
    set: function (want) {
      try { if (want === "system") { localStorage.removeItem(KEY); } else { localStorage.setItem(KEY, want); } }
      catch (e) { /* no storage: the choice lasts for this page */ }
      apply();
    }
  };
  apply();
  if (/(?:^|[?&])peek=1(?:&|$)/.test(location.search.slice(1))) { document.documentElement.classList.add("peeked"); }
  if (sheet) { document.documentElement.classList.add("peeked", "sheet"); }
  if (system && system.addEventListener) {
    system.addEventListener("change", function () { if (choice() === "system") { apply(); } });
  }
}());
