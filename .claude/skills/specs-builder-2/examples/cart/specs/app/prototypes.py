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


def tokens_of(out) -> None:
    """A page that takes its look from the tokens names only tokens there are: a name with no token draws nothing, and says nothing."""
    shell = out.root / SHELL
    if not shell.is_file() or TOKENS_CSS not in shell.read_text(encoding="utf-8"):
        return
    try:
        known = {variable(t) for t in flat_tokens(out.root)}
    except (ValueError, OSError) as wrong:
        out.fault(TOKENS, 0, f"cannot be read: {wrong}")
        return
    root = out.root / PROTOTYPES
    written = [p for folder in ("assets/css", "screens", "components") for p in sorted((root / folder).glob("*")) if p.suffix in (".css", ".html")]
    texts = {p: p.read_text(encoding="utf-8") for p in written}
    known |= {name for text in texts.values() for name in re.findall(r"(--[\w-]+)\s*:", text)}
    for path, text in texts.items():
        for line, row in enumerate(text.splitlines(), 1):
            for name in re.findall(r"var\((--[\w-]+)\s*\)", row):              # one with a fallback says what happens without it
                if name not in known:
                    out.fault(path.relative_to(out.root).as_posix(), line, f"{name} is no token of {TOKENS}")


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
