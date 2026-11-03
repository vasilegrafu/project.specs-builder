"""The evidence's files as the reading scripts write and read them: Markdown, the text alone. A file an earlier
specification kept as a page -- its text in a `<script type="text/markdown">` block -- is read as that text.
"""
from __future__ import annotations

import re
from pathlib import Path

EVIDENCE = "evidence"
DOCUMENT = "data/document.md"            # what marks a specification's folder
TEXT_RE = re.compile(r'<script type="text/markdown"[^>]*>\n?(.*?)</script>', re.DOTALL)


def text_of(raw: str) -> str:
    """The text a file holds: an earlier page's block, or the file as it is."""
    found = TEXT_RE.search(raw)
    return found.group(1) if found else raw


def held(path: Path) -> str:
    return text_of(path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n"))


def heading_of(text: str) -> str:
    """A text's first heading; nothing where there is none."""
    found = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return found.group(1) if found else ""


def document(text: str) -> str:
    """A file of the evidence: its text, ending in one line break."""
    return text.rstrip("\n") + "\n"


def spec_of(path: Path) -> Path | None:
    """The specification a path stands in, if any: the nearest folder above it that holds data/document.md."""
    return next((p for p in [path, *path.parents] if (p / DOCUMENT).is_file()), None)
