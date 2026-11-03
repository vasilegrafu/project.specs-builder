<!-- specs-builder README: written by the skill. What you add outside this block stays. -->
# Parcelpost: the product specification

This folder is the specification of Parcelpost: what it must do and be, how it is used and how it looks. It is whole in itself:
what people wrote, the application that shows it, and how to build from it.

## To read it

Open `index.cmd` on Windows, or run `sh index.sh` elsewhere, and the specification opens in your browser. It needs Python 3.14 or
later and nothing else. For someone without Python, `python app/spec.py export` writes it all as one HTML file.

## To build from it

Give the folder to a coding agent of any make. It reads [AGENTS.md](AGENTS.md) by itself, which sends it to
[app/guide/build.md](app/guide/build.md), the procedure in whatever technology. It asks with `python app/spec.py`, and
`python app/spec.py overview` is where it starts.

## What it holds

- `data/`: one file for each thing the specification says, in plain text.
- `prototypes/`: how the product looks and every word it shows.
- `evidence/`: what was read to write it, where anything was.
- `stamps/`: what was reviewed and agreed, kept by the tools and never edited by hand.
- `app/`: the application, the same for every specification. Close it and nothing is left running.
<!-- /specs-builder README -->
