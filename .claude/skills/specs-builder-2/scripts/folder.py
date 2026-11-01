"""What every specification's folder holds beside its data: the application, copied whole so the folder works alone
and keeps the version it was made with; the two launchers; the line that keeps the database out of git; and the
product's page the prototypes are drawn in. Shared by new_spec.py and import_site.py.
"""
from __future__ import annotations

import shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
APP = SKILL / "app"
LAUNCH_CMD = ('@echo off\r\nrem Opens this specification: starts its application and the browser on it. Close this '
              'window to stop it.\r\npython "%~dp0app\\serve.py" --open %*\r\nif errorlevel 1 pause\r\n')
LAUNCH_SH = ('#!/bin/sh\n# Opens this specification: starts its application and the browser on it. Ctrl+C stops it.\n'
             'cd "$(dirname "$0")" && exec python3 app/serve.py --open "$@"\n')
SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>
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


def write_shell(target: Path, body_class: str = "") -> None:
    """The product's page, around every prototype."""
    path = target / "prototypes/page.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SHELL.replace("{body_class}", body_class), encoding="utf-8", newline="\n")
