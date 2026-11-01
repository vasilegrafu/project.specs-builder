// The behaviour of the product's prototype: what its pages do beyond what assets/js/live.js gives every prototype
// (states, variants, the wireframe view). The product's own file: `spec.py --write` never writes it. It is a
// reference of what each screen does, never the product's code.
(function () {
  "use strict";
  var main = document.querySelector("[data-prototype]");
  var screen = main ? main.getAttribute("data-prototype") : "";
  var live = window.live;
  var sample = window.SAMPLE;
  var params = new URLSearchParams(location.search);
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December"];

  // a state the product's own script reaches -- a form refused, a day full, the visit booked -- shown as live.js
  // shows one asked for by the Prototype page
  function show(state) {
    live.state = state;
    function words(list) { return (list || "").split(/[\s,]+/).filter(function (w) { return w; }); }
    Array.prototype.forEach.call(document.querySelectorAll("[data-when], [data-unless]"), function (el) {
      var when = words(el.getAttribute("data-when")), unless = words(el.getAttribute("data-unless"));
      el.hidden = !((!when.length || when.indexOf(state) >= 0) && unless.indexOf(state) < 0);
    });
    document.dispatchEvent(new CustomEvent("live:change", { detail: { state: state, as: live.as } }));
  }

  function day(iso) {
    var parts = iso.split("-");
    return parseInt(parts[2], 10) + " " + MONTHS[parseInt(parts[1], 10) - 1] + " " + parts[0];
  }

  if (screen === "SC1") {
    // R11, and the decision on X2: Open today says the hours of the day it is, and closed on a Sunday.
    var hours = sample.hours[new Date().getDay()];
    document.getElementById("today-hours").textContent = hours;
    if (hours === "closed") {
      document.getElementById("today-h").textContent = "Closed today";
      document.getElementById("today-hours").hidden = true;
    }
  }

  if (screen === "SC3") {
    // R4: Book a visit with opens the form with this one chosen; the variant is the nurse's page.
    var bookWith = document.getElementById("book-with");
    function chosen() {
      bookWith.setAttribute("href", "SC4-book-a-visit.html?doctor=" + (live.as === "nurse" ? "sam-whitfield" : "amara-okafor"));
    }
    document.addEventListener("live:change", chosen);
    chosen();
  }

  if (screen === "SC4") {
    var doctor = document.getElementById("doctor"), time = document.getElementById("time");
    var date = document.getElementById("date"), email = document.getElementById("email");
    // B2, and the decision on X1: the Time offers the usual times of the one chosen.
    function times() {
      var chosen = sample.team[doctor.value];
      time.innerHTML = "<option value=\"\">Choose</option>";
      (chosen ? chosen.times : []).forEach(function (t) {
        var option = document.createElement("option");
        option.textContent = t;
        time.appendChild(option);
      });
    }
    doctor.addEventListener("change", times);
    // the refused state, asked for by the Prototype page, marks the three fields the walk saw refused (E20)
    document.addEventListener("live:change", function (event) {
      var refused = event.detail.state === "validation";
      [date, time, email].forEach(function (field) { field.classList.toggle("lc-is-invalid", refused); });
    });
    // R4: opened from a page of the team, that one is chosen.
    if (params.get("doctor") && sample.team[params.get("doctor")]) { doctor.value = params.get("doctor"); }
    times();
    // R2, R3, B1: a day from tomorrow, a time and an email, or the form is refused field by field; a day with no
    // free time is said with the nearest free times (E23); otherwise the visit is booked.
    document.getElementById("book-go").addEventListener("click", function () {
      var wrongDay = !date.value || date.value <= sample.today;
      var wrongTime = !time.value;
      var wrongEmail = !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value.trim());
      if (wrongDay || wrongTime || wrongEmail) {
        show("validation");
        date.classList.toggle("lc-is-invalid", wrongDay);
        time.classList.toggle("lc-is-invalid", wrongTime);
        email.classList.toggle("lc-is-invalid", wrongEmail);
        document.getElementById("date-msg").hidden = !wrongDay;
        document.getElementById("time-msg").hidden = !wrongTime;
        document.getElementById("email-msg").hidden = !wrongEmail;
        return;
      }
      if (doctor.value === sample.full.doctor && date.value === sample.full.day) { show("full"); return; }
      var chosen = sample.team[doctor.value];
      document.getElementById("booked-with").textContent = chosen.name + ", " + chosen.role;
      document.getElementById("booked-when").textContent = day(date.value) + " at " + time.value;
      document.getElementById("booked-about").textContent = document.getElementById("reason").value || "--";
      document.getElementById("booked-email").textContent = email.value.trim();
      show("success");
    });
  }

  if (screen === "SC7") {
    // R6: Cancel the visit cancels it, and the page says so.
    document.getElementById("cancel-go").addEventListener("click", function () { show("success"); });
  }

  if (screen === "SC8") {
    // R8: the sample account's email and password sign in, and My visits opens; anything else is refused above the
    // form, both fields marked, the email kept (E36).
    var mail = document.getElementById("email"), password = document.getElementById("password");
    document.getElementById("sign-in-go").addEventListener("click", function () {
      if (mail.value.trim() === sample.account.email && password.value === sample.account.password) {
        location.href = live.carry("SC5-my-visits.html");
        return;
      }
      show("validation");
    });
    document.addEventListener("live:change", function (event) {
      var refused = event.detail.state === "validation";
      mail.classList.toggle("lc-is-invalid", refused);
      password.classList.toggle("lc-is-invalid", refused);
    });
  }
})();
