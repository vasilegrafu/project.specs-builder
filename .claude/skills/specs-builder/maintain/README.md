# Keeping specs-builder

For whoever changes the skill itself. Nothing here is read while writing a
specification. [PRD.md](../PRD.md) says what the skill is built to do, and
[DECISIONS.md](../DECISIONS.md) every decision with its date.

## A change to the application

Edit `app/`, the skill's own copy. The tests and `new_spec.py` both read it,
and every other copy is made from it. Then:

```
python .claude/skills/specs-builder/maintain/roll_out.py
```

Every example, and every target beside the skill that has a specification,
takes it, with `AGENTS.md` written again from `app/guide/AGENTS.md`. Close any
specification that is open first. One that would not check clean under the new
application keeps the one it had, and the run says so: mend its data, or use
`--force`. `--check` says which are behind and changes nothing, and the selftest
runs it, so a copy left behind fails.

Don't roll out while the selftest runs: it reads the same files.

A command changed is changed in `app/guide/query.md` too. A view or a command
changed is said in the manual and the tutorial as well, in their HTML itself, for
nothing builds those pages: the selftest runs the worked example they hold, and
holds every command they name to the command line.

## The application's files

- `spec.py`, the command line; `serve.py` and `api.py`, the server and what it
  answers.
- `load.py`, `nodefile.py`, `prototypes.py`: the data read and held to
  `grammar.json`.
- `logic.py` and `edit.py`: every change.
- `review.py`: staleness.
- `finish.py`: what is open, impact, trace and ready.
- `content.py`: what a specification says, held to what it must say: the faults
  `open` lists and `ready` will not pass, and the gaps a review reads.
- `shared.py`: a piece the screens share, written once and stamped into each.
- `inbox.py`: what whoever builds asks back.
- `evidence.py`: the sources' places, the prints of what was read and the
  captured sites' checks.
- `merge.py` and `agents.json`: an agent's staging file judged and merged. Each
  role's facets are in its brief and in `agents.json`, and the selftest holds the
  two together.
- `query.py`: what a builder asks, with `model.py`, the slices, `drawn.py`, what
  the prototypes draw, `meant.py`, what the data means, and `answer.py`, how each
  is told.
- Under `drawn.py`: `markup.py`, a prototype's HTML as a tree; `cascade.py`, its
  styles resolved as a browser would; `samples.py`, its sample data; and
  `redrawn.py`, what moved in the drawing between two snapshots.
- `build.py`: snapshots, coverage and what moved.
- `matrix.py`: the Matrix.
- `export.py`: the one file for readers without Python.
- `guide/`: the instructions a folder carries, its README among them.
- `web/`: the views. `engine.js`, the routes and most views, loaded last;
  `evidence.js`, the evidence's views and the Markdown they are drawn from;
  `prototype.js`, the prototype as a tool; `menu.js`, the bar, its menus and search;
  `help.js`, the Help view; `card.js`, the ID cards and their Preview; `side.js`,
  the tree of a part; `graphmap.js` and `matrix.js`, the Graph and the Matrix;
  `flowmap.js`, a flow's diagram; `foundations.js`, what a foundation's rows look
  like; `theme.js`, the appearance; `request.js`, a request for a change;
  `runtime/`, what runs inside a prototype's frame.
- `web/style.css`: the look, its tokens first: surfaces, text in three steps, one
  accent, a colour for each part, the scales. A new rule takes its colours and
  sizes from them, and the selftest holds every text colour at 4.5:1. `maps.css`,
  `prototype.css` and `views.css` follow it, loaded in that order: their rules
  win in that order too, so a rule is not moved between them lightly.

## The tests

`tests/selftest.py` proves the whole skill on copies of the shop, each check
planting the fault it is about. It takes a few minutes: run it in the background
and report the result. Its areas are the files of `tests/areas/`, with what they
share in `tests/support.py`; `--only building` runs one, `--list` names them. An
area that crashes fails alone, and a check that fails says which of its conditions
did. A new check goes in the area it is about.

`tests/scale.py` is not a test: it times the application on 50,000 nodes.
`tests/drive.mjs` drives a real Chrome with real input for the Graph's walk and the
pictures: the skill needs nothing beside it.
