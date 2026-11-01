// The behaviour of the product's prototype: what its pages do beyond what assets/js/live.js gives every prototype
// (states, variants, dialogs, the wireframe view). The product's own file: `spec.py --write` never writes it. It is a
// reference of what each screen does, never the product's code.
(function () {
  "use strict";
  var main = document.querySelector("[data-prototype]");
  var screen = main ? main.getAttribute("data-prototype") : "";
  var live = window.live;
  var sample = window.SAMPLE;

  // a state the product's own script reaches -- a form refused, the link sent, the cart emptied -- shown as live.js
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

  function money(amount) {
    return "€" + amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  if (screen === "SC3") {
    // R4: Add to cart puts the quantity chosen, one to five (B1), in the cart and opens it.
    document.getElementById("add").addEventListener("click", function () {
      location.href = live.carry("SC5-the-cart.html");
    });
  }

  if (screen === "SC5") {
    // R5: a line's minus and plus change its quantity, one to five (B1); the minus at one removes the line, as
    // Remove does; the summary follows, with delivery free from fifty euros (B2). The last line gone, the cart is empty.
    var lines = document.querySelector("#lines tbody");
    function total() {
      var sum = 0;
      Array.prototype.forEach.call(lines.querySelectorAll("tr"), function (row) {
        var qty = parseInt(row.querySelector("input").value, 10);
        var line = parseFloat(row.getAttribute("data-price")) * qty;
        row.querySelector(".js-line").textContent = money(line);
        sum += line;
      });
      var delivery = sum >= sample.freeDeliveryFrom ? 0 : sample.delivery;
      document.getElementById("subtotal").textContent = money(sum);
      document.getElementById("delivery").textContent = delivery ? money(delivery) : "Free";
      document.getElementById("total").textContent = money(sum + delivery);
      if (!lines.querySelector("tr")) { show("empty"); }
    }
    lines.addEventListener("click", function (event) {
      var row = event.target.closest ? event.target.closest("tr") : null;
      if (!row) { return; }
      var field = row.querySelector("input");
      var qty = parseInt(field.value, 10);
      if (event.target.classList.contains("js-more")) { field.value = Math.min(qty + 1, sample.mostOfOne); }
      else if (event.target.classList.contains("js-fewer")) {
        if (qty <= 1) { row.parentNode.removeChild(row); } else { field.value = qty - 1; }
      } else if (event.target.classList.contains("js-remove")) {
        event.preventDefault();
        row.parentNode.removeChild(row);
      } else { return; }
      total();
    });
    document.getElementById("code-form").addEventListener("submit", function (event) { event.preventDefault(); });
  }

  if (screen === "SC7") {
    // R7: the sample account's email and password sign in, and the profile opens; anything else is refused above
    // the form, both fields marked, what was typed kept (E27).
    var email = document.getElementById("email"), password = document.getElementById("password");
    document.getElementById("sign-in-go").addEventListener("click", function () {
      if (email.value.trim() === sample.account.email && password.value === sample.account.password) {
        location.href = live.carry("SC11-my-profile.html");
        return;
      }
      show("validation");
    });
    document.addEventListener("live:change", function (event) {
      var refused = event.detail.state === "validation";
      email.classList.toggle("is-invalid", refused);
      password.classList.toggle("is-invalid", refused);
    });
  }

  if (screen === "SC8") {
    // R8, B6: a form with a field wrong is refused, each field saying why; one with every field right makes the
    // account and opens the profile.
    document.getElementById("sign-up-go").addEventListener("click", function () {
      var said = document.getElementById("su-email").value.trim();
      var word = document.getElementById("su-password").value;
      var again = document.getElementById("confirm").value;
      var wrong = !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(said) || word.length < 8 || !/\d/.test(word) || word !== again;
      if (wrong) { show("validation"); return; }
      location.href = live.carry("SC11-my-profile.html");
    });
  }

  if (screen === "SC9") {
    // R9, B7: the page after says the same whether or not an account has the email.
    document.getElementById("forgot-go").addEventListener("click", function () {
      show("success");
    });
  }

  if (screen === "SC14") {
    // R13: a filter shows the orders of its statuses: Open the placed and the paid, Shipped the shipped and the
    // delivered (E55).
    var holds = { all: null, open: ["placed", "paid"], shipped: ["shipped", "delivered"], cancelled: ["cancelled"] };
    var filters = document.getElementById("filters");
    filters.addEventListener("click", function (event) {
      var link = event.target.closest ? event.target.closest("a[data-filter]") : null;
      if (!link) { return; }
      event.preventDefault();
      var wanted = holds[link.getAttribute("data-filter")];
      Array.prototype.forEach.call(filters.querySelectorAll("a"), function (a) { a.removeAttribute("aria-current"); });
      link.setAttribute("aria-current", "page");
      Array.prototype.forEach.call(document.querySelectorAll("#admin-orders tbody tr"), function (row) {
        row.hidden = wanted !== null && wanted.indexOf(row.getAttribute("data-status")) < 0;
      });
    });
  }
})();
