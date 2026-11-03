"""A page's styles resolved the way a browser would, for what prototypes use: classes, tags, attributes, descendants,
:where and :is. What a value depends on, a state or a width, is said beside it."""
from __future__ import annotations

import re
from pathlib import Path

import prototypes
from markup import Mark, Page

# what a pseudo-class depends on that no page shows by itself: a condition, not a part of the match
STATE_PSEUDO = {"hover", "focus", "focus-visible", "focus-within", "active", "visited", "checked", "disabled",
                "enabled", "invalid", "valid", "placeholder-shown", "target", "open", "required", "optional",
                "read-only", "empty", "link", "any-link", "indeterminate", "user-invalid"}


# --- the product's styles --------------------------------------------------------------------------------------------
class Rule:
    def __init__(self, selectors: list[str], declarations: list[tuple[str, str]], media: str, order: int, line: int) -> None:
        self.selectors, self.declarations, self.media, self.order, self.line = selectors, declarations, media, order, line


def split_outside(text: str, mark: str) -> list[str]:
    """Text split at a mark that stands outside quotes, brackets and parentheses."""
    out, depth, quote, start = [], 0, "", 0
    for at, char in enumerate(text):
        if quote:
            quote = "" if char == quote else quote
        elif char in "\"'":
            quote = char
        elif char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        elif char == mark and depth == 0:
            out.append(text[start:at])
            start = at + 1
    out.append(text[start:])
    return out


def css_rules(text: str, first: int = 0) -> list[Rule]:
    """Every rule of a style sheet, in order: its selectors, its declarations, and the @media it stands under."""
    text = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.DOTALL)
    rules: list[Rule] = []

    def block(at: int, media: str) -> int:
        while at < len(text):
            opening, closing = text.find("{", at), text.find("}", at)
            if closing != -1 and (opening == -1 or closing < opening):
                return closing + 1
            if opening == -1:
                return len(text)
            prelude = text[at:opening].strip()
            line = text.count("\n", 0, opening) + 1
            if prelude.startswith(("@media", "@supports", "@container", "@layer")):
                inner = prelude.split(None, 1)[1] if " " in prelude else ""
                at = block(opening + 1, f"{media} and {inner}" if media else inner)
                continue
            depth, end = 1, opening + 1
            while end < len(text) and depth:
                depth += {"{": 1, "}": -1}.get(text[end], 0)
                end += 1
            if not prelude.startswith("@"):
                declarations = []
                for piece in split_outside(text[opening + 1:end - 1], ";"):
                    if ":" in piece:
                        prop, value = piece.split(":", 1)
                        declarations.append((prop.strip().lower(), " ".join(value.split())))
                rules.append(Rule([s.strip() for s in split_outside(prelude, ",") if s.strip()], declarations, media,
                                  first + len(rules), line))
            at = end
        return at

    block(0, "")
    return rules


SIMPLE_RE = re.compile(r"(::?[\w-]+(?:\((?:[^()]|\([^()]*\))*\))?|\.[\w-]+|#[\w-]+|\[[^\]]*\]|\*|[a-zA-Z][\w-]*)")


def compounds(selector: str) -> list[tuple[str, str]]:
    """A selector as its compounds, each with the combinator before it."""
    pieces = re.split(r"\s*([>+~])\s*|\s+(?![^()]*\))(?![^\[]*\])", selector.strip())
    out, combinator = [], " "
    for piece in pieces:
        if piece is None or piece == "":
            continue
        if piece in (">", "+", "~"):
            combinator = piece
            continue
        out.append((combinator, piece))
        combinator = " "
    return out


def matches_compound(page: Page, node: Mark, compound: str, notes: set) -> bool:
    for simple in SIMPLE_RE.findall(compound):
        if simple == "*":
            continue
        if simple.startswith("::"):
            notes.add(simple)
            continue
        if simple.startswith(":"):
            name, _, inner = simple[1:].partition("(")
            inner = inner[:-1] if inner else ""
            if name in ("where", "is", "matches"):
                if not any(matches_compound(page, node, alt.strip(), notes) for alt in split_outside(inner, ",")):
                    return False
            elif name == "not":
                if any(matches_compound(page, node, alt.strip(), set()) for alt in split_outside(inner, ",")):
                    return False
            elif name in ("first-child", "last-child", "only-child"):
                parent = page.parent.get(id(node))
                kin = [c for c in parent.children if isinstance(c, Mark)] if parent is not None else [node]
                if (name == "first-child" and kin[0] is not node) or (name == "last-child" and kin[-1] is not node) \
                        or (name == "only-child" and len(kin) != 1):
                    return False
            elif name in STATE_PSEUDO or name.startswith("-"):
                notes.add(f":{simple[1:]}")
            continue
        if simple.startswith("."):
            if simple[1:] not in node.classes():
                return False
        elif simple.startswith("#"):
            if node.attrs.get("id") != simple[1:]:
                return False
        elif simple.startswith("["):
            found = re.match(r"\[\s*([\w-]+)\s*(?:([~^$*|]?=)\s*[\"']?([^\"'\]]*)[\"']?)?\s*\]", simple)
            if not found:
                continue
            name, how, value = found.groups()
            if name not in node.attrs:
                return False
            held = node.attrs[name]
            if how and not {"=": held == value, "~=": value in held.split(), "^=": held.startswith(value),
                            "$=": held.endswith(value), "*=": value in held,
                            "|=": held == value or held.startswith(value + "-")}[how]:
                return False
        elif simple.lower() != node.tag:
            return False
    return True


def matches(page: Page, node: Mark, selector: str) -> set | None:
    """Whether a selector reaches a node, and what it depends on beyond it -- a :hover, a ::before -- or None."""
    parts = compounds(selector)
    if not parts:
        return None
    notes: set = set()

    def reach(at: Mark, index: int) -> bool:
        combinator, compound = parts[index]
        if not matches_compound(page, at, compound, notes):
            return False
        if index == 0:
            return True
        if combinator == ">":
            parent = page.parent.get(id(at))
            return parent is not None and reach(parent, index - 1)
        if combinator in ("+", "~"):
            parent = page.parent.get(id(at))
            kin = [c for c in parent.children if isinstance(c, Mark)] if parent is not None else []
            before = kin[:kin.index(at)] if at in kin else []
            return any(reach(b, index - 1) for b in (before[-1:] if combinator == "+" else before))
        return any(reach(up, index - 1) for up in page.ancestors(at))
    return notes if reach(node, len(parts) - 1) else None


def specificity(selector: str) -> tuple:
    def of(text: str) -> list[int]:
        counts = [0, 0, 0]
        for simple in SIMPLE_RE.findall(text):
            if simple.startswith("::"):
                counts[2] += 1
            elif simple.startswith((":where", ":matches")):
                continue
            elif simple.startswith((":is", ":not")):
                inner = simple[simple.index("(") + 1:-1]
                best = max((of(alt) for alt in split_outside(inner, ",")), default=[0, 0, 0])
                counts = [x + y for x, y in zip(counts, best)]
            elif simple.startswith("#"):
                counts[0] += 1
            elif simple.startswith((".", "[", ":")):
                counts[1] += 1
            elif simple != "*":
                counts[2] += 1
        return counts
    return tuple(of(selector))


class Styles:
    """The product's styles as they reach the elements of a prototype: each sheet its page links, in order, the tokens'
    among them."""

    def __init__(self, root: Path) -> None:
        self.rules: list[Rule] = []
        self.files: list[str] = []
        shell = root / prototypes.SHELL
        linked = re.findall(r'<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"', shell.read_text(encoding="utf-8")) if shell.is_file() else []
        for href in linked:
            if href == prototypes.TOKENS_CSS:
                text = prototypes.tokens_css(root)
            elif (root / prototypes.PROTOTYPES / href).is_file():
                text = (root / prototypes.PROTOTYPES / href).read_text(encoding="utf-8-sig")
                self.files.append(f"{prototypes.PROTOTYPES}/{href}")
            else:
                continue
            self.rules += css_rules(text, len(self.rules))
        self.tokens: dict[str, str] = {}
        for token in prototypes.flat_tokens(root):
            self.tokens.setdefault(str(token["value"]).lower(), prototypes.variable(token))

    def reaching(self, page: Page, node: Mark) -> list[tuple]:
        """Each declaration that reaches a node: (specificity, order, property, value, selector, media, notes, line)."""
        out = []
        for rule in self.rules:
            for selector in rule.selectors:
                notes = matches(page, node, selector)
                if notes is not None:
                    out += [(specificity(selector), rule.order, prop, value, selector, rule.media, tuple(sorted(notes)), rule.line)
                            for prop, value in rule.declarations]
        return sorted(out, key=lambda d: (d[0], d[1]))

    def plain(self, page: Page, node: Mark) -> dict[str, tuple]:
        """What holds for a node with no condition: each property's winning value and where it came from."""
        out: dict[str, tuple] = {}
        for _, _, prop, value, selector, media, notes, line in self.reaching(page, node):
            if media or notes:
                continue
            important = value.endswith("!important")
            if prop in out and out[prop][2] and not important:
                continue
            out[prop] = (value.replace("!important", "").strip(), selector, important, line)
        return out

    def variables(self, page: Page, node: Mark) -> dict[str, str]:
        """The custom properties a node sees: its own and those it inherits."""
        out: dict[str, str] = {}
        for at in [*reversed(page.ancestors(node)), node]:
            for prop, held in self.plain(page, at).items():
                if prop.startswith("--"):
                    out[prop] = held[0]
        return out

    def resolve(self, value: str, variables: dict[str, str]) -> str:
        for _ in range(10):
            found = re.search(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*(?:\([^()]*\)[^()]*)*))?\)", value)
            if not found:
                break
            value = value[:found.start()] + variables.get(found.group(1), (found.group(2) or "").strip()) + value[found.end():]
        return value

    def token_of(self, written: str, value: str) -> str:
        named = re.findall(r"var\(\s*(--[\w-]+)", written)
        named += [self.tokens[v.lower()] for v in re.findall(r"#[0-9a-fA-F]{3,8}\b|\b\d+(?:\.\d+)?(?:px|rem|em)\b", value)
                  if v.lower() in self.tokens]
        return ", ".join(dict.fromkeys(n for n in named if n in self.tokens.values()))
