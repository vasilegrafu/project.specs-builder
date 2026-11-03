# Setting up specs-builder

## What you need

| You need | For | Check with |
|---|---|---|
| **Python 3.14 or later** | Everything. Nothing else has to be installed | `python --version` |
| **A browser** | Reading a specification, and requesting a change | |
| **Claude Code** | Writing and changing a specification. Reading one needs only Python and a browser | |
| **An internet connection** | Only to draw flow diagrams, in the application and in an export, and the Graph page. Without one you see the diagram's text, and the Graph page says so | |

The application uses Python's standard library and nothing more. It listens
on `127.0.0.1` only, so nothing outside your computer can reach it.

### Optional extras

Both of these only help the skill read existing material. Leave them out and
it still works.

| Extra | What it adds | Without it |
|---|---|---|
| **tree-sitter**, with a grammar for each language | `scan_code.py` reads code by its structure | Python is read by `ast` and other languages by patterns, and the output says which |
| **Playwright for Python** | `crawl.py` walks a whole site by script | The walk is done by hand in the session's browser |

To add Playwright:

```
pip install playwright
python -m playwright install chromium
```

`crawl.py` has not yet been run with Playwright in a real session, so treat
the walk by script as untested.

## Install it

1. Put the folder where Claude Code finds skills: `.claude/skills/specs-builder`
   in a project, or `~/.claude/skills/specs-builder` for all your projects.
2. Check Python, using the command your launchers will use:

   | System | Command | The launcher that uses it |
   |---|---|---|
   | Windows | `python --version` | `index.cmd` |
   | macOS, Linux | `python3 --version` | `index.sh` |

3. Open an example, to prove it runs. Run `examples/shop/specs/index.cmd`, or
   `sh examples/shop/specs/index.sh`. Your browser should open on Voltline.

## Check it works

The selftest proves the whole skill on copies of the shop, planting each
fault it checks for. From the repository's root:

```
python .claude/skills/specs-builder/tests/selftest.py
```

It takes between two and six minutes, and it ends with `PASSED` or `FAILED`
and a count. `--list` names its areas, and `--only building` runs one in
seconds. Each specification can also check itself:

```
python app/spec.py check
```

Run that from the specification's folder. It ends with
`PASSED -- 0 problem(s)`, or names each problem with its file and line.

## Start a specification

The skill does this for you. To do it by hand:

```
python .claude/skills/specs-builder/scripts/new_spec.py invoices --name "Invoices" --kind application --summary "Customers take an invoice out of the portal as a PDF, so that they stop writing to support for it."
```

`--kind` is one of `application`, `api`, `library`, `part` or `process`, or a
mix such as `"application, api"`. The new folder holds everything: its data,
its own copy of the application, and its launchers.

Keep the folder in git, apart from `.cache/` and `export/`, which its own
`.gitignore` leaves out.

## Open a specification

| | |
|---|---|
| Windows | Run `index.cmd` in the specification's folder |
| macOS, Linux | Run `sh index.sh` in the specification's folder |
| On a port of your choosing | `python app/serve.py --open --port 8765` |

Close the window, or press Ctrl+C, to stop it. While it runs, it picks up any
change to the data by itself.

## Bring an old specification up to date

A specification keeps its own copy of the application, so a newer skill doesn't
reach it until you ask. Close that specification's window first, then run:

```
python .claude/skills/specs-builder/scripts/new_spec.py my-spec --update-app
```

Your data is not touched. A newer application can ask more of the data, so the
specification is checked under it. If it doesn't pass, it keeps the application it
had, and you're told what to mend. Use `--force` to take the new one anyway and mend
the data under it.

**Do not start an application from the skill's own `app/` folder while you
copy.** A running server can lock the folder, so the delete fails and the
copy goes wrong. Open a specification from its own folder instead.

## When something goes wrong

| What you see | What it means, and what to do |
|---|---|
| `specs-builder needs Python 3.14 or later` | Your `python` is older. Install 3.14, or put it first on your PATH |
| `Python was not found` on Windows | Windows is offering its Store shortcut. Install Python and tick "Add to PATH", or turn the alias off under Settings > Apps > Advanced app settings > App execution aliases |
| `index.sh` says `python3` is not found | The launcher asks for `python3`. Install it, or run `python app/serve.py --open` |
| The window opens and closes at once | Run `python app/serve.py --open` in a terminal to read the error |
| A button or view you expect is missing | The tab has old code. Press Ctrl+F5 |
| A flow shows text instead of a diagram | There is no connection to the CDN that serves the diagram library. The steps below it say the same thing |
| `The graph is not drawn` | There is no connection to the CDN that serves D3. Each node's page still shows its links |
| Every view shows a list of problems | The data does not load, usually after a hand edit. Each problem names its file and line. Until it is fixed, the application shows the last good data |
| `refused` on an agreed specification | An agreed specification takes no changes. `python app/spec.py do set document status draft` opens it again |
