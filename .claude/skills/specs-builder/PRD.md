# Initial requirements

What specs-builder is built to do, stated as the requirements it started
from; [DECISIONS.md](DECISIONS.md) holds what was decided and the phases. It is the
second form of the skill: the same specification -- a PRD, what the product
means, its flows, screens, prototypes and design system, for an API its
endpoints -- kept as data and shown by an application, rather than written as a
site of pages from which a graph is read. File names and
layouts below are the plan, not requirements, and may change while every
requirement stays true.

## Why

In the first form of the skill the pages were the source and the graph was read
out of them: links are written as key lines (`Serves: G2`), as IDs in named table
columns and as `data-spec-*` attributes, and a grammar of relations says
where each is stated. Reading them back is where most faults come from: a
link of the wrong kind dropped in silence or crashing the check, a misspelled
key read as prose, two sides of one relation kept in agreement by hand,
fingerprints that miss part of a field, operations that are all-or-none only
when they refuse, no locking, a cache that misses the stamps. A review of the
skill on 2026-10-25 listed 27 such items. Kept as data, most of them cannot
happen at all.

## R1. A specification is an application, not a site

A specification is a folder that holds its data and the application that
shows it. It is opened by starting the application -- `index.cmd`
on Windows, `index.sh` elsewhere -- which starts a local server and opens the
browser on it. There is no `index.html` and no pages written by a script:
every view is drawn when it is asked for, from the data as it is.

## R2. The application is built in layers, with one implementation of each

- **Data**: the model in SQLite while it is worked on, and in text files,
  one per node, which are what git sees (R3).
- **Validation**: the grammar as data -- every kind of node, every relation
  with the kinds it may join, the least and most of each, status rules,
  severities -- applied before anything is written.
- **Logic**: the operations (add, set, tie, untie, rename, remove, split,
  confirm), staleness and fingerprints, the ID counters and the IDs retired,
  the log of changes with their reasons, snapshots and what changed since.
- **API**: JSON over HTTP from a server bound to 127.0.0.1 -- read a node, a
  view, the graph around a node; post a request for a change (decision 52).
- **Presentation**: one JavaScript engine and a template per kind of view.

The command line (`spec.py`, the query tool) calls the logic directly, with
no server, so an agent works as it does now. Each change is one transaction,
all or none, and the one server process is the only writer.

## R3. The data is text in git; SQLite is built from it

Each node -- a requirement, a goal, a rule, an entity, a role, a screen, a
component, a flow, an endpoint, a question, a decision -- is one text file,
its fields and its links as fields and its prose as prose. A fresh clone
builds the database from the files; a change through the logic writes both.
Diffs stay readable and merges possible. A file that does not parse, or a
link that does not resolve, stops the load with its file and line; nothing
is reset in silence.

## R4. Prototypes keep their markup as files; their meaning is data

- `prototypes/components/C1.html`: each component's drawings, one for each of
  its variants.
- `prototypes/screens/SC3.html`: a screen's markup, free HTML and CSS, whole, so
  that it opens by itself. A piece the screens share is written once, in
  `prototypes/shared/C1.html`, and `spec.py stamp` writes it into every
  prototype that holds it (decision 69).
- `data/screens/SC3.*`: the screen and each element by its `el` -- its name,
  its kind, its component and variant, what it shows, what it is about, where
  it leads, its states.
- `product.css`, the tokens and the sample data beside them.

An element carries one anchor, `el`; what it shows and stands on is data,
validated and queried, never an attribute to parse. The load holds the two
sides to each other: every `el` in a screen has its record, every record its
`el`, and every variant its drawing. What the data holds of the drawing beyond
that -- everything shown anchored, each state listed, each link said -- is held
when the specification is agreed (decision 68).

## R5. Views over the data, with three that draw the design

The views of nodes, of lists (requirements, the gaps, the glossary), of
matrices (who may do what, what traces to what) and of the graph are a query
and a template each. Three draw the design:

- **Design system**: the foundations from the tokens -- colours with their
  contrast, type, spacing -- and each component listed, its variants drawn on
  its own page, beside where it is used, its rules and whether any of it is
  stale.
- **Screen**: what it is, where it is reached from and where it leads, its
  elements, states, variants and transitions, and what it stands on; hovering
  an element marks it in the prototype.
- **Prototype**: the screen running full size and clickable, with switches
  for state, width and sample data; links shown as numbered marks on its
  elements, each opening what it is, what it shows, what it is about and its
  criteria; a flow walked screen by screen.

## R6. A change is safe by construction

- A link to an ID that is not there, or between kinds the grammar does not
  allow, is refused when it is written.
- A relation is stated on one side; its other side is a query (a rule's
  "Enforced by", a page's "Shown on", "Tested by", "Depends on it").
- What a node means is fingerprinted from the fields its kind declares as
  meaning, its spacing made even, so a change of spacing does not make anything
  stale and a change of wording always does; each relation says which end's change makes it stale.
- A page reviewed against what it stands on keeps that stamp, its own links
  included; untying and tying again, renaming or retargeting never clears a
  stamp it did not change. Confirming shows what moved, and is recorded --
  who, when, what it was confirmed against.
- An ID is never used twice: the retired ones are kept, and one written again
  is refused.
- Cycles across nodes and the least of each relation are rules in the grammar,
  and each is a problem at its file and line.
- An agreed node may not stand on a draft one, nor carry a stale link.
- A change may carry a reason -- a decision or a question -- and `history` says it.
- A snapshot is taken only of a specification that passes, and records every
  file, so what changed covers everything.

## R7. Agents keep working through the command line

The skill's procedures -- write-ask, ask-write, reverse-engineer, UX, review,
answer, change, agree -- work as in specs-builder, through operations on the
data rather than edits of pages. An agent that builds a product asks the
query tool, as now, and takes snapshots into its code, as now.

## R8. Self-contained

Python 3.14 and its standard library only: `http.server`, `sqlite3`, `json`,
nothing to install. The skill names no other skill: what it reuses of
specs-builder -- the grammar, the writing and asking guides, the agents'
briefs, parts of the check -- is copied into it.

## R9. The files are the master; changes are managed and tracked without git

The node files are the master copy: one file per node, the pattern
docs-as-code requirements tools settled on, so a diff reads like the
specification and two people changing two nodes never meet. SQLite is
built from them and never committed.

- A change is made through the logic -- an agent's operation on the command
  line, a person's request taken up the same way (decision 52) -- validated, applied in one
  transaction, and written to the node's file in the same step; one process
  writes at a time, and the command line waits on a lock while the server
  writes.
- A file edited by hand is noticed by its fingerprint, held to the grammar
  and loaded; one with a fault is refused at its file and line, and the last
  good database stays.
- Every change is appended to `stamps/changes.jsonl` -- when, who, which
  operation, which node, each field before and after, the reason where one
  is given; a hand edit is recorded as one. Each node's History view is read
  from it.
- Git, where the folder is in one, adds per-line diffs, blame and branches;
  nothing depends on it.
