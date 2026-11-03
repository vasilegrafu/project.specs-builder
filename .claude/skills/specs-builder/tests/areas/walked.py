"""The Graph, with a real mouse."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from support import SKILL


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """The Graph walked with a real mouse in a real Chrome, where this computer can: it needs Node and Chrome, and is
    left out, saying so, where either is missing."""
    if not shutil.which("node"):
        print("     the Graph's walk left out: it needs Node")
        return []
    root = tmp / "walked"
    shutil.copytree(clean, root)
    done = subprocess.run(["node", str(SKILL / "tests/graph_walk.mjs"), str(root)], capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHON": sys.executable, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=400)
    if "no Chrome found" in done.stdout + done.stderr:
        print("     the Graph's walk left out: it needs Chrome")
        return []
    if done.returncode:
        print(done.stdout[-1500:] + done.stderr[-500:])
    return [("the Graph walked with a real mouse: every click, double click and drag in its pictures does what it says", done.returncode == 0)]
