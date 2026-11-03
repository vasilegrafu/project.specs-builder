"""A prototype read as a browser would parse it: its marks as a tree, each with where it stands, what shows it and what
it holds. Nothing here knows a specification's data: `drawn.py` asks what a screen draws of this."""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import prototypes

HANDLE_RE = re.compile(r"^(SC\d+|C\d+)\.(\d+)$")
SCREEN_FILE_RE = re.compile(r"^(SC\d+)\.html$")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
IMPLIED = {"li": {"li"}, "p": {"p"}, "option": {"option"}, "tr": {"tr", "td", "th"}, "td": {"td", "th"}, "th": {"td", "th"},
           "dt": {"dt", "dd"}, "dd": {"dt", "dd"}}          # a tag that closes these where the markup leaves them open
INLINE = {"a", "abbr", "b", "bdi", "cite", "code", "em", "i", "kbd", "mark", "q", "s", "samp", "small", "span", "strong", "sub",
          "sup", "time", "u", "var"}                        # what stands in the line of the words around it
INTERACTIVE = {"a", "button", "input", "select", "textarea", "form", "label", "dialog", "details", "summary"}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
UNSEEN = {"script", "style", "template", "head", "title", "meta", "link", "noscript"}
CONDITIONS = ("data-when", "data-unless", "data-as", "data-unless-as")
SAID_AS = {"data-when": "only when", "data-unless": "not when", "data-as": "only as", "data-unless-as": "not as"}
WORD_ATTRIBUTES = ("placeholder", "alt", "aria-label", "title")
FIELD_RULES = ("required", "min", "max", "step", "minlength", "maxlength", "pattern", "inputmode", "autocomplete",
               "accept", "multiple")


# --- the prototype as a tree -----------------------------------------------------------------------------------------
class Mark:
    """One element of a prototype: its tag, its attributes, the line it starts on, and what it holds, words as strings."""

    def __init__(self, tag: str, attrs: dict[str, str], line: int) -> None:
        self.tag, self.attrs, self.line = tag, attrs, line
        self.children: list = []

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Mark):
                yield from child.walk()

    def classes(self) -> list[str]:
        return self.attrs.get("class", "").split()

    def raw(self) -> str:
        out = []
        for child in self.children:
            if isinstance(child, str):
                out.append(child)
            elif child.tag not in UNSEEN:
                out.append(child.raw() if child.tag in INLINE else f" {child.raw()} ")
        return "".join(out)

    def text(self) -> str:
        """All its words, in the order they are drawn, as a browser spaces them: `ring <a>us</a>.` is `ring us.`"""
        return " ".join(self.raw().split())

    def own_text(self) -> str:
        return " ".join(" ".join(c.split()) for c in self.children if isinstance(c, str) and c.strip())


class Reader(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Mark("#page", {}, 1)
        self.stack = [self.root]
        self.lines_before = 0

    def mark(self, tag: str, attrs: list) -> Mark:
        node = Mark(tag, {k: v or "" for k, v in attrs}, self.getpos()[0] - self.lines_before)
        self.stack[-1].children.append(node)
        return node

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if self.stack[-1].tag in IMPLIED.get(tag, ()):
            self.stack.pop()
        node = self.mark(tag, attrs)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.mark(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        for at in range(len(self.stack) - 1, 0, -1):
            if self.stack[at].tag == tag:
                del self.stack[at:]
                return

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.stack[-1].children.append(data)


class Page:
    """One prototype, parsed inside the product's page, as a browser draws it, so that what `body` or a class on it sets
    reaches the elements: its tree, each node's parent, and the screen or component it is. A line is the prototype's own."""

    def __init__(self, root: Path, rel: str, ref: str) -> None:
        self.rel, self.screen = rel, ref
        reader = Reader()
        body = (root / rel).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        shell = root / prototypes.SHELL
        before, _, after = (shell.read_text(encoding="utf-8-sig").replace("\r\n", "\n") if shell.is_file() else "{{body}}").partition("{{body}}")
        reader.lines_before = before.count("\n")
        reader.feed(before + body + after)
        reader.close()
        self.tree = reader.root
        self.parent: dict[int, Mark] = {}
        for node in self.tree.walk():
            for child in node.children:
                if isinstance(child, Mark):
                    self.parent[id(child)] = node
        self.main = (next((n for n in self.tree.walk() if "data-prototype" in n.attrs), None)
                     or next((n for n in self.tree.walk() if n.tag == "body"), self.tree))

    def elements(self, node: Mark | None = None) -> list[Mark]:
        """Every element under the screen's main, in the order it is drawn, with nothing unseen."""
        out = []
        for child in (node or self.main).children:
            if isinstance(child, Mark) and child.tag not in UNSEEN:
                out.append(child)
                out += self.elements(child)
        return out

    def ancestors(self, node: Mark) -> list[Mark]:
        out = []
        while id(node) in self.parent:
            node = self.parent[id(node)]
            out.append(node)
        return out

    def handle(self, node: Mark) -> str:
        if node.attrs.get("data-el"):
            return f"{self.screen}.{node.attrs['data-el']}"
        return node.attrs.get("data-part", "")

    def owner(self, node: Mark) -> str:
        """The nearest handle at or above a node: whose words they are."""
        for at in [node, *self.ancestors(node)]:
            if self.handle(at):
                return self.handle(at)
            if at is self.main:
                break
        return ""

    def conditions(self, node: Mark) -> dict[str, list[str]]:
        """When a node shows: each condition of it and of what holds it, by its attribute."""
        out: dict[str, list[str]] = {}
        for at in [node, *self.ancestors(node)]:
            for attribute in CONDITIONS:
                if at.attrs.get(attribute):
                    out.setdefault(attribute, []).extend(at.attrs[attribute].split())
        return out


def shows(conditions: dict, state: str, variant: str) -> bool:
    """Whether a node with these conditions shows in a state and a variant, as the prototype's runtime decides it."""
    if "data-when" in conditions and state not in conditions["data-when"]:
        return False
    if state in conditions.get("data-unless", []):
        return False
    if "data-as" in conditions and variant not in conditions["data-as"]:
        return False
    return variant not in conditions.get("data-unless-as", [])


def when_said(conditions: dict) -> str:
    return "; ".join(f"{SAID_AS[a]} {', '.join(w)}" for a, w in conditions.items())
