// The sample data of the product's prototype: what its pages show in place of a server's answers.
// The product's own file: `spec.py --write` never writes it. Taken from the captures of the shop (S2): the test
// customer, Ana, her cart and her account; the products are the catalogue's, as the walk saw them.
(function () {
  window.SAMPLE = {
    account: { email: "ana@example.com", password: "sample-2026", name: "Ana Petrescu" },
    cart: [
      { slug: "hush-700", name: "Hush 700", price: 299.00, qty: 1 },
      { slug: "volt-65", name: "Volt 65 charger", price: 39.00, qty: 2 }
    ],
    freeDeliveryFrom: 50.00,       // B2: delivery is free from fifty euros
    delivery: 4.90,
    mostOfOne: 5                   // B1: up to five of a product
  };
}());
