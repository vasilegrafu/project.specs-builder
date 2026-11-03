// The sample data of the product's prototype: what its pages show in place of a server's answers.
// The product's own file: `spec.py --write` never writes it. Taken from the captures of the clinic's site (S2): the
// test patient, Priya Nair, made up for the walk; the team, their usual times and the opening hours as the walk saw them.
(function () {
  window.SAMPLE = {
    today: "2026-10-11",                 // the day of the walk: a Sunday
    account: { email: "priya@example.com", password: "sample-2026", name: "Priya Nair" },
    team: {                              // B2: a visit starts at one of the usual times of the one it is with
      "amara-okafor": { name: "Dr Amara Okafor", role: "general practitioner",
                        times: ["08:30", "09:00", "09:30", "10:00", "11:00", "14:00", "14:30", "16:00"] },
      "tom-hale": { name: "Dr Tom Hale", role: "general practitioner",
                    times: ["08:00", "08:30", "10:30", "11:30", "15:00", "15:30"] },
      "ines-barros": { name: "Dr In\u00eas Barros", role: "general practitioner",
                       times: ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"] },
      "sam-whitfield": { name: "Sam Whitfield", role: "practice nurse",
                         times: ["08:00", "08:20", "08:40", "09:00", "09:20", "13:00", "13:20", "13:40"] },
      "lena-voss": { name: "Dr Lena Voss", role: "general practitioner",
                     times: ["09:00", "10:00", "11:00", "14:00", "15:00"] },
      "ravi-menon": { name: "Ravi Menon", role: "physiotherapist",
                      times: ["08:00", "08:40", "09:20", "10:00", "13:00", "13:40"] }
    },
    full: { doctor: "tom-hale", day: "2026-10-20" },   // E23: a day with no free time, as the walk saw it
    hours: ["closed", "08:00 \u2013 18:30", "08:00 \u2013 18:30", "08:00 \u2013 13:00", "08:00 \u2013 18:30",
            "08:00 \u2013 17:00", "09:00 \u2013 12:00"]   // Sunday first, as the week's days are numbered
  };
}());
