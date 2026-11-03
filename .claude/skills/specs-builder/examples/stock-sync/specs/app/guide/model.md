# The data: the specification as a graph

The specification is a graph: nodes, each saying one thing, and links between them. It is kept as text, one file for each
node, in `data/`, and `app/spec.py` reads those files whenever it is asked. A row of a table in a node's file is a node of
its own where its kind has an ID: a requirement's criterion, a screen's element, a component's part, an entity's state.

What is said is in the nodes. What is drawn is in `prototypes/`, and the nodes say where: a screen's prototype carries one
`data-el` for each element, a component's drawing one `data-part` for each part and one `data-variant` for each variant.
Words are the same in any technology; the drawings are a picture to build to, never code to copy.

## How an agent reads it

With `python app/spec.py`: `overview` first, then `plan`, then for each slice `unit`, `open`, `tests` and `look`, as
`guide/build.md` says and `guide/query.md` lists. `spec.py kinds [kind]` says what each kind holds, by the names the
operations take. A program that reads JSON rather than asking takes `spec.py export --model`:

1. `export/model/index.json`: every node, its kind, its name and its file, and the slices.
2. `export/model/nodes/<ID>.json`: all of one node, and its links both ways.
3. `export/model/edges.tsv`: every link, `src`, `rel`, `dst`.
4. `export/model/stands.tsv`: what stands on what, `node`, `rel`, `on`: what turns stale when `on` changes.
5. `export/model/openapi.json`: the API's description, where there is one.

## The kinds

| Kind | ID | Where | Is | Fields and texts |
|---|---|---|---|---|
| document | `document` | `data/document.md` | the product as a whole: what is wrong today, who it is for, what is left out, how it is released | name, kind, status, without (the parts kept out on purpose: domain, api), summary, problem, users, journey, non-goals, assumptions, boundary, interface, release plan, more |
| goal | `G` | `data/goals/` | an outcome the product is for, with what is counted | name, measured by, today, target, about |
| requirement | `R` | `data/requirements/` | behaviour the product must have, with the tests it must pass | name, priority, from, statement, why, details |
| criterion | `<parent>.` | a row of a requirement | one acceptance criterion of a requirement, R7.3: a test it must pass, kept under its ID for good | says |
| quality | `Y` | `data/qualities/` | one quality the product must have -- speed, accessibility -- and the requirement that holds it, or why none does | name, status, says |
| constraint | `L` | `data/constraints/` | what is fixed from outside the product, and so not the product's to choose | name, says |
| decision | `D` | `data/decisions/` | a choice made, why, and what was turned down | name, decision, because, instead |
| question | `Q` | `data/questions/` | what is not settled, why it matters, and who answers it | name, answers, question, why |
| addition | `AD` | `data/additions/` | what was added in the skill's own judgement -- a case, a row, a requirement the user did not give -- unsettled until the user confirms it | name, says, why |
| risk | `K` | `data/risks/` | what could go wrong for the product, how likely, and what is done about it | name, of, likelihood, risk, if, mitigation |
| term | `T` | `data/terms/` | a word of the product's, what it means, and what it names | name, also, means |
| rule | `B` | `data/rules/` | what must always hold, written once | name, says, except |
| role | `U` | `data/roles/` | who uses the product, and what each may do | name, who, about |
| entity | `N` | `data/entities/` | a thing the product keeps, with what each of its fields means and the states it moves through | name, about, fields, lifecycle |
| state | `<parent>.` | a row of a entity | one state of an entity, N2.open: what it means, and where it may move | means |
| screen | `SC` | `data/screens/` | one view of the product, with its elements and the prototype that draws it | name, kind, address, who, reached by, from, purpose, data, states, transitions, variants, layout |
| element | `<parent>.` | a row of a screen | one element of a screen, SC3.9: what it shows and does, and what it stands on | name, is, does, states, heard as |
| component | `C` | `data/components/` | one piece of the interface, drawn once and used on every screen that has it | name, from, purpose, rules, variants |
| part | `<parent>.` | a row of a component | one part of a component, C3.1: what it shows and does | name, is, does, states, heard as |
| foundation | `FD` | `data/foundations/` | one part of the design's foundations -- colours, type, spacing, motion -- and its rules | name, says |
| flow | `F` | `data/flows/` | one way through the product, told as the one who goes through it, step by step | name, user, trigger, purpose, diagram, steps, goes wrong |
| endpoint | `A` | `data/endpoints/` | one thing the product answers when it is called: what it takes, what it answers, how it fails | name, kind, surface, purpose, who may call, takes, answers, fails, limits, example |
| source | `S` | `data/sources/` | material the specification was read from, its role, and where it is | name, role, where, version, about, coverage |
| finding | `E` | `data/findings/` | one thing read in a source, with its quote and how it was seen | where, lens, seen, became in, found, quote, limits |
| contradiction | `X` | `data/contradictions/` | where findings disagree, and how it was settled | settled, became in, says |

## The links

| Relation | From | To | Read back as |
|---|---|---|---|
| serves | requirement, flow | goal | served by |
| enforces | requirement | rule | enforced by |
| depends on | requirement | requirement | needed by |
| refines | requirement | requirement | refined by |
| conflicts with | requirement | requirement | conflicts with |
| governs | rule | entity | governed by |
| has | requirement, screen, component, entity | criterion, element, part, state | part of |
| may | role | requirement, flow, endpoint, screen | may be done by |
| may not | role | requirement, flow, endpoint, screen | may not be done by |
| may or may not | role | requirement, flow, endpoint, screen | not known whether done by |
| is | element, part | component | used by |
| shows | element, part, screen, endpoint | requirement | shown by |
| about | element, part, screen, endpoint, decision, question, risk, constraint | anything | spoken of by |
| asks | element, part | question | asked by |
| leads to | element, part, screen | screen | reached from |
| made of | component | component | used in |
| follows | screen, component | foundation | followed by |
| displays | screen | state | shown on |
| passes | flow | screen | passed by |
| carries | flow | requirement | carried by -- derived by the loader from the requirement IDs its Steps and When it goes wrong name; nothing to write |
| calls | flow | endpoint | called by |
| moves | state | state | moved to from |
| moves as seen in | state, screen | finding, contradiction, rule | shows a move of |
| means | term | anything | named by |
| met by | quality | requirement | meets |
| from | finding | source | read in |
| became | finding, contradiction | anything | came from |
| between | contradiction | finding | disputed in |
| adds to | addition | anything | added by |

Evidence -- the sources, the findings and the contradictions -- says where the specification came from. It is never what
is built, so the answers for building leave it out; `unit --evidence` and `trace` give it.
