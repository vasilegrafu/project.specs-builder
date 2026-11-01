# Measurement

- **What it is:** How you will know whether the product is working for its users and for the business. It covers what is counted, where the count comes from, and who looks at it.
- **Applies when:** The document has goals, which is always. It is the area that makes every goal's Target checkable after release.
- **If left unsaid:** The product ships and nobody can say whether a goal was met, because nothing was counted. The data needed turns out not to have been recorded from the start and cannot be recovered.
- **Ask:**
  1. For each goal: where exactly will its number come from once the product is live?
  2. Does that number exist today, so there is a baseline to compare with?
  3. What is the one thing a user does that shows they got the value -- and can the product tell that it happened?
  4. Who will look at these numbers, how often, and what will they do differently because of them?
  5. Is there anything you must not record about users?
- **Options:**
  - count by hand -- look in the data or ask customers at intervals; fine for a handful of customers and a few numbers.
  - record the few events behind the goals -- the product notes each event a goal's metric counts; small, deliberate, and enough to answer the questions that matter.
  - a product analytics tool -- record everything users do and explore later; rich, and it brings consent obligations and a habit of looking at numbers nobody acts on.
  - reports inside the product -- customers see their own numbers; that is a feature for them, separate from measuring your goals.
- **First release:** For every goal, name the event or the count behind its metric and ask engineering to record it from day one, even if it is read by hand. An analytics tool and dashboards wait.
- **Often forgotten:** Recording from the first day, since history cannot be rebuilt. Your own team's and test accounts' activity inflating the numbers. Consent and privacy law for tracking. A metric that can be improved without the goal being served. The baseline, measured before release rather than recalled after.
- **Becomes:** A sharper Measured by and Today in each goal; a proof quality requirement or a requirement to record named events; an open question for engineering on where each count comes from; a privacy constraint; a non-goal for dashboards.
