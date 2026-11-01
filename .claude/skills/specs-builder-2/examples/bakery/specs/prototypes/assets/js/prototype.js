// What Mill Lane Bakery's prototype does beyond what the runtime gives every prototype (states, variants, the wireframe
// view): an order goes from the form to Order placed and to Orders, and the staff mark it ready. It keeps what it changes in
// the browser; ?reset=1 starts again. A reference of what each screen does, never the product's code. Each piece names the
// requirement it shows.
(function () {
  "use strict";
  var main = document.querySelector("[data-prototype]");
  var screen = main ? main.getAttribute("data-prototype") : "";
  var live = window.live;
  var sample = window.SAMPLE;
  var params = new URLSearchParams(location.search);
  var DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December"];

  // a state only this script reaches, shown as the runtime shows one asked for by the Prototype page
  function show(state) {
    live.state = state;
    function list(words) { return (words || "").split(/[\s,]+/).filter(function (w) { return w; }); }
    Array.prototype.forEach.call(document.querySelectorAll("[data-when], [data-unless]"), function (el) {
      var when = list(el.getAttribute("data-when")), unless = list(el.getAttribute("data-unless"));
      el.hidden = !((!when.length || when.indexOf(state) >= 0) && unless.indexOf(state) < 0);
    });
    document.dispatchEvent(new CustomEvent("live:change", { detail: { state: state, as: live.as } }));
  }

  function byId(id) { return document.getElementById(id); }
  function all(selector, root) { return Array.prototype.slice.call((root || document).querySelectorAll(selector)); }
  function today() { var d = new Date(); d.setHours(0, 0, 0, 0); return d; }
  function iso(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
  function inDays(n) { var d = today(); d.setDate(d.getDate() + n); return iso(d); }
  function dateOf(text) { var p = text.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function words(text) { var d = dateOf(text); return DAYS[d.getDay()] + " " + d.getDate() + " " + MONTHS[d.getMonth()]; }

  // the nth day from today the bakery is open: sample orders never fall on a Monday
  function openDay(n) {
    var offset = 0, seen = -1;
    while (true) {
      if (sample.closedDays.indexOf(dateOf(inDays(offset)).getDay()) < 0) { seen += 1; if (seen === n) { return inDays(offset); } }
      offset += 1;
    }
  }
  function seeded(o) {
    return { number: o.number, cake: o.cake, size: o.size, day: openDay(o.openDay), name: o.name, phone: o.phone, words: o.words, allergies: o.allergies, status: o.status };
  }
  function priceOf(cakeName, size) {
    var cake = sample.cakes.filter(function (c) { return c.name === cakeName; })[0];
    return cake ? cake.price + (size === "large" ? sample.largeExtra : 0) : 0;
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest ? event.target.closest("a") : null;
    if (link && link.getAttribute("href") === "#content") {    // the page's <base> would send it away
      event.preventDefault();
      byId("content").focus();
    }
  });

  if (screen === "SC3") {
    var form = byId("order"), details = byId("details"), place = byId("place"), cake = byId("cake"), day = byId("day");
    var FIELDS = ["cake", "day", "size", "words", "name", "phone"];

    // B3: only a cake can be ordered
    sample.cakes.forEach(function (c) {
      var option = document.createElement("option");
      option.value = c.id; option.textContent = c.name;
      cake.appendChild(option);
    });
    day.min = inDays(sample.notice);                           // R5
    byId("day-field").querySelector(".ml-hint").id = "day-hint";

    // R3.6: Order this cake brings the cake with it; a cake no longer on the list brings nothing
    if (params.get("cake")) { cake.value = params.get("cake"); if (!cake.value) { cake.value = ""; } }

    function size() { var r = form.querySelector('input[name="size"]:checked'); return r ? r.value : ""; }

    function chosen() {
      var c = sample.cakes.filter(function (x) { return x.id === cake.value; })[0];
      var s = size();
      all("[data-cake]").forEach(function (pic) { pic.hidden = !c || pic.getAttribute("data-cake") !== c.id; });
      byId("chosen-empty").hidden = !!c;
      byId("chosen-none").hidden = !!c;
      byId("chosen-name").hidden = !c;
      byId("chosen-name").textContent = c ? c.name : "";
      byId("chosen-size").hidden = !c || !s;
      byId("chosen-size").textContent = s === "large" ? "Large, serves 14" : "Small, serves 8";
      byId("chosen-price").hidden = !c || !s;
      byId("chosen-price").textContent = c && s ? "€" + priceOf(c.name, s) + " to pay at pick-up" : "";
    }
    form.addEventListener("change", chosen);
    chosen();

    // R4 and R5: what each detail needs
    function faults() {
      var bad = {};
      if (!cake.value) { bad.cake = "Please choose a cake."; }
      if (!size()) { bad.size = "Please choose a size."; }
      if (!day.value) {
        bad.day = "Please choose a pick-up day.";
      } else {
        var gap = Math.round((dateOf(day.value) - today()) / 86400000);
        if (gap < sample.notice) { bad.day = "We need two days’ notice. Please choose a later day."; }
        else if (sample.closedDays.indexOf(dateOf(day.value).getDay()) >= 0) { bad.day = "We are closed on Mondays. Please choose another day."; }
      }
      if (byId("words").value.length > 30) { bad.words = "Please keep the words to 30 characters."; }
      if (!byId("name").value.trim()) { bad.name = "Please tell us your name."; }
      if (!/^[+\d][\d\s()-]*$/.test(byId("phone").value.trim())) { bad.phone = "Please enter a phone number we can ring."; }
      return bad;
    }

    function paint(bad) {
      FIELDS.forEach(function (name) {
        var fix = byId(name + "-fix");
        fix.textContent = bad[name] || "";
        fix.hidden = !bad[name];
        byId(name + "-field").classList.toggle("is-refused", !!bad[name]);
        if (byId(name)) { byId(name).setAttribute("aria-invalid", bad[name] ? "true" : "false"); }
      });
      var count = Object.keys(bad).length;
      byId("check").textContent = count === 1 ? "Please check the detail below." : "Please check the " + count + " details below.";
    }

    function apply(state) {
      if (state === "validation") { paint(faults()); } else if (state !== "loading") { paint({}); }
      details.disabled = state === "loading";
      place.classList.toggle("is-sending", state === "loading");   // R3.2: pressed twice, sent once
    }
    document.addEventListener("live:change", function (event) { apply(event.detail.state); });

    // R5: a day the bakery cannot do is said as soon as it is chosen
    day.addEventListener("change", function () {
      if (live.state === "validation") { paint(faults()); return; }
      var bad = faults();
      var fix = byId("day-fix");
      fix.textContent = day.value && bad.day ? bad.day : "";
      fix.hidden = !fix.textContent;
      byId("day-field").classList.toggle("is-refused", !fix.hidden);
    });

    function nextNumber(orders) {
      var top = orders.reduce(function (n, o) { return Math.max(n, parseInt(o.number.slice(3), 10)); }, 1042);
      return "ML-" + (top + 1);
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (live.state === "loading") { return; }
      var bad = faults();
      if (Object.keys(bad).length) {
        show("validation");
        byId("check").focus();
        return;
      }
      var name = cake.options[cake.selectedIndex].textContent;
      var s = size();
      var order = { cake: name, size: s, day: day.value, name: byId("name").value.trim(), phone: byId("phone").value.trim(),
                    words: byId("words").value.trim(), allergies: byId("allergies").value.trim(), status: "placed", price: priceOf(name, s) };
      show("loading");
      setTimeout(function () {
        var orders = live.kept("orders", null) || sample.orders.map(seeded);
        order.number = nextNumber(orders);
        orders.push(order);
        live.keep("orders", orders);          // R3
        live.keep("placed", order);           // R6
        location.href = "SC4.html";
      }, 700);
    });

    if (live.state !== "normal") { apply(live.state); }
  }

  if (screen === "SC4") {
    if (live.state === "empty") { location.replace("SC3.html"); }   // R6.3
    // R6: the order just placed; opened alone, the sample of R3.1; a reload places nothing
    var placed = live.kept("placed", null);
    var shown = placed || { number: sample.placed.number, cake: sample.placed.cake, size: sample.placed.size, day: openDay(sample.placed.openDay), name: sample.placed.name, price: sample.placed.price };
    byId("number").textContent = shown.number;
    byId("f-cake").textContent = shown.cake + ", " + shown.size;
    byId("f-day").textContent = words(shown.day);
    byId("f-name").textContent = shown.name;
    byId("f-price").textContent = "€" + shown.price;
  }

  if (screen === "SC5") {
    var orders = live.kept("orders", null) || sample.orders.map(seeded);
    var template = byId("order-row");
    template.remove();
    template.removeAttribute("id");
    var failed = null;

    function dayLabel(d) {
      if (d === inDays(0)) { return "Today"; }
      if (d === inDays(1)) { return "Tomorrow"; }
      return words(d);
    }

    function note(order) {
      var said = [];
      if (order.words) { said.push("Words: " + order.words + "."); }
      if (order.allergies) { said.push("Allergies: " + order.allergies + "."); }
      return said.join(" ");
    }

    function row(order) {
      var el = template.cloneNode(true);
      var ready = order.status === "ready";
      function part(n) { return el.querySelector('[data-part="C6.' + n + '"]'); }
      el.classList.toggle("is-ready", ready);
      part(1).textContent = dayLabel(order.day);
      part(2).textContent = order.number;
      part(3).textContent = order.cake + ", " + order.size;
      part(4).textContent = order.name;
      part(5).textContent = order.phone;
      part(5).setAttribute("href", "tel:" + order.phone.replace(/\s/g, ""));
      part(6).textContent = note(order);
      part(7).textContent = ready ? "Ready" : "To do";
      part(7).className = "ml-status " + (ready ? "ml-status-ready" : "ml-status-todo");
      part(8).hidden = ready;
      part(8).setAttribute("aria-label", "Mark ready: " + order.number);
      part(10).hidden = failed !== order.number;
      part(8).addEventListener("click", function () { mark(order); });     // R10
      return el;
    }

    // R9: the soonest pick-up day first, under To do and Ready; an order whose day has passed has gone
    function render() {
      var kept = orders.filter(function (o) { return o.day >= inDays(0); });
      kept.sort(function (a, b) { return a.day < b.day ? -1 : a.day > b.day ? 1 : a.number < b.number ? -1 : 1; });
      var todo = byId("to-do"), done = byId("ready");
      todo.textContent = ""; done.textContent = "";
      var counts = { placed: 0, ready: 0 };
      kept.forEach(function (order) {
        counts[order.status] += 1;
        (order.status === "ready" ? done : todo).appendChild(row(order));
      });
      todo.parentNode.hidden = !counts.placed;
      done.parentNode.hidden = !counts.ready;
      return kept.length;
    }

    function mark(order) {
      failed = null;
      order.status = "ready";
      live.keep("orders", orders);
      if (live.state === "save-failed") { live.state = "normal"; }
      render();
      var next = document.querySelector('#to-do button[data-part="C6.8"]');
      if (next) { next.focus(); }
    }

    document.addEventListener("live:change", function (event) {
      // R10.4: the first order to do, as if its mark could not be saved
      var first = orders.filter(function (o) { return o.status === "placed" && o.day >= inDays(0); }).sort(function (a, b) { return a.day < b.day ? -1 : 1; })[0];
      failed = event.detail.state === "save-failed" && first ? first.number : null;
      render();
    });

    byId("sign-in").addEventListener("submit", function (event) {         // R11
      event.preventDefault();
      var password = byId("password");
      if (password.value === sample.staffPassword) {
        live.keep("staff", true);
        password.value = "";
        show(render() ? "normal" : "empty");
      } else {
        show("wrong-password");
      }
    });

    var count = render();
    if (live.state === "normal" && params.get("signin") && !live.kept("staff", false)) { show("unauthorized"); }
    else if (live.state === "normal" && !count) { show("empty"); }
    else if (live.state === "save-failed") { show("save-failed"); }
  }
}());
