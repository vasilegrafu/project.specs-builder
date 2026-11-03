# Building the product from this specification

This folder is a product specification, whole in itself. It says what the product must do and be; it never says how to
build it. The technology, the architecture and the code are yours, or the person's you build for. This guide is the
procedure, for an agent of any make, in any technology. It needs Python 3.14 or later to run `app/spec.py`, and nothing
else. People read the same specification in its application, `index.cmd` or `index.sh`.

## What you build from

- **The answers of `app/spec.py`**: every requirement with its acceptance criteria, every entity with its fields and
  lifecycle, every rule, every role and what it may do, every flow, every screen with who opens it, what it shows, its
  states, its layout and each element of its prototype, every component, every endpoint, and what holds over the whole:
  the users, the qualities, the constraints, the decisions. They are read from `data/` as it stands. `export --model`
  writes them as JSON files where a program of yours wants them.
- **What draws the look**, in `prototypes/`: each screen's prototype (`prototypes/screens/`), each component's drawings
  (`prototypes/components/`), the page around them (`page.html`), the product's styles (`assets/css/product.css`), its
  design tokens (`tokens.json`; `tokens` gives them as the CSS the page links, which no file holds). They are a picture
  to build to, in your technology, never code to copy. `look` tells you which to open; `outline`, `words`, `forms`,
  `links`, `states` and `styles` read a screen's prototype for you. To
  see one drawn, `python app/serve.py --port 8765`, then `http://127.0.0.1:8765/prototype/SC3.html`, with `?state=<state>`
  or `?as=<variant>`.
- **The reference data**: `prototypes/assets/js/sample.js` where the specification has one (`sample`), and the words of
  the prototypes: the people, the times, the prices, the texts the product shows. Seed the product's data from them
  where the specification says nothing else, and ask for what they do not hold.
- **Nothing else.** `app/`, `.cache/`, `export/` and `stamps/` belong to the tool, and are never edited by hand.
- **What it does not hold, you design**: the architecture, and where `list endpoint` says no API is specified, the API,
  from the screens' data and the requirements. Say in your plan what you designed.

## The procedure

1. **Check it can be trusted**: `python app/spec.py verify`. If it exits 1, the data does not load, or something changed
   and was not reviewed, and every answer says which: say so to the person, and build only what they agree to.
2. **Learn the product**: `overview`. Read what holds over the whole -- the qualities (accessibility, speed,
   availability), the constraints and the decisions -- before any code: they bind every slice.
3. **Agree a plan**: `plan` gives the slices in the order to build them. First the foundation everything stands on (the
   document, the rules, the roles, the data, the design's foundations and components), then the screens and endpoints no
   flow passes, then one slice for each flow. A requirement is completed in the last slice that builds something showing
   it, never before the first flow that names it or what it depends on; `tests <slice>` says which it completes and which
   it only carries on.
   Choose the technology and the architecture with the person, and write a short plan of how. The specification says
   what and why, never how.
4. **Build each slice, in order**:
   1. `unit <slice>`: all the slice needs, in one answer. Where it says what it left out, ask for that too.
   2. `open <slice>`: what is not settled in it. Ask the person; never decide it in code. Build what does not depend on
      it meanwhile.
   3. `tests <slice>` (`--gherkin` for scenarios): write the tests first, each naming its case's ID, as `R4.1` or `R4_1`, in its name
      or a comment beside it: those names are all that ties the code to the specification, and an ID never moves. A
      criterion that names a day or an hour assumes a clock: set the test's clock to it, and keep the product's time
      zone in one place.
   4. `look <screen>` for each screen and `look <component>` for each component: open the prototype and find each element
      by its selector, as `[data-el="3"]`. Or ask: `outline <screen>` for its elements, `words` for its copy, `forms`
      for its fields, `states` for what each state changes, `styles <element>` for its values, `schema` and `lifecycle`
      for the data, `permissions` for who may, and `tests <screen> --ui` for what a test of it checks.
   5. Write the code. Name the requirement's ID in the code and in the commit that carry it, so that a requirement is
      found from the code.
   6. The slice is done when its tests pass and `coverage --target <your code>` names every criterion of every
      requirement it completes. A slice that carries on a requirement another slice completes builds its part of it;
      the requirement is done in the slice that completes it. Test a criterion the way it says, through what it names:
      `coverage` reads names, so a test that stands in for one it cannot run yet hides the gap. Where a criterion names
      what a later slice builds, test what exists now, say what is left, and finish it in that slice.
5. **A must before a should; never a wont.** `overview` and `plan` list what is never built.
6. **Record what you built from.** When the build is done and the person agrees, propose `snapshot --target <your code>`
   and run it once they say yes: it writes the specification as it stands into your code project's
   `.snapshots/specs-builder/`. Commit it with the code, so that whoever builds next, on any machine, knows what it was
   built from. It remembers where the code is, so `coverage` needs no `--target` after it.
7. **When the specification changes**: `changed --target <your code>` says what moved since that snapshot: each node new,
   gone or changed with its before and after, each screen's elements as its prototype draws them, the styles, the tokens
   and the sample data, with the slices to build again, the tests to run again and those to take out. Build only those,
   run those tests, then propose a new snapshot. No git is needed.

## Rules

- Never decide in code what the specification leaves open: an open question, an addition not confirmed. Ask the person,
  and leave the question for whoever keeps the specification: `ask "<question>" --about <IDs> --by "<who>"`.
- Never add behaviour the specification does not ask for; never leave out what it asks for. If you think it is wrong, say
  so: the person changes the specification, and the next answer reads it as changed.
- Keep the record of what is built in your code project, not here: this folder says what is wanted, not what is done.
- If a question cannot be answered from these, `find <words>` searches every node, and `node <ID> --depth 2` shows what
  is around it.

## The commands

`app/guide/query.md` lists each command with an example. `app/guide/model.md` is the data's form: every kind of node,
every field, every relation.
