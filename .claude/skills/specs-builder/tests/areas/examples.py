"""The examples: each carries the skill's application, loads clean, and quotes what its material says."""
from __future__ import annotations

import shutil
from pathlib import Path

from support import loading, SKILL


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    import evidence

    checks = []
    # each specification carries the app it was made with (decision 7): every example's is the skill's own,
    # and every example loads clean
    mine = {p.relative_to(SKILL / "app").as_posix(): p.read_bytes()
            for p in (SKILL / "app").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    for example in sorted((SKILL / "examples").glob("*/specs")):
        theirs = {p.relative_to(example / "app").as_posix(): p.read_bytes()
                  for p in (example / "app").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        drift = sorted(n for n in mine.keys() | theirs.keys() if mine.get(n) != theirs.get(n))
        name = example.parent.name
        checks.append((f"the {name} example carries the skill's app as it is{': ' + ', '.join(drift) if drift else ''}", not drift))
        copy = tmp / f"example-{name}"
        shutil.copytree(example, copy, ignore=shutil.ignore_patterns(".cache", "__pycache__"))
        found = loading.load(copy)
        checks.append((f"the {name} example loads clean: {len(found.nodes)} nodes" + (f" -- {found.problems[:2]}" if found.problems else ""), not found.problems))
        here = loading.load(example)
        missed = []
        for n in here.nodes.values():
            if n.kind != "finding" or not n.fields.get("quote"):
                continue
            src = next((e.dst for e in here.edges if e.src == n.id and e.rel == "from"), "")
            there = evidence.source_place(example, here.nodes[src].fields.get("where", "")) if src else None
            file = evidence.file_of(there, n.fields.get("where", "")) if there is not None else None
            if file is None or evidence.squeeze(n.fields["quote"]) not in evidence.squeeze(file.read_text(encoding="utf-8", errors="replace")):
                missed.append(n.id)
        checks.append((f"every quote of the {name} example is in the file its finding names" + (f" -- not: {', '.join(missed[:5])}" if missed else ""), not missed))
    return checks
