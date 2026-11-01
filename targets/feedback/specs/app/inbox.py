"""What waits to be taken in: a change requested in the application, or a question from those building from the
specification about what it does not settle. Written into inbox.md beside the data -- never into the data, whose
keeper decides -- and taken in through Claude Code: the change made and the entry closed, or made an open question.

    spec.py ask "Does the limit count lines from another device?" --about R4 --by "the builder"
    spec.py inbox                        what waits, each with its number
    spec.py inbox --raise 2 [--answers the product side]   made an open question, tied to what it is about
    spec.py inbox --close 2              done or answered in the specification; taken out

The file is a table a person can read and edit; it is in git, so nothing asked is lost. While anything waits in
it, `ready` holds the specification and `verify` says so to whoever builds.
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

import load as loading

INBOX = "inbox.md"
HEAD = ("# Waiting to be taken in\n\n"
        "Changes requested in the application, and questions those building from the specification asked back: each\n"
        "is made in the specification and closed (`spec.py inbox --close <no>`), or made an open question (`--raise <no>`).\n"
        "Written by the application and `spec.py ask`; never part of the data.\n\n"
        "| No | Asked | By | About | What it asks |\n|---|---|---|---|---|\n")


def natural(ident: str) -> list:
    return [int(x) if x.isdigit() else x for x in re.findall(r"\d+|\D+", str(ident))]


def cells(line: str) -> list[str]:
    """A table line's cells, a `\\|` inside one kept as a bar."""
    inner = line.strip()[1:-1] if line.strip().endswith("|") else line.strip()[1:]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", inner)]


def read(root: Path) -> list[dict]:
    """What waits, in the order it was asked."""
    path = root / INBOX
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        row = cells(line)
        if len(row) < 5 or not row[0].isdigit():
            continue                                  # the table's head and its rule
        out.append({"no": int(row[0]), "asked": row[1], "by": row[2],
                    "about": [i for i in re.split(r"[,\s]+", row[3]) if i], "question": row[4]})
    return out


NEXT = re.compile(r"<!-- next: (\d+) -->")


def next_no(root: Path) -> int:
    """The number the next question takes: never one given before, though what had it was taken out."""
    path = root / INBOX
    held = NEXT.search(path.read_text(encoding="utf-8")) if path.is_file() else None
    return max([int(held.group(1)) if held else 1] + [e["no"] + 1 for e in read(root)])


def write(root: Path, entries: list[dict], after: int | None = None) -> None:
    esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")  # noqa: E731
    after = after if after is not None else next_no(root)
    body = "".join(f"| {e['no']} | {esc(e['asked'])} | {esc(e['by'])} | {', '.join(e['about'])} | {esc(e['question'])} |\n"
                   for e in entries)
    path = root / INBOX
    fresh = path.with_suffix(".md.part")
    fresh.write_text(HEAD.replace("\n\n|", f"\n<!-- next: {after} -->\n\n|", 1) + body, encoding="utf-8", newline="\n")
    os.replace(fresh, path)


def ask(root: Path, question: str, about: list[str], by: str, done: loading.Load | None = None) -> dict:
    """A question or a request put in the inbox: what it is about must be nodes of the specification. `done` is the data as
    loaded, where the asker already holds it."""
    question = " ".join(question.split())
    if not question:
        raise ValueError("a question says what it asks")
    if not by.strip():
        raise ValueError("a question says who asks it: --by")
    done = done or loading.load(root)
    unknown = [i for i in about if i not in done.nodes]
    if unknown:
        raise ValueError(f"{', '.join(unknown)}: no node has that ID -- --about names what the question is about")
    entries = read(root)
    entry = {"no": next_no(root), "asked": datetime.now().strftime("%Y-%m-%d %H:%M"),
             "by": by.strip(), "about": sorted(dict.fromkeys(about), key=natural), "question": question}
    write(root, entries + [entry], entry["no"] + 1)
    return entry


def take(root: Path, no: int) -> dict:
    """An entry taken out of the inbox."""
    entries = read(root)
    found = next((e for e in entries if e["no"] == no), None)
    if found is None:
        raise KeyError(f"#{no}: nothing waits in the inbox with that number")
    write(root, [e for e in entries if e["no"] != no])
    return found


def raise_(root: Path, no: int, answers: str = "", who: str = "") -> str:
    """An entry made an open question of the specification, tied to what it is about, then taken out: the ID made."""
    import logic                                      # here, not above: the logic reads the inbox through finish
    entry = next((e for e in read(root) if e["no"] == no), None)
    if entry is None:
        raise KeyError(f"#{no}: nothing waits in the inbox with that number")
    words = entry["question"]
    name = words if len(words) <= 60 else words[:57].rsplit(" ", 1)[0] + "..."
    op = ["add", "question", name, f"question={words}", f"why=asked by {entry['by']} while building, {entry['asked']}"]
    if entry["about"]:
        op.append(f"about={', '.join(entry['about'])}")
    if answers.strip():
        op.append(f"answers={answers.strip()}")
    result = logic.apply(root, [op], who=who or "the keeper", because=f"inbox #{no}, asked by {entry['by']}")
    if result.problems:
        raise ValueError("; ".join(m for _, _, m in result.problems))
    take(root, no)
    return result.applied[0].split("->")[-1].strip()
