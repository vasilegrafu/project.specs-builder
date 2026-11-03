# Checking an assumption

When a document rests on something nobody knows, the answer is in the
world, not in the session. This file holds the cheapest ways to find out,
by the risk the assumption is about. Each assumption in a document says
how it could be checked; choose from here the cheapest check that could
prove it false.

Three rules apply to every check.

- **Fix the threshold first.** Before running it, write what result
  confirms the assumption and what refutes it. A threshold chosen after
  the result is not a check.
- **Watch what people do, not what they say they would do.** "Would you
  use this?" is answered yes by nearly everyone and predicts nothing.
  What someone did last time, what they pay for now, and what they do
  when offered the thing are worth writing down.
- **Write the result into the document, whatever it shows.** A confirmed
  assumption moves into the Problem or a requirement as something known,
  with where it was learned. A refuted one changes the document, and the
  change is a row in Decisions.

## Value: will they want it?

| Check | Use when | How | Confirms or refutes | Costs |
|---|---|---|---|---|
| **problem interviews** | nobody has yet spoken to the people who are meant to have the problem | Speak to five to ten of them, one at a time. Ask about the last time it happened, what they did, what it cost, what they have tried. Do not mention the idea until the end, if at all. | confirmed when most describe the problem unprompted and have tried to solve it; refuted when they must be led to it, or have never tried anything | a week |
| **what they pay now** | the claim is that people will pay | Ask what they spend today, in money or hours, on the problem or on the alternative, and who approves that spending. | confirmed when there is a budget or a visible cost; refuted when the problem costs them nothing they notice | part of the interviews |
| **trying what exists** | something already on the market might do the job | Use the two closest existing products for a week on the real work. | refuted when one does the job; otherwise what each failed at becomes the requirements | a week, and no building |
| **a page and a sign-up** | the question is whether the promise attracts strangers | One page stating who it is for and what it does, with a way to leave an email address. Send people with the problem to it. | fix beforehand what share of visitors must sign up; compare | a few days, plus reaching the people |
| **a commitment** | interviews went well and more than warmth is needed | Ask for something that costs them: a deposit, a signed letter of intent, an introduction to their manager, an hour a week to try it. | confirmed by those who give it; "let me know when it is ready" is a no | a conversation each |
| **doing it by hand** | the product would automate something | Deliver the result to a few customers yourself, by hand, behind an email address or a form. They get the value; you learn every step. | confirmed when they keep using it and would miss it; refuted when they drift away although it works | weeks, and no building |

Questions for a problem interview, in order:

1. Tell me about the last time you had to do this. What happened?
2. What was the hardest part?
3. What did you do about it? What else have you tried?
4. What does it cost you when it goes wrong?
5. If you could change one thing about how this works, what would it be?
6. Who else is involved when this happens?
7. Is there anything I should have asked?

Do not pitch, do not ask "would you use", and do not correct them. Write
down their words, not a summary of them.

## Usability: can they use it?

| Check | Use when | How | Confirms or refutes | Costs |
|---|---|---|---|---|
| **a sketch walk-through** | the flow is new to the users | Draw the views on paper or in any drawing tool. Give one person a task from the journey and ask them to say what they would press and what they expect. Say nothing. | confirmed when most finish unaided; each place two people stop is a finding | an afternoon and five people |
| **a clickable mock-up** | the sketch passed and the detail matters | The same, with screens that link together and do nothing behind. | as above | days |
| **the person behind the curtain** | the product would do something clever | The user sees the interface; a person produces the answers by hand. | shows whether the cleverness is wanted before it is built | days |

Five people find most of the problems; the sixth finds what the first
five found.

## Feasibility: can it be built?

This is engineering's, asked as an open question for engineering. The
product side's part is to ask early, about the thing that would hurt most
if the answer were no.

| Check | Use when | How | Confirms or refutes | Costs |
|---|---|---|---|---|
| **a spike** | a requirement depends on something nobody on the team has done | Engineering spends a fixed, short time proving the one uncertain thing, and throws the code away. | the answer to the question, with what was learned | days, fixed in advance |
| **asking the owner** | it depends on someone else's system | Ask whoever owns that system what it allows, in writing. | their answer | an email |

## Viability: does it work as a business?

| Check | Use when | How | Confirms or refutes | Costs |
|---|---|---|---|---|
| **the sum on one page** | there is a price and a cost in mind | Write price times customers on one side, and the cost to build, run, sell and support on the other, each as a range with what it rests on. | refuted when even the favourable end does not cover the cost | an hour, and it exposes which numbers are guesses |
| **the price conversation** | the price is a guess | Name the price to people who have the problem and watch the reaction. Ask what they would compare it with. | confirmed by a commitment at that price; a flinch is information | part of the interviews |
| **the qualified opinion** | law, tax, a contract or a regulated field is involved | Put the specific question to someone qualified. | their written answer | their fee |
