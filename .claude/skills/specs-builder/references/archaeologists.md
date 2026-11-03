# The agents, and the waves they work in

Material is read by agents of the skill's own, each starting from nothing
and holding only its brief, so that nothing it reads is crowded out by the
rest. Their briefs are files in [../agents/](../agents/), one per role,
with [../agents/rules.md](../agents/rules.md) holding what every one of
them obeys: what it never does, the shape of its staging file, how a
finding is found. The main agent -- the one the user talks to -- starts
them, merges what comes back, and holds what needs the user: the scope,
the goals, the decisions, the requirements. Where the session cannot start
agents, the main agent makes each agent's pass itself, in turn, from the
same brief, and says so in its report.

Every command below is `python app/spec.py <command>`, in the
specification's folder; the reading scripts are the skill's,
`scripts/<name>`.

## The waves

An investigation of material runs in eight waves. A wave starts when
what it reads is there, not when the one before it is done: waves that
share no input run side by side, and only the browser is held by one
agent at a time. Each wave is written down where the next can read it.

| Wave | Who | Alongside | Reads | Writes | What does it deterministically |
|---|---|---|---|---|---|
| 1. Scout | the main agent | -- | the material's surface: its files, a site's pages | `evidence/scout.md` | `scout.py --plan`; `crawl.py --list` |
| 2. Gate | the user | -- | the scout's report | the role, the scope, the parts to build, the depth and the why, as decisions | -- |
| 3. Capture and collect | the web archaeologist walks; the code, API, data, test and documentation archaeologists read files; the visual archaeologist reads the captures once the walk is done | all at once, six at a time; the browser exclusive | each its own material | `evidence/captures/<site>/`; `evidence/staging/<role>.md` | `crawl.py`, `watch.js`, `capture.js`, `a11y_tree.py`; `spec.py merge --check`, by each agent on its own file |
| 4. Merge | the main agent, as each agent answers | wave 3 still running | each staging file | findings, the sources' coverage, `evidence/reports/<file>.md`, `evidence/staging/disagreements.md` | `spec.py merge`, which takes only what the material bears out |
| 5. Synthesise and reconcile | the usage archaeologist, the meaning archaeologist, the reconciler | all three at once, on the merge | the merged findings, the captures, the screenshots; the disagreements kept | `evidence/analysis/usage.md`, `evidence/analysis/meaning.md`, their staging files; contradictions proposed | `spec.py merge` of their staging files |
| 6. Analyse | the main agent, as product analyst | -- | the analyses, the reports, the user's answers | the requirements, the Domain, the screens with their states, the flows, the design -- through `spec.py do` | the logic, which holds every change to the grammar |
| 7. Investigate and critique | the investigator, the critic | both at once: the one takes `spec.py open`'s **to investigate** in its ranked order, the other the folder | `spec.py open`; the whole folder | `evidence/staging/investigator.md`, `evidence/staging/critic.md` | `spec.py merge`; the weights of `spec.py open` |
| 8. Check | the command line | -- | every node | -- | `spec.py check`, `spec.py open`, `spec.py ready` |

Waves 6 and 7 go round only at the full depth, and at most three times.

## The depths

How far the reading goes is chosen at the gate, before anything is read,
and recorded as a decision. The scout's report says, for this material,
how many agents each depth starts.

| Depth | Waves | Stops when | For |
|---|---|---|---|
| `quick` | 1 to 6, and 8; wave 5 without the reconciler | the specification is written; what is not settled -- contradictions, what to investigate, what only documents say -- is listed, not chased | a first look, a demo, a small product |
| `standard` | all, wave 7 once | what is to investigate at or above the line is settled or reported as not settleable, and the critic's objections are answered once | the default |
| `full` | all; 6 and 7 up to three times | `spec.py open` holds only what is for people, or three rounds are done | a rebuild, or a specification that will be agreed |

The user can stop after any wave and keep a usable specification: what
each wave writes is held to the grammar as it is written.

## The ranking of what to investigate

`spec.py open` ranks what is to investigate by what leans on each row,
the heaviest first, and carries the weight: 3 for each `must`
requirement that leans on it, through the graph -- its screen, its rule,
its entity, its question; 1 for each other requirement; 2 more where who
may do what is in it. The line is 3: at the standard depth the
investigator settles what weighs 3 or more and reports the rest; at the
full depth it goes on below it, three rounds at most.

## Reading again

Material changes. A second reading does not start from nothing: each
line of a source's coverage keeps the print of what its part was when it
was read, and `spec.py open` lists each part whose print is not what it
is now, under **material changed since it was read**, with the findings
that rest on it; `scout.py --plan` says the same, with the agent to start
again on each. Only those agents are started, on those parts. When their
staging file merges, the part's line is read again, its print what it is
now; a finding whose quote still stands in the part stands, and one whose
quote is gone is corrected or taken out.

## Who reads what

| Agent | Brief | Started when | Its facets, as its brief names them and `spec.py merge` requires them |
|---|---|---|---|
| code archaeologist | [code-archaeologist.md](../agents/code-archaeologist.md) | the scope holds source code; one per part that stands apart -- a back end, a front end, a service | `routes`, `controllers`, `services`, `components`, `messages`, `validation`, `states`, `integrations`, `feature-flags`, `permissions`, `configuration`, `dependencies`, `errors`, `jobs` |
| API archaeologist | [api-archaeologist.md](../agents/api-archaeologist.md) | code that holds routes or an API description, in the scout's plan; by the main agent's hand, a site's captured calls, a HAR or a trace | `endpoints`, `parameters`, `request-bodies`, `responses`, `status-codes`, `errors`, `authentication`, `authorization`, `side-effects`, `pagination`, `versioning`, `events`, `traces`, `agreement` |
| data archaeologist | [data-archaeologist.md](../agents/data-archaeologist.md) | the scope holds source code: its schemas, migrations, models, enums, seeds | `entities`, `fields`, `relations`, `constraints`, `status-sets`, `lifecycle-columns`, `tenancy`, `audit`, `migrations`, `seeds`, `retention`, `identifiers` |
| test archaeologist | [test-archaeologist.md](../agents/test-archaeologist.md) | the scope holds source code: its tests, fixtures, mocks, reports | `asserted-behaviour`, `asserted-rules`, `boundaries`, `failures`, `roles`, `journeys`, `mocked-systems`, `fixtures`, `skipped`, `untested`, `reports`, `naming` |
| documentation archaeologist | [documentation-archaeologist.md](../agents/documentation-archaeologist.md) | documents, tickets, interviews, a specification, help pages, records of the product running given as documents | `glossary`, `concepts`, `users-and-roles`, `workflows`, `stated-requirements`, `rules-and-numbers`, `wording`, `constraints`, `decisions`, `needs-and-pains`, `measures`, `dates-and-versions`, `records` |
| web archaeologist | [web-archaeologist.md](../agents/web-archaeologist.md) | a running site or application | `views`, `navigation`, `controls`, `forms`, `validation`, `dialogs`, `hover-and-focus`, `keyboard`, `empty-states`, `loading-states`, `error-states`, `permissions`, `widths`, `requests`, `stop-points` |
| visual archaeologist | [visual-archaeologist.md](../agents/visual-archaeologist.md) | screenshots, the styles a walk captured, the code's style sheets and assets | `layout`, `hierarchy`, `spacing`, `density`, `typography`, `colors`, `icons`, `imagery`, `components`, `component-states`, `responsive`, `contrast`, `assets`, `measurement` |
| usage archaeologist | [usage-archaeologist.md](../agents/usage-archaeologist.md) | the material shows screens, or a product in use | `screens`, `layouts`, `navigation`, `components`, `responsive`, `entry-points`, `user-goals`, `flows`, `decisions`, `branches`, `states`, `permissions` |
| meaning archaeologist | [meaning-archaeologist.md](../agents/meaning-archaeologist.md) | there is material: always | `terms`, `aliases`, `entities`, `fields`, `lifecycles`, `rules`, `calculations`, `roles`, `permissions`, `capabilities`, `unknowns` |
| reconciler | [reconciler.md](../agents/reconciler.md) | the merge kept disagreements | none: it proposes contradictions, and the merge holds its file to no facet |
| investigator | [investigator.md](../agents/investigator.md) | what `spec.py open` lists has something to find out | none: it answers each question and state it is given, and the merge holds its file to no facet |
| critic | [critic.md](../agents/critic.md) | the document is written | `supported`, `inference`, `screenshots-agree`, `code-and-ui-agree`, `observed-claims`, `missing-states`, `wording`, `scope`, `classified`, `not-claimed`, `rules-hold`, `limits` |


- **Twelve agents, each with one job.** Seven collect, one per kind of
  material: code, API, data, tests, documents, the site, the look. Two
  synthesise, on what the merge holds: the usage archaeologist joins
  findings into screens and flows -- how the product is used -- and the
  meaning archaeologist into terms, entities with their lifecycles,
  rules and roles -- what it means. Three check: the reconciler, the
  investigator, the critic. Each facet of the material has one owner:
  the data archaeologist reads the models and migrations, the test
  archaeologist the tests, the visual archaeologist measures the look
  and the usage archaeologist names what is one component; nothing is
  found twice. An integration, a setting, a trace, an asset, a log is a
  facet of one of them, not an agent of its own.
- **Which agents a material starts**: source code starts the code
  archaeologist (one per part), the data and the test archaeologists,
  the API archaeologist where routes answer a front end or a description
  is there, and the visual archaeologist where it holds style sheets or
  assets; a live site the web archaeologist, then the visual one on its
  captures; screenshots the visual archaeologist; documents the
  documentation archaeologist. The usage archaeologist follows wherever
  there is an interface, and the meaning archaeologist always. Every
  agent that did not run is said in the report to the user, with why.
- **At most six at once.** More are queued, and start as one finishes.
- **One browser.** The web archaeologist walks alone, and so does the
  investigator when it needs the browser; the visual archaeologist reads
  what the walk captured, after it.
- **The synthesisers come after the merge.** The usage and the meaning
  archaeologists read merged findings, never staging files, so that what
  they build on has its IDs; the meaning archaeologist reads the usage
  analysis too, to set a thing's state beside a screen's.
- **The main agent reads answers and reports, never staging files.**
  Each agent checks its own file with `spec.py merge --check` before it
  answers; what the main agent reads of its work is its eight-line
  answer and the report the merge keeps in `evidence/reports/`.
- **The product analyst is the main agent**: it holds what the user said
  -- the problem, the goals, the scope, the decisions -- and writes the
  specification from that and from the analyses together, through the
  operations.

## Starting an agent

Its whole task is this, with what is in angle brackets filled:

```
You are the <role> of the product specification in <folder>. The skill is in <skill>.
Read <skill>/agents/rules.md, then <skill>/agents/<brief>.md, and work as they say.
Your sources: <each by its ID, as `python app/spec.py node S2` shows it, and the part of it that is yours>.
The scope: <what of the product the specification is about, as the user chose it>.
<For the web archaeologist and the investigator: the address, the hosts in scope, how to enter, and that you
are the only agent using the browser.>
Write only what your brief names. When you are done, answer as rules.md says.
```

Nothing else of the conversation goes into it: an agent reads its
sources, not the main agent's expectations of them.

## Merging

Each agent checks its own staging file before it answers, with `python
app/spec.py merge evidence/staging/<its file> --check`, which judges the
file as the merge will and writes nothing; so what reaches the merge has
been corrected by whoever wrote it, and the main agent sends nothing
back. As each agent answers, the main agent runs `python app/spec.py
merge evidence/staging/<its file>` -- that one file; `merge` alone takes
every staging file, and is for when all have answered, since an agent
still writing its file would have it taken half done.

The merge is all or nothing. It refuses the whole file, saying every
reason, while a facet of its role has no row or a row says other than
`found`, `none` with where it looked, or `n/a` with why; while a finding
names a source there is not, a lens or a word of Seen there is not, says
nothing of what was found, or carries no quote though it was `seen`,
`run` or `said`; while a quote is not in the file its Where names, or that
file is a file of data; while a finding is one the specification holds
already. Otherwise it makes one change: a source the agent declared
added with the next free ID, each finding a node with the next `E`, each
Coverage row a line of its source's coverage with the print of what the
part is now, a version the source lacks written. What the agent said of
its work -- its facets, its disagreements, its report -- is kept in
`evidence/reports/<file>.md`, so that what it looked at and found nothing
in stays on record; its disagreements are gathered in
`evidence/staging/disagreements.md` for the reconciler, which `spec.py
open` lists, and `ready` refuses, while it stands. The main agent writes
each contradiction the reconciler proposes that holds, `do add
contradiction "<what disagrees>" between="E3, E9"`, with the question
that asks it, and then removes the file. The staging file goes once it is
merged.

## The analysis

The usage archaeologist's `evidence/analysis/usage.md` says which views
are one screen and of what kind, the navigation, the components, and
each screen's states, observed and likely; and the entry points, the
goals, the flows with their branches, the decisions, the states each flow
ends in, and who may take which path. The meaning archaeologist's
`evidence/analysis/meaning.md` says the terms and their aliases, the
entities with their lifecycles, the rules with their exceptions, the
roles and what each may do. The product analyst writes the screens,
their states and transitions, the flows, the Domain and the requirements
from them -- each piece still naming the finding it rests on, in its
Evidence column or as a finding that `became` it.

## The critic

Once the specification is written, the critic is started on the folder
alone. It begins from `spec.py open` -- the requirements on weak ground,
the findings that became nothing, what is to investigate -- and answers
each of its facets. Its objections come back as staged findings and as
its report; the main agent merges the findings and settles each
objection: a correction, a contradiction, an open question, or an
investigation.
