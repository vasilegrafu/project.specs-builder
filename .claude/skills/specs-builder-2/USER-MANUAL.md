# specs-builder-2: user manual

This manual is for people who use the skill: whoever writes a specification,
reviews one, or builds from one. To install it, see [SETUP.md](SETUP.md).

- [The idea in one minute](#the-idea-in-one-minute)
- [Three ways to start](#three-ways-to-start)
- [A first specification, step by step](#a-first-specification-step-by-step)
- [The application](#the-application)
- [The words it uses](#the-words-it-uses)
- [Changing a specification](#changing-a-specification)
- [Agreeing a specification](#agreeing-a-specification)
- [Handing it on](#handing-it-on)
- [Building from it](#building-from-it)
- [Every command](#every-command)
- [Where the files go](#where-the-files-go)
- [What it cannot do yet](#what-it-cannot-do-yet)

## The idea in one minute

A specification here is a set of small facts, each in its own text file, tied
to one another by links. A requirement is a file. So is a goal, a rule, a
screen and an open question. When a screen shows a requirement, that is a
link, not a sentence.

Three things follow from that.

- **The application reads the facts directly.** Nothing is generated and
  nothing has to be kept in step.
- **It can follow the links.** It can tell you why a requirement exists, what
  shows it, and what a change would affect.
- **Every change goes through one gate.** A change that would break the
  specification is refused whole, and every change that passes is logged.

The skill writes what the product must do and why, never how to build it.

## Three ways to start

Ask for it by name in Claude Code, so that there is no doubt which you mean:
say `specs-builder-2` in your request.

| You have | Say something like | What happens |
|---|---|---|
| An idea, in your own words | "Use specs-builder-2. Customers should be able to download their invoices as PDFs." | **Write-ask.** The skill writes it up complete, then asks what it needs to know |
| Only a name or a rough goal | "Use specs-builder-2 and ask me about an invoice portal." | **Ask-write.** The skill asks, and writes from your answers |
| Something that already exists | "Use specs-builder-2 to reverse-engineer `./my-app`." | **Reverse-engineer.** The skill reads the code, documents or running site with its agents, and notes where each fact came from |

The three mix freely within one specification.

Four rules hold in every mode.

- **It completes the behaviour, but never invents a fact.** It adds the cases
  you did not mention and marks each one as an addition until you confirm it.
  Numbers, laws and facts about your users are asked, never guessed.
- **It writes only what is needed.** A section with nothing to say is left out.
- **It says what and why, never how.** A requirement is behaviour someone
  outside the product can observe.
- **You decide.** What the skill proposes is yours only once you confirm it.

## A first specification, step by step

The skill normally runs these commands for you. Doing it once by hand is the
quickest way to see how it works. Every command below is run by the selftest,
so they work exactly as written.

Create the specification, then go into its folder:

```
python .claude/skills/specs-builder-2/scripts/new_spec.py invoices --name "Invoices" --kind application --summary "Customers take an invoice out of the portal as a PDF, so that they stop writing to support for it."
cd invoices
```

Check it, and add the goal that everything else serves:

<!-- walkthrough -->
```
python app/spec.py check
python app/spec.py do add goal "Fewer letters to support"
```

A requirement must have at least one acceptance criterion, so the two go in
together, as one change. Put these two lines in a file called `first.txt`.
`$1` means "what the first line made":

<!-- first.txt -->
```
add requirement "Download an invoice" priority=must statement="When a customer selects Download on an invoice, the portal shall give them its PDF." serves=G1
add-row $1 says="Given a paid invoice, when Download is selected, then its PDF is saved."
```

Then apply it, add an open question, and read the result:

<!-- walkthrough -->
```
python app/spec.py do --file first.txt
python app/spec.py do add question "How long invoices are kept" question="How long are invoices kept?" why="It decides what the list shows" answers="the product side" about=R1
python app/spec.py node R1
python app/spec.py open
```

`open` lists everything not settled, and Q1 is there. Before you change
something, ask what it would affect:

<!-- walkthrough -->
```
python app/spec.py impact R1
```

It says Q1 would need reading again. Answer the question. An answer becomes a
decision, with its reason:

<!-- walkthrough -->
```
python app/spec.py do answer Q1 "Seven years." because="The law where the shop sells"
```

Now change the requirement. `--because` goes in the log:

<!-- walkthrough -->
```
python app/spec.py do set R1 priority should --because "Support can wait a release"
python app/spec.py stale  # exits 1: something is stale
```

The decision D1 stands on R1, and R1 has just changed, so D1 is now **stale**:
someone must read it again against the change. Once you have, confirm it:

<!-- walkthrough -->
```
python app/spec.py do confirm D1
python app/spec.py verify
```

`verify` now says the specification may be built from. See the requirement as
the tests a builder will write, and export the whole thing as one file:

<!-- walkthrough -->
```
python app/spec.py tests R1 --gherkin
python app/spec.py export
```

The export is in `export/invoices.html`. To see it all in the application, run
`index.cmd` on Windows, or `sh index.sh` on macOS and Linux.

To try a change without making it, add `--dry-run` to any `do`.

## The application

Run `index.cmd` on Windows, or `sh index.sh` on macOS and Linux, in the
specification's folder.

### The top bar

| In the bar | What it does |
|---|---|
| **Search** (Ctrl K or /) | Finds any node or row by its ID, its name or its words |
| **Printer** | Opens this page on a sheet of A4 in a new tab |
| **Export** | Saves the whole specification as one HTML file |
| **?** | Help, inside the application |
| **Appearance** | System, light or dark |

Below the bar are the parts, always in the same order: Document, Evidence,
Decisions, Requirements, Domain, API, UX, Prototype, Matrix and Graph. A part's
**word** opens its page. The small **arrow** beside it opens a short menu of what it
holds, with the letters its IDs begin with and a count. The menu stays until you
press the arrow again, click elsewhere, press Escape or choose something.
Prototype, Matrix and Graph have no menu: each opens its page straight away.

### Finding your way on a page

- **The tree on the left** holds everything in the part. Drag its edge to widen
  it, or press « to fold it away.
- **On this page**, on the right of a long page, jumps to a heading. On a
  narrow window it sits above the page.
- **Previous and next** are the small `‹ R3` and `R5 ›` buttons at the top right
  of a node's page and again at its foot. They follow the order of the tree, and
  a pause over one shows the name it leads to.
- **An ID's kind.** Pause on any ID, on a page, in a tree, in the Matrix or in the
  Graph, and a small tip says what it is: Requirement, Flow and so on.
- **An ID's card.** Right click any ID, or hold a finger on it on a phone or
  tablet, and a card says what it is, with its links by kind. Right click an ID inside a card and another opens beside it, so
  you can walk from node to node from any page. Right clicking in an earlier card
  replaces the cards after it, and a node already open flashes. The pin keeps a
  card open from page to page. Any card can be dragged by its top. **×** closes a card, Escape closes the newest, and
  a click on the page closes all but the pinned. Past six cards the oldest fold
  to a strip at the bottom left, to bring back with a click. The icons at
  its foot are **Open**, **Preview**, which shows that page in a popup without
  leaving this one, **Request a change**, then **Around**, **Layers** and **Impact**, which show that
  node in the Graph, and **Matrix**, which shows all its links. The row below
  holds Open and those four again, each with a small arrow: they open in another
  tab.

### The pages to know

| Page | Where | Shows |
|---|---|---|
| **The overview** | Click the name, top left | What the specification holds, and how well its requirements are backed |
| **What is open** | Document menu | Everything not settled, including what builders asked back |
| **What is built** | Document menu | What the code carries, once there is code. See [Building from it](#building-from-it) |
| **Stale** | Document menu, when there is any | What must be read again after a change |
| **A flow** | UX menu | Its user story, the requirements it carries, its diagram and its steps |
| **Matrix** | The bar | Every node and link, walked one at a time. See [The matrix](#the-matrix) |
| **Graph** | The bar | The whole specification, folded by kind. See [The graph](#the-graph) |
| **The icons under a title** | Any node's page | **Around**: that node in focus, with what it is linked to. **Layers**: only what connects to it. **Impact**: what a change to it would reach, a step at a time. **Matrix**: all its links. Each has a twin with a small arrow, to open in another tab. **Request a change** stands apart |
| **Every screen drawn** | UX menu | All the screens as small pictures, flow by flow |
| **Design system** | UX menu | Colours, type, spacing and components |

### The prototype

Prototype, in the bar, opens the screens as a working tool. Its toolbar picks
the screen, a state or variant, the look or the wireframe, and the width. Click
a mark on a screen to inspect that element: its row in the specification, what
it stands on, and its size and colours. The fold button at the end of the
toolbar hides the bars to give the screen more room.

### The matrix

Matrix, in the bar, is the way to read the links one at a time. It opens on a
grid: a row and a column for each kind, and in each cell the number of links
going from the row's kind to the column's. A dot is a gap, with no link at all.

| To | Do this |
|---|---|
| See the links between two kinds | Click a number in the grid. A kind's name opens that kind |
| See what a part or a kind holds | Click its name in the tree. A kind shows what it is, how it is linked and its nodes. Only the arrow beside a name folds it |
| Find a node | Open it in the tree on the left, or type in **Find a node** and press Enter |
| See a node's links | Click it. They are listed by sort, both ways, each with its count |
| Go on to the Graph | The icons under the node's name: Around, Impact and Layers, each beside its twin for another tab |
| Read links between nodes | The lists name nodes, as the Graph does: `C12`, not `C12.1`, with how many links reach it. Only the tree opens a node to its rows, and clicking a row in a list tells the link itself |
| See one connection | Click a link. The right side tells both ends, how it reads from each, what goes stale if one end changes, whether it is stale now, and the file and line it is written on |
| Go to the far end | Click the arrow on the link, or **Go to** on the right |
| Go back along your way | Click a node in **Walked**, under the page |
| Return to the grid | The grid icon at the top of the tree |
| Fold the whole tree | The collapse icon beside it |
| Go back or forward through what you opened | The back and forward arrows beside those. They stay inside the Matrix |
| See only what needs attention | The list under **Find a node**: **Stale**, **No links** or **Open questions** |
| Narrow a long list of links | Type in **Filter these links** |
| See which screens or other kinds touch a node | **By kind**, above its links. It is kept for next time |
| See what is stale at a glance | An amber number in the grid holds stale links |
| See how two nodes are joined | The path icon, or **Path from** on a node, then choose the two ends |

A criterion or an element is listed in the tree under the node that holds it.
Its links count as that node's too, marked with the row they come from, as
`from SC3.13`. Links inside one node are left out, and shown when you choose
the row itself.

A path prefers links a change passes along, so it says why one node bears on
the other. Where no such chain exists it shows any chain, and says so.

The Matrix fetches only what you are looking at, so it opens at once on a large
specification, and it needs no internet connection. The keyboard works in the
tree: the arrows move and open, and Enter chooses. The edge of the tree and of
the right side each drag to another width, which is kept, and a double click
puts it back. On a phone the three sides become the tabs Nodes, Links and Connection. The printer prints what
is in view.

### The graph

Graph, in the bar, draws everything in the specification and how it is linked.
It opens folded: one bubble for each kind with its count, such as Requirements
16, and a line between two kinds saying how many links join them.

| To | Do this |
|---|---|
| Open a kind | Click its bubble. It becomes a box of its nodes, and the lines go to the nodes |
| Fold it again | Click the box's title |
| Select a node | Click it, or find it. It stays selected from one picture to the next, until its **x**. Back returns to the same picture |
| See more of a big kind | Click the last tile of its box, the one that says how many are left |
| See what a node is, in any picture | Right click it. Its card opens with its name, what it says and how it stands |
| See what something is linked to | Point at it. Its links light up and the rest fade |
| Move a kind | Drag its bubble, or its box by the title |
| Pan and zoom | Drag the background, and scroll |
| See everything again | The fit icon, or the icons that open and fold every kind |
| Go to a node | Type in **Find a node**, and press Enter |

A criterion or an element is not drawn on its own. It counts as the node that
holds it, so a link from `R4.2` shows as a link from `R4`. The kinds you opened
are kept in your browser. The printer prints the graph as it stands on screen.

The top of the page has two scopes. **All** has the map and Layers, for the whole
specification. **Selected** has Around, Layers and Impact, for one node. A pause on
any icon says what it does. Each fetches only what it shows, so they stay quick on a very
large specification.

| Picture | What it shows | How to use it |
|---|---|---|
| **Around** | One node in the middle, what it is linked to around it, and nothing else | Click a node to spread its links, double click to put it in the middle, drag it to pin it. The arrows narrow it to links out or in, and the steps icons spread what is around the middle |
| **Impact** | What stands on a node, then what stands on those | Click a node to go a step further. The number beside it says how many stand on it |
| **Layers** | The top menu's order, left to right: goals, requirements, the domain, endpoints, flows, screens and components, in bands sized by how many links join them | Click a kind or a band for its nodes, and scroll over them to go on down the kind. **Hide** folds a column. Click a node to select it, and see only what connects to it: one step out, two, or all the way, by the icons above. There the links followed are drawn, the node's own the strongest, and a pause on a node shows the rest of its links. Double click to see what is around it |

Graph needs an internet connection the first time it opens, to fetch D3, the
library that lays it out. Without one the page says so.

### Asking for a change

The application reads. You change a specification by asking Claude Code, which
makes the change, goes through everything that stands on it, the nodes and the
screens, and shows you what it would adjust before it does.

To ask from the browser, press **Request a change** on a node's page or its card.
Say what should change. The first time, it asks your name. The request waits under
**What is open**, in `inbox.md`, beside the data and never in it, so nothing
changes yet. In Claude Code, `python app/spec.py inbox` lists what waits, and
Claude takes each one up and closes it. While anything waits, the specification
cannot be agreed.

If you edit a file by hand instead, the application notices and logs it.

## The words it uses

A **requirement** has one testable sentence. Beside it, **Why** says who needs it
and what goes wrong without it, and **Details** says what it covers and what it
does not. Both are there only where there is something to say. Rewording a Why
turns nothing stale; changing Details does.

| Word | Meaning |
|---|---|
| **Node** | One fact with an ID: a goal `G1`, a requirement `R4`, a rule `B1`, a screen `SC3`, a question `Q1` |
| **Row** | A part of a node with its own ID: a criterion `R4.2`, a screen's element `SC3.13` |
| **Addition** | Something the skill added on its own judgement, `AD1`. It stays open until you confirm it |
| **Open question** | Something not settled, why it matters, and who answers it |
| **Decision** | A settled choice, with its reason and what was turned down |
| **Stale** | It stands on something that changed since it was last read. Read it again, then confirm it |
| **Finding** | One thing read in existing material, with its quote and source |
| **Agreed** | The person it is for has accepted it. It then takes no changes until it is set back to draft |

### How well a requirement is backed

Each requirement and rule gets one word, worked out from the findings behind
it. You never type it. The first that holds is the one shown:

| Word | It means |
|---|---|
| `disputed` | The findings behind it disagree, and that is not settled |
| `corroborated` | Quoted from two sources or more, at least one of them the product itself |
| `seen` | Seen in the product itself, in its code or running |
| `documented` | Only documents say so. Nobody has looked at the product for it |
| `inferred` | Concluded from the material, never seen as such |
| `added` | The skill's own judgement, not yet confirmed |
| `stated` | No finding behind it: you said so |

What is open lists the `disputed`, `inferred` and `added` ones as weak ground,
and the `documented` ones as claims to check against the product. None of these
stops an agreement. To move a requirement up, read the product for it. Editing
the word is not possible.

## Changing a specification

1. **Ask what it touches.** `python app/spec.py impact R4`.
2. **Make the change**, by asking Claude Code or with `do`. If behaviour moves,
   change the requirement first.
3. **Record why.** Use `--because`, or a decision for anything with a real choice.
4. **Read what went stale**, then `do confirm <id>` for each.

Asked why something exists, use `python app/spec.py trace R4`: what it stands
on, the findings with their quotes, and what shows it. `history R4` says what
changed, when, by whom and why.

## Agreeing a specification

`python app/spec.py ready` says whether it may be agreed, and lists every
reason it may not. Among them:

- additions not confirmed
- open questions for the product side
- qualities or risks left open, or a quality nobody has written
- flows whose story cannot be told
- questions from builders not taken in
- anything stale

Open questions for engineering do not hold it up. Only the person it is for
agrees it:

```
python app/spec.py do set document status agreed
```

This is refused while anything stands in the way. Once agreed, every change is
refused until you set it back with `do set document status draft`.

## Handing it on

**To print one page,** press the printer in the bar. The page opens alone on a
white A4 sheet in a new tab. Check it, then press **Print** to send it to paper
or save a PDF. Each sheet has a foot with the page's name and "Page 1 of 3".
Long screens fill the sheet's width and run on to the next sheet, and a flow's
diagram keeps to one sheet. On the prototype, you get the screen in the state
you are looking at.

**To share the whole specification,** press **Export** in the bar, or run
`python app/spec.py export`. You get one HTML file that holds everything, for
someone with no Python: every node, every prototype, ID cards on a right click, and
a flow diagram for each flow. It is also kept in `export/`.

Two limits apply to the export:

- Its flow diagrams need an internet connection when the file is opened.
  Without one, a flow shows its diagram's text, and its steps say the same.
- Printing the whole export leaves out the prototype screens. To print a
  screen, use the printer on its page.

## Building from it

Whoever builds the product, a person or a coding agent, asks the same command
line. Each command takes `--json`.

| Step | Command |
|---|---|
| See what is here | `python app/spec.py overview` |
| Plan the work as user stories | `python app/spec.py story` |
| Get the order to build in | `python app/spec.py plan` |
| Get all one thing needs | `python app/spec.py unit R4` |
| Get its tests | `python app/spec.py tests R4 --gherkin` |
| Check it may be built from | `python app/spec.py verify` |
| Record what the code is built from | `python app/spec.py snapshot --target ../code` |
| See what moved since, and what to redo | `python app/spec.py changed --target ../code` |
| See what the code carries | `python app/spec.py coverage` |

**Every test names the criterion it proves.** Write `R4.2` or `R4_2` in the
test's name or a comment beside it. Scenarios from `tests --gherkin` already do.
Those names are the only tie between the code and the specification, and
`coverage` reads them. It exits 1 while a criterion of a `must` or a `should`
has no test. It reads names only, so it cannot tell you that a test passes.

**Ask back. Never guess, and never edit.** Where the specification does not
settle what you are building:

```
python app/spec.py ask "Does the limit of five count other devices?" --about R4 --by "the builder"
```

The question waits in `inbox.md`, outside the data, and appears first under What
is open. Whoever keeps the specification makes it an open question, or answers
it and closes it. `ready` holds while any waits. Build what does not depend on
the answer meanwhile.

## Every command

Run these in the specification's folder. `--json` works on the commands for
writers and builders, and `--spec <folder>` points at another specification.

**Checking and reading**

| Command | Does |
|---|---|
| `check` | Holds every file to the grammar, and says each problem at its file and line |
| `build` | Checks, then rebuilds the database. Exports and the application do this themselves |
| `node R4` | A node and its links both ways |
| `history [R4]` | What changed, when, by whom and why |
| `stale` | Everything standing on something that changed |
| `kinds [question]` | What each kind holds, by the names `do` takes |
| `open` | Everything not settled |
| `impact R4` | What it stands on, and what a change would turn stale |
| `trace R4` | Why it is there, and where it shows |
| `ready` | Whether it may be agreed. Exits 1 with every reason while it may not |
| `story [F1]` | A flow as a user story, with what it carries |
| `inbox` | What builders asked back. `--raise N` makes one a question, `--close N` takes it out |
| `export` | The whole specification as one file. `--into` names another place |

**Changing, with `do`**

| Operation | Does |
|---|---|
| `add <kind> "<name>" key=value` | Adds a node with the next free ID |
| `add-row <id> key=value` | Adds a criterion, an element, a part or a state |
| `add-line <id> <table> [first] key=value` | Adds a line to a table on a node |
| `remove-line <id> <table> <first>` | Takes that line out |
| `set <id> <key> <value>` | Sets a field, a text, a cell or a whole table |
| `tie <id> <relation> <id>`, `untie` | Adds or removes one link |
| `remove <id> [--untie]` | Removes a node and its rows. Its ID is never used again |
| `retarget <old> <new>` | Moves every link and mention to another node |
| `answer <question> "<decided>" because=...` | Settles a question into a decision |
| `confirm-added <id>` | Confirms an addition |
| `confirm <id>` | Confirms a stale node has been read again |

`do --file <file>` makes one change of every line of a file, all or none. Add
`--dry-run` to see the effect, and `--because` and `--who` for the log.

**Reading material,** which the skill's agents use: `merge [file]`, with
`--check` to judge a file and write nothing.

**Building:** `overview`, `ask`, `plan`, `unit`, `tests`, `verify`, `snapshot`,
`changed` and `coverage`, described in [Building from it](#building-from-it).

## Where the files go

```
my-spec/
  data/           the specification: one file to a node. Keep this in git
  prototypes/     the screens, components and design tokens
  evidence/       what was read: captures, agents' reports, analyses
  stamps/         the change log, IDs used, what was reviewed, where the code is
  inbox.md        questions from builders, when there are any
  app/            the application: spec.py, serve.py and the views
  index.cmd       opens it on Windows
  index.sh        opens it on macOS and Linux
  .cache/         the database, rebuilt whenever it is needed. Not in git
  export/         the exported file. Not in git
```

Change the data by asking Claude Code, or with `do`. A file edited by hand is
noticed and logged, but the operations are what keep a change checked and
reaching everything that stands on it.

## What it cannot do yet

- **Walking a site by script is untested.** `crawl.py` has never run with
  Playwright in a real session. A walk by hand in the session's browser works.
- **`coverage` has only been tried on a made-up codebase.** No real code built
  from a specification names its IDs yet.
- **There is no command to update a specification's application.** See
  [SETUP.md](SETUP.md#bring-an-old-specification-up-to-date) for the copy by hand.
- **The export depends on a CDN for its diagrams,** and printing it leaves out
  the prototype screens. See [Handing it on](#handing-it-on).
- **The export leaves out the matrix and the graph.** They are only in the
  application.
- **The A4 tab shows one long sheet.** To see where the pages break, use the
  browser's print preview.
- **It writes what and why, never how.** Technical design, estimates and
  backlogs are not what it is for.
