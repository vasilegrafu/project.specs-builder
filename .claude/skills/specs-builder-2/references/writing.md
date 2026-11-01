# Writing the document

How each part of the specification is written, with a weak and a strong
version, and at the end the fixed words a review reads for. Every part is
written through an operation, `python app/spec.py do ...`, never by
editing a node's file around it: `spec.py kinds <kind>` says what each
kind holds, by the names the operations take.

## Completing what the user wrote

The user writes a few sentences; the document must hold everything an
engineer needs. The skill closes that distance with its own judgement,
under one rule: **complete the behaviour, never invent a fact, and mark
what was added.**

What the skill does to the user's words without marking anything:

- puts each thing where it belongs, and says it once;
- recasts it in the section's form: a requirement in a sentence with one
  `shall`, a criterion as Given, when, then, a goal with what is counted;
- replaces a vague word by what the user evidently meant where their own
  words give it ("in a minute" for "quickly"), and asks where they do
  not;
- splits what holds two things, and names the goal each requirement
  serves;
- writes the non-goals their words imply ("only for me" is a non-goal for
  other users).

What the skill adds from its own judgement, and marks:

- the cases the user did not mention and an engineer will meet: what
  happens when it cannot be done, the boundaries of a rule, the user who
  is not allowed, the empty state;
- the usual answer of a product area that plainly applies, from
  [aspects.md](aspects.md): one sign-in method, a bin for what is
  deleted, a plain export;
- a definition a term needs before it can be tested: "a day's move is
  measured from the previous close";
- a priority or a release, where their words did not rank.

Each addition is a node of its own, an addition, `AD1` onwards, which
says what was added and is tied to what it added to -- a requirement, a
criterion, a screen, a row:

```
add addition "A failed download" says="When the PDF cannot be produced, the portal says the download failed and offers to try again" why="nothing said what happens when it fails" added_to=R3
```

Added in the same change as what it adds to, it names it by `$n`:
`add-row R3 says="Given ..."` and then `tie $2 adds to $1`, where the
addition was the second operation and the row the first. It stays,
shown on what it added to and on the Open view, until the user confirms
it -- `do confirm-added AD1`, or `confirm-added R3` for every addition to
R3 and its rows -- or corrects it, which is a change to what it added to
and then the same confirmation. A specification cannot be agreed while
one remains.

What is never added, however plausible:

- a fact about the world: how many users, what they do today, what they
  will pay, what a competitor offers, what the law requires;
- a number the user did not give: a baseline, a target, a limit, a date,
  a threshold. A missing baseline is `not measured`; any other missing
  number is asked, and until it is answered it is an open question;
- a goal. The outcome the product is for is the user's alone;
- a choice of technology.

When in doubt whether something is behaviour or fact: if it can only be
found out by looking at the world, it is a fact.

## Where the text stands, and how it is laid out

Every node is a file of its own in `data/`, by its kind's folder and its
ID -- `data/requirements/R7.md` -- with a header of `key: value` lines,
closed to keys its kind does not have, and its texts as Markdown under
the headings its kind names; the document is `data/document.md`. The
operations write them: `add` makes a node with the next free ID,
`add-row` a criterion, an element or a part, `set` a field or a text,
`tie` and `untie` a link, `remove` a node once nothing links to it. Each
change is held to the grammar whole before anything is kept, logged in
`stamps/changes.jsonl`, and refused, with nothing changed, where it would
leave a fault. An ID is never given twice: one removed is retired.

Write a paragraph one sentence to a line. It reads the same, and a later
change shows as the sentence that changed, which a person can review.

What is not settled is said where it is read. Each open question is a
node, `Q1` onwards -- `add question "<a short name>" question="..."
why="..." answers=<who> about=R3` -- tied by `about` to what it is about;
an element or a part that raises it says so in its Asks column. Each
addition is tied to what it added to. The node view of everything a
question or an addition stands on says so at its top, and the Open view
and `spec.py open` list them all; nothing is written by hand to say it.

## The sections

The document's texts are its sections; everything with an ID of its own
is a node of its kind. The first eight rows are what a specification
holds before it is agreed; the rest are written only when there is
something to put in them.

| Part | Where it lives | Holds |
|---|---|---|
| Summary | the document's text under its header, `set document summary "..."` | three sentences: what, for whom, for what outcome |
| Problem | the document's `Problem` | what goes wrong today, for whom, what it costs, how that is known |
| Users | the document's `Users` | who uses it, by role, and what they do today |
| Goals | goals, `G1` | the outcome, what is counted (`measured by`), `today`, `target` |
| Non-goals | the document's `Non-goals` | what a reader would expect and will not get, each with why |
| Requirements | requirements, `R1`, with their criteria `R1.1` | a statement with one `shall`, a priority, the goal it serves, the criteria |
| Qualities | qualities, `Y1`, one for every quality of the list below | the requirement, `status: none` and why, or `status: open` |
| Open questions | questions, `Q1` | the question, why it matters, who answers (`answers`), `about` what |
| Journey | the document's `Journey` | the main piece of work, step by step, as it is walked today |
| Interface | the document's `Interface` | each view, what the user does there, and what it shows when empty, loading and failing; left out where screens hold it |
| Constraints | constraints, `L1` | what is fixed from outside, `about` what it touches |
| Risks | risks, `K1` | what could go wrong, which of the four risks it is `of`, `If it happens`, `likelihood`, `Mitigation`, `about` what |
| Release plan | the document's `Release plan` | each release, the requirements it holds, what the user can then do |
| Assumptions | the document's `Assumptions` | what was taken as true without knowing, and how to check it |
| Additions | additions, `AD1` | what the skill added from its own judgement, `added to` what |
| Decisions | decisions, `D1` | what was chosen, `Because`, `Instead of`, `about` what |
| Sources | sources, `S1` | each piece of material, its `role`, `where` it is, its `version` |
| Glossary | terms, `T1` | words used in a sense an outsider would not guess, `also` their other names |

## Problem

The problem is what is wrong today for a particular person, before any
product exists. Say how it is known: who said it, what was counted, and
no more than that source supports. Five interviews show what five people
said, not what customers want.

- Weak: *There is no good app for tracking invoices.* (a missing product,
  not a problem)
- Strong: *Customers cannot take an invoice out of the portal, so they
  write to support: 41 of 620 tickets last quarter asked for one as a
  file.*

## Users and the journey

A user is a role, named as the people in it name it, and written from
what was seen or said: what they do, how often, what they are trying to
get done. No invented name, age or biography -- a persona nobody observed
is fiction that reads like data.

The journey is one piece of work from what starts it to what counts as
done, as numbered steps. Write it as it is walked today, including the
step that goes wrong, so that the requirements can be read against it.
Every `must` requirement should be findable on the journey; one that is
not is either a missing step or an unnecessary requirement.

## Goals

A goal is a change in the world that can be measured, not a thing
delivered. The test: could everything be built as specified and the goal
still be missed? If not, it is a requirement written as a goal. A value
nobody has measured is `not measured`, never a guess. A guard-rail goal --
the thing that must not get worse -- is a goal like any other.

- Weak: *Launch the export feature.* / *Improve satisfaction.*
- Strong: *Tickets asking for an invoice as a file fall from 14 a month to
  under 5 within a quarter of release.*

## Non-goals

Silence is read as inclusion. Write down what an engineer would otherwise
build towards: the bulk version, the admin screen, the other platform, old
data. Each carries its reason. "Not rewriting the billing system" is noise
unless someone would have assumed it.

## Requirements

Written as one change set, a file of operations, `spec.py do --file`:

```
add requirement "Cancel by reply" priority=must serves=G1 from="S2, the reply handler in the booking system's message module" statement="When a patient replies NO to a reminder, the booking system shall cancel the appointment and tell the patient it is cancelled."
add-row $1 says="Given a reminded appointment, when its patient replies NO, then the appointment shows as cancelled and the patient is sent one message saying so."
add-row $1 says="Given a reply that is neither YES nor NO, when it arrives, then the appointment stays as it was."
```

and kept as `data/requirements/R3.md`:

```
---
id: R3
name: Cancel by reply
priority: must
from: S2, the reply handler in the booking system's message module
serves: G1
---

When a patient replies NO to a reminder, the booking system shall cancel the appointment and tell the patient it is cancelled.

## Accepted when

- R3.1 Given a reminded appointment, when its patient replies NO, then the appointment shows as cancelled and the patient is sent one message saying so.
- R3.2 Given a reply that is neither YES nor NO, when it arrives, then the appointment stays as it was.
```

Each criterion carries its own ID, `R3.2`, which `add-row` gives, the
next free number of its requirement, and which never moves, so that a
test named after a criterion keeps naming it when another is put
between. A criterion taken out leaves its number retired.

A requirement states behaviour someone outside the product can observe,
in one sentence that opens with one of the opening words below and holds
one `shall`. `serves` names its goal. `enforces` names the rule of the
Domain it makes true, where the specification has one
([domain.md](domain.md)): a rule is written once, as a node of its own,
and the requirement that enforces it is tied to it, `tie R3 enforces B1`.
`depends on` names the requirements that must be in place for this one,
`refines` the broader one it makes precise, and `conflicts with` one
that cannot hold with it -- each only where there is one, never itself,
and the loader refuses a cycle; a conflict left is written to be
resolved, and the decision that resolves it says how. `from` is there
only where the requirement was taken from material, and names the
source. The tests it must pass:

- **Necessary.** It names the goal it serves. If nobody's goal needs it,
  it goes.
- **Singular.** One `shall`. "And" in the response usually hides a second
  requirement.
- **Unambiguous.** No vague word. Name the actor, the trigger and the
  response; give numbers their units and their limits.
- **Verifiable.** Someone could write a test for it without asking a
  question. Its acceptance criteria are those tests.
- **Free of design.** "Stores it in the documents table" is a design;
  "keeps it for ten years" is a requirement. A technology the user names
  goes to Constraints if it is fixed from outside, and to Open questions,
  for engineering, if it is a preference.
- **Complete with its unwanted case.** What happens when it cannot be
  done is part of it: an `If ..., then` requirement, or a criterion.

The statement stays one sentence: whatever more there is to say goes in
two texts beside it, each only where it has something to say.

- **Why**, `set R3 why "..."`: who needs it and what goes wrong without
  it, in a sentence or three, from what the user said or the material
  shows -- the document, the goal, a rule, a decision, a finding. A reason
  that only sounds right is an invented fact: where none is given, leave
  it out, or ask with a question node. Rewording it turns nothing stale.
- **Details**, `set R3 details "..."`: what it covers and what it does
  not, an example, a limit a reader would otherwise ask about. It holds
  no behaviour a tester must check: that is a criterion. A change here
  reaches what stands on it, as a change to the statement does.

The priority is the user's, never a default:

| Priority | Meaning |
|---|---|
| `must` | the goal it serves is not met without it |
| `should` | wanted, and the release still stands without it |
| `could` | taken only if it costs little |
| `wont` | asked for and deliberately left out of this work; it needs no goal and no criteria, and it says why |

If everything is `must`, nothing is ranked: ask which the release would
still ship without.

Acceptance criteria are `Given <situation>, when <action>, then <a result
that can be seen>`, one behaviour each, with real values: "an invoice of
200 lines", not "a large invoice". Between them a requirement's criteria
cover the ordinary case, each boundary the statement names (the first,
the last, zero, the limit), the case where it cannot be done, and the
case where the user is not allowed; then what a builder would otherwise
have to guess: a second attempt, two people at once, what happens to what
was already there. Go through those for each requirement rather than
stopping at the first two: a requirement with one or two criteria is
usually one with cases left out. A case the user did not state is an
addition until confirmed. The result is something a tester observes --
"the appointment shows as confirmed" -- not an internal fact.

## Quality requirements

There is a quality node for every quality in the list below, named by
it, so that nothing is left to be assumed. Each holds one of three
things:

- the requirement, with the number it is held to and the condition the
  number holds under, `status: met`, and `met by` the requirements that
  hold it;
- `status: none` and the reason, which is as useful to an engineer as a
  number: "as the portal's today" tells them not to build for more;
- `status: open`, where nobody has said yet. It is counted among what is
  open, and keeps the specification from being agreed.

- Weak: *The page must load fast.*
- Strong: *The PDF is delivered within 10 seconds for an invoice of up to
  200 lines.*

## Interface

A view is what the user sees and can do at one point, named as the users
would name it. It is not a layout: how it looks is the designer's. Each
row says what the view shows with nothing yet, while waiting, and when it
fails or refuses, with `n/a:` and the reason where a state cannot occur.
Wording the user reads -- a message, a label that carries meaning -- is
written out, because someone will otherwise invent it at the keyboard.

This section is the short form, for a specification with no screens.
Where screens are written ([ux.md](ux.md)), each view becomes a screen
with its states, and this section is emptied, `set document interface
""`: the states live in one place.

## Constraints

A constraint is fixed from outside the product decision: a law, a
contract, a system that already exists, a date, a budget. A preference for
a technology is not a constraint; it is an open question for engineering.
Each is a node, `L1` onwards, kept for good, so that a requirement, a
question or a decision can name it. Its `about` names by ID what it
touches -- the entity, the requirement -- and is the one place that ties
it: an ID named in its words alone ties nothing.

## Release plan

A release is a version that could be used on its own. The first is the
thinnest path across the whole journey -- every step present, each as
simple as it can be -- so that it can be put in front of a user and the
least certain assumption tested early. A release cut by layer ("the data
model", "the screens") releases nothing. Where the section is present,
every `must` requirement is held by some release.

## Assumptions and open questions

An **assumption** is something the document takes to be true without
knowing; write the cheapest way it could be found false, from
[checking-assumptions.md](checking-assumptions.md). An **addition** is the other kind: something the skill wrote from its own
judgement to complete the document, waiting for the user to confirm or
correct it. An **open question** is something nobody has answered; say why
it matters and who answers. A question that what exists can answer --
the code, the running application, a document in reach -- is the skill's
own to find out before anyone is asked: who answers is `investigate:`
and what to read or to try, as `investigate: try a 0 in Amount on V3`.
It is answered, and goes, before the specification is agreed.
What the product side wants engineering to tell it -- can this be done,
within this time, with that system -- is an open question for
engineering, never a requirement.

## Risks

A **risk** is known and still dangerous: something that could make the
work fail or cost more than planned, which of the four risks it is of
-- value, usability, feasibility, viability -- what happens if it does,
how likely it is, and what is done about it. It is not an assumption,
which is taken as true and waits for its check, and not an open
question, which waits for an answer: a risk has been answered, with its
mitigation. One with none yet is open: the Open view lists it, and it
keeps the specification from being agreed until it has one, or becomes an assumption with its
check or an open question. A risk is the user's: the skill asks what
could go wrong and what would be done about it, and never writes one
from its own judgement, because the material never says what might
fail.

## Decisions

One decision per choice that someone might otherwise reopen: what was
chosen, `Because`, and `Instead of` what was turned down. The last is the
one that saves the argument later. Where two sources disagreed, the user
chose, and the decision says what lost. A decision is a node, `D1`
onwards, tied by `about` to what it touches -- the one place that ties
it, as it is for a question, a risk and a constraint -- so that `spec.py
impact D3` says what rests on it, `set D3 because "..."` changes it
where it stands, and `tie D3 about N2` adds to what it touches. A
question answered becomes one by `answer`, [finishing.md](finishing.md).

## Sources

Where a specification was written from material -- code, documents, a
running application, screenshots, another product -- each piece is a
source, `S1`: what it is, `where` it can be found again, its `role` from
the list below, and its `version`. A requirement taken from material
carries a `from` naming the source and the place in it; a requirement
the user stated has none. How each kind of material is read, and what
each role allows, comes with the reverse-engineer mode (phase 5b).

## The fixed words

A review reads for the words below; the material roles, the qualities
and the vague and technology words are in the grammar too, as data, so
that `spec.py open` notes a vague word where it stands. A word is changed
in both places, `app/grammar.json` under `words` and here.

### Material roles

What a piece of material is to this product. The user gives it.

| Role | The material is |
|---|---|
| `rebuild` | the product as it is, to be built again |
| `extend` | the product that exists, to be changed or added to |
| `example` | someone else's product, or an earlier one, to take ideas from |
| `intent` | a description of what is wanted |
| `evidence` | something that shows the problem |

### Opening words

A requirement's sentence opens with one of these.

| Opens with | When | Form |
|---|---|---|
| `The` | always true | The <product> shall ... |
| `When` | something happens | When <trigger>, the <product> shall ... |
| `While` | a condition holds | While <state>, the <product> shall ... |
| `Where` | only where a feature applies | Where <feature>, the <product> shall ... |
| `If` | something goes wrong | If <condition>, then the <product> shall ... |

### Qualities

Every one has a quality node in a specification.

| Quality | Asks | Its requirement carries |
|---|---|---|
| `speed` | how long may the user wait at the slowest step, under what load | a number |
| `capacity` | how many users, records and requests, now and in a year | a number |
| `availability` | when must it work, and how long may it be down | a number |
| `security` | who may do and see what, and what must it withstand | a rule |
| `privacy` | what is held about a person, on what ground, for how long | a rule |
| `accessibility` | who must be able to use it, to what standard | a rule, or a named standard |
| `devices` | on what must it run, and alongside what | a list |
| `languages` | which languages, time zones, currencies and formats | a list |
| `proof` | what must be provable afterwards, to whom, for how long | a rule |

### Vague words

A requirement, an acceptance criterion and a quality requirement may not
hold these: each lets two readers build two things.

| Word | Say instead |
|---|---|
| `fast`, `quick`, `quickly`, `slow`, `instant`, `instantly`, `immediately`, `real-time`, `responsive`, `performant`, `efficient` | a time, and the load it holds under |
| `easy`, `easily`, `simple`, `simply`, `intuitive`, `user-friendly`, `seamless`, `smooth`, `clean`, `modern` | what the user can do, in how many steps, without what help |
| `robust`, `reliable`, `stable`, `resilient` | the failure, and what the product does when it happens |
| `scalable`, `flexible`, `extensible`, `configurable` | the number it must reach, or what must be changeable and by whom |
| `secure`, `securely`, `safe`, `safely` | who may not do what, or the attack it withstands |
| `appropriate`, `reasonable`, `adequate`, `sufficient`, `relevant`, `suitable`, `necessary` | the rule that decides |
| `usually`, `normally`, `generally`, `typically`, `often`, `sometimes` | the condition under which it does, and what happens otherwise |
| `some`, `several`, `many`, `few`, `various` | a number or a range |
| `as needed`, `if needed`, `if possible`, `where possible`, `as appropriate`, `where applicable`, `when necessary` | the condition, or drop the clause |
| `etc`, `and so on`, `and/or`, `including but not limited to` | the whole list |
| `tbd`, `todo`, `to be decided`, `to be defined` | an open question, with who answers it |

### Allowed phrases

These hold a vague word and are not vague: they ask for a count or
compare one, and the count itself is what the sentence is about. They
are skipped.

| Phrase |
|---|
| `how many`, `as many`, `how few`, `as few`, `how often`, `as often` |

### Technology words

A requirement that holds one of these may be saying how, not what. It is
noted, never refused: move the choice to Constraints
with what fixes it, ask it as an open question for engineering, or leave
it where the word is the user's own.

| Word |
|---|
| `database`, `table`, `column`, `endpoint`, `microservice`, `queue`, `cache`, `class`, `framework`, `library`, `SQL`, `REST` |
