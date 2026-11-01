# What there is to build from

The scout's report: what each material holds, what of the specification can be built from all of it, and what reading it would take. Choose what to build before anything else is read.

- **Scouted:** 2026-10-11
- **Material:** ../dev

## Material

| Material | Kind | Files | What it holds |
|---|---|---|---|
| ../dev | code | 10 | Python 8; 1 file(s) of tests; 2 document(s) |

## What can be built

Each part of the specification, and whether the material can build it: `full`, `part`, `none`; for the prototype `alike` -- made alike to how the product looks -- or `grey`.

| Part | Can be built | From | What would make it whole |
|---|---|---|---|
| Evidence | full | every material, each with what was read of it | - |
| Requirements | full | code: what it does, its rules, limits and words; documents: what was asked for | the why -- the problem, the goals and their numbers, the priorities -- is asked of the user, always |
| Flows | part | documents: workflows; their stories, from the users and the goals | a running site, or the code of the interface, to see each step and branch; who the users are and the goals each flow serves, from the user |
| Design System | none | - | a running site or the style sheets, for the values; a look nobody gave is asked, not invented |
| Screens | none | - | a running site, to reach each state; until then each unseen state is likely, with how to find it |
| Prototype | none | - | screenshots or a running site, to make it look as the product does |
| Gaps | full | everything not settled, not read or not accounted for | - |

## What it would take

| Wave | Agent | Reads |
|---|---|---|
| Collect | code archaeologist | ../dev: the whole |
| Collect | data archaeologist | ../dev: its models, migrations, enums and seeds |
| Collect | test archaeologist | ../dev: its tests, fixtures and mocks, 1 file(s) |
| Collect | documentation archaeologist | the documents in ../dev |
| Synthesise | meaning archaeologist | the merged findings, and the usage analysis |
| Reconcile | reconciler | the disagreements the merge kept |
| Investigate | investigator | what the Gaps page says to find out |
| Critique | critic | the whole, and nothing of what was meant |

About 0 route(s), 0 endpoint(s), 0 view(s), 1 file(s) of tests and 2 document(s) to account for; 8 agent(s) in all, at most six at a time, one at a time in the browser.

## The depths

How far the reading goes, chosen at the gate: the agents each depth starts, and when it stops.

| Depth | Agents | Who runs | Stops when |
|---|---|---|---|
| quick | 5 | the collectors and the synthesisers; no reconciler, investigator or critic | the document is written; what is not settled is listed, not chased |
| standard | 8 | all, the investigator and the critic once | the gaps above the line are settled or reported, the critic's objections answered once |
| full | 8 to 12 | all, the investigator and the critic up to three times | the Gaps page holds only what is for people, or three rounds are done |

## What changed since

This specification has read this material before, and no part it hashed has changed since.

## To choose

- What the material is to the product: `rebuild`, `extend`, `example`, `intent` or `evidence`.
- Which parts of the specification to build, from the table above.
- What of the material is in scope: what is left out that a reader would expect becomes a non-goal.
- The depth: `quick`, `standard` or `full`, from the table above.
- Why: what the work is for, what should be better afterwards and by what number, and who uses it.
