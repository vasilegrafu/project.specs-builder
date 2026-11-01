# The Domain: what the product means

Beside what the product must do stands what it means: the words it uses,
the things it is about and the states each passes through, the rules it
enforces on them, and who may do what. They are the **Domain** of the
application's menu, after Requirements, and each is a node of its own: a
term `T1`, an entity `N1` with its states `N1.open`, a rule `B1`, a role
`U1`. A rule holds whether a user meets it on a screen, through an API or
in a job that runs at night: it is written once, and the requirements
that make it true are tied to it. In reverse-engineer, the meaning
archaeologist's analysis is in their shape, and the product analyst
copies, checks and names findings.

They are optional: a specification with none loads clean, and they are
offered once the requirements of anything with rules or things of its
own are written. `spec.py kinds term|entity|rule|role` says what each
holds, by the names the operations take.

## The four kinds

| Kind | Holds | Written with |
|---|---|---|
| term, `T1` | what it means; `also`, what else it is called and where; `names`, the node it names | `add term "invoice" means="..." also="bill (the manual), receipt (the code)" names=N1` |
| entity, `N1` | what it is to the user; its Fields; its States, each a row `N1.issued`; its Lifecycle | `add entity "Invoice" about="..."`, then `add-row N1 state=issued means="..."`, `add-line N1 fields ...`, `add-line N1 lifecycle ...` |
| rule, `B1` | one sentence a tester could check; `Except`; `applies to` the entities it governs | `add rule "Download once issued" says="..." applies_to=N1`, `tie R2 enforces B1` |
| role, `U1` | `who` is in it; its Actions, each `yes`, `no` or `?` on a requirement, a flow, a screen or an endpoint | `add role "accountant" who="..."`, then `tie U1 may R1 "download an issued invoice"` |

An ID is never renumbered, and one removed is never given again.

## When a thing goes in

- **A term** goes in where two sources name one thing differently --
  "Save" on the screen, `commit` in the code, "submit" in the manual --
  or where it means something a new engineer would not guess. A word
  every reader knows in its everyday sense does not. `names` is the
  entity or the requirement the term names; `also` lists each other name
  with where it is used.
- **An entity** goes in where a rule governs it, where it has a
  lifecycle, or where it is stored and shown: by the name a user would
  give it, with one or two sentences of what it is to the user. Where
  the skill added it, an addition says so, `added to` it.
- **A rule** is one sentence a tester could check -- *an invoice can be
  downloaded only once it is issued* -- that applies to an entity, may
  have exceptions, is enforced by requirements, and rests on findings
  (each finding that `became` it) or on an addition. A rule with no
  finding and no addition is not written; an exception no finding shows
  is not written either.
- **A role** is each kind of user and system actor the findings show.
  Each action is a line of its Actions -- `tie U1 may R1 "download an
  issued invoice"`, `tie U2 may not R1 ...`, `tie U3 may or may not R1
  ...` -- and a `may or may not` is what nobody knows, never a guess: a
  question asks it.

Where the specification is a part of a larger system, a thing the part
reads and never owns -- a customer, kept by the whole -- is an entity
all the same, so that every ID leads somewhere, with who owns it and
where it is defined said in its text. The document's Boundary names it,
and the part never writes it a lifecycle of its own.

## The lifecycle

An entity's states are its rows -- `| State | Means | Moves to | Seen in |`
-- so that a state is a node, `N1.issued`, which a screen can display
(`tie SC3 displays N1.issued`) and a finding can show. Its Lifecycle
table says each move:

| State | Event | Guard | Effect | Next |
|---|---|---|---|---|
| draft | issued, on a date | -- | -- | issued |
| issued | -- | -- | -- | -- |

Every state has a row; a state nothing moves has `--` for the rest. A
move goes to a state that has a row, and names its event; the guard
says only when, the effect what else happens, each `--` where there is
none. A state no screen displays is a gap for a review, not a fault: the
user never sees it, or no screen is tied to it yet.

## Rules and requirements

A requirement that makes a rule true is tied to it, `tie R2 enforces
B1`, and the rule's node shows each requirement that enforces it: the
link is written once, on the requirement, and read both ways. A rule
enforced by nothing is a gap: a requirement to write, or a rule the
specification leaves to what exists. A `must` that enforces no rule and
is shown by nothing is a gap too -- right for a quality or a thing
behind the scenes, a gap otherwise. `spec.py trace R2` reaches the rule
it enforces and the entity that rule governs; `spec.py trace B1`, the
requirements, the findings and the screens.

How well a rule stands is its `confidence`, worked out from the findings
behind it as a requirement's is: `disputed`, `corroborated`, `seen`,
`documented`, `inferred`, `added` or `stated`.

## What is not settled

A question about a rule or an entity is tied to it, `about=B1`; an
addition to it is `added to` it. The node view of the rule or the entity
says so at its top, and `spec.py open` lists it, so that nobody builds it
as agreed.
