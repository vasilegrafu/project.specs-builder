"""One node's file, read with the line each thing stands on.

A file is a header of `key: value` lines between two `---` lines, then the node's text in Markdown. The text before
the first `## ` heading is its main section; each `## ` heading opens a section its kind declares. What a section
means -- prose, a list of children, a list of actions -- is the grammar's to say; this module only splits the file
and says where each piece is, so that every fault is told at its line.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

FENCE = "---"


def cells(row: str) -> list[str]:
    """A table row's cells, the outer `|` taken off, a `\\|` kept as a `|` in its cell."""
    inner = row.strip()
    inner = inner[1:] if inner.startswith("|") else inner
    inner = inner[:-1] if inner.endswith("|") and not inner.endswith("\\|") else inner
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", inner)]


@dataclass
class Section:
    name: str                                   # "" for the text before the first heading
    line: int                                   # where it starts
    lines: list[tuple[int, str]] = field(default_factory=list)

    def first(self) -> int:
        """The line its words start on: its heading's line where it has none."""
        return next((number for number, raw in self.lines if raw.strip()), self.line)

    def text(self) -> str:
        """Its prose, as written, without the blank lines around it; a line written `\\# …`, so as not to be read as
        a heading, read as the `# …` it says."""
        return "\n".join(raw[1:] if raw.startswith("\\#") else raw for _, raw in self.lines).strip()

    def table(self) -> tuple[list[str], list[tuple[int, list[str]]], list[tuple[int, str]]]:
        """Its one Markdown table: the header's cells, each row's cells with its line, and what is wrong with its
        form. A `|` inside a cell is written `\\|`."""
        rows = [(n, raw.strip()) for n, raw in self.lines if raw.strip()]
        faults: list[tuple[int, str]] = []
        if not rows:
            return [], [], faults
        stray = [n for n, raw in rows if not raw.startswith("|")]
        for n in stray:
            faults.append((n, "a table's section holds only its table: every line starts with `|`"))
        rows = [(n, raw) for n, raw in rows if raw.startswith("|")]
        if len(rows) < 2 or not re.fullmatch(r"\|(\s*:?-+:?\s*\|)+", rows[1][1].replace(" ", "")):
            faults.append((rows[0][0] if rows else self.line, "a table starts with its header row, then a "
                                                               "`|---|---|` line under it"))
            return [], [], faults
        head = cells(rows[0][1])
        body = []
        for n, raw in rows[2:]:
            found = cells(raw)
            if len(found) != len(head):
                faults.append((n, f"this row has {len(found)} cells, and the table's header {len(head)}"))
                continue
            body.append((n, found))
        return head, body, faults

    def items(self) -> tuple[list[tuple[int, str]], list[int]]:
        """Its list items, `- …`, each with its line, a line indented under one taken as its continuation; and the
        lines that are neither, which a list section does not allow."""
        items: list[tuple[int, str]] = []
        stray: list[int] = []
        for number, raw in self.lines:
            if raw.startswith("- "):
                items.append((number, raw[2:].strip()))
            elif raw.startswith("  ") and raw.strip() and items:
                items[-1] = (items[-1][0], f"{items[-1][1]} {raw.strip()}")
            elif raw.strip():
                stray.append(number)
        return items, stray


@dataclass
class NodeFile:
    path: Path
    header: dict[str, tuple[str, int]] = field(default_factory=dict)       # key -> (value, line)
    sections: dict[str, Section] = field(default_factory=dict)
    faults: list[tuple[int, str]] = field(default_factory=list)


def read(path: Path) -> NodeFile:
    """The file split into its header and its sections, with what is wrong with its form."""
    held = NodeFile(path)
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != FENCE:
        held.faults.append((1, "a node's file starts with a line `---`, then its header"))
        return held
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == FENCE), None)
    if end is None:
        held.faults.append((1, "the header is never closed: a second `---` line ends it"))
        return held
    for i in range(1, end):
        raw = lines[i]
        if not raw.strip():
            continue
        key, colon, value = raw.partition(":")
        if not colon or not key.strip() or key != key.lstrip():
            held.faults.append((i + 1, f"`{raw.strip()}` is not a `key: value` line"))
            continue
        key = key.strip().lower()
        if key in held.header:
            held.faults.append((i + 1, f"`{key}` is said twice; first on line {held.header[key][1]}"))
            continue
        held.header[key] = (value.strip(), i + 1)
    current = held.sections[""] = Section("", end + 2)
    for i in range(end + 1, len(lines)):
        raw = lines[i]
        if raw.startswith("## "):
            name = raw[3:].strip()
            if name in held.sections:
                held.faults.append((i + 1, f"the section `{name}` is opened twice; first on line "
                                           f"{held.sections[name].line}"))
            current = held.sections[name] = Section(name, i + 1)
            continue
        if raw.startswith("# "):
            held.faults.append((i + 1, "a node's name is its header's `name:`, not a `# ` heading"))
            continue
        current.lines.append((i + 1, raw))
    return held
