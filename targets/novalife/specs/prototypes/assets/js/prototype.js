// The behaviour of NovaLife's prototype: what its pages do beyond what assets/js/live.js gives every prototype
// (states, variants, dialogs, the specification on the page). The product's own file: `spec.py --write` never
// writes it.
//
// It does what the requirements say, on window.SAMPLE, and nothing they do not: each piece names the requirement it
// carries, so that an engineer reads it as a reference, never as the product's code. What it changes it keeps with
// live.keep(name, value) and reads with live.kept(name, fallback), so that it lasts from one page to the next: a
// time chosen in booking is still chosen after signing in, a booking made shows in My bookings and in the staff's
// Bookings, a booking cancelled frees its time. ?reset=1, or Reset on the Prototype page, starts the samples again.
// It finds what it works on by the element numbers of each screen's page, data-el.
(function () {
  "use strict";
  var main = document.querySelector("[data-prototype]");
  var screen = main ? main.getAttribute("data-prototype") : "";
  var S = window.SAMPLE || {};
  var live = window.live;
  if (!main || !live) { return; }

  // --- what the prototype finds its way by ------------------------------------------------------------------------
  function one(n) { return main.querySelector('[data-el="' + n + '"]'); }
  function all(n) { return Array.prototype.slice.call(main.querySelectorAll('[data-el="' + n + '"]')); }
  function state(name) { window.postMessage({ live: true, state: name }, "*"); }
  function go(page, as) { location.href = page + (as ? "?as=" + as : ""); }
  function param(name) { return new URLSearchParams(location.search).get(name); }
  function on(el, event, run) { if (el) { el.addEventListener(event, function (e) { e.preventDefault(); run(e); }); } }
  function value(n) { var el = one(n); return el ? (el.value || "").trim() : ""; }
  function say(n, text) { all(n).forEach(function (el) { el.textContent = text; }); }

  // --- what is kept between pages ---------------------------------------------------------------------------------
  function bookings() { return live.kept("bookings", S.bookings); }
  function keepBookings(list) { live.keep("bookings", list); }
  function typeOf(id) { return S.types.filter(function (t) { return t.id === id; })[0] || S.types[0]; }
  function doctorOf(id) { return S.doctors.filter(function (d) { return d.id === id; })[0] || S.doctors[0]; }
  function patient() { return live.kept("patient", S.patient); }

  // --- dates and times, as written in the United States -----------------------------------------------------------
  var DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December"];
  function dateOf(iso) { var p = iso.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function iso(d) { return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); }
  function day(isoDate) {
    var d = dateOf(isoDate);
    return DAYS[d.getDay()] + ", " + MONTHS[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear();
  }
  function clock(hhmm) {
    var h = +hhmm.split(":")[0], m = hhmm.split(":")[1];
    return (h % 12 || 12) + ":" + m + " " + (h < 12 ? "AM" : "PM");
  }
  function when(b) { return day(b.date) + ", " + clock(b.time); }
  function minutes(hhmm) { return +hhmm.split(":")[0] * 60 + +hhmm.split(":")[1]; }
  function hhmm(total) { return ("0" + Math.floor(total / 60)).slice(-2) + ":" + ("0" + total % 60).slice(-2); }
  function startOf(b) { return new Date(b.date + "T" + b.time); }
  function now() { return new Date(S.now); }

  // --- R14: a doctor's free times on a day, for a type: their hours, less days away and what is booked ------------
  function freeTimes(doctorId, isoDate, typeId) {
    var doctor = doctorOf(doctorId), type = typeOf(typeId), hours = doctor.hours[dateOf(isoDate).getDay()];
    var away = live.kept("away:" + doctorId, doctor.away);
    if (!hours || away.indexOf(isoDate) >= 0 || dateOf(isoDate) < dateOf(S.now.slice(0, 10))) { return []; }
    var busy = bookings().filter(function (b) {
      return b.doctor === doctorId && b.date === isoDate && b.status === "booked";
    }).map(function (b) { var s = minutes(b.time); return [s, s + typeOf(b.type).minutes]; });
    var out = [];
    for (var t = hours[0] * 60; t + type.minutes <= hours[1] * 60; t += 30) {
      var clash = busy.some(function (r) { return t < r[1] && r[0] < t + type.minutes; });
      if (!clash) { out.push(hhmm(t)); }
    }
    return out;
  }
  function slotsFor(doctorId, isoDate, typeId) {
    var doctors = doctorId ? [doctorId] : typeOf(typeId).doctors;
    var out = [];
    doctors.forEach(function (d) {
      freeTimes(d, isoDate, typeId).forEach(function (t) { out.push({ doctor: d, time: t }); });
    });
    return out.sort(function (a, b) { return minutes(a.time) - minutes(b.time); });
  }
  function nearestDays(doctorId, isoDate, typeId, count) {
    var found = [], d = dateOf(isoDate);
    for (var i = 1; i <= 60 && found.length < count; i++) {
      d.setDate(d.getDate() + 1);
      if (slotsFor(doctorId, iso(d), typeId).length) { found.push(iso(d)); }
    }
    return found;
  }

  // the slots of a day, drawn from the first slot of the page as their pattern (C9)
  function drawSlots(n, slots, showDoctor, chosen, pick) {
    var first = one(n);
    if (!first) { return; }
    var row = first.parentNode, pattern = first.cloneNode(true);
    all(n).forEach(function (el) { el.parentNode.removeChild(el); });
    slots.forEach(function (s) {
      var b = pattern.cloneNode(true);
      b.textContent = clock(s.time) + (showDoctor ? ", " + doctorOf(s.doctor).name : "");
      var on = chosen && chosen.time === s.time && chosen.doctor === s.doctor;
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.addEventListener("click", function (e) {
        e.preventDefault();
        Array.prototype.forEach.call(row.children, function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        pick(s);
      });
      row.appendChild(b);
    });
  }
  function fillTypes(select, chosen) {
    select.innerHTML = "";
    S.types.forEach(function (t) {
      var o = document.createElement("option");
      o.value = t.id; o.textContent = t.name + " · " + t.minutes + " minutes · $" + t.price;
      if (t.id === chosen) { o.selected = true; }
      select.appendChild(o);
    });
  }
  function fillDoctors(select, typeId, chosen, any) {
    select.innerHTML = "";
    if (any) { var a = document.createElement("option"); a.value = ""; a.textContent = "Any doctor"; select.appendChild(a); }
    typeOf(typeId).doctors.forEach(function (id) {
      var o = document.createElement("option");
      o.value = id; o.textContent = doctorOf(id).name;
      if (id === chosen) { o.selected = true; }
      select.appendChild(o);
    });
  }

  // a booking made: kept, with the time no longer free (R6); "just taken" when someone else took it meanwhile
  function book(pending, name, by) {
    var t = S.takenWhileBooking || {};
    if (t.doctor === pending.doctor && t.date === pending.date && t.time === pending.time && !live.kept("taken-once")) {
      live.keep("taken-once", true);
      return null;
    }
    var b = { id: "b" + Date.now(), type: pending.type, doctor: pending.doctor, date: pending.date,
              time: pending.time, patient: name, by: by, status: "booked" };
    var list = bookings();
    list.push(b);
    keepBookings(list);
    return b;
  }
  function takenSays(pending) {
    var next = freeTimes(pending.doctor, pending.date, pending.type).slice(0, 2).map(clock);
    return "Sorry, " + clock(pending.time) + " on " + day(pending.date).split(",").slice(0, 2).join(",") +
      " was just booked by someone else. Nothing is booked." +
      (next.length ? " The nearest free times with " + doctorOf(pending.doctor).name + ": " + next.join(" and ") + "." : "");
  }

  // --- SC2: Book this opens booking with its type chosen (R6, R7) ---------------------------------------------------
  if (screen === "SC2") {
    main.addEventListener("click", function (e) {
      var a = e.target.closest ? e.target.closest('[data-part="C4.4"]') : null;
      if (a && a.getAttribute("data-type")) { e.preventDefault(); live.keep("pending", { type: a.getAttribute("data-type") }); go("SC8-choose-a-time.html", live.as); }
    });
  }

  // --- SC8: choose a type, a doctor, a day and a free time (R6, R7, R14) ------------------------------------------
  if (screen === "SC8") {
    var pending = live.kept("pending", {});
    var type = param("type") || pending.type || "first-consultation";
    var chosen = pending.time ? { doctor: pending.doctor, time: pending.time } : null;
    fillTypes(one(5), type);
    fillDoctors(one(7), type, pending.doctor || "", true);
    one(8).value = pending.date || "2026-11-20";
    one(8).min = S.now.slice(0, 10);
    var draw = function () {
      var t = typeOf(one(5).value);
      say(6, "Price: $" + t.price);
      var slots = slotsFor(one(7).value, one(8).value, t.id);
      if (!slots.length) {
        var near = nearestDays(one(7).value, one(8).value, t.id, 2).map(function (d) { return day(d).split(",").slice(0, 2).join(","); });
        say(11, "No doctor who gives " + t.name + " is free on " + day(one(8).value).split(",").slice(0, 2).join(",") +
                ". The nearest days with a free time: " + near.join(" and ") + ".");
        state("full");
      } else if (live.state === "full" || live.state === "validation") { state("normal"); }
      drawSlots(10, slots, !one(7).value, chosen, function (s) { chosen = s; if (live.state === "validation") { state("normal"); } });
    };
    one(5).addEventListener("change", function () { chosen = null; fillDoctors(one(7), one(5).value, "", true); draw(); });
    one(7).addEventListener("change", function () { chosen = null; draw(); });
    one(8).addEventListener("change", function () { chosen = null; draw(); });
    all(12).forEach(function (a) {
      on(a, "click", function () {
        if (!chosen) { state("validation"); return; }
        live.keep("pending", { type: one(5).value, doctor: chosen.doctor, date: one(8).value, time: chosen.time });
        if (live.as === "signed-in") { go("SC10-confirm-the-booking.html", "signed-in"); }
        else { go("SC9-sign-in.html"); }
      });
    });
    draw();
  }

  // the way on once signed in or the account is open: to book the time kept, or to My bookings (R6, R16)
  var held = live.kept("pending", {});
  function onward() { go(held.time ? "SC10-confirm-the-booking.html" : "SC12-my-bookings.html", "signed-in"); }

  // --- SC9: sign in, or reset; from booking, the time is kept (R16, R6) ---------------------------------------------
  if (screen === "SC9") {
    if (held.time) {
      say(3, "Sign in or create an account to book " + typeOf(held.type).name + " with " + doctorOf(held.doctor).name +
             ", " + when(held) + ". We'll keep this time while you do.");
    } else { all(3).forEach(function (el) { el.hidden = true; el.removeAttribute("data-unless-as"); }); }
    on(one(7), "click", function () {
      if (!value(5) || !value(6) || value(6) === "wrong") { state("validation"); return; }
      live.keep("patient", S.patient);
      onward();
    });
    on(one(20), "click", function () { if (value(19)) { state("success"); } });
  }

  // --- SC21: create an account, its own form; from booking, the time is kept and booked on next (R16, R6) ----------
  if (screen === "SC21") {
    if (held.time) {
      say(5, typeOf(held.type).name + " with " + doctorOf(held.doctor).name + ", " + when(held) + ".");
    } else { one(4).hidden = true; }
    on(one(18), "click", function () {
      var details = [7, 8, 9, 11, 12, 15, 16].map(value), today = S.now.slice(0, 10);
      var why = details.some(function (d) { return !d; }) ? (details[2] ? "Fill in every detail." : "Enter your date of birth.")
              : details[2] > today ? "Date of birth can't be in the future."
              : details[5] !== details[6] ? "The two passwords don't match." : "";
      if (why) { say(17, why); state("validation"); return; }
      if (details[3].toLowerCase() === S.patient.email) { state("taken"); return; }
      live.keep("patient", { first: details[0], last: details[1], email: details[3] });
      onward();
    });
  }

  // --- SC10: check, and book (R6, R7) -----------------------------------------------------------------------------
  if (screen === "SC10") {
    var p = live.kept("pending", {});
    if (p.time) {
      var t10 = typeOf(p.type);
      say(6, t10.name); say(7, doctorOf(p.doctor).name); say(8, when(p)); say(9, t10.minutes + " minutes");
      say(10, "$" + t10.price); say(11, patient().first + " " + patient().last);
    }
    var bookIt = function () {
      if (!p.time) { go("SC11-booking-confirmed.html", "signed-in"); return; }
      var made = book(p, patient().first + " " + patient().last, "online");
      if (!made) { say(16, takenSays(p)); state("taken"); return; }
      live.keep("pending", {}); live.keep("last", made.id);
      go("SC11-booking-confirmed.html", "signed-in");
    };
    on(one(14), "click", bookIt);
    on(one(18), "click", bookIt);
  }

  // --- SC11: what was booked (R6) ---------------------------------------------------------------------------------
  if (screen === "SC11") {
    var last = bookings().filter(function (b) { return b.id === live.kept("last", ""); })[0];
    if (last) {
      var t11 = typeOf(last.type);
      say(5, t11.name + ", " + t11.minutes + " minutes"); say(6, doctorOf(last.doctor).name);
      say(7, when(last)); say(8, "$" + t11.price + ", paid at the visit");
    }
  }

  // --- SC12: my bookings, to come and past, and cancelling one (R17, R15) -------------------------------------------
  if (screen === "SC12") {
    var who = patient().first + " " + patient().last, target = null;
    var comingPattern = one(4).cloneNode(true), pastPattern = one(10).cloneNode(true);
    [comingPattern, pastPattern].forEach(function (x) { x.removeAttribute("data-when"); x.removeAttribute("data-unless"); x.hidden = false; });
    var drawMine = function () {
      var mine = bookings().filter(function (b) { return b.patient === who; });
      var coming = mine.filter(function (b) { return b.status === "booked" && startOf(b) >= now(); })
                       .sort(function (a, b) { return startOf(a) - startOf(b); });
      var past = mine.filter(function (b) { return b.status !== "booked" || startOf(b) < now(); })
                     .sort(function (a, b) { return startOf(b) - startOf(a); });
      [4, 10].forEach(function (n) { all(n).forEach(function (el) { el.parentNode.removeChild(el); }); });
      var pastHead = one(9);
      coming.forEach(function (b) {
        var card = comingPattern.cloneNode(true);
        card.querySelector('[data-el="5"]').textContent = typeOf(b.type).name + " with " + doctorOf(b.doctor).name;
        card.querySelector('[data-el="6"]').textContent = when(b);
        card.querySelector('[data-el="7"]').addEventListener("click", function () {
          target = b;
          say(21, "Cancel " + typeOf(b.type).name + " with " + doctorOf(b.doctor).name + " on " + when(b) +
                  "? Its time will be offered to others.");
        }, true);
        pastHead.parentNode.insertBefore(card, pastHead);
      });
      past.forEach(function (b) {
        var row = pastPattern.cloneNode(true), mark = row.querySelector('[data-el="11"]');
        row.firstChild.textContent = typeOf(b.type).name + " with " + doctorOf(b.doctor).name + ", " + when(b) + " ";
        if (b.status === "cancelled" && mark) { mark.hidden = false; mark.removeAttribute("data-when"); }
        else if (mark) { mark.parentNode.removeChild(mark); }
        pastHead.parentNode.appendChild(row);
      });
      if (!mine.length) { state("empty"); }
    };
    drawMine();
    on(one(15), "click", function () {
      one(14).close();
      if (!target) { return; }
      if (startOf(target) - now() < 24 * 3600 * 1000) { state("too-late"); return; }
      var list = bookings().map(function (b) { if (b.id === target.id) { b.status = "cancelled"; } return b; });
      keepBookings(list); drawMine(); state("cancelled");
    });
  }

  // --- SC13: the staff sign in, and each role opens where it works (R12, R18) --------------------------------------
  if (screen === "SC13") {
    on(one(5), "click", function () {
      var email = value(3).toLowerCase();
      if (!email || !value(4)) { state("validation"); return; }
      var account = S.staff.filter(function (s) { return s.email === email; })[0];
      if (!account || value(4) === "wrong") { state("validation"); return; }
      if (account.role === "Doctor") { go("SC16-free-times.html", "doctor"); }
      else { go("SC14-staff-bookings.html", account.role === "Front desk" ? "front-desk" : ""); }
    });
    on(one(12), "click", function () { if (value(11)) { state("success"); } });
  }

  // --- SC14: the day's bookings, found and cancelled for a caller (R15, R6) -----------------------------------------
  if (screen === "SC14") {
    var victim = null, rowPattern = one(8).parentNode.cloneNode(true);
    one(4).innerHTML = '<option value="">All doctors</option>' + S.doctors.map(function (d) {
      return '<option value="' + d.id + '">' + d.name + "</option>"; }).join("");
    var drawDay = function () {
      var table = one(6), q = value(5).toLowerCase();
      Array.prototype.slice.call(table.querySelectorAll("tr")).slice(1).forEach(function (r) { r.parentNode.removeChild(r); });
      var dayList = bookings().filter(function (b) {
        return b.date === value(3) && b.status === "booked" && (!value(4) || b.doctor === value(4));
      });
      var shown = dayList.filter(function (b) { return !q || b.patient.toLowerCase().indexOf(q) >= 0; })
                         .sort(function (a, b) { return minutes(a.time) - minutes(b.time); });
      shown.forEach(function (b) {
        var r = rowPattern.cloneNode(true), c = r.children;
        c[0].textContent = clock(b.time); c[1].textContent = doctorOf(b.doctor).name; c[2].textContent = b.patient;
        c[3].textContent = typeOf(b.type).name; c[4].textContent = b.by === "online" ? "Online" : "Front desk, for a caller";
        c[5].querySelector("button").addEventListener("click", function () {
          victim = b;
          say(15, "Cancel " + b.patient + "'s " + typeOf(b.type).name + " with " + doctorOf(b.doctor).name + ", " + when(b) + "?");
        }, true);
        (table.tBodies[0] || table).appendChild(r);
      });
      say(20, "No bookings on " + day(value(3)).split(",").slice(0, 2).join(",") + ".");
      say(21, "No booking on " + day(value(3)).split(",").slice(0, 2).join(",") + " matches “" + value(5) + "”.");
      if (live.state === "unauthorized") { return; }
      state(!dayList.length ? "empty" : !shown.length ? "no-results" : live.state === "cancelled" ? "cancelled" : "normal");
    };
    [3, 4].forEach(function (n) { one(n).addEventListener("change", drawDay); });
    one(5).addEventListener("input", drawDay);
    on(one(16), "click", function () {
      one(14).close();
      if (!victim) { return; }
      keepBookings(bookings().map(function (b) { if (b.id === victim.id) { b.status = "cancelled"; } return b; }));
      say(18, victim.patient + "'s booking at " + clock(victim.time) + " is cancelled, and its time is free again.");
      state("cancelled"); drawDay();
    });
    drawDay();
  }

  // --- SC15: booking for a caller, in their name, recorded as made by the staff (R6) --------------------------------
  if (screen === "SC15") {
    var pick = null;
    fillTypes(one(10), "first-consultation");
    fillDoctors(one(11), "first-consultation", "lee", false);
    one(12).value = "2026-11-20";
    var drawCaller = function () {
      drawSlots(14, slotsFor(one(11).value, one(12).value, one(10).value), false, pick, function (s) { pick = s; });
    };
    one(10).addEventListener("change", function () { pick = null; fillDoctors(one(11), one(10).value, "", false); drawCaller(); });
    [11, 12].forEach(function (n) { one(n).addEventListener("change", function () { pick = null; drawCaller(); }); });
    on(one(15), "click", function () {
      if (!value(5)) { state("validation"); return; }
      if (!pick) { return; }
      var details = all(4).map(function (f) { return f.value.trim(); });
      var p15 = { type: one(10).value, doctor: pick.doctor, date: one(12).value, time: pick.time };
      var made = book(p15, details[0] + " " + details[1], "front desk");
      if (!made) { say(18, takenSays(p15)); state("taken"); return; }
      say(16, "Booked: " + typeOf(made.type).name + " with " + doctorOf(made.doctor).name + ", " + when(made) + ", for " +
              made.patient + ". Recorded as booked by Alex Chen for a caller. ");
      var again = one(17); if (again) { all(16)[0].appendChild(again); }
      state("success");
    });
    drawCaller();
  }

  // --- SC16: a doctor's weekly hours and days away (R14, R18) -------------------------------------------------------
  if (screen === "SC16") {
    var doc = live.as === "doctor" ? "lee" : "lee";
    if (live.as === "doctor") { one(3).disabled = true; }
    one(3).innerHTML = S.doctors.map(function (d) { return '<option value="' + d.id + '">' + d.name + "</option>"; }).join("");
    var drawHours = function () {
      var d = doctorOf(one(3).value), from = all(8), to = all(9);
      [1, 2, 3, 4, 5, 6, 0].forEach(function (wd, i) {
        var h = d.hours[wd];
        from[i].value = h ? clock(hhmm(h[0] * 60)) : ""; to[i].value = h ? clock(hhmm(h[1] * 60)) : "";
      });
      var away = live.kept("away:" + d.id, d.away), item = one(11).parentNode, list = item.parentNode;
      Array.prototype.slice.call(list.children).slice(1).forEach(function (x) { list.removeChild(x); });
      item.hidden = !away.length;
      away.forEach(function (a, i) {
        var li = i ? item.cloneNode(true) : item;
        li.querySelector('[data-el="11"]').textContent = day(a);
        if (i) { list.appendChild(li); }
      });
    };
    one(3).value = doc;
    one(3).addEventListener("change", function () { state("normal"); drawHours(); });
    on(one(15), "click", function () { say(16, "Saved. Booking now offers " + doctorOf(one(3).value).name + "'s new free times."); state("success"); });
    on(one(14), "click", function () {
      var d = one(3).value, when14 = value(13);
      if (!when14) { return; }
      var clash = bookings().filter(function (b) { return b.doctor === d && b.date === when14 && b.status === "booked"; });
      if (clash.length) {
        say(17, doctorOf(d).name + " has " + clash.length + " booking" + (clash.length > 1 ? "s" : "") + " on " +
                day(when14).split(",").slice(0, 2).join(",") + ". Cancel each, and book it again for the patient, before marking the day away.");
        var first = one(18), ul = first.parentNode;
        all(18).slice(1).forEach(function (x) { ul.removeChild(x); });
        clash.forEach(function (b, i) {
          var li = i ? first.cloneNode(true) : first;
          li.textContent = clock(b.time) + ", " + b.patient + ", " + typeOf(b.type).name;
          if (i) { ul.appendChild(li); }
        });
        state("conflict"); return;
      }
      var away = live.kept("away:" + d, doctorOf(d).away).concat([when14]).sort();
      live.keep("away:" + d, away); drawHours(); state("normal");
    });
    drawHours();
  }

  // --- SC17, SC18: the administrator saves, and visitors see it (R13) -----------------------------------------------
  if (screen === "SC17") { on(one(7), "click", function () { state("success"); }); }
  if (screen === "SC18") {
    [15, 21].forEach(function (n) { all(n).forEach(function (b) { b.addEventListener("click", function () { state("success"); }); }); });
    all(18).forEach(function (b) {
      on(b, "click", function () { b.parentNode.parentNode.removeChild(b.parentNode); state("success"); });
    });
  }

  // --- SC19: staff accounts, added with a link, never without an administrator (R19) --------------------------------
  if (screen === "SC19") {
    var removing = null;
    all(8).forEach(function (b) { b.addEventListener("click", function () {
      removing = b.closest("tr");
      say(18, "Remove " + removing.children[0].textContent + "? They will no longer be able to sign in.");
    }, true); });
    one(12).addEventListener("click", function () {
      var fields = all(11), email = fields[1].value.trim().toLowerCase();
      var taken = Array.prototype.some.call(one(4).querySelectorAll("tr"), function (r) {
        return r.children[1] && r.children[1].textContent.toLowerCase() === email; });
      if (taken) { state("taken"); return; }
      var row = one(4).querySelectorAll("tr")[1].cloneNode(true);
      row.children[0].textContent = fields[0].value.trim(); row.children[1].textContent = fields[1].value.trim();
      row.children[2].textContent = fields[2].value;
      (one(4).tBodies[0] || one(4)).appendChild(row);
      say(14, fields[0].value.trim() + " is added. We've sent a link to set a password to " + fields[1].value.trim() + ".");
      state("success");
    });
    on(one(19), "click", function () {
      one(17).close();
      if (!removing) { return; }
      var admins = Array.prototype.filter.call(one(4).querySelectorAll("tr"), function (r) {
        return r.children[2] && r.children[2].textContent === "Administrator"; });
      if (removing.children[2].textContent === "Administrator" && admins.length < 2) { state("last-admin"); return; }
      removing.parentNode.removeChild(removing); state("normal");
    });
  }

  // --- SC20: a new password, typed twice (R19, R16) -----------------------------------------------------------------
  if (screen === "SC20") {
    on(one(6), "click", function () {
      if (!value(3) || value(3) !== value(4)) { state("validation"); return; }
      state("success");
    });
  }
})();
