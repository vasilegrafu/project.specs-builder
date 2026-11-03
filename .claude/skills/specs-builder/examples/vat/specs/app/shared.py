"""A piece the screens share -- a site's header, its footer -- written once.

Its markup is one file, `prototypes/shared/C1.html`, named for its component: what goes inside the element that is the component,
each thing in it carrying its part, `data-part="C1.2"`. A screen's prototype holds the piece in an element of its own -- its tag, its
class, its anchor -- marked `data-stamp="C1"`, and leaves what is inside to the file: `spec.py stamp` writes the file into every
prototype that holds it. So a change of a shared piece is one change, and no prototype keeps an old copy: while one does, `spec.py
ready` says which.
"""
from __future__ import annotations

import re
from pathlib import Path

import prototypes

SHARED = f"{prototypes.PROTOTYPES}/shared"
SCREENS = f"{prototypes.PROTOTYPES}/screens"
HOST = re.compile(r'<([a-z][a-z0-9]*)\b[^>]*\sdata-stamp="(C\d+)"[^>]*>')


def markups(root: Path) -> dict[str, str]:
    """Each shared piece's markup, by its component's ID."""
    folder = root / SHARED
    return {path.stem: path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip("\n")
            for path in sorted(folder.glob("C*.html"))} if folder.is_dir() else {}


def hosts(text: str) -> list[tuple[str, int, int, str]]:
    """Each element of a prototype marked data-stamp: its component, where what is inside it starts and ends, and the indent of its line."""
    out = []
    for start in HOST.finditer(text):
        tag, depth, at = start.group(1), 1, start.end()
        tags = re.compile(rf"<{tag}\b[^>]*>|</{tag}\s*>")
        while depth:
            found = tags.search(text, at)
            if not found:
                break
            depth += -1 if found.group(0).startswith("</") else 1
            at = found.end()
        if depth:
            continue
        line = text.rfind("\n", 0, start.start()) + 1
        indent = re.match(r"[ \t]*", text[line:]).group(0)
        out.append((start.group(2), start.end(), text.rfind("</", 0, at), indent))
    return out


def plain(markup: str) -> list[str]:
    """What a piece holds, line by line, without the white space around each line or blank lines: two copies are the same when these are."""
    return [line.strip() for line in markup.split("\n") if line.strip()]


def stamped(text: str, held: dict[str, str]) -> str:
    """The prototype with each host holding its piece's markup, indented within it."""
    for ref, start, end, indent in reversed(hosts(text)):
        if ref in held and plain(text[start:end]) != plain(held[ref]):      # white space alone is left as it is
            inside = "\n".join(f"{indent}{line}" if line.strip() else "" for line in held[ref].split("\n"))
            text = f"{text[:start]}\n{inside}\n{indent}{text[end:]}"
    return text


def stamp(root: Path) -> list[str]:
    """Each shared piece written into every prototype that holds it. Says which prototypes moved."""
    held, moved = markups(root), []
    folder = root / SCREENS
    for path in sorted(folder.glob("*.html")) if folder.is_dir() else []:
        raw = path.read_bytes().decode("utf-8")
        text = raw.replace("\r\n", "\n")
        wanted = stamped(text, held)
        if wanted != text:
            path.write_bytes((wanted.replace("\n", "\r\n") if "\r\n" in raw else wanted).encode("utf-8"))
            moved.append(path.relative_to(root).as_posix())
    return moved


def faults(done) -> list[dict]:
    """A host whose copy is not its piece's, a host with no piece, and a piece of no component."""
    root, out = done.root, []
    held = markups(root)
    for ref in held:
        if ref not in done.nodes or done.nodes[ref].kind != "component":
            out.append({"id": ref, "file": f"{SHARED}/{ref}.html", "line": 0, "says": f"a shared piece of no component: there is no {ref} in the data"})
    folder = root / SCREENS
    for path in sorted(folder.glob("*.html")) if folder.is_dir() else []:
        text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        if "data-stamp" not in text:
            continue
        rel = path.relative_to(root).as_posix()
        for ref, start, end, _ in hosts(text):
            line = text.count("\n", 0, start) + 1
            if ref not in held:
                out.append({"id": path.stem, "file": rel, "line": line, "says": f"it holds {ref} as a shared piece, and that piece is not there"})
            elif plain(text[start:end]) != plain(held[ref]):
                out.append({"id": path.stem, "file": rel, "line": line, "says": f"what it holds of {ref} is not its shared piece: run `spec.py stamp`, or "
                                                                                f"change the piece, where it is written once"})
    return out
