# Asking

How questions are asked, in every mode. In write-ask they are the few
clarifying questions that follow each thing the user writes. In ask-write
they are the whole session, and the skill leads. In reverse-engineer
they are three before writing -- what the material is, as a single
choice asked alone; what is in scope, as a multiple choice over what was
found; and the why, with the number behind each goal -- and then the few
that the material could not answer.

A good question is one the user can answer in seconds and that changes
what gets built. Before asking anything, check that the document does not
already answer it.

## Choosing the format

Pick the format that fits the question, not the one used last time.

| Format | Fits | How to ask it |
|---|---|---|
| **single choice** | a decision with a few known ways to go | two to four real options, each with what it gives and what it costs; the recommended one first, with its reason; always room for an answer of their own |
| **multiple choice** | scope, and anything where several can be true: which of these are in, which have happened to you, which devices | every plausible item, so that ticking is faster than writing; say that none is an answer |
| **yes or no** | one thing that is either so or not | the question, and what each answer leads to |
| **a number or a range** | how many, how often, how long, how much | the unit, and a few ranges to pick from when a number is hard to give from memory |
| **ranking** | priorities: what comes first when not everything fits | three to five items to put in order; ask for the top one first if the list is long |
| **a scenario** | behaviour at an edge, where an abstract question gets an abstract answer | a concrete situation with real values -- "it is Friday 17:55, the payment failed twice, the customer closes the page" -- then: what should happen? Offer two or three outcomes where they are clear |
| **this or that** | a trade-off between two goods | the two ends, what each costs, and where the user stands between them |
| **an example to react to** | wording, tone, layout of information | write two or three versions of the message, label or list, and ask which is closest and what is wrong with it |
| **fill the gap** | a sentence that is nearly complete | the sentence with its gap: "A sharp move is a one-day move of ___ or more" |
| **free answer** | what only the user knows and no list can anticipate: the problem, the last time it happened, their own words | one open question, with what a useful answer contains, and no options |

Rules for all of them:

- **Say why it matters**, in one sentence, before the question: what gets
  built wrong if it is left unsaid. In engineering terms where the user
  is an engineer.
- **A decision with real trade-offs carries a recommendation**, tied to
  something the user has said, and what would change it. Where nothing
  they said favours an option, say so and say which fact would decide it.
- **A fact carries no recommendation.** Nobody can choose how many
  customers there are, or what happened to them last month.
- **Options are real.** Never pad to three; never offer a straw man.
  Include the smallest, and "not yet" wherever that is a real answer.
- **Where the environment offers a way to present choices to pick from,
  use it** for the choice formats, and write the why, and the
  recommendation with its reason, before the choices appear.

## How many at once

- **A round is one to four questions on one topic.** Related questions
  go together: the three facts about a portfolio, the four boundaries of
  one requirement. Unrelated ones do not share a round.
- **A decision that changes the shape of the product is asked alone**:
  who it is for, the main outcome, the limit, build or not.
- **In write-ask and reverse-engineer, at most five clarifying questions after
  writing**, the most deciding first, and only those whose answer would
  change what was just written. If there are none, ask none.
- **Say where things stand** after each round in ask-write: what was
  recorded, and roughly how many questions are left at the chosen depth.

## Imagining the product

In ask-write, the lists in [aspects.md](aspects.md) are the floor, not the
ceiling. Before each stretch of questions, picture this particular product
in use and ask what the picture raises. Each lens below yields questions
no general list holds; write them in the user's own terms, with their own
nouns.

| Lens | Picture | It raises |
|---|---|---|
| the first minute | someone opens it for the first time, with nothing in it | what they see, what they must do first, what they need at hand |
| an ordinary day | the main journey, done for the hundredth time | what is tedious, what they wish it remembered, what they skip |
| the worst day | the thing it depends on is down, the data is wrong, the user is in a hurry | what they see, what they can still do, who is told |
| the busiest day | ten times the usual: users, records, events at once | what slows, what is shown first, what is dropped |
| the edge of the rule | the value exactly on the threshold, the empty list, the very long name, midnight, month end | which side the boundary falls on |
| the other user | someone who does the same work differently: a newcomer, another role, another site | what must differ for them, or that they are out |
| the mistake | the user does the wrong thing: deletes, sends, pays twice | whether it can be undone, and until when |
| misuse | someone uses it for what it was not meant for, or tries to see what is not theirs | what is refused, and what they see |
| a year later | it has been used daily for a year | how much data there is, what has piled up, what nobody cleans |
| the day it ends | the user leaves, the customer cancels, the product is replaced | what happens to what they made |
| the neighbour | the other tools open on the same screen | what is copied between them, which one is right when they disagree |
| the delight | the one thing that would make them tell a colleague | whether it belongs in the first release or is a distraction |
| the competitor | what they use today, done slightly better | why they would still switch |

When a lens turns up something the catalogue of areas lacks, ask it
anyway. When it turns up something already written, do not ask it again.

## What an answer becomes

| The user says | Then |
|---|---|
| picks an option, or gives their own | it is written where it belongs; a choice gets a decision with what was turned down |
| confirms something the skill added | `confirm-added` takes the addition out; a choice among options gets a decision |
| corrects something the skill added | what it added to is changed as they said, then `confirm-added` takes the addition out |
| "you decide" | repeat the recommendation in one line and ask for a yes; only then is it theirs |
| "I don't know", to a decision | recommend the smallest option that keeps the others open |
| "I don't know", to a fact | an assumption, with the cheapest check from [checking-assumptions.md](checking-assumptions.md) |
| "why?" | explain from [concepts.md](concepts.md), in three sentences, then ask again |
| "more" on an area | open that area's entry in `areas/` and ask its questions in turn |
| "skip" or "later", or no answer | it stays an open question; move on |
| answers an open question | written where it belongs, then `answer Q3 "..."` makes it a decision and takes the question out ([finishing.md](finishing.md)) |
| something that contradicts the document | say what it contradicts and ask which stands; never blend the two |
| an answer that is a how | say so; ask what the user must be able to do or see; keep the how as an open question for engineering |
