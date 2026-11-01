// What the Feedback website's prototype does beyond showing: only what the requirements say, each piece naming its own.
(function () {
  "use strict";
  function go(state) { location.search = "?state=" + state; }

  // R6: a person picks 1 to 5 stars; the number is said beside them, so that a rating is never shown by stars alone
  var set = document.querySelector("[data-stars]");
  if (set) {
    var stars = Array.prototype.slice.call(set.querySelectorAll(".fb-star"));
    var note = set.querySelector(".fb-stars-note");
    set.addEventListener("change", function (e) {
      var n = Number(e.target.value);
      stars.forEach(function (s, i) { s.classList.toggle("is-on", i < n); });
      if (note) { note.textContent = n + " of 5"; }
    });
  }

  // R1.2 nothing to send; R5.3 an address that does not look right; R2 kept, with thanks
  var form = document.querySelector("[data-feedback]");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var rated = form.querySelector("input[name=rating]:checked");
      var words = form.querySelector("textarea:not([hidden])").value.trim();
      var address = form.querySelector("input[type=text]:not([hidden])").value.trim();
      if (!rated && !words) { go("validation"); return; }
      if (address && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(address)) { go("bad-address"); return; }
      go("success");
    });
  }

  // R17: the customer confirms, then is opted out
  var stop = document.querySelector("[data-stop]");
  if (stop) { stop.addEventListener("click", function () { go("success"); }); }
})();
