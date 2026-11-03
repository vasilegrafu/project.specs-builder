"""What reads material, apart from the application: each script's own test, the scripts that run in a page, and the agents'
briefs held to the facets the merge asks of them."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from support import SKILL

TESTED = ("a11y_tree", "api_spec", "crawl", "material_plan", "scan_code", "scout", "source_maps", "tokens")
IN_THE_PAGE = ("capture.js", "watch.js")


def brief(role: str) -> Path:
    """An agent's brief: a role that collects or synthesises is an archaeologist."""
    named = SKILL / "agents" / f"{role}-archaeologist.md"
    return named if named.is_file() else SKILL / "agents" / f"{role}.md"


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    checks = []
    for name in TESTED:
        done = subprocess.run([sys.executable, "-B", str(SKILL / "scripts" / f"{name}.py"), "--selftest"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
        last = done.stdout.strip().splitlines()[-1] if done.stdout.strip() else done.stderr.strip()[-200:]
        checks.append((f"{name}.py passes its own test" + ("" if done.returncode == 0 else f" -- {last}"), done.returncode == 0))
    written = sorted(p.stem for p in (SKILL / "scripts").glob("*.py") if "def run_selftest" in p.read_text(encoding="utf-8"))
    checks.append(("every script with a test of its own is run here", written == sorted(TESTED)))

    node = shutil.which("node")
    if node:
        for name in IN_THE_PAGE:
            done = subprocess.run([node, "--check", str(SKILL / "scripts" / name)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            checks.append((f"{name}, which runs in a page, parses" + ("" if done.returncode == 0 else f" -- {done.stderr[-200:]}"), done.returncode == 0))
        broken = [p.name for p in sorted((SKILL / "app/web").rglob("*.js"))
                  if subprocess.run([node, "--check", str(p)], capture_output=True).returncode]
        checks.append((f"every script of the application parses{': ' + ', '.join(broken) if broken else ''}", not broken))
    else:
        print("     the scripts that run in a page left out: they need Node", flush=True)

    facets = json.loads((SKILL / "app/agents.json").read_text(encoding="utf-8"))["facets"]
    for role, wanted in facets.items():
        text = brief(role).read_text(encoding="utf-8")
        missing = [f for f in wanted if f not in text]
        checks.append((f"the {role} brief names every facet the merge asks of it" + (f" -- not: {', '.join(missing)}" if missing else ""), not missing))
    briefs = {p.stem.removesuffix("-archaeologist") for p in (SKILL / "agents").glob("*.md")} - {"rules"}
    checks.append(("every agent's brief has its facets, and every role its brief", briefs == set(facets)))
    return checks
