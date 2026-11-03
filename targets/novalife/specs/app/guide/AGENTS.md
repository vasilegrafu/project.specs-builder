<!-- specs-builder: written by the skill. Change nothing between this line and the one that ends the block; write your own notes outside it. -->
# The specification in this folder

This folder is a product specification: what the product must do, how it is used and how it looks. People read it in its application, `index.cmd` or `index.sh`. An agent reads it, builds from it and changes it by the rules below. It says what and why, never how: the technology, the architecture and the code are yours, or the person's you build for.

## To read it

- Ask `python app/spec.py <command>`, from this folder or by its path from anywhere. It needs Python 3.14 or later and nothing else, and it answers from `data/` as it stands. `overview` first: it says what the product is and how to build it.
- `data/` holds one file for each thing the specification says, in plain text, and `prototypes/` holds how the product looks. Ask the tool rather than parsing them.
- An ID means one thing everywhere: `R` a requirement, `G` a goal, `Y` a quality, `L` a constraint, `D` a decision, `Q` an open question, `AD` an addition not confirmed, `K` a risk, `T` a term, `N` an entity, `B` a rule, `U` a role, `F` a flow, `SC` a screen, `C` a component, `FD` a foundation, `A` an endpoint, `S` a source, `E` a finding, `X` a contradiction. `R4.2` is a criterion of R4, `SC3.5` an element of SC3, `C1.2` a part of C1, `N1.open` a state of N1. An ID is never used for anything else, and never given again.
- `app/guide/query.md` lists every command, and `app/guide/model.md` is the data's form.

## To build from it

- Follow `app/guide/build.md`: the procedure, step by step, in whatever technology.
- `python app/spec.py verify` before building: if it exits 1, something changed and was not reviewed. Say so. Every answer says it too, first.
- `overview`, then `plan`, then for each slice `unit`, `open`, `tests` and `look`.
- What is drawn -- the prototypes, the components' drawings, the product's styles and tokens -- is a picture to build to in your technology, never code to copy. `look <screen>` names each, and `outline`, `words`, `forms`, `links`, `states` and `styles` read a screen's prototype for you. `schema`, `lifecycle`, `permissions`, `rules`, `glossary`, `qualities`, `messages`, `tokens`, `sample` and `openapi` give what the product means.
- Build what the requirements require, a `must` before a `should`. Never build a `wont`.
- Before any code, write a short plan of how it will be built and have it agreed.
- Each acceptance criterion becomes at least one test, named with its ID, as in `R12.1` or `R12_1`. Name the requirement's ID in the code and the commit that carry it, so that it is found from the code.
- A requirement is done when every one of its criteria passes. `python app/spec.py coverage --target <the code>` lists those no test names yet: it reads names, and running the tests is yours.
- Once a build is done and the person agrees, `python app/spec.py snapshot --target <the code>` records what it was built from, in the code's `.snapshots/specs-builder/`. Commit it with the code.
- When the specification changes, `python app/spec.py changed --target <the code>` says what moved since, before and after, with the slices to build again, the tests to run again and those to take out.
- Where the specification is silent, or says a thing is not settled, ask the person. `python app/spec.py ask "<question>" --about <IDs> --by "<who>"` leaves it for whoever keeps the specification, in `inbox.md`. Never decide it in code, and build what does not depend on it meanwhile.
- Keep the record of what is built in the code project, not here: this folder says what is wanted, not what is done. An agent that only builds changes nothing here but `inbox.md`, and that by `ask`.

## To change it

For whoever keeps the specification, with the specs-builder skill. An agent that only builds skips this part.

- Change the specification through its operations, never by writing into `data/`: `python app/spec.py do set R4 priority should --because Q3`. `do --help` lists them, `kinds` says what each kind holds, and `--dry-run` says what would change. Each is checked, written and logged, or refused with nothing changed.
- A piece marked `data-stamp` is written once, in `prototypes/shared/`: change it there, then run `python app/spec.py stamp`.
- Change a prototype by editing its file in `prototypes/`. An element's anchor, `data-el` or `data-part`, stays; what an element means is its row in the data.
- Never change `app/`, `.cache/`, `export/`, `stamps/` or the block of this file.
- Before a change, `impact <ID>` says what it reaches. After it, `stale` lists what stands on it: read each again, change what no longer holds, and `do confirm <ID> <print>`, with the print `stale` shows beside it: a confirmation with no print, or an older one, is refused. Never confirm what you have not read.
- `check` holds every file to the grammar, and `ready` says whether the specification may be agreed. While its status is `agreed`, a requirement changes only after `do set document status draft`.
- These rules are the short form. The specs-builder skill holds the whole procedure: use it for more than a small change.
<!-- /specs-builder -->
