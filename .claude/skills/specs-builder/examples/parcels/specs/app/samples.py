"""What the sample data of the prototypes holds: `sample.js` read as a literal, never run."""
from __future__ import annotations

import re
from pathlib import Path

import prototypes

SAMPLE = f"{prototypes.PROTOTYPES}/assets/js/sample.js"


# --- sample data -----------------------------------------------------------------------------------------------------
class Literal:
    """A JavaScript literal -- an object, an array, a string, a number, true, false, null -- read as JSON reads it."""

    def __init__(self, text: str, at: int) -> None:
        self.text, self.at = text, at

    def gap(self) -> None:
        while self.at < len(self.text):
            if self.text[self.at].isspace():
                self.at += 1
            elif self.text.startswith("//", self.at):
                end = self.text.find("\n", self.at)
                self.at = len(self.text) if end == -1 else end
            elif self.text.startswith("/*", self.at):
                end = self.text.find("*/", self.at)
                self.at = len(self.text) if end == -1 else end + 2
            else:
                break

    def value(self) -> object:
        self.gap()
        char = self.text[self.at:self.at + 1]
        if char == "{":
            self.at += 1
            out = {}
            while True:
                self.gap()
                if self.text[self.at] == "}":
                    self.at += 1
                    return out
                key = self.value() if self.text[self.at] in "\"'`" else self.word()
                self.gap()
                if self.text[self.at] != ":":
                    raise ValueError(f"no colon after {key} at {self.at}")
                self.at += 1
                out[str(key)] = self.value()
                self.gap()
                if self.text[self.at] == ",":
                    self.at += 1
        if char == "[":
            self.at += 1
            items = []
            while True:
                self.gap()
                if self.text[self.at] == "]":
                    self.at += 1
                    return items
                items.append(self.value())
                self.gap()
                if self.text[self.at] == ",":
                    self.at += 1
        if char in "\"'`":
            end, chars = self.at + 1, []
            while self.text[end] != char:
                if self.text[end] == "\\":
                    end += 1
                    chars.append({"n": "\n", "t": "\t"}.get(self.text[end], self.text[end]))
                elif char == "`" and self.text.startswith("${", end):
                    raise ValueError("a template string with a value in it")
                else:
                    chars.append(self.text[end])
                end += 1
            self.at = end + 1
            return "".join(chars)
        found = re.match(r"-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", self.text[self.at:])
        if found:
            self.at += found.end()
            return float(found.group(0)) if re.search(r"[.eE]", found.group(0)) else int(found.group(0))
        word = self.word()
        if word in ("true", "false"):
            return word == "true"
        if word in ("null", "undefined"):
            return None
        raise ValueError(f"{word or char}: not a literal")

    def word(self) -> str:
        found = re.match(r"[A-Za-z_$][\w$]*", self.text[self.at:])
        if not found:
            raise ValueError(f"no name at {self.at}")
        self.at += found.end()
        return found.group(0)


def sample_values(root: Path) -> tuple[dict, list[str]]:
    path = root / SAMPLE
    values, failed = {}, []
    if path.is_file():
        text = path.read_text(encoding="utf-8-sig")
        for found in re.finditer(r"(?:window\.|\b(?:var|let|const)\s+)([A-Za-z_$][\w$]*)\s*=\s*(?=[\[{\"'`\d-])", text):
            try:
                values[found.group(1)] = Literal(text, found.end()).value()
            except (ValueError, IndexError) as problem:
                failed.append(f"{found.group(1)}: {problem}")
    return values, failed
