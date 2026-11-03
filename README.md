# specs-builder

Describe a product in your own words, and Claude writes its specification with
you: what it must do and why, its requirements, its screens with working
prototypes, and the questions nobody has answered yet. You read it all as a small
website on your own computer, with a map of how everything connects.

It's a skill for [Claude Code](https://code.claude.com/docs/en/quickstart.md),
Anthropic's coding assistant.

**New to all this? Start with [GETTING-STARTED.md](GETTING-STARTED.md).** It
assumes you've never used a terminal, and takes about 20 minutes.

## In short

1. Install Python 3.14 or later, and Claude Code.
2. Run `check-setup.cmd` on Windows, or `sh check-setup.sh` on macOS and Linux.
3. Run `open-example.cmd`, or `sh open-example.sh`, to see a finished example.
4. Start `claude` in this folder and say:

   > Use specs-builder to write a spec for a portal where customers download
   > their invoices.

You need a paid Claude plan to write specifications. Reading one needs only Python
and a browser.

## What's in this folder

| | |
|---|---|
| [GETTING-STARTED.md](GETTING-STARTED.md) | Setup and first use, step by step |
| `check-setup` | Checks your computer, and says what's missing |
| `open-example` | Opens a finished example in your browser |
| `.claude/skills/specs-builder/` | The skill itself |
| [`README.md`](.claude/skills/specs-builder/README.md) there | What the skill does |
| [`TUTORIAL.html`](.claude/skills/specs-builder/TUTORIAL.html) there | Make one small website with Claude Code, step by step, then see a full-size one |
| [`USER-MANUAL.html`](.claude/skills/specs-builder/USER-MANUAL.html) there | Everything, from zero, in the `user-manual/` pages |
| [`SETUP.md`](.claude/skills/specs-builder/SETUP.md) there | Setup in technical detail, and how to run its tests |
| `.claude/skills/specs-builder/examples/` | Seven finished specifications to explore. Everything in them is made up |
| `targets/novalife/` | A real project: the specification of the NovaLife Clinic website. Open it with `open-novalife` |

`.claude` starts with a dot, so your computer may hide it. It's there.

## Licence

[MIT](LICENSE). What it uses from others is in
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
