# Initial requirements

What specs-builder-2 is being built to do, stated as the requirements it
starts from, with the decisions taken so far and those still open. It is the
next form of what specs-builder makes: the same specification -- a PRD, what
the product means, its flows, screens, prototypes and design system, for an
API its endpoints -- kept as data and shown by an application, rather than
written as a site of pages from which a graph is read. File names and
layouts below are the plan, not requirements, and may change while every
requirement stays true.

## Why

In specs-builder the pages are the source and the graph is read out of
them: links are written as key lines (`Serves: G2`), as IDs in named table
columns and as `data-spec-*` attributes, and a grammar of 34 relations says
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
  view, the graph around a node; post a change set, with a dry run.
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

- `prototypes/components/C1.html`: each component's markup once, with its
  variants, its states and the slots for its words.
- `prototypes/screens/SC3.html`: a screen's layout, free HTML and CSS, made of
  component instances -- `<c-button el="14" variant="primary">Add to cart</c-button>`
  -- that the engine expands; it does not copy their markup.
- `data/screens/SC3.*`: the screen and each element by its `el` -- its name,
  its kind, its component and variant, what it shows, what it is about, where
  it leads, its states.
- `product.css`, the tokens and the sample data beside them.

An element carries one anchor, `el`; what it shows and stands on is data,
validated and queried, never an attribute to parse. The load holds the two
sides to each other: every `el` in a screen has its record, every record its
`el`, and every `<c-…>` and variant is a declared component.

## R5. Views over the data, with three that draw the design

The views of nodes, of lists (requirements, the gaps, the glossary), of
matrices (who may do what, what traces to what) and of the graph are a query
and a template each. Three draw the design:

- **Design system**: the foundations from the tokens -- colours with their
  contrast, type, spacing -- and each component drawn live in every variant
  and state, light and dark, at each width, beside where it is used, its
  rules and whether any of it is stale.
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
  meaning, normalised, so a typo does not make anything stale and a change of
  meaning always does; each relation says which end's change makes it stale.
- A page reviewed against what it stands on keeps that stamp, its own links
  included; untying and tying again, renaming or retargeting never clears a
  stamp it did not change. Confirming shows what moved, and is recorded --
  who, when, what it was confirmed against.
- An ID is never used twice: the retired ones are kept, and one written again
  is refused.
- Cycles across nodes, nodes nothing reaches, and the least of each relation
  are rules in the grammar, each with its severity; an exemption carries its
  reason and is still listed.
- An agreed node may not stand on a draft one, nor carry a stale link.
- A change may carry a reason -- a decision or a question -- and what changed
  since a snapshot is grouped by it.
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
  line, a person's form in the application -- validated, applied in one
  transaction, and written to the node's file in the same step; one process
  writes at a time, and the command line waits on a lock while the server
  writes.
- A file edited by hand is noticed by its fingerprint, held to the grammar
  and loaded; one with a fault is refused at its file and line, and the last
  good database stays.
- Every change is appended to `stamps/changes.jsonl` -- when, who, which
  operation, which node, each field before and after, the reason where one
  is given; a hand edit is recorded as one. Each node's History view is read
  from it, and `changed` says why each thing moved.
- Git, where the folder is in one, adds per-line diffs, blame and branches;
  nothing depends on it.

## Decided

O1-O5 were the open questions; the user took each as recommended.


| # | Decision | Taken |
|---|---|---|
| 1 | A specification is an application over a database of its model, not a site of pages | 2026-10-25 |
| 2 | Layers: data, validation, logic, API, HTML and JavaScript; a local Python server serves the engine | 2026-10-25 |
| 3 | Started by `index.cmd` (and `index.sh`), which runs the server and opens the browser; no `index.html` | 2026-10-25 |
| 4 | Prototypes: components' markup once, screens' layout as component instances with an `el` anchor, meaning and links as data | 2026-10-25 |
| 5 | A new skill, specs-builder-2, beside specs-builder, used only when named until it replaces it | 2026-10-25 |
| 6 | Its target is `targets/novalife-2/`, filled by migrating `targets/novalife/` | 2026-10-25 |
| 7 | O1: the application's code is copied into each specification, as `tools/` is now, so a folder works alone and keeps the version it was made with | 2026-10-25 |
| 8 | O2: whoever has no Python gets an export on demand -- a PDF or one HTML report -- made with rich-content when it is to be sent | 2026-10-25 |
| 9 | O3: a node's file is Markdown with a strict header of `key: value` lines, closed to unknown keys; the standard library reads it | 2026-10-25 |
| 10 | O4: editing in the browser comes after the read-only views, as a phase of its own | 2026-10-25 |
| 11 | O5: once it replaces specs-builder, it takes over the name and the old skill is retired | 2026-10-25 |
| 12 | The node files stay the master copy and SQLite is built from them; a git-friendly text database of one file per record, rather than SQLite committed with a diff driver (no merges), one JSON line per row (prose escaped), or Dolt (a program to install, versioning beside git) | 2026-10-25 |
| 13 | Phase 5 in two: 5a, the modes that write and change by hand -- write-ask, ask-write, the UX, the endpoints, review, answer, change, agree -- with the operations and commands they need and the guides copied in; 5b, reverse-engineer, with the agents, the reading scripts and the evidence's folder | 2026-10-25 |
| 14 | What the skill adds from its own judgement is a node of its own, an addition `AD1`, tied by `adds to` to what it completes, a row too, rather than a header key on the node, which a row has not; confirmed, it is taken out and its ID retired | 2026-10-25 |
| 15 | An open question is settled by one operation, `answer`, which makes a decision of it, moves every link to the question onto the decision and removes the question -- refused while a text still names it -- rather than a change set written by hand | 2026-10-25 |
| 16 | An agent hands back what it found in the staging file it writes in specs-builder -- findings, coverage, facets, disagreements, report -- which `spec.py merge` judges whole and makes into operations applied as one change, rather than a change set written by the agent | 2026-10-25 |
| 17 | What is not nodes of the evidence -- captures, each agent's report, the analyses, the scout's report -- is Markdown in `evidence/` beside `data/`, shown by the application; what was read of each source is a Coverage table on the source, each line with the print of its part | 2026-10-25 |
| 19 | Editing in the browser covers all the command line does -- fields, texts, tables, rows, links, nodes made and removed, answers, confirmations, agreeing -- each form making the same operations; prototype markup stays written by hand | 2026-10-25 |
| 20 | A browser edit carries a name, asked once and kept in that browser, logged as `--who` is; each form carries the version of the node it was drawn from, and a change since refuses it | 2026-10-25 |
| 21 | The export is one self-contained HTML file written by the application with the standard library, `spec.py export`, so the skill names no other skill (R8); a PDF to send is made from it outside the skill | 2026-10-25 |
| 22 | The application's parts in one order everywhere -- the menu, the overview and the export: Document, Evidence, Decisions, Requirements, Domain, API, UX, Prototype; the Prototype a gallery of every screen by the flows that pass it, then the screens in no flow, and in the export each screen drawn once | 2026-10-25 |
| 23 | The bar in two rows: the name with the document's kind and status, then search, Help, the appearance and Edit; below, the parts, each opening a panel -- a rail with what the part holds and its links, then a card per kind with its count and its first five -- in place of a page per part; search over every node and row from the bar; Help a view of its own; the appearance System, Light or Dark, kept in the browser and in the export | 2026-10-25 |
| 24 | Decision 23 made plainer, the panels too big: each part opens a short menu of its kinds with their counts, and its own pages; the Prototype no menu, but the prototype itself as specs-builder showed it -- a toolbar (view, marks, screen, state or variant, width), the screen full size, an inspector on the element picked, fed by the runtime's messages; the runtime reading `data-el` and `data-part` as handles and marking nothing unless asked; the brand the name alone | 2026-10-26 |
| 25 | A pause over an ID's link opens its card, as in specs-builder: its kind, its name, a sentence or two and the facts that place it, each kind's card listed in the grammar (`"card"`), and whether anything about it is unsettled or stale; the card's Preview the application itself in a popup in the middle of the screen, on the node's page without the bar, the whole screen on a phone; no card on a touch screen, and none in the export for now; an ID's link no tooltip of its own, the card in its place; each kind in a part's menu with the letters its IDs begin with, Goals (G); the scrollbars thin | 2026-10-27 |
| 26 | A part's pages have its tree down the left, as specs-builder had: the part's name at its head, leading to a page of everything the part holds, each node named whole; each kind with its letters and count, folding open to its nodes, the kind in view open; the part's own pages below; the node open marked; the page beside it the rest of the width, nothing on its right; under 1024px a button opening it as a drawer; none on the overview, Help, the document's pages, the prototype tool or the preview; a node's name in it cut after eight words, an entry cut shown whole after a pause; its edge dragged to a width kept for each part, its « folding it to a rail kept for all; a part's name in the bar, and the first entry of its menu, leading to the part's page. A card kept within the window, the preview's small frame too; the scrollbars narrower and plainer to see, the prototype's as well | 2026-10-27 |
| 27 | The look is the Quiet workbench, from a review of both appearances: neutral surfaces in steps (the page, a panel, raised for what floats, sunken for a hover -- in the dark a hover lifts), text in three steps, one accent (indigo) kept for what is clicked or chosen; a kind's colour is its part's, the letters on an ID telling the kinds of one part apart, amber for what is open and red for trouble, never for a priority; one scale each for type and corners; prose at a reading measure, out of its box, lists and tables in theirs; the export in the same neutrals; the selftest holding every text colour at 4.5:1 or more on the page and a panel, in both appearances | 2026-10-27 |
| 28 | A flow has its diagram, drawn by Mermaid above its steps: the one its Diagram section holds, written in Mermaid, or else one made from its steps -- each in order, a step beginning If and what goes wrong to the side, the flows it hands over to -- in the application's look, a box named by an ID opening it. Mermaid (MIT) is fetched from the CDN at one exact version, 11.9.0, not kept in the repository; without a connection the diagram's text is shown. The section carries no meaning, so a diagram changed turns nothing stale; the six examples have their diagrams back from the specs they were imported from; the export shows the diagram's text | 2026-10-27 |
| 29 | A foundation's tables have a column of what each row looks like, drawn from the row's own values where they can be -- a colour's swatch and its contrast, a text style's sample at its size, weight, line height and colour, the spacing scale, a control's padding and heights, corners, borders, shadows, contrast pairs, the focus ring, the signs of an icon set -- read in the ways the examples and novalife-2 write them; a rule in words stays as it is. A part's menu no longer begins with Everything in: a click on the part opens its page | 2026-10-27 |
| 30 | Every flow is told as a user story, from what it holds -- as its user, I want to do what it is named, so that the goals it serves; a job, started by its trigger -- with every requirement its steps name, its priority, how well it is backed and its criteria: what a team plans from. One implementation, `finish.story`, read by the application (`/api/story`), the export and `spec.py story`; `ready` holds the specification while a flow's story cannot be told; the skill's writing of flows (references/ux.md, the usage archaeologist, reverse-engineering's step 6) names a flow as what its user does and ends each step with the requirement it carries | 2026-10-28 |
| 31 | A change made in the application is tried first, written nowhere: what it would turn stale -- each node standing on what it changes, and the wave after, from `impact` -- is said where its form is before it is saved, with Save anyway and Cancel; a change that turns nothing stale is saved at once, and says so. The dry run is the logic's own, so the warning is exactly what the save would do | 2026-10-28 |
| 32 | Whoever builds asks back through the specification, never guessing and never editing it: `spec.py ask "..." --about R4 --by <who>` writes the question into `inbox.md`, beside the data and in git, never into the data; the keeper sees it first under What is open, and makes it an open question tied to what it is about (`inbox --raise`, or Make it a question in the application) or closes it once the specification answers it; `ready` holds and `verify` says it while any waits; numbers are never given twice | 2026-10-29 |
| 33 | How well a requirement or a rule stands is worked out whenever the data is read (`load.standing`), from the findings that became it or a row of it, and is never written: `confidence` left the grammar's fields and the files gave it up, and a file that still says it is refused. The words and their order are the first skill's; the 127 words the examples held came out the same. What is open lists those documented only beside those on weak ground, rules with requirements; neither holds an agreement | 2026-10-31 |
| 34 | What the code carries is read from the code (`build.coverage`, `spec.py coverage`, What is built): a test names the criterion it proves, `R4.2` or `R4_2`, and the requirement is covered criterion by criterion, not by being named once; `coverage` exits 1 while a criterion of a `must` or `should` has no test, and says what the code names that the specification has not. It reads names and says so: never that a test passes. Only files of a language of code are opened; tests are known by the usual places and by CartTests.cs and Shop.Tests/; the specification's own folder is left out should the code hold it. A snapshot leaves where the code is in `stamps/target.json`, so `coverage`, `impact` and `trace` need not be told | 2026-10-31 |
| 35 | Along a page (`web/aids.js`): an outline of its headings where it has three or more, beside it from 1400px and above it under that; and on a node's page, small icon links to the node before and after it in the order of the tree, at its top beside the breadcrumb and again at its foot, the ID on the button and the name on a pause | 2026-10-31 |
| 36 | Every page prints from a printer in the bar, which opens it alone on a sheet of A4 in a tab of its own (`?print=1`), shown first as it will come out, always light and never to be edited, and Print there sends it on. On paper, from there or by the browser's own print: A4 with margins of its own (`@page`), so that the padding is no setting of the browser's; a foot saying what the page is and which sheet of how many; rows free to split so that no sheet is left half empty; a flow's diagram whole on one sheet, in the page's colours by the print stylesheet since it is drawn ahead; a screen across the whole 174mm of the sheet at its own width, running on from sheet to sheet. A frame is one solid block to a printer, cut where the sheet ends, so a long screen is one frame to a sheet, each in a box no taller than the sheet, the page in it moved and never scrolled so that what sticks to its top does not come again, and each cut made above whatever it would go through. The scale is A4's and never the window's. The prototype's sheet is the screen alone, in the state it is shown in. The sheet shows one long page, not each sheet apart: real pages on screen would need Paged.js, and the print preview shows the breaks | 2026-10-31 |
| 37 | Every screen drawn (`#/prototypes`) is written: its route, styles and `/api/prototypes` stood since 2026-10-26 with no view behind them, so the overview's link and the UX menu's ended in an error. The selftest now holds that every view a route opens is written | 2026-10-31 |
| 38 | The export shows what the application shows, by the application's own code: `web/card.js` and `web/flowmap.js` run in it over what the file holds as data (every ID's card, its name, each flow's words), so the two cannot differ, with the application's colours and its rules for a card and a diagram. A pause over an ID opens its card, with no Preview since there is no application behind it; each flow has its diagram above its steps, made from them where it holds none. Mermaid alone is not in the file: it comes from the CDN when the file is opened, and without a connection a flow shows its diagram's text | 2026-10-31 |
| 39 | An Export button in the bar, beside the printer: the same file `spec.py export` writes, written to `export/` and handed to the browser to keep (`POST /api/export`, behind the same origin check as a change, since it writes); a specification that does not load is refused, and the button says so | 2026-10-31 |
| 40 | Three documents for people, beside the session's SKILL.md: README.md, what it is and how to start; SETUP.md, installing it, checking it and what goes wrong; USER-MANUAL.md, using it. They are held to what is true: the selftest runs the manual's worked example, command by command, on a new specification, and holds every command and operation the documents name to the command line, and every link in them to a file there is | 2026-10-31 |
| 41 | A Graph page beside the Prototype draws every node and link, each kind folded to a bubble with its count until it is opened to a box of its nodes. Drawn with D3 (ISC) from the CDN at one exact version: the application already drew its graph around a node as SVG, so the page shares its colours, its fading and its links, and the appearance and printing need nothing of their own. Cytoscape.js was the other choice, and has compound nodes ready; ELK was refused for its licence. What a node holds is counted as that node, 201 nodes and 763 pairs of the shop's 541 and 1,570, and only the kinds are laid out, the nodes in ID order in their box, so opening every kind took 82 ms. The export leaves it out | 2026-10-31 |
| 42 | A Matrix page before the Graph reads the links one at a time: a grid of the links between kinds, an empty cell a gap, beside a tree of every node; a node's links by sort, both ways; a link told whole, with its file and line and what goes stale. Built for a specification far larger than any yet: the page never holds it. `app/matrix.py` answers a small part at a time from the database, the tree draws only the rows in view and fetches 200 at a time, the links between kinds are written to a table of their own in ID order as the database is built, Find asks the database, and the application's look at every file goes to one side and no oftener than every two seconds. `tests/scale.py` writes a real specification of 54,000 nodes and times each question. No library, so it needs no connection. The export leaves it out | 2026-11-01 |
| 43 | The Matrix turned from a browser into a tool for review: the tree narrows to what is stale, unlinked or has an open question; a node's or a cell's links narrow to a few words, asked of the server for the page holds only part of them; a node's links group by sort or by the kind at their far end; the grid's heads open their kinds and it marks cells holding stale links; and a path gives the shortest chain between two nodes, by links a change passes along where there is one, for that says why one bears on the other. Flows carry no stored link to requirements (the user left that out, 2026-11-01), so a path reaches a requirement from a flow through a screen | 2026-11-01 |
| 44 | The Graph holds only what it shows, for a picture of everything in a large specification is slow and unreadable alike. The map opens from the counts between kinds, and a kind opens to its 60 most linked nodes, a tile doubling that; 9.4 MB fell to what is in view on 54,000 nodes. Focus takes the place of the graph around a node: one node, what it is linked to by kind, a click spreading a node's own links. Impact is what stands on a node, a step at a time. Layers runs from goals to what builds them. All SVG with D3 as before: canvas or WebGL would draw more, and more was not what the reader lacked | 2026-11-01 |
| 45 | Layers tells the truth at any size. Measured on 54,000 nodes, 24 of each kind drawn as nodes was fast and said little: a sample, its lines sparse. So a kind is a block and the links between kinds are bands, which hold everything; a block or a band opens to nodes, the wheel walks a kind 24 rows at a time, a column can be hidden, and `#/graph/layers:R4` holds only what connects to one node, going on in one direction each way so that a trace does not turn back through everything. A specification of 150 nodes or fewer in its layers opens on its nodes | 2026-11-01 |
| 46 | An ID's card opens on a right click everywhere, the export too, for a pause opened cards no one asked for as a pointer crossed a page; the card's Open in another tab stands for the browser's menu it replaces. The Graph has two scopes, all of it (Map, Layers) and one selected node (Around, Layers, Impact), the node staying selected from picture to picture, and its Layers go one step out by default, two, or all the way. Instructions on the page went: counts stay, and an icon says what it does on a pause | 2026-11-01 |
| 47 | Cards cascade, for a specification is read by following links without losing the place: a right click on an ID in a card opens another beside it, one from an earlier card replaces what came after it, a node already open flashes so that a chain cannot go round, a pin keeps a card from page to page, six stand open and older ones fold to a strip. Each card lists the node's links by kind, asked when it opens, so that any node is reached from any page. A scroll no longer closes a card | 2026-11-01 |
| 48 | Layers stands in the top menu's order, goals, requirements, domain, endpoints, flows, screens, components, so that a reader finds the same things in the same order on every page. Only the columns moved: a trace keeps its own way from why to what makes it, for following the menu's order instead would stop it reaching a flow from a screen, and each node reaches what it did | 2026-11-01 |
| 49 | A card's foot holds its ways out in two rows, here and in another tab, the second marked with a small arrow, so that a node reaches the Graph and the Matrix from where the reader stands. A finger held on an ID opens its card, by pointer events, for an iPhone or iPad says no contextmenu and left touch without cards; one press opens one card where Android says both, and a card's buttons grow where nothing hovers | 2026-11-01 |
| 50 | Layers of a node puts the links first, for its lines were thin, faint and crossing. Rows stand beside what they link to, only the links the trace walked are drawn, the node's own the strongest, and the rest wait for a pause on a node. On the shop example that cut crossings by about half or more; columns wrapped to half their height did not, and were left out. The Graph's bar is a toolbar to look at: as low as the menu's row, a darker tray, and its icons in boxes | 2026-11-01 |
| 51 | A very large specification opens at once. Measured on 54,000 nodes, the Graph was fast and what stood round it was not: the first page took 12 s, each page 1 s and a card 365 ms. The files are looked at by folder, 15 ms where asking each file took 220, still before each answer, so that an edit made elsewhere shows on the next page; every node's names are asked only when the data has changed, by the `version` the summary carries; and the menu does its checks once, from what the server holds | 2026-11-01 |
| 52 | The application reads; changes go through Claude Code. Edit mode saved one node and marked what stood on it stale, and stopped there: what follows takes judgement, and it could never touch a screen. Claude makes the change, goes through what stands on it, nodes and screens, and shows what it would adjust first, by the same `spec.py` operations and checks. Edit mode, its forms and `POST /api/changes` went (this replaces decisions 19 and 20 in the application; `logic.apply(expect=)` stays). **Request a change**, on a node's page or card, keeps those with only a browser in it: it waits in `inbox.md`, beside the data and never in it, and holds `ready` like a question asked back | 2026-11-01 |
| 53 | A requirement keeps its one testable sentence, for a longer one is harder to test and hides a second requirement, and gains two optional texts: Why, who needs it and what goes wrong without it, which turns nothing stale; and Details, what it covers and what it does not, which does. Criteria go through more cases. A reason nobody gave is left out or asked: it is a fact like any other | 2026-11-01 |
| 54 | A part of the bar is two controls: its word opens its page and a small arrow opens its menu, the same with a mouse, by touch and in the drawer. A menu opening on a hover got in the way of what was under it, and on a touch screen the word could not reach its page at all. Nothing opens on a hover now | 2026-11-01 |
| 55 | The Matrix and the Graph agree: both count what a node holds as that node. A node's links, a cell and a path name nodes, one row to a node with how many links it stands for, and only the tree opens a node to its rows; a row of a list still opens the link itself, with the row it is written on | 2026-11-01 |
| 18 | The importer carries an earlier specification's evidence -- its captures, reports, analyses, scout's report and coverage -- and the six examples are imported again with it, each beside its material, `dev/` | 2026-10-25 |


## Phases

1. **Done 2026-10-25. The data**: the node files' form (decision 9), the grammar as data, the loader
   into SQLite with every check of R6 that needs no history, for four kinds on
   the shop example.
2. **2a done 2026-10-25: the server (`app/serve.py`, `app/api.py`), `index.cmd` and `index.sh`, the engine (`app/web/`) and the views of the overview, a list per kind, a node with its links both ways, a role's permissions and the graph around a node. 2b done 2026-10-25: screens with their elements, components with their parts and variants, and entities, in the data as tables whose rows are nodes; the prototypes as markup with one anchor per element (`data-el`, `data-part`), held to the data both ways, in the product's page shell; and the screen, prototype, component and design-system views.** The application, read-only: the server, `index.cmd` and `index.sh`,
   the engine, and the views of a requirement, a screen, a prototype, the
   design system, the gaps and the graph, on the shop example. Judged by the
   user with the pages in front of them before anything further.
3. **Done 2026-10-25: `app/logic.py`, `app/edit.py`, `app/review.py`; `spec.py do`, `history`, `stale`; `POST /api/changes`, `/api/history`, `/api/stale`; the History and Stale views.** The logic: the operations, staleness and confirming, counters and
   retired IDs, the change log, through the command line and the API.
4. **Done 2026-10-25, 4b with it -- `app/build.py` and `spec.py overview | plan | unit | tests | verify | snapshot | changed`, snapshots kept in the code with a print of every prototype file: every kind of the earlier form in the grammar -- the document, qualities, constraints, decisions, questions, risks, terms, entities' states, foundations, flows, endpoints, sources, findings, contradictions; `scripts/import_site.py`, which reads a specification of the earlier form through its own reading and its pages; the six examples and NovaLife, in `targets/novalife-2/`, imported and loading clean.** Everything: every kind and view; the importer from specs-builder's
   pages, copied into this skill; the six examples, and NovaLife into
   `targets/novalife-2/`; the query tool, snapshots and changed.
5. **Done 2026-10-25. 5a (decisions 13-15): the modes that write and change by hand, in SKILL.md; the guides
   copied into `references/` and written for the data -- writing, asking, aspects and its areas, concepts,
   checking assumptions, the Domain, the UX, the endpoints, finishing; the addition kind; the operations
   `answer`, `confirm-added`, `retarget`, `add-line`, `remove-line`, `add-row` of a state by its word, `set` of
   a whole table; an agreed specification refusing change, and agreeing refused while anything stands in the
   way; `spec.py open | impact | trace | ready | kinds` (`app/finish.py`), the words a review reads for in the
   grammar; the Open view and what is unsettled on each node; `scripts/new_spec.py`. 5b (decisions 16-18):
   reverse-engineer in SKILL.md; the twelve agents' briefs and their rules in `agents/`, their facets in
   `app/agents.json`; reading material, reading a live site and the agents' guide in `references/`; the
   evidence's own folder, `evidence/`, and a Coverage table on each source (`app/evidence.py`); `spec.py merge
   [--check]` (`app/merge.py`); `spec.py open` listing what is to investigate, ranked, the material changed
   since it was read, the files no coverage accounts for, the captured sites' faults; the Evidence view with its
   files, captures with their screenshots, a finding leading to where it was read; the reading scripts copied,
   writing Markdown through `scripts/textfile.py`; the examples imported again with their evidence and
   material.** The procedures: SKILL.md's modes and the agents, working through the operations; the selftest.
6. **Done 2026-10-25 (decisions 19-21): editing in the browser -- `app/web/edit.js` and the Edit switch, every
   node's parts as forms, a node made from each list, answering, confirming and agreeing, each form posting
   operations with the version it was drawn from; `logic.apply(expect=...)` refusing a change made against what
   moved since; the forms' shape from the grammar (`api.form`); a link written only in a table's cell refused when
   tied as a whole -- and the export, `app/export.py` and `spec.py export`, one HTML file with every node, every ID
   a link within it, and each prototype drawn in a sandboxed frame with the product's styles, scripts and pictures
   inlined.** Editing in the browser (decision 10) and the export (decision 8).
   **6b done 2026-10-25 (decisions 22-23): the parts in one order; the Prototype gallery (`api.prototypes`,
   `#/prototypes`) and the export's Prototype section; the bar in two rows with a panel per part (`web/menu.js`,
   `api.menu` kept per change of the data); search (`api.search`, `/api/search`); the Help view (`web/help.js`);
   the appearance (`web/theme.js`, and the export's own switch); the page per part taken out, its address
   leading to the overview. 6c done 2026-10-26 (decision 24): a plain menu per part; the prototype as a tool
   (`#/prototype`, the toolbar and the inspector in `web/engine.js`); `runtime/live.js` and `live.css` reading
   specs-builder-2's anchors. 6d done 2026-10-27 (decision 25): the ID cards (`api.card`, `/api/card/<id>`,
   `web/card.js`, each kind's `"card"` in `grammar.json`) and their Preview (`/?peek=1`). 6e done 2026-10-27
   (decision 26): the tree of a part (`web/side.js`) and the part's page again (`#/group/<part>`). 6f done
   2026-10-27 (decision 27): the Quiet workbench, the tokens and rules of `web/style.css` and the contrast check.
   6g done 2026-10-27 (decision 28): a flow's diagram (`web/flowmap.js`, Mermaid from the CDN, the flow's
   Diagram section). 6h done 2026-10-27 (decision 29): a foundation's examples (`web/foundations.js`); the
   menu's Everything in taken out. 6i done 2026-10-28 (decision 30): a flow as a user story (`finish.story`,
   `web/story.js`, `spec.py story`, the export, `ready`). 6j done 2026-10-28 (decision 31): what a change would turn
   stale, said before it is saved (`logic.apply(dry=True).stale`, `/api/changes` with `dry`, `web/edit.js`). 6k done
   2026-10-29 (decision 32): a builder asks back (`inbox.py`, `spec.py ask`/`inbox`, `/api/inbox`, What is open). 6l done
   2026-10-31 (decision 33): how well a requirement stands is worked out, never written (`load.standing`). 6m done
   2026-10-31 (decision 34): what the code carries is read from the names in it (`build.coverage`, What is built). 6n done
   2026-10-31 (decisions 35 to 37): along a page, its outline and the nodes beside it, each page on a sheet of A4
   from a printer in the bar (`web/aids.js`), and Every screen drawn, written at last. 6o done 2026-10-31 (decision
   38): the export has the application's cards and diagrams, by the application's own code. 6p done 2026-10-31
   (decision 40): README.md, SETUP.md and USER-MANUAL.md, the manual's worked example run by the selftest. 6q done
   2026-10-31 (decision 41): the Graph page, `web/graphmap.js`, every node and link, folded by kind, with D3. 6r done
   2026-11-01 (decision 42): the Matrix page, `web/matrix.js`, `app/matrix.py`, `tests/scale.py`. 6s done 2026-11-01
   (decision 43): filters, grouping, stale marks and paths. 6t done 2026-11-01 (decision 44): the Graph's four pictures. 6u done 2026-11-01 (decision 45): Layers in bands and by node. 6v done 2026-11-01 (decision 46): cards on a right click, the Graph's two scopes. 6w done 2026-11-01 (decision 47): cards that cascade. 6x done 2026-11-01 (decision 48): Layers in the menu's order. 6y done 2026-11-01 (decision 49): a card's ways out, and cards by touch. 6z done 2026-11-01 (decision 50): Layers of a node, links first; the Graph's toolbar. 6aa done 2026-11-01 (decision 51): a large specification opens at once. 6ab done 2026-11-01 (decision 52): the application reads; changes go through Claude Code. 6ac done 2026-11-01 (decision 53): a requirement's Why and Details. 6ad done 2026-11-01 (decision 54): a part's word and its arrow. 6ae done 2026-11-01 (decision 55): the Matrix names nodes, as the Graph does.**
7. **The replacement** (decision 11), when the user decides.
