#!/usr/bin/env python3
"""Read the styles a live site's captures hold, and write them as design tokens; or move a specification's values into its tokens.

    python scripts/tokens.py <captures>                      # what the captures show, as a table to read
    python scripts/tokens.py <captures> --json <file>        # and write it as design tokens
    python scripts/tokens.py --apply <spec> [--dry]          # the look's values into tokens.json, every page naming them
    python scripts/tokens.py --selftest

`--apply` is for a specification whose styles still write values: each colour a custom property of
`prototypes/assets/css/*.css` defines becomes a token named after it, the sheets' prefix taken off (`--vl-brand`
becomes `--color-brand`), a token that already holds the value is renamed to it, the definition goes, and every page,
sheet and foundation that wrote the value or the old name names the token. Colours no token holds are listed with
their file and line, to be given a token under their meaning; it exits 1 while any is left. `spec.py check` refuses
a colour written as a value once there is a tokens.json.

<captures> is the folder of a live site's captures, `evidence/captures/<site>/` of a
specification (references/reading-a-live-site.md). Every capture's
`## Styles` section is read, one `style:` line at a time:

    style: button "Download": color #ffffff; background-color #1a5fb4; border-radius 6px; padding 8px 16px

-- the element, then its properties and their values, as the page holds
them, separated by `;` (or by `,` in a line written by hand). From every
line the colours are read, with the part they colour -- text, surface,
border -- and the font sizes, families, weights and line heights, the radii,
the widths of borders, the spacing and the shadows. A value seen once is a
value; a value seen across views is a token.

An element that shows no text -- an icon's button, a hidden input, marked
`(no text)` by capture.js -- gives no type: its size and font are the
browser's, not the product's. In a capture taken before that mark, a button
or a field whose family is one name alone, with no fallback, is taken for
such an element. A shadow's colours are the shadow's, not colours of their
own, and a translucent colour says its alpha in its description.

The table printed is for the one who writes the foundations: each value,
how often it was seen, in which views and as what. `--json` writes the same
as design tokens in the format of the Design Tokens Community Group
(2025.10): a group per kind with its `$type`, each token with its `$value`
and, under `$extensions`, where it was seen. The names are neutral --
`text-1`, `size-2` -- by how often a colour was seen and by size: what each
means is said in the foundations, and the product's own values are in
assets/css/product.css. `scripts/spec.py` checks a specification's
`design-system/tokens.json` where there is one.

Standard library only.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textfile  # noqa: E402
import scout  # noqa: E402
from scout import SITE_INVENTORY  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
EXAMPLE_SITE = SKILL / "examples" / "shop" / "specs" / "evidence" / "captures" / "site"
EXAMPLE_TOKENS = SKILL / "examples" / "shop" / "specs" / "prototypes" / "tokens.json"

COLOUR_RE = re.compile(r"#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)")
LENGTH_RE = re.compile(r"(?<![\w.#-])(-?\d+(?:\.\d+)?)(px|rem|%)(?![\w%])")
# What a property is called, by the words a capture may use for it.
NAMES = {"colour": "color", "background": "background-color", "background-colour": "background-color",
         "border-colour": "border-color", "font": "font-family", "radius": "border-radius", "weight": "font-weight",
         "size": "font-size"}
PART = {"color": "text", "background-color": "surface", "fill": "surface", "border": "border",
        "border-color": "border", "outline": "border", "outline-color": "border", "stroke": "border"}
# Each kind of dimension, by the properties it is read from.
DIMENSIONS = {"font-size": ("font-size",), "line-height": ("line-height",), "radius": ("border-radius",),
              "border-width": ("border", "border-width", "outline", "outline-width"),
              "spacing": ("padding", "margin", "gap", "row-gap", "column-gap")}
DIMENSION_NAMES = {"font-size": "size", "line-height": "line", "radius": "radius", "border-width": "width",
                   "spacing": "space"}
TYPE = {"font-size", "font-family", "font-weight", "line-height"}   # what an element that shows no text does not give
NO_TEXT = "(no text)"                                               # how capture.js marks such an element
SHADOWS = ("box-shadow", "text-shadow")
WEIGHTS = {"normal": 400, "bold": 700, "lighter": 300, "bolder": 800}


@dataclass
class Seen:
    """One value, and where it was seen."""
    count: int = 0
    views: list[str] = field(default_factory=list)
    parts: list[str] = field(default_factory=list)

    def add(self, view: str, part: str) -> None:
        self.count += 1
        if view not in self.views:
            self.views.append(view)
        if part and part not in self.parts:
            self.parts.append(part)


def hex_of(colour: str) -> tuple[str, float]:
    """A colour as #rrggbb, and its alpha."""
    colour = colour.strip().lower()
    if colour.startswith("#"):
        digits = colour[1:]
        if len(digits) == 3:
            digits = "".join(d * 2 for d in digits)
        alpha = int(digits[6:8], 16) / 255 if len(digits) == 8 else 1.0
        return "#" + digits[:6], round(alpha, 3)
    numbers = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", colour)]
    red, green, blue = (max(0, min(255, round(n))) for n in (numbers + [0, 0, 0])[:3])
    alpha = numbers[3] if len(numbers) > 3 else 1.0
    return f"#{red:02x}{green:02x}{blue:02x}", round(alpha, 3)


def styles_of(text: str) -> list[str]:
    """The `style:` lines of a capture's `## Styles` section."""
    part = re.search(r"^## Styles\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return [line[len("style:"):].strip() for line in (part.group(1).splitlines() if part else [])
            if line.startswith("style:") and "<<" not in line]


def element_of(line: str) -> str:
    """What a style line is about: the element, and its words in quotes, before its properties."""
    return line.rpartition('": ')[0] + '"' if '": ' in line else line.partition(": ")[0]


def shows_no_text(line: str, said: list[tuple[str, str]]) -> bool:
    """Whether the element of a style line shows no text, so that its type is the browser's: marked so by capture.js,
    or, in a capture taken before that mark, a button or a field whose family is one name alone."""
    element = element_of(line)
    if NO_TEXT in element:
        return True
    family = next((value for name, value in said if name == "font-family"), "")
    return bool(family) and "," not in family and element.split(" ", 1)[0].lower() in ("button", "input", "select")


def layers(value: str) -> list[dict[str, object]]:
    """A shadow's layers, each with its colour and its offsets, blur and spread, as the format writes them."""
    out: list[dict[str, object]] = []
    for layer in re.split(r",(?![^(]*\))", value):
        colour = COLOUR_RE.search(layer)
        lengths = [(float(n), unit) for n, unit in LENGTH_RE.findall(COLOUR_RE.sub("", layer))]
        if colour is None or len(lengths) < 2:
            continue
        hexed, alpha = hex_of(colour.group(0))
        lengths += [(0.0, "px")] * (4 - len(lengths))
        out.append({"color": colour_value(hexed, alpha),
                    **{key: {"value": amount(n), "unit": unit}
                       for key, (n, unit) in zip(("offsetX", "offsetY", "blur", "spread"), lengths)},
                    **({"inset": True} if "inset" in layer else {})})
    return out


CUT = ("...", "…")   # how a value cut short ends


def shadows_of(found: "Read") -> list[tuple[str, Seen]]:
    """The shadows seen, the most seen first: one cut short in a capture -- ending `...` -- is counted with the whole
    shadow that starts with its layers, where one was seen; else it stands with the layers it has whole."""
    whole = {value: Seen(seen.count, list(seen.views), list(seen.parts)) for value, seen in found.shadows.items()
             if not value.endswith(CUT)}
    for value, seen in found.shadows.items():
        if not value.endswith(CUT):
            continue
        held = layers(value)
        into = next((other for other in sorted(whole, key=len, reverse=True) if layers(other)[:len(held)] == held), None)
        if into is None:
            whole[value] = Seen(seen.count, list(seen.views), list(seen.parts))
            continue
        whole[into].count += seen.count
        whole[into].views += [view for view in seen.views if view not in whole[into].views]
    return sorted(whole.items(), key=lambda item: -item[1].count)


def colour_value(hexed: str, alpha: float) -> dict[str, object]:
    value: dict[str, object] = {"colorSpace": "srgb",
                                "components": [round(int(hexed[i:i + 2], 16) / 255, 4) for i in (1, 3, 5)],
                                "hex": hexed}
    if alpha != 1.0:
        value["alpha"] = alpha
    return value


def declarations(line: str) -> list[tuple[str, str]]:
    """A style line's properties and their values: what stands after the element, split at `;`, or at `,` where
    there is none."""
    _, _, said = line.rpartition('": ') if '": ' in line else line.partition(": ")
    said = said or line
    pieces = said.split(";") if ";" in said else re.split(r",(?![^(]*\))", said)
    out = []
    for piece in pieces:
        words = piece.strip().split(None, 1)
        if words:
            name = words[0].lower().rstrip(":")
            out.append((NAMES.get(name, name), words[1].strip() if len(words) > 1 else ""))
    return out


class Read:
    """Everything the captures of one site show, kind by kind."""

    def __init__(self) -> None:
        self.colours: dict[str, Seen] = {}
        self.dimensions: dict[str, dict[tuple[float, str], Seen]] = {kind: {} for kind in DIMENSIONS}
        self.families: dict[str, Seen] = {}
        self.weights: dict[int, Seen] = {}
        self.shadows: dict[str, Seen] = {}
        self.lines = 0

    def take(self, view: str, line: str) -> None:
        self.lines += 1
        said = declarations(line)
        textless = shows_no_text(line, said)
        for name, value in said:
            if textless and name in TYPE:
                continue
            if name in SHADOWS:
                if layers(value):
                    self.shadows.setdefault(re.sub(r"\s+", " ", value.strip()), Seen()).add(view, name)
                continue
            for colour in COLOUR_RE.findall(value):
                hexed = hex_of(colour)
                key = hexed[0] if hexed[1] == 1.0 else f"{hexed[0]}/{hexed[1]}"
                self.colours.setdefault(key, Seen()).add(view, PART.get(name, "other"))
            for kind, names in DIMENSIONS.items():
                if name in names:
                    for amount, unit in LENGTH_RE.findall(value):
                        if float(amount) > 0:
                            self.dimensions[kind].setdefault((float(amount), unit), Seen()).add(view, name)
            if name == "font-family" and value:
                self.families.setdefault(value.strip(), Seen()).add(view, "")
            if name == "font-weight":
                weight = WEIGHTS.get(value.strip().lower()) or (int(value) if value.strip().isdigit() else 0)
                if weight:
                    self.weights.setdefault(weight, Seen()).add(view, "")


def read(folder: Path) -> Read:
    """Read the styles of every capture in a site's folder: each its text."""
    found = Read()
    for path in scout.captures_in(folder):
        view = re.match(r"(V\d+)", path.name)
        for line in styles_of(textfile.text_of(path.read_text(encoding="utf-8-sig", errors="replace")
                                                      .replace("\r\n", "\n"))):
            found.take(view.group(1) if view else path.stem, line)
    return found


def amount(number: float) -> int | float:
    return int(number) if number == int(number) else number


def where(seen: Seen) -> str:
    return (f"seen {seen.count} time{'s' if seen.count != 1 else ''}, in {', '.join(seen.views)}"
            + (f", as {', '.join(seen.parts)}" if seen.parts else ""))


def extension(seen: Seen) -> dict[str, object]:
    return {"specs-builder": {"seen": seen.count, "views": seen.views, **({"as": seen.parts} if seen.parts else {})}}


def tokens(found: Read, folder_name: str) -> dict[str, object]:
    """What was read, as design tokens."""
    out: dict[str, object] = {"$description": f"The values the captures in {folder_name} show, read by tokens.py: "
                                              f"what a live site was seen to use. What each means is said in the "
                                              f"foundations."}
    if found.colours:
        group: dict[str, object] = {"$type": "color"}
        numbered: dict[str, int] = {}
        for key, seen in sorted(found.colours.items(), key=lambda item: (-item[1].count, item[0])):
            part = max(seen.parts, key=lambda p: (p != "other", -seen.parts.index(p))) if seen.parts else "other"
            numbered[part] = numbered.get(part, 0) + 1
            hexed, _, alpha = key.partition("/")
            # a translucent colour says so: by its hex alone, black at 54% reads as black
            said = f"{hexed} at {amount(round(float(alpha) * 100, 1))}%, " if alpha else ""
            group[f"{part}-{numbered[part]}"] = {"$value": colour_value(hexed, float(alpha) if alpha else 1.0),
                                                 "$description": said + where(seen),
                                                 "$extensions": extension(seen)}
        out["color"] = group
    for kind, values in found.dimensions.items():
        if values:
            group = {"$type": "dimension"}
            for number, ((size, unit), seen) in enumerate(sorted(values.items()), start=1):
                group[f"{DIMENSION_NAMES[kind]}-{number}"] = {"$value": {"value": amount(size), "unit": unit},
                                                              "$description": where(seen),
                                                              "$extensions": extension(seen)}
            out[kind] = group
    if found.families:
        group = {"$type": "fontFamily"}
        for number, (family, seen) in enumerate(sorted(found.families.items(), key=lambda item: -item[1].count),
                                                start=1):
            names = [name.strip().strip("'\"") for name in family.split(",") if name.strip()]
            group[f"family-{number}"] = {"$value": names if len(names) > 1 else names[0],
                                         "$description": where(seen), "$extensions": extension(seen)}
        out["font-family"] = group
    if found.weights:
        group = {"$type": "fontWeight"}
        for weight, seen in sorted(found.weights.items()):
            group[f"weight-{weight}"] = {"$value": weight, "$description": where(seen),
                                         "$extensions": extension(seen)}
        out["font-weight"] = group
    if found.shadows:
        group = {"$type": "shadow"}
        for number, (value, seen) in enumerate(shadows_of(found), start=1):
            held = layers(value)
            group[f"shadow-{number}"] = {"$value": held if len(held) > 1 else held[0], "$description": where(seen),
                                         "$extensions": extension(seen)}
        out["shadow"] = group
    return out


def render(found: Read, folder: Path) -> str:
    """What the captures show, as a table to read."""
    rows = [f"{folder}: {found.lines} style line(s)", "", "| Kind | Value | Seen | In | As |", "|---|---|---|---|---|"]
    for key, seen in sorted(found.colours.items(), key=lambda item: -item[1].count):
        rows.append(f"| colour | {key} | {seen.count} | {', '.join(seen.views)} | {', '.join(seen.parts)} |")
    for kind, values in found.dimensions.items():
        for (size, unit), seen in sorted(values.items()):
            rows.append(f"| {kind} | {amount(size)}{unit} | {seen.count} | {', '.join(seen.views)} | "
                        f"{', '.join(seen.parts)} |")
    for family, seen in found.families.items():
        rows.append(f"| font-family | {family} | {seen.count} | {', '.join(seen.views)} | |")
    for weight, seen in sorted(found.weights.items()):
        rows.append(f"| font-weight | {weight} | {seen.count} | {', '.join(seen.views)} | |")
    for value, seen in shadows_of(found):
        rows.append(f"| shadow | {value} | {seen.count} | {', '.join(seen.views)} | {', '.join(seen.parts)} |")
    if len(rows) == 4:
        rows.append("| | no style line read: a capture's `## Styles` holds `style:` lines | | | |")
    return "\n".join(rows)


def dumped(held: dict[str, object]) -> str:
    return json.dumps(held, indent=2, ensure_ascii=False) + "\n"


# --- the values moved into tokens.json ------------------------------------------------------------------------------------
PROTOTYPES = "prototypes"
TOKENS_FILE = f"{PROTOTYPES}/tokens.json"
SHELL = f"{PROTOTYPES}/page.html"
TOKENS_CSS = "assets/css/tokens.css"
LITERAL = "/* literal:"
VALUE_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\([^)]*\)")
TOKEN_NAME = re.compile(r"(?<![\w-])(--[A-Za-z][\w-]*)")


def normal(value: str) -> str:
    """A colour as it is compared: a hex in full and in lower case, a function with its spaces taken out."""
    value = value.strip().lower()
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) in (3, 4):
            digits = "".join(d * 2 for d in digits)
        return "#" + digits
    return re.sub(r"\s+", "", value)


def flat_values(held: dict) -> list[tuple[str, str, str, dict]]:
    """Each token of a tokens file: its group path, its name, its value as a page writes it, and the token itself."""
    found = []

    def walk(group: str, node: dict) -> None:
        for key, value in node.items():
            if key.startswith("$") or not isinstance(value, dict):
                continue
            if "$value" in value:
                said = value["$value"]
                shown = said.get("hex") if isinstance(said, dict) and "hex" in said else \
                    f"{said.get('value')}{said.get('unit', '')}" if isinstance(said, dict) and "value" in said \
                    else ", ".join(map(str, said)) if isinstance(said, list) else str(said)
                found.append((group, key, shown, value))
            else:
                walk(f"{group}.{key}" if group else key, value)
    walk("", held)
    return found


def variable_of(group: str, name: str) -> str:
    return "--" + "-".join(filter(None, [group.replace(".", "-"), name]))


@dataclass
class Applied:
    """What `--apply` did and what it could not."""
    moved: list[str] = field(default_factory=list)          # each custom property moved into a token
    renamed: list[str] = field(default_factory=list)        # each token renamed to what the styles call it
    replaced: int = 0                                       # each colour written as a value, now its token
    left: list[str] = field(default_factory=list)           # each colour no token holds, at its file and line
    unused: list[str] = field(default_factory=list)         # each token nothing names


def apply(spec: Path, prefix: str | None = None, dry: bool = False) -> Applied:
    """The look's values moved into `prototypes/tokens.json`, and every page made to name them. A custom property the
    product's sheet defines with a colour -- `--vl-brand: #2563eb` -- becomes the token `color.brand`, the prefix the
    sheets share taken off; a token that already holds the value takes that name instead; the definition goes, and every
    `var(--vl-brand)` names the token. A shadow defined with a colour in it becomes a shadow token. Then every colour
    written as a value in the sheets, the markup and the foundations' tables is replaced by the token that holds it,
    and those no token holds are listed, with the file and line, for whoever keeps the look to name. The page shell is
    made to link the tokens' sheet. `dry` says what would be done and writes nothing."""
    out = Applied()
    root = spec
    place = root / PROTOTYPES
    tokens_path = root / TOKENS_FILE
    held = json.loads(tokens_path.read_text(encoding="utf-8")) if tokens_path.is_file() else \
        {"$description": "The look's values, every colour the pages draw with: a foundation names each, and the pages take it from here."}
    sheets = sorted((place / "assets/css").glob("*.css")) if (place / "assets/css").is_dir() else []
    pages = [p for folder in ("screens", "components", "shared") if (place / folder).is_dir() for p in sorted((place / folder).glob("*.html"))]
    shell = root / SHELL
    texts: dict[Path, str] = {p: p.read_text(encoding="utf-8") for p in [*sheets, *pages, *([shell] if shell.is_file() else [])]}
    # 1. the custom properties the sheets define with a colour in them
    defined: list[tuple[str, str, Path]] = []
    for sheet in sheets:
        clean = re.sub(r"/\*.*?\*/", " ", texts[sheet], flags=re.DOTALL)
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;}]+)", clean):
            if VALUE_COLOUR.search(value):
                defined.append((name, value.strip(), sheet))
    if prefix is None:
        names = [n[2:] for n, _, _ in defined]
        prefix = ""
        if len(names) > 1 and all("-" in n for n in names):
            heads = {n.split("-", 1)[0] for n in names}
            prefix = heads.pop() + "-" if len(heads) == 1 else ""
    by_value: dict[str, str] = {}                           # each value, and the variable of the token that holds it
    for group, name, shown, _ in flat_values(held):
        by_value.setdefault(normal(shown), variable_of(group, name))
    renames: dict[str, str] = {}                            # each custom property, and the token variable it becomes
    taken: dict[str, str] = {}                              # each value a property of this run gave its token, by that token
    for name, value, _ in defined:
        bare = name[2:]
        bare = bare[len(prefix):] if prefix and bare.startswith(prefix) else bare
        plain = VALUE_COLOUR.fullmatch(value.strip()) is not None
        group = "color" if plain else "shadow" if "shadow" in bare else ""
        if not group:
            continue                                        # a value with a colour in it that is no colour and no shadow: left, and listed
        if bare == group:
            bare = "base"
        key = normal(value)
        if key in taken:                                    # two properties, one value: the second names the first's token
            renames[name] = taken[key]
            out.moved.append(f"{name} -> {taken[key]}, which holds the same value")
            continue
        found = next(((g, n, t) for g, n, s, t in flat_values(held) if normal(s) == key), None)
        new = variable_of(group, bare)
        if found is not None:                               # the token is there under a captured name: it takes this one
            g, n, t = found
            if (g, n) != (group, bare):
                held.setdefault(group, {"$type": "color" if group == "color" else "shadow"})
                del held[g][n]
                held[group][bare] = t
                out.renamed.append(f"{variable_of(g, n)} -> {new}")
        else:
            held.setdefault(group, {"$type": "color" if group == "color" else "shadow"})
            held[group][bare] = {"$value": value if group == "shadow" else normal(value), "$description": f"from {name} in the product's styles"}
        by_value[key] = taken[key] = new
        renames[name] = new
        out.moved.append(f"{name} -> {new}")
    # 2. the definitions taken out, and every use renamed
    gone = "\x00"                                           # where a definition was, until the lines are counted
    for path, text in list(texts.items()):
        if path.suffix == ".css":
            for name in renames:
                text = re.sub(rf"(?<![\w-]){re.escape(name)}\s*:\s*[^;}}]+;[ \t]*(?:/\*[^\n]*?\*/)?", gone, text)
        for name, new in renames.items():
            text = re.sub(rf"var\(\s*{re.escape(name)}(?=\s*[,)])", f"var({new}", text)
        texts[path] = text
    # 3. every colour still written as a value: its token, or listed
    def replacing(text: str, css: bool, where: str) -> str:
        lines = text.split("\n")
        for at, row in enumerate(lines):
            if LITERAL in row:
                continue
            spans = []
            if css:
                for m in re.finditer(r":[^;{}]*", re.sub(r"/\*.*?\*/", lambda c: " " * len(c.group(0)), row)):
                    spans.append((m.start(), m.end()))
            else:
                for m in re.finditer(r'\b(?:style|fill|stroke|stop-color)\s*=\s*"[^"]*"', row):
                    spans.append((m.start(), m.end()))
            edited = row
            for start, end in reversed(spans):
                piece = row[start:end]
                if "url(" in piece:
                    continue

                def swap(m: re.Match) -> str:
                    key = normal(m.group(0))
                    if key in by_value:
                        out.replaced += 1
                        return f"var({by_value[key]})"
                    out.left.append(f"{where}:{at + 1}: {m.group(0)}")
                    return m.group(0)
                edited = edited[:start] + VALUE_COLOUR.sub(swap, piece) + edited[end:]
            lines[at] = edited
        return "\n".join(lines)
    for path, text in list(texts.items()):
        texts[path] = replacing(text, path.suffix == ".css", path.relative_to(root).as_posix())
    foundations = {}
    folder = root / "data" / "foundations"
    for path in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")
        for at, row in enumerate(lines):
            def swap(m: re.Match) -> str:
                key = normal(m.group(0))
                if key in by_value:
                    out.replaced += 1
                    return by_value[key]
                out.left.append(f"{path.relative_to(root).as_posix()}:{at + 1}: {m.group(0)}")
                return m.group(0)
            lines[at] = VALUE_COLOUR.sub(swap, row)
        edited = "\n".join(lines)
        if edited != text:
            foundations[path] = edited
    # 4. the shell links the tokens' sheet
    if shell.is_file() and TOKENS_CSS not in texts[shell]:
        link = f'<link rel="stylesheet" href="{TOKENS_CSS}">\n'
        texts[shell] = re.sub(r'(?m)^([ \t]*)(<link[^>]*rel="stylesheet")', lambda m: f"{m.group(1)}{link}{m.group(1)}{m.group(2)}", texts[shell], count=1) \
            if 'rel="stylesheet"' in texts[shell] else texts[shell].replace("</head>", f"{link}</head>", 1)
    # 5. what nothing names
    named = set()
    for text in [*texts.values(), *(p.read_text(encoding="utf-8") for p in folder.glob("*.md"))] if folder.is_dir() else texts.values():
        named |= set(TOKEN_NAME.findall(text))
    for group, name, _, _ in flat_values(held):
        if variable_of(group, name) not in named:
            out.unused.append(variable_of(group, name))
    for path, text in texts.items():                       # the lines that held only a definition go, the rest close up
        text = re.sub(rf"(?m)^[ \t]*{gone}(?:[ \t]*{gone})*[ \t]*\n", "", text)
        texts[path] = re.sub(rf"[ \t]*{gone}", "", text)
    if dry:
        return out
    tokens_path.parent.mkdir(parents=True, exist_ok=True)
    tokens_path.write_text(json.dumps(held, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for path, text in texts.items():
        if text != path.read_text(encoding="utf-8"):
            path.write_text(text, encoding="utf-8", newline="\n")
    for path, text in foundations.items():
        path.write_text(text, encoding="utf-8", newline="\n")
    return out


def said_applied(done: Applied, spec: Path) -> str:
    lines = [f"{spec}: {len(done.moved)} value(s) moved into {TOKENS_FILE}, {len(done.renamed)} token(s) renamed, "
             f"{done.replaced} colour(s) written as a value now name their token"]
    lines += [f"  moved: {m}" for m in done.moved]
    lines += [f"  renamed: {r}" for r in done.renamed]
    if done.left:
        lines.append(f"{len(dict.fromkeys(done.left))} colour(s) no token holds -- add each to {TOKENS_FILE} under its meaning, then apply again:")
        lines += [f"  {left}" for left in dict.fromkeys(done.left)]
    if done.unused:
        lines.append(f"{len(done.unused)} token(s) nothing names: {', '.join(done.unused)}")
    return "\n".join(lines)


def run_selftest() -> int:
    bad: list[str] = []

    def expect(label: str, got: object, wanted: object) -> None:
        if got != wanted:
            bad.append(f"{label}: got {got!r}, wanted {wanted!r}")
        print(f"{'FAILED' if got != wanted else 'ok'}  {label}")

    expect("a short hex colour is read in full", hex_of("#FfF"), ("#ffffff", 1.0))
    expect("an rgb colour is read as hex", hex_of("rgb(9, 105, 218)"), ("#0969da", 1.0))
    expect("an rgba colour keeps its alpha", hex_of("rgba(0, 0, 0, 0.5)"), ("#000000", 0.5))
    one = Read()
    one.take("V1", 'button "Save": color #ffffff; background-color rgb(26, 95, 180); border-radius 6px; '
                   'padding 8px 16px; font-size 0.875rem; font-weight bold; font-family "Inter", sans-serif')
    expect("each colour is read with the part it colours", {k: v.parts for k, v in one.colours.items()},
           {"#ffffff": ["text"], "#1a5fb4": ["surface"]})
    expect("each length is read as its kind", {k: sorted(v) for k, v in one.dimensions.items() if v},
           {"font-size": [(0.875, "rem")], "radius": [(6.0, "px")], "spacing": [(8.0, "px"), (16.0, "px")]})
    expect("a weight in words is read as a number", list(one.weights), [700])
    two = Read()
    two.take("V2", "Back: border 1px solid #0969da, colour #0969da, background #ffffff, at the right of the heading")
    expect("a line written by hand is read at its commas", ({k: v.parts for k, v in two.colours.items()},
                                                            sorted(two.dimensions["border-width"])),
           ({"#0969da": ["border", "text"], "#ffffff": ["surface"]}, [(1.0, "px")]))
    three = Read()
    three.take("V3", 'button "Edit" (no text): color #4169e1; font-family Arial; font-size 18px; line-height 24px; '
                     'border-radius 50%')
    three.take("V3", 'input "1 Star": color #000000; font-family Arial; font-size 13.3333px')
    three.take("V3", 'button "Home": color rgba(0, 0, 0, 0.54); font-family "Inter", Arial; font-size 14px; '
                     'line-height 24.5px; box-shadow rgba(0, 0, 0, 0.2) 0px 3px 1px -2px, rgba(0, 0, 0, 0.14) 0px 2px '
                     '2px 0px')
    expect("an element that shows no text gives no type, and a field on a lone family is taken for one",
           (sorted(three.dimensions["font-size"]), sorted(three.dimensions["line-height"]), list(three.families)),
           ([(14.0, "px")], [(24.5, "px")], ['"Inter", Arial']))
    expect("a radius in percent is read", sorted(three.dimensions["radius"]), [(50.0, "%")])
    expect("a shadow's colours are its own, not colours of the product",
           sorted(three.colours), ["#000000", "#000000/0.54", "#4169e1"])
    three.take("V4", 'button "Save": color #000000; box-shadow rgba(0, 0, 0, 0.2) 0px 3px 1px -2px, rgba(0, 0, 0...')
    expect("a shadow cut short is counted with the whole one it starts",
           [(value[:24], seen.count) for value, seen in shadows_of(three)], [("rgba(0, 0, 0, 0.2) 0px 3", 2)])
    shadow = tokens(three, "a site")["shadow"]
    expect("a shadow is read as its layers", shadow["shadow-1"]["$value"][0] if isinstance(shadow, dict) else None,
           {"color": {"colorSpace": "srgb", "components": [0.0, 0.0, 0.0], "hex": "#000000", "alpha": 0.2},
            "offsetX": {"value": 0, "unit": "px"}, "offsetY": {"value": 3, "unit": "px"},
            "blur": {"value": 1, "unit": "px"}, "spread": {"value": -2, "unit": "px"}})
    translucent = tokens(three, "a site")["color"]
    expect("a translucent colour says its alpha",
           next(str(v["$description"]).split(",")[0] for v in translucent.values()
                if isinstance(v, dict) and "alpha" in v.get("$value", {})) if isinstance(translucent, dict) else None,
           "#000000 at 54%")
    written = tokens(one, "a site")
    expect("the tokens carry their types", sorted(k for k, v in written.items() if isinstance(v, dict)),
           ["color", "font-family", "font-size", "font-weight", "radius", "spacing"])
    colours = written["color"]
    expect("a colour is a value of the format", colours["surface-1"]["$value"] if isinstance(colours, dict) else None,
           {"colorSpace": "srgb", "components": [0.102, 0.3725, 0.7059], "hex": "#1a5fb4"})
    expect("what this writes is JSON that reads back as it was", json.loads(dumped(written)) == written, True)
    if EXAMPLE_TOKENS.is_file():
        kept = {normal(shown) for group, _, shown, _ in flat_values(json.loads(EXAMPLE_TOKENS.read_text(encoding="utf-8"))) if group == "color"}
        seen = {normal(shown) for group, _, shown, _ in flat_values(tokens(read(EXAMPLE_SITE), "evidence/captures/site")) if group == "color"}
        expect("the shop's tokens, named by meaning, keep the colours its captures show", len(kept & seen) >= 8, True)
    else:
        bad.append(f"{EXAMPLE_TOKENS} is not there")
    for message in bad:
        print("ERROR " + message)
    print(f"{'FAILED' if bad else 'PASSED'} -- {len(bad)} problem(s)")
    return 1 if bad else 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Read the styles of a live site's captures as design tokens.")
    parser.add_argument("folder", nargs="?", type=Path, help="the folder of a live site's captures")
    parser.add_argument("--json", type=Path, help="write the design tokens to this file")
    parser.add_argument("--selftest", action="store_true", help="check this script against the shop's captures")
    parser.add_argument("--apply", type=Path, metavar="SPEC",
                        help="move the look's values of this specification into its tokens.json, and make every page name them")
    parser.add_argument("--prefix", help="with --apply: the prefix the product's custom properties share, `vl-`; found if not said")
    parser.add_argument("--dry", action="store_true", help="with --apply: say what would be done, and write nothing")
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    if args.apply:
        if textfile.spec_of(args.apply.resolve()) != args.apply.resolve():
            parser.error(f"{args.apply} is no specification's folder: one that holds data/document.md")
        done = apply(args.apply, args.prefix, args.dry)
        print(said_applied(done, args.apply))
        return 1 if done.left else 0
    if args.folder is None or scout.site_inventory(args.folder) is None:
        parser.error(f"the folder of a live site's captures is required: one that holds its {SITE_INVENTORY}")
    found = read(args.folder)
    print(render(found, args.folder))
    if args.json:
        name = args.folder.resolve()
        spec_root = textfile.spec_of(name)
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(dumped(tokens(found, name.relative_to(spec_root).as_posix() if spec_root else
                                           args.folder.as_posix())), encoding="utf-8", newline="\n")
        print(f"written: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
