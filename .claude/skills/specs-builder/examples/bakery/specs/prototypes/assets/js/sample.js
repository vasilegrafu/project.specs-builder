// The sample data of Mill Lane Bakery's prototype: what its pages show in place of a server's answers. The bakery, its
// cakes and its rules are the owner's (D4 to D7). The customers and their orders are made up to fill the list, with Rosa
// Bell from R3.1 and phone numbers from the range kept for drama.
(function () {
  window.SAMPLE = {
    notice: 2,              // B1: days of notice for a cake
    closedDays: [1],        // B2: the days of the week the bakery is closed, 0 for Sunday
    largeExtra: 10,         // a large cake costs this much more, in euros
    staffPassword: "sample",
    cakes: [
      { id: "victoria", name: "Victoria sponge", price: 28 },
      { id: "fudge", name: "Chocolate fudge cake", price: 32 },
      { id: "carrot", name: "Carrot cake", price: 30 }
    ],
    orders: [               // openDay: which open day from today the pick-up day is, 0 the first
      { number: "ML-1039", cake: "Carrot cake", size: "small", openDay: 0, name: "Ana Costa", phone: "07700 900204", words: "", allergies: "", status: "ready" },
      { number: "ML-1040", cake: "Victoria sponge", size: "large", openDay: 0, name: "Tom Ward", phone: "07700 900118", words: "Happy birthday Joe", allergies: "", status: "placed" },
      { number: "ML-1041", cake: "Chocolate fudge cake", size: "small", openDay: 1, name: "Priya Shah", phone: "07700 900367", words: "", allergies: "", status: "placed" },
      { number: "ML-1042", cake: "Carrot cake", size: "large", openDay: 3, name: "Sam Reid", phone: "07700 900451", words: "Well done Mia", allergies: "Walnuts", status: "placed" }
    ],
    placed: { number: "ML-1043", cake: "Victoria sponge", size: "large", openDay: 5, name: "Rosa Bell", price: 38 }   // R3.1: what Order placed shows when opened alone
  };
}());
