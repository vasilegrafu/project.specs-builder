# The commands, one by one

`app/spec.py` answers from `data/` and `prototypes/` as they stand. It keeps what it read in `.cache/` until a file
changes, and writes nothing else unless the command is to write. Run it from the specification's folder, or from anywhere
by its path, or with `--spec <folder>`. It needs Python 3.14 or later and nothing else.

    python app/spec.py <command> [what] [options]

`spec.py <command> --help` gives that command's row of this guide. Every answer in this guide is markdown, holds no more than `--budget` characters (40000 unless said; 0 for no bound),
says what it left out and the command that gets it, and ends with what to ask next. `--json` gives everything as JSON
for a program, with no bound. A node is named by its ID with its name beside it. An ID the tool does not know is answered
with the nearest it does. If anything is stale, the answer says so first.

It exits 0 when it has answered; 1 when the answer is something to act on -- `open` that lists anything, `coverage` while
a must or a should has no test, `verify` when something is stale or does not load -- and 2 when it is asked wrongly.

## To learn the product

| Command | Answers |
|---|---|
| `capabilities` | What it lets people do: each flow as an outcome, who may take it, the rules it meets, the requirements it carries and the screens and endpoints it goes through, with a last row for the requirements no flow carries. `overview` holds it too. |
| `overview` | What the product is: its summary, its users, its qualities, its constraints, its decisions, its risks, what it holds, the slices in order, where the look is, what is never built, and how to build it. The first call. |
| `list <kind>` | Every node of a kind, with what it says: `list requirement`, `list rule`, `list screen`. `list kinds` gives every kind, what it is and how many there are. |
| `find <words>` | Every node that says the words, with the field and the words around them: `find 24 hours`. Evidence comes last. |

## To build

| Command | Answers |
|---|---|
| `plan` | The slices, in the order to build them: what each builds, what it uses that an earlier slice built, the requirements it completes, those it carries on, the rules it enforces, how many criteria say it is done, and what blocks it. A requirement is completed in the last slice that builds something showing it. |
| `unit <slice or ID>` | All one slice needs, in one answer: `unit foundation`, `unit rest`, `unit F1`, or any node, as `unit SC3`. Each node in full, the requirements it carries, the rules, the entities, who may, what is not settled, what the evidence did not establish, the risks, and where the look is. `--evidence` adds the findings behind it. |
| `look <screen or component>` | How it looks: each element with its selector, its states, the layout, the components it is made of, the product's values, and the foundations it follows -- the rules of the look it is drawn by -- then the rest. |
| `tests <slice, ID or all>` | The criteria of each requirement it completes, each with its ID (`R4.1`); the requirements it only carries on, with the slice where each is tested; each rule that must hold; each transition that must happen, of a screen or an entity. A rule or an entity gives the requirements that stand on it. `--gherkin` writes scenarios; `--ui` gives what a test of each screen checks: each element's words in each state, each transition, each field's boundaries. |
| `outline <screen> [--state S] [--as V]` | Its prototype as a tree, line by line as drawn: each element with its handle (`SC3.4`, a component's part `C9.2`), its name, what it is, its words, where it goes, what it stands on and when it shows; with `--state` or `--as`, only what shows then. |
| `words <screen>` | Every word the screen shows, element by element, as text, a placeholder, a label or an alternative, and when it shows: the copy to use as it is. |
| `forms <screen>` | Each form and where it is sent; each field with its label, its type, its rules -- required, a lowest, a highest, a length, a pattern -- its options and what it stands on; each button; each message it shows; and what the requirements they stand on say, whole, as a limit may be kept there alone. |
| `links <screen>` | Where each element leads, a screen and how it opens, a place on the page, a dialog; what leads to the screen from the others; its transitions as the data states them. |
| `states <screen>` | Each state and variant: how to open it (`?state=`, `?as=`), what it shows and what it hides; the states the data says, observed or likely; the widths the styles change it at, and what changes; its layout. |
| `styles <screen, element or .class>` | The values it is drawn with, from the product's styles and tokens as a browser would apply them: for an element, its own values with the token each is, what it inherits, and what changes on hover, on focus and at each width; for a screen, each element's main values; for a class, its rules. |
| `tokens` | The design tokens: each variable, its value, what it is for, the foundations that name it and the prototypes its value reaches; the same as the CSS the page links as `assets/css/tokens.css`, which no file holds; and what the page links from elsewhere, its web fonts among them. Every colour is a token: no sheet, prototype or foundation writes one. |
| `sample` | The prototypes' sample data, as JSON: fixtures for tests, never the product's data. |
| `messages` | Every message the product shows: what a screen says in a state other than its normal one, its alerts, and what each endpoint answers when it fails. |
| `open <slice or ID>` | What is not settled there: each open question with why it matters, who answers it and what it blocks; what the evidence did not establish; what was added and not yet confirmed; what leans on something to investigate; the prototypes to look at, with the token that moved under each. `open` alone is the keeper's whole list. |

## To know what it means

| Command | Answers |
|---|---|
| `schema [entity]` | Each entity, or one, as JSON Schema: each field with what it means; a field that holds the state takes the lifecycle's states; the rules that govern it. A type, or whether a field is required, is not added where the data does not say it: ask. |
| `lifecycle <entity>` | Its moves -- from, on, only if, then, to -- its states with what each moves to and the screens that show it, a diagram, and the rules that govern it. |
| `permissions` | Who may do what: each action, each role yes, no or ?. A ? is asked. |
| `rules [rule]` | Each rule, or one: what it says, its exceptions, what it governs, the requirements that make it true, how well it stands. |
| `glossary` | The product's words, what each means and what else it is called, and every named thing: the names to use in the code. |
| `qualities` | Each quality with its status and what it must be, and each constraint. |
| `openapi` | The API's description, OpenAPI 3 written from the endpoints that have a method and a path. |

## To find your way

| Command | Answers |
|---|---|
| `node <ID> [--depth N]` | One node in full, its file, and every node within N links of it (1 unless said). |
| `edges <ID> [--rel R]` | Every link from and to a node, both ways. |
| `trace <R>` | Why it is there: what it stands on, the findings it came from with their quotes, where it shows, who may do it. |
| `impact <ID>` | What a change of it would reach. |
| `story [F1]` | A flow as a user story, with every requirement it carries: a piece of work to plan. |

## To check the work

| Command | Answers |
|---|---|
| `coverage [R4] [--target <code>]` | Each requirement with its criteria and the tests and code that name it; each criterion no test names; each ID the code names that the specification has not. Exits 1 while a must or a should has a criterion no test names. It reads names: it cannot tell that a test passes, or that it proves what it names. `coverage <code>` says the same. |
| `changed --target <code> [--since S] [--until S]` | What moved since what the code was built from: the newest snapshot, or `--since` one by its stamp, beside the specification now, or beside `--until` a later one: the nodes new, gone and changed with each field's before and after; each screen's elements and fields as its prototype draws them; the styles, tokens and sample data; the slices to build again; the tests to run again and to take out; and the screens a change of the look reaches. No git is read. |
| `snapshot --target <code> [--keep N]` | Records the specification as it stands, every node and what each prototype draws, as what the code was built from, in the code's `.snapshots/specs-builder/`, committed with the code. The newest 3 are kept unless `--keep` says otherwise. `--list` lists them and writes nothing. |
| `changes` | What moved since the specification was last agreed: each node added, changed or removed. For whoever keeps it. |
| `stamp` | Each shared piece of `prototypes/shared/` written into every prototype that holds it. For whoever keeps it. |
| `verify` | Whether it may be built from now: it loads clean and nothing is stale. It names what builders asked and what is open. Exits 1 if not. |

## To leave something for whoever keeps it

| Command | Answers |
|---|---|
| `ask "<question>" --about <IDs> --by "<who>"` | Writes the question into `inbox.md`, beside `data/`, never into it. Build what does not depend on it meanwhile. |
| `export --model [--into <folder>]` | Writes the data as `export/model/`: `index.json`, a file for each node, `edges.tsv`, `stands.tsv`, and `openapi.json` where there is an API, for a program that reads JSON rather than asking. `export` alone writes the whole specification as one HTML page for people. |

## Examples

    python app/spec.py overview
    python app/spec.py plan
    python app/spec.py unit foundation
    python app/spec.py look SC3
    python app/spec.py outline SC3 --state empty
    python app/spec.py styles SC3.4
    python app/spec.py schema
    python app/spec.py tests R4 --gherkin
    python app/spec.py open F1
    python app/spec.py node R4 --depth 2
    python app/spec.py edges B1
    python app/spec.py find delivery
    python app/spec.py verify
    python app/spec.py overview --json
