# Integrations and API

- **What it is:** How the product works with the other software its users already rely on. It covers connections to named products, an interface other programs can call, and data that must stay in step.
- **Applies when:** The work the product supports begins or ends in another system: a calendar, an accounting package, a payment provider, an email service, a customer's own software. A product that is the whole of its users' workflow needs none.
- **If left unsaid:** Users copy data between two screens by hand, which is the complaint that sinks adoption. Or engineering builds a general interface for integrations nobody has asked for.
- **Ask:**
  1. What do users have open next to this product while they work?
  2. What do they copy from one to the other today?
  3. Which of those systems must it work with for a customer to say yes?
  4. Which direction does the data go, and how fresh must it be: instantly, hourly, overnight?
  5. When the two disagree, which one is right?
- **Options:**
  - files in and out -- export from one, import to the other; works with anything and costs the user time each occasion.
  - a general connector service -- a third-party automation tool links the products; quick to offer, limited, and the customer pays for and maintains it.
  - a built connection to one named product -- reliable and smooth; each is a continuing commitment as the other product changes.
  - your own interface for programs -- customers and partners build what they need; a public promise that is hard to change once made.
- **First release:** At most one connection, to the system named by the first customers as a condition of saying yes; otherwise files. An interface for other programs waits until someone specific wants to build on it.
- **Often forgotten:** The other system being down, slow or changed. A user who disconnects, or whose permission in the other system expires. The same record edited on both sides. Limits on how often the other system may be called. Who supports the customer when the fault is in between. Fees and terms of the other party.
- **Becomes:** A constraint naming each outside system and who owns it; requirements for connecting, for failure and for disagreement; open questions for engineering on what the other system allows; non-goals for the connections not made.
