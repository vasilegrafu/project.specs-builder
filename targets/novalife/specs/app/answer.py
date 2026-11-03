"""An answer to whoever builds from the specification: markdown a person or an agent reads, or JSON for a program.

Each answer has a title, its sections, what to ask next and how the command exits. Markdown stays within a budget of
characters: the lightest sections are left out first, and the answer says which, with the command that gets each.
JSON holds everything, so it is not cut.
"""
from __future__ import annotations

import json

BUDGET = 40000                                          # characters an answer holds unless --budget says otherwise


def cell(said: object) -> str:
    """Anything as one cell of a markdown table."""
    if isinstance(said, list):
        said = ", ".join(str(x) for x in said)
    return " ".join(str(said or "").split()).replace("|", "\\|") or "-"


def table(head: list[str], rows: list[list[object]]) -> list[str]:
    """A markdown table; nothing where there are no rows."""
    if not rows:
        return []
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head),
            *("| " + " | ".join(cell(c) for c in row) + " |" for row in rows)]


def short(text: object, most: int = 90) -> str:
    said = " ".join(str(text).split())
    return said if len(said) <= most else said[:most - 1].rstrip() + "…"


class Answer:
    """What a command answers: its sections, each with a weight -- the lightest left out first when the budget is
    spent -- what it holds as data, what to ask next, and how the command exits."""

    def __init__(self, title: str) -> None:
        self.title = title
        self.sections: list[tuple[int, str, list[str], str]] = []    # weight, heading, lines, how to ask for it
        self.data: dict = {}
        self.next: list[str] = []
        self.exit = 0
        self.warning = ""                               # what must be said before the answer: nodes that are stale

    def add(self, heading: str, lines: list[str], weight: int = 5, ask: str = "") -> None:
        if lines:
            self.sections.append((weight, heading, lines, ask))

    def json(self) -> str:
        return json.dumps({"answer": self.title, **({"warning": self.warning} if self.warning else {}),
                           **self.data, "next": self.next}, indent=1, ensure_ascii=False, default=str) + "\n"

    def markdown(self, budget: int = BUDGET) -> str:
        spent, chosen, left = len(self.title), set(), []
        for i in sorted(range(len(self.sections)), key=lambda i: -self.sections[i][0]):
            _, heading, lines, ask = self.sections[i]
            size = sum(len(line) + 1 for line in lines) + len(heading) + 4
            if budget and spent + size > budget and chosen:
                left.append((heading, ask))
                continue
            chosen.add(i)
            spent += size
        out = [f"# {self.title}", ""] + ([f"> {self.warning}", ""] if self.warning else [])
        for i, (_, heading, lines, _) in enumerate(self.sections):
            if i in chosen:
                out += ([f"## {heading}", ""] if heading else []) + lines + [""]
        if left:
            out += ["## Left out, to keep this answer within its budget", "",
                    *(f"- {h or 'a part of it'}" + (f": `{a}`" if a else "") for h, a in left), ""]
        if self.next:
            out += ["Next: " + " · ".join(f"`{n}`" for n in self.next), ""]
        return "\n".join(out).rstrip("\n") + "\n"
