# specs-builder-2

A Claude Code skill that writes a product specification and keeps it as a
small local application, instead of a pile of documents.

You describe a product, or point at one that already exists. The skill
writes what it must do and why: goals, requirements with their acceptance
criteria, rules, flows, screens with working prototypes, endpoints, and the
questions nobody has answered yet. You read all of it in your browser, and
change it by asking Claude Code.

It works from start to finish. [What it cannot do yet](user-manual/limits.html)
lists the gaps.

## What makes it different

- **It is data, not pages.** Every goal, requirement and screen is one small
  text file. The application reads them, so there is nothing to keep in step
  by hand.
- **Every link is real.** "This screen shows R4" is a link the application
  can follow both ways, so it can answer why something exists and what a
  change would affect.
- **Every change is checked.** A change that would break the specification
  is refused whole, and every change is logged with who made it and why.
- **It says what is not settled.** Open questions, things the skill added
  on its own judgement, and work a change has made stale are all listed in
  one place, and a specification cannot be agreed while they stand.
- **Nothing to install but Python.** Each specification carries its own
  application, so it opens on any computer with Python 3.14.

New to it? The [tutorial](TUTORIAL.html) makes one small website with Claude Code,
step by step, then shows Voltline at full size. The [user manual](USER-MANUAL.html)
covers everything.

## Start

You need [Python 3.14 or later](SETUP.md#what-you-need) and a browser. Then,
in Claude Code, ask for it by name:

> Use specs-builder-2 to write a spec for a portal where customers download
> their invoices.

To read a product that already exists:

> Use specs-builder-2 to reverse-engineer the app in `./my-app`.

To see a finished one first, open an example. On Windows:

```
.claude\skills\specs-builder-2\examples\shop\specs\index.cmd
```

On macOS or Linux:

```
sh .claude/skills/specs-builder-2/examples/shop/specs/index.sh
```

Your browser opens on Voltline, a made-up electronics shop. Press the **?**
in the bar for the tour.

## The documents

| Read this | For |
|---|---|
| [SETUP.md](SETUP.md) | Installing it, checking it works, and fixing what goes wrong |
| [TUTORIAL.html](TUTORIAL.html) | Learning it: one small website made step by step, from a sentence to a prototype |
| [USER-MANUAL.html](USER-MANUAL.html) | Everything, from zero: what a specification is, working with Claude, how to read each module, a change from start to finish, and every command |
| [examples/README.md](examples/README.md) | Seven finished specifications to read and copy from |
| [SKILL.md](SKILL.md) | What Claude follows when it uses the skill |
| [PRD.md](PRD.md) | Why it is built this way: every decision and its date |

## What is in this folder

| Folder | Holds |
|---|---|
| `app/` | The application. Every specification gets its own copy |
| `scripts/` | Starting a specification, and reading code, sites and API descriptions |
| `agents/` | The briefs of the agents that read existing material |
| `references/` | How each part of a specification is written |
| `examples/` | Seven products and the specification of each |
| `tests/` | The selftest, which proves the whole skill on copies of the shop |
