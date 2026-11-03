"""What every specification's folder holds beside its data: the application, copied whole so the folder works alone
and keeps the version it was made with; the two launchers; the line that keeps the database out of git; the instructions
an agent finds by itself, AGENTS.md and CLAUDE.md; and the product's page the prototypes are drawn in. Shared by
new_spec.py and import_site.py.
"""
from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
APP = SKILL / "app"
LAUNCH_CMD = ('@echo off\r\nrem Opens this specification: starts its application and the browser on it. Close this '
              'window to stop it.\r\npython "%~dp0app\\serve.py" --open %*\r\nif errorlevel 1 pause\r\n')
LAUNCH_SH = ('#!/bin/sh\n# Opens this specification: starts its application and the browser on it. Ctrl+C stops it.\n'
             'cd "$(dirname "$0")" && exec python3 app/serve.py --open "$@"\n')
AGENTS_START = "<!-- specs-builder:"
AGENTS_END = "<!-- /specs-builder -->"
README_START = "<!-- specs-builder README:"
README_END = "<!-- /specs-builder README -->"
SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>
<link rel="stylesheet" href="assets/css/tokens.css">
<link rel="stylesheet" href="assets/css/product.css">
<script src="assets/js/sample.js" defer></script>
<script src="assets/js/prototype.js" defer></script>
</head>
<body{body_class}>
{{body}}
</body>
</html>
"""


def write_app(target: Path) -> None:
    """The application and its launchers, written over what was there."""
    shutil.rmtree(target / "app", ignore_errors=True)
    shutil.copytree(APP, target / "app", ignore=shutil.ignore_patterns("__pycache__"))
    (target / "index.cmd").write_bytes(LAUNCH_CMD.encode("utf-8"))
    (target / "index.sh").write_text(LAUNCH_SH, encoding="utf-8", newline="\n")
    (target / ".gitignore").write_text(".cache/\nexport/\n", encoding="utf-8", newline="\n")
    write_agents(target)


def write_agents(target: Path) -> None:
    """AGENTS.md, which agents of any make read by themselves, and CLAUDE.md, which sends Claude Code to it. The block
    between its two marks is the skill's; whatever else is in the file is whoever wrote it, and stays."""
    block = (APP / "guide/AGENTS.md").read_text(encoding="utf-8").strip()
    path = target / "AGENTS.md"
    held = path.read_text(encoding="utf-8") if path.is_file() else ""
    start, end = held.find(AGENTS_START), held.find(AGENTS_END)
    if start >= 0 and end > start:
        text = held[:start] + block + held[end + len(AGENTS_END):]
    else:
        text = f"{block}\n{held}" if held else f"{block}\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    claude = target / "CLAUDE.md"
    said = claude.read_text(encoding="utf-8") if claude.is_file() else ""
    if "AGENTS.md" not in said:
        claude.write_text(f"@AGENTS.md\n{said}", encoding="utf-8", newline="\n")
    write_readme(target)


def product_name(target: Path) -> str:
    """The product's name, as its document says it."""
    path = target / "data/document.md"
    held = path.read_text(encoding="utf-8") if path.is_file() else ""
    name = next((line.split(":", 1)[1].strip() for line in held.splitlines() if line.startswith("name:")), "")
    return name or target.parent.name if target.name == "specs" else name or target.name


def write_readme(target: Path) -> None:
    """README.md, for whoever is handed the folder: what it is, how to read it and how to build from it. As in AGENTS.md, the block
    between its two marks is the skill's, and whatever else is in the file stays."""
    block = (APP / "guide/README.md").read_text(encoding="utf-8").strip().replace("{{name}}", product_name(target))
    path = target / "README.md"
    held = path.read_text(encoding="utf-8") if path.is_file() else ""
    start, end = held.find(README_START), held.find(README_END)
    if start >= 0 and end > start:
        text = held[:start] + block + held[end + len(README_END):]
    else:
        text = f"{block}\n{held}" if held else f"{block}\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def differing(mine: Path, theirs: Path) -> list[str]:
    """The files that are not the same in the two folders, __pycache__ apart."""
    skip = ["__pycache__"]
    found = filecmp.dircmp(mine, theirs, ignore=skip)
    out = found.left_only + found.right_only + found.diff_files + found.funny_files
    return out + [f"{name}/{inner}" for name in found.common_dirs for inner in differing(mine / name, theirs / name)]


def update_app(target: Path, force: bool = False) -> int:
    """A specification takes the skill's application. The data is not touched. The new one goes in beside the old, and the
    old comes back if the specification does not check clean under it: a newer application may ask more of the data, and a
    folder that opened before an update still opens after it. `force` keeps the new one, to mend the data under it."""
    app, fresh, old = target / "app", target / "app.new", target / "app.old"
    if not (target / "data").is_dir() or not app.is_dir():
        print(f"{target}: no specification here: it holds no data/ and app/", file=sys.stderr)
        return 2
    if app.resolve() == APP.resolve():
        print(f"{target}: this is the skill's own application", file=sys.stderr)
        return 2
    changed = differing(app, APP)
    if not changed:
        write_agents(target)
        print(f"{target}: its application is up to date")
        return 0
    for leftover in (fresh, old):
        shutil.rmtree(leftover, ignore_errors=True)
    shutil.copytree(APP, fresh, ignore=shutil.ignore_patterns("__pycache__"))
    try:
        os.replace(app, old)
        os.replace(fresh, app)
    except OSError:
        if old.exists() and not app.exists():
            os.replace(old, app)
        shutil.rmtree(fresh, ignore_errors=True)
        print(f"{target}: its application is in use. Close its window, then run this again", file=sys.stderr)
        return 1
    done = subprocess.run([sys.executable, "-B", str(app / "spec.py"), "check"], cwd=target, capture_output=True, text=True, encoding="utf-8")
    if done.returncode and not force:
        shutil.rmtree(app, ignore_errors=True)
        os.replace(old, app)
        print(done.stdout + done.stderr, end="")
        print(f"{target}: left as it was: the data does not check clean under the new application. Mend what it says, "
              f"or use --force to take the new one and mend it after", file=sys.stderr)
        return 1
    shutil.rmtree(old, ignore_errors=True)
    shutil.rmtree(app / "__pycache__", ignore_errors=True)
    (target / "index.cmd").write_bytes(LAUNCH_CMD.encode("utf-8"))
    (target / "index.sh").write_text(LAUNCH_SH, encoding="utf-8", newline="\n")
    write_agents(target)
    said = done.stdout.strip().splitlines()[-1] if done.stdout.strip() else ""
    print(f"{target}: its application is updated, {len(changed)} file(s). {said}\n"
          f"If it is open, close it and open it again.")
    return 0


def write_shell(target: Path, body_class: str = "") -> None:
    """The product's page, around every prototype."""
    path = target / "prototypes/page.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SHELL.replace("{body_class}", body_class), encoding="utf-8", newline="\n")
