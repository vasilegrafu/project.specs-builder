"""The prototypes held to the data, both ways.

A screen's prototype, `prototypes/screens/SC3.html`, is the markup of the screen in the product's look; a
component's, `prototypes/components/C1.html`, its drawings, one `data-variant` for each of its variants. The markup
carries one anchor per element -- `data-el="9"`, `data-part="C3.1"` -- and nothing else of what the element means:
what it shows, what it is about, what component it is, is its row in the data. So every anchor must have its row,
every row its anchor, every variant its drawing; and a `data-spec-*` attribute, how links were written in markup
before, is refused where it is found.
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

PROTOTYPES = "prototypes"
SHELL = f"{PROTOTYPES}/page.html"           # the product's page: its look, around every prototype
TOKENS = f"{PROTOTYPES}/tokens.json"        # the look's values: every colour, size and font, in one file
TOKENS_CSS = "assets/css/tokens.css"        # made from them whenever it is asked for: there is no such file to fall behind
SLOTS = ("{{body}}", "{{title}}")
WATCHED = ("data-el", "data-part", "data-variant")


class Anchors(HTMLParser):
    """Each anchor, and each attribute a link was once written in, with the line it is on."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: list[tuple[str, str, int]] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        line = self.getpos()[0]
        for name, value in attrs:
            if name in WATCHED or name.startswith("data-spec-"):
                self.found.append((name, value or "", line))

    handle_startendtag = handle_starttag


READ: dict[str, tuple[tuple[int, int], list[tuple[str, str, int]]]] = {}    # each file's anchors, by its time and size


def anchors(path: Path) -> list[tuple[str, str, int]]:
    """A file's anchors, read again only when the file has changed since."""
    seen = path.stat()
    stamp = (seen.st_mtime_ns, seen.st_size)
    held = READ.get(str(path))
    if held is not None and held[0] == stamp:
        return list(held[1])
    parser = Anchors()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    READ[str(path)] = (stamp, list(parser.found))
    return parser.found


COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\([^)]*\)")   # a colour written as a value
LITERAL = "/* literal:"                                                 # on a line, why a value is written there after all


def colours_in(text: str, css: bool) -> list[tuple[int, str]]:
    """Each colour a style writes as a value, with its line: in a sheet, inside a declaration's value; in markup, inside a
    `style` attribute or a drawing's `fill`, `stroke` or `stop-color`. One inside `url(...)` is a picture's, and a line that
    says `/* literal: why */` is left alone."""
    out = []
    for line, row in enumerate(text.splitlines(), 1):
        if LITERAL in row:
            continue
        row = re.sub(r"/\*.*?\*/", " ", row)
        row = re.sub(r"url\([^)]*\)", "url()", row)
        if css:
            values = [part.partition(":")[2] for piece in row.split("{") for part in piece.split(";") if ":" in part]
        else:
            values = re.findall(r'\b(?:style|fill|stroke|stop-color)\s*=\s*"([^"]*)"', row)
        for value in values:
            out += [(line, found) for found in COLOUR.findall(value)]
    return out


def tokens_of(out) -> None:
    """The look's values live in `tokens.json`, and a page takes them from there: it names only tokens there are -- a name
    with no token draws nothing, and says nothing -- and writes no colour of its own, in its styles, its markup or a
    foundation's text, for a value written twice is changed once."""
    shell = out.root / SHELL
    if not shell.is_file():
        return
    held = (out.root / TOKENS).is_file()
    linked = TOKENS_CSS in shell.read_text(encoding="utf-8")
    if held and not linked:
        out.fault(SHELL, 0, f"the page shell does not link {TOKENS_CSS}, so no page sees the tokens of {TOKENS}")
    if not linked:
        return
    try:
        known = {variable(t) for t in flat_tokens(out.root)}
    except (ValueError, OSError) as wrong:
        out.fault(TOKENS, 0, f"cannot be read: {wrong}")
        return
    root = out.root / PROTOTYPES
    written = [p for folder in ("assets/css", "screens", "components", "shared") if (root / folder).is_dir()
               for p in sorted((root / folder).glob("*")) if p.suffix in (".css", ".html")]
    written.append(shell)
    texts = {p: p.read_text(encoding="utf-8") for p in written}
    known |= {name for text in texts.values() for name in re.findall(r"(--[\w-]+)\s*:", text)}
    for path, text in texts.items():
        name = path.relative_to(out.root).as_posix()
        for line, row in enumerate(text.splitlines(), 1):
            for found in re.findall(r"var\((--[\w-]+)\s*\)", row):             # one with a fallback says what happens without it
                if found not in known:
                    out.fault(name, line, f"{found} is no token of {TOKENS}")
        for line, colour in colours_in(text, path.suffix == ".css"):
            out.fault(name, line, f"{colour} is a colour written here: the look's values live in {TOKENS}, and a page names "
                                  f"its token, `var(--color-...)`; `scripts/tokens.py --apply` moves it there, or `{LITERAL} why */` "
                                  f"on the line keeps it")
    for node in sorted(out.nodes.values(), key=lambda n: n.id):
        if node.kind != "foundation":
            continue
        said = str(node.fields.get("says", ""))
        for colour in dict.fromkeys(COLOUR.findall(said)):
            try:
                at = next(i for i, row in enumerate((out.root / node.file).read_text(encoding="utf-8").splitlines(), 1) if colour in row)
            except (OSError, StopIteration):
                at = node.line
            out.fault(node.file, at, f"{node.id} writes the colour {colour}: a foundation names its token, `--color-...`, and the value "
                                     f"lives in {TOKENS}, where the pages take it from")
        for name in dict.fromkeys(re.findall(r"(?<![\w-])(--[A-Za-z][\w-]*)", said)):
            if name not in known:
                try:
                    at = next(i for i, row in enumerate((out.root / node.file).read_text(encoding="utf-8").splitlines(), 1) if name in row)
                except (OSError, StopIteration):
                    at = node.line
                out.fault(node.file, at, f"{name} is no token of {TOKENS}")


REACHING: dict[str, tuple[tuple, dict[str, dict[str, str]]]] = {}   # each specification's look as it reaches its prototypes, by the files' stamps


def tokens_reaching(root: Path) -> dict[str, dict[str, str]]:
    """For each prototype, by its file, the tokens that reach its drawing and their values: those its markup names, those the
    page shell names, and those in the rules of the product's sheets whose selectors can reach it -- a rule by a class the
    markup carries, or by no class at all. A value changed among them changes what the prototype shows. Read again only
    when a file among them has."""
    from cascade import css_rules
    shell = root / SHELL
    place = root / PROTOTYPES
    drawn = [p for folder in ("screens", "components") if (place / folder).is_dir() for p in sorted((place / folder).glob("*.html"))]
    sheets = sorted((place / "assets/css").glob("*.css")) if (place / "assets/css").is_dir() else []
    files = [*drawn, *sheets, *([shell] if shell.is_file() else []), *([root / TOKENS] if (root / TOKENS).is_file() else [])]
    stamp = tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in files)
    kept = REACHING.get(str(root))
    if kept is not None and kept[0] == stamp:
        return kept[1]
    values = {variable(t): str(t["value"]) for t in flat_tokens(root)} if (root / TOKENS).is_file() else {}
    rules = []
    defined: dict[str, str] = {}                        # a custom property the sheets define, and what it names
    for sheet in sheets:
        for rule in css_rules(sheet.read_text(encoding="utf-8-sig")):
            classes = {c for s in rule.selectors for c in re.findall(r"\.([\w-]+)", s)}
            named = {n for _, v in rule.declarations for n in re.findall(r"var\(\s*(--[\w-]+)", v)}
            rules.append((classes, named))
            for prop, value in rule.declarations:
                if prop.startswith("--"):
                    defined[prop] = value
    shared = set(re.findall(r"var\(\s*(--[\w-]+)", shell.read_text(encoding="utf-8"))) if shell.is_file() else set()

    def resolved(names: set[str]) -> dict[str, str]:
        out, seen = {}, set()
        while names:
            name = names.pop()
            if name in seen:
                continue
            seen.add(name)
            if name in values:
                out[name] = values[name]
            elif name in defined:
                names |= set(re.findall(r"var\(\s*(--[\w-]+)", defined[name]))
        return dict(sorted(out.items()))

    out: dict[str, dict[str, str]] = {}
    for path in drawn:
        text = path.read_text(encoding="utf-8")
        carried = {c for attr in re.findall(r'class\s*=\s*"([^"]*)"', text) for c in attr.split()}
        names = set(re.findall(r"var\(\s*(--[\w-]+)", text)) | shared
        for classes, named in rules:
            if not classes or classes & carried:
                names |= named
        out[path.relative_to(root).as_posix()] = resolved(names)
    REACHING[str(root)] = (stamp, out)
    return out


def flat_tokens(root: Path) -> list[dict]:
    """The tokens, flattened, each with its group, its type, its value as a page writes it, and what it is for."""
    path = root / TOKENS
    if not path.is_file():
        return []
    found = []

    def walk(group: str, held: dict, kind: str | None) -> None:
        kind = held.get("$type", kind)
        for key, value in held.items():
            if key.startswith("$") or not isinstance(value, dict):
                continue
            if "$value" in value:
                said = value["$value"]
                shown = said.get("hex") if isinstance(said, dict) and "hex" in said else \
                    f"{said.get('value')}{said.get('unit', '')}" if isinstance(said, dict) and "value" in said \
                    else ", ".join(map(str, said)) if isinstance(said, list) \
                    else said if isinstance(said, (str, int, float)) else json.dumps(said)
                found.append({"group": group, "name": key, "type": value.get("$type", kind), "value": shown, "about": value.get("$description", "")})
            else:
                walk(f"{group}.{key}" if group else key, value, kind)
    walk("", json.loads(path.read_text(encoding="utf-8")), None)
    return found


def variable(token: dict) -> str:
    """The name a page knows a token by: --<group>-<name>."""
    return "--" + "-".join(filter(None, [token["group"].replace(".", "-"), token["name"]]))


def tokens_css(root: Path) -> str:
    """Every token as a CSS variable, made from tokens.json as it stands, so that a value changed there changes every page."""
    tokens = flat_tokens(root)
    return ("/* Made from prototypes/tokens.json each time it is asked for: change a value there. */\n:root {\n"
            + "".join(f"  {variable(t)}: {t['value']};\n" for t in tokens) + "}\n")


def check(g: dict, out) -> None:
    root = out.root / PROTOTYPES
    tokens_of(out)
    drawn = any(spec.get("prototype") and any(n.kind == kind for n in out.nodes.values())
                for kind, spec in g["kinds"].items())
    if drawn:
        shell = out.root / SHELL
        if not shell.is_file():
            out.fault(SHELL, 0, "there is no page shell: the product's page, its look around every prototype, "
                                "with {{title}} and {{body}} where each goes")
        else:
            held = shell.read_text(encoding="utf-8")
            for slot in SLOTS:
                if held.count(slot) != 1:
                    out.fault(SHELL, 0, f"the page shell holds {slot} {held.count(slot)} times, and needs it once")
    for kind, spec in g["kinds"].items():
        folder = spec.get("prototype")
        if not folder:
            continue
        owned = {n.id: n for n in out.nodes.values() if n.kind == kind}
        place = root / folder
        files = {p.stem: p for p in sorted(place.glob("*.html"))} if place.is_dir() else {}
        for stem, path in files.items():
            if stem not in owned:
                out.fault(name_of(out, path), 0, f"a prototype of no {kind}: there is no {stem} in the data")
        for ident, node in sorted(owned.items()):
            path = files.get(ident)
            if path is None:
                out.fault(node.file, node.line, f"{ident} has no prototype: {PROTOTYPES}/{folder}/{ident}.html")
                continue
            found = anchors(path)
            name = name_of(out, path)
            for attr, _, line in found:
                if attr.startswith("data-spec-"):
                    out.fault(name, line, f"`{attr}` in the markup: what an element shows, is and stands on is "
                                          f"data now, in its row in {node.file}")
            parts = [(v, line) for a, v, line in found if a == "data-part"]
            for value, line in parts:
                if out.nodes.get(value, None) is None or out.nodes[value].kind != "part":
                    out.fault(name, line, f"`data-part=\"{value}\"` names no part of a component")
            if kind == "screen":
                screen(out, node, name, found)
            elif kind == "component":
                component(out, node, name, found)


def screen(out, node, name: str, found: list) -> None:
    drawn: dict[str, int] = {}
    for attr, value, line in found:
        if attr != "data-el":
            continue
        if not value.isdigit():
            out.fault(name, line, f"`data-el=\"{value}\"` is not an element's number")
            continue
        drawn.setdefault(value, line)
    rows = {n.id.rsplit(".", 1)[1]: n for n in out.nodes.values() if n.parent == node.id and n.kind == "element"}
    for number, line in sorted(drawn.items(), key=lambda kv: int(kv[0])):
        if number not in rows:
            out.fault(name, line, f"`data-el=\"{number}\"` has no row in {node.file}'s Elements: {node.id}.{number} "
                                  f"is not there")
    for number, element in sorted(rows.items(), key=lambda kv: int(kv[0])):
        if number not in drawn:
            out.fault(element.file, element.line, f"{element.id} is drawn nowhere: {name} has no "
                                                  f"`data-el=\"{number}\"`")


def component(out, node, name: str, found: list) -> None:
    drawn: dict[str, int] = {}
    for attr, value, line in found:
        if attr == "data-variant":
            drawn.setdefault(value, line)
    said = {row["variant"]: row["line"] for row in node.fields.get("variants", [])}
    for variant, line in drawn.items():
        if variant not in said:
            out.fault(name, line, f"`data-variant=\"{variant}\"` is no variant of {node.id}: its Variants table "
                                  f"has {', '.join(said) or 'none'}")
    for variant, line in said.items():
        if variant not in drawn:
            out.fault(node.file, line, f"{node.id}'s variant `{variant}` is drawn nowhere: {name} has no "
                                       f"`data-variant=\"{variant}\"`")


def name_of(out, path: Path) -> str:
    return path.relative_to(out.root).as_posix()
