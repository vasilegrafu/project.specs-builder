"""Edits of one node's file, at the level of its lines.

A header key set or taken out, a section's text replaced, a cell of a row changed, a row or an item added or taken
out: each takes a file's text and gives it back changed only where it must be, so that a file written by hand keeps
its form everywhere else -- its spacing, its order, its own words. What is wrong with the result is the loader's to
say; these only place the change.
"""
from __future__ import annotations

import re

import nodefile

FENCE = "---"


def split(text: str) -> list[str]:
    return text.replace("\r\n", "\n").split("\n")


def joined(lines: list[str]) -> str:
    text = "\n".join(lines).rstrip("\n") + "\n"
    return re.sub(r"\n{3,}", "\n\n", text)


def fence_end(lines: list[str]) -> int:
    if not lines or lines[0].strip() != FENCE:
        raise ValueError("a node's file starts with a line `---`")
    return next(i for i in range(1, len(lines)) if lines[i].strip() == FENCE)


def set_header(text: str, key: str, value: str, order: list[str]) -> str:
    """The header's `key:` set to `value`, or taken out where `value` is empty; a new key goes where the grammar
    orders it among those there."""
    lines = split(text)
    end = fence_end(lines)
    at = next((i for i in range(1, end) if lines[i].partition(":")[0].strip().lower() == key), None)
    if at is not None:
        if value:
            lines[at] = f"{key}: {value}"
        else:
            del lines[at]
        return joined(lines)
    if not value:
        return joined(lines)
    rank = {k: i for i, k in enumerate(order)}
    place = 1
    for i in range(1, end):
        there = lines[i].partition(":")[0].strip().lower()
        if there in rank and rank[there] <= rank.get(key, len(order)):
            place = i + 1
    lines.insert(place, f"{key}: {value}")
    return joined(lines)


def sections(lines: list[str]) -> list[tuple[str, int, int]]:
    """Each section's title, the line its heading is on (the closing fence for the text under the header), and
    the line after its last."""
    end = fence_end(lines)
    outside = nodefile.outside_fences(lines, end + 1)
    heads = [(i, lines[i][3:].strip()) for i in sorted(outside) if lines[i].startswith("## ")]
    out = [("", end, heads[0][0] if heads else len(lines))]
    for n, (i, title) in enumerate(heads):
        out.append((title, i, heads[n + 1][0] if n + 1 < len(heads) else len(lines)))
    return out


def set_section(text: str, title: str, body: str, order: list[str]) -> str:
    """A section's text replaced by `body`; a new section placed where the grammar orders it; one given no text
    taken out, its heading with it."""
    lines = split(text)
    found = {t: (start, stop) for t, start, stop in sections(lines)}
    block = ["", *split(body.strip()), ""] if body.strip() else []
    if title in found:
        start, stop = found[title]
        if title == "":
            lines[start + 1:stop] = block or [""]
        elif block:
            lines[start + 1:stop] = block
        else:
            del lines[start:stop]
        return joined(lines)
    if not block:
        return joined(lines)
    rank = {t: i for i, t in enumerate(order)}
    after = [t for t, _, _ in sections(lines) if t and rank.get(t, len(order)) > rank.get(title, len(order))]
    place = found[after[0]][0] if after else len(lines)
    lines[place:place] = [f"## {title}", *block]
    return joined(lines)


def row(cells: list[str]) -> str:
    return "| " + " | ".join(" ".join(str(c).split()).replace("|", "\\|") for c in cells) + " |"


def set_cell(text: str, line: int, column: int, value: str) -> str:
    lines = split(text)
    cells = nodefile.cells(lines[line - 1])
    cells[column] = value
    lines[line - 1] = row(cells)
    return joined(lines)


def append_row(text: str, title: str, cells: list[str], head: list[str], order: list[str]) -> str:
    """A row added under the last of a section's table -- the section, its header and its rule made where there
    is none yet."""
    lines = split(text)
    found = {t: (start, stop) for t, start, stop in sections(lines)}
    if title not in found:
        return set_section(text, title, "\n".join([row(head), "|" + "---|" * len(head), row(cells)]), order)
    start, stop = found[title]
    last = max((i for i in range(start + 1, stop) if lines[i].strip().startswith("|")), default=None)
    if last is None:
        lines[start + 1:stop] = ["", row(head), "|" + "---|" * len(head), row(cells), ""]
    else:
        lines.insert(last + 1, row(cells))
    return joined(lines)


def append_item(text: str, title: str, item: str, order: list[str]) -> str:
    """An item, `- …`, added after the last of a section's list -- the section made where there is none yet."""
    lines = split(text)
    found = {t: (start, stop) for t, start, stop in sections(lines)}
    if title not in found:
        return set_section(text, title, f"- {item}", order)
    start, stop = found[title]
    last = max((i for i in range(start + 1, stop) if lines[i].startswith("- ")), default=None)
    if last is None:
        lines[start + 1:stop] = ["", f"- {item}", ""]
    else:
        while last + 1 < stop and lines[last + 1].startswith("  ") and lines[last + 1].strip():
            last += 1                                   # past the item's continuation lines
        lines.insert(last + 1, f"- {item}")
    return joined(lines)


def set_line(text: str, line: int, value: str) -> str:
    lines = split(text)
    lines[line - 1] = value
    return joined(lines)


def delete_line(text: str, line: int) -> str:
    lines = split(text)
    del lines[line - 1]
    while line - 1 < len(lines) and lines[line - 1].startswith("  ") and lines[line - 1].strip():
        del lines[line - 1]                             # an item's continuation goes with it
    return joined(lines)


def new_node(header: list[tuple[str, str]], sections_said: list[tuple[str, str]]) -> str:
    """A new node's file: its header, then its text and its sections, each as given."""
    out = [FENCE, *(f"{k}: {v}" for k, v in header if v), FENCE]
    for title, body in sections_said:
        if not body.strip():
            continue
        out += ([""] if not title else ["", f"## {title}"]) + ["", *split(body.strip())]
    return joined(out)
