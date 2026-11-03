// The sample data of NovaLife's prototype: what its pages show in place of a server's answers.
// The product's own file: `spec.py --write` never writes it.
//
// Every name, time, price and hour here is a SAMPLE, made up so that the flows can be walked: none is the clinic's.
// The clinic's own come from its staff, through the staff area (R13). The rules the samples follow are the
// requirements': free times are each doctor's hours less what is booked, one appointment starting as the one
// before it ends (R14); a patient cancels online up to 24 hours before (R15); prices in US dollars (R7).
window.SAMPLE = {
  // the moment the prototype pretends it is: a Tuesday morning
  now: "2026-10-20T10:00",

  services: [
    { id: "general-medical-care", name: "General medical care", as: "" },
    { id: "prevention-and-early-detection", name: "Prevention and early detection", as: "prevention" },
    { id: "longevity-and-healthy-aging", name: "Longevity and healthy aging", as: "longevity" },
    { id: "high-tech-personalized-healthcare", name: "High-tech, personalized healthcare", as: "high-tech" }
  ],

  types: [
    { id: "first-consultation", name: "First consultation", service: "general-medical-care", minutes: 60,
      price: 120, doctors: ["lee", "moreno"] },
    { id: "follow-up-visit", name: "Follow-up visit", service: "general-medical-care", minutes: 30,
      price: 95, doctors: ["lee", "moreno"] },
    { id: "annual-check-up", name: "Annual check-up", service: "prevention-and-early-detection", minutes: 60,
      price: 250, doctors: ["patel"] },
    { id: "longevity-assessment", name: "Longevity assessment", service: "longevity-and-healthy-aging",
      minutes: 90, price: 300, doctors: ["patel"] },
    { id: "health-data-review", name: "Health data review", service: "high-tech-personalized-healthcare",
      minutes: 45, price: 150, doctors: ["moreno"] }
  ],

  // each doctor's weekly hours, by day of the week (0 is Sunday), from and to in hours, and their days away
  doctors: [
    { id: "lee", name: "Dr. Lee", hours: { 1: [9, 13], 2: [9, 17], 4: [13, 18], 5: [9, 13] },
      away: ["2027-01-01"] },
    { id: "moreno", name: "Dr. Moreno", hours: { 1: [9, 17], 2: [9, 17], 3: [9, 17], 4: [9, 17], 5: [9, 17] },
      away: [] },
    { id: "patel", name: "Dr. Patel", hours: { 1: [8, 12], 3: [8, 16], 5: [8, 12] }, away: [] }
  ],

  // the patient who signs in, and the bookings the clinic already has
  patient: { first: "Jordan", last: "Smith", email: "jordan.smith@example.com" },
  bookings: [
    { id: "b1", type: "first-consultation", doctor: "lee", date: "2026-11-20", time: "10:00",
      patient: "Jordan Smith", by: "online", status: "booked" },
    { id: "b2", type: "follow-up-visit", doctor: "lee", date: "2026-10-21", time: "09:00",
      patient: "Jordan Smith", by: "online", status: "booked" },
    { id: "b3", type: "annual-check-up", doctor: "patel", date: "2026-10-02", time: "09:00",
      patient: "Jordan Smith", by: "online", status: "booked" },
    { id: "b4", type: "follow-up-visit", doctor: "lee", date: "2026-11-20", time: "09:00",
      patient: "Casey Brown", by: "online", status: "booked" },
    { id: "b5", type: "annual-check-up", doctor: "patel", date: "2026-11-20", time: "08:00",
      patient: "Robin Diaz", by: "front desk", status: "booked" },
    { id: "b6", type: "first-consultation", doctor: "lee", date: "2026-12-24", time: "14:00",
      patient: "Casey Brown", by: "online", status: "booked" }
  ],

  // a time someone else books while the visitor is booking it, to walk "just taken" (R6)
  takenWhileBooking: { doctor: "lee", date: "2026-11-20", time: "12:00" },

  // the staff accounts; email "taken" is one that already has an account
  staff: [
    { name: "Sam Rivera", email: "sam.rivera@example.com", role: "Administrator" },
    { name: "Alex Chen", email: "alex.chen@example.com", role: "Front desk" },
    { name: "Dr. Lee", email: "lee@example.com", role: "Doctor" }
  ]
};
