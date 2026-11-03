"""The design system's values, on their way to every page."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from support import SKILL


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """tokens.json reaches every page by itself: through the application, in the export, and in a new specification."""
    import socket
    import urllib.request

    root = tmp / "tokened"
    shutil.copytree(SKILL / "examples/bakery/specs", root)
    path = root / "prototypes/tokens.json"
    text = path.read_text(encoding="utf-8")
    assert "#b0244d" in text
    path.write_text(text.replace("#b0244d", "#123456"), encoding="utf-8")

    def spec(*words: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", "app/spec.py", *words], cwd=root, capture_output=True, text=True, encoding="utf-8", check=False)

    spec("export")
    told = "".join(p.read_text(encoding="utf-8") for p in (root / "export").glob("*.html"))
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = subprocess.Popen([sys.executable, "-B", "app/serve.py", "--port", str(port)], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    served = ""
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/prototype/assets/css/tokens.css", timeout=2) as answer:
                    served = answer.read().decode("utf-8")
                break
            except OSError:
                time.sleep(.1)
    finally:
        server.terminate()
        server.wait(10)
    # the look reaches the prototypes: a value changed lists those it reaches, with what moved, until each is looked at
    path.write_text(text, encoding="utf-8")                                     # the value back, so the stamps start true
    spec("do", "set", "document", "status", "draft", "--because", "a trial")
    path.write_text(text.replace("#b0244d", "#123456").replace("#3c6a3d", "#234567"), encoding="utf-8")   # the action, everywhere; success, on C6 alone
    opened = spec("open").stdout
    reached = re.search(r"prototypes to look at[^:]*: (.+)", spec("ready").stdout)
    looked = reached.group(1).split(", ") if reached else []
    path.write_text(text.replace("#3c6a3d", "#234567"), encoding="utf-8")                      # the action back: success alone moved
    narrow = re.search(r"prototypes to look at[^:]*: (.+)", spec("ready").stdout)
    narrowed = narrow.group(1).split(", ") if narrow else []
    spec("do", "confirm-drawn", "C6")
    after = re.search(r"prototypes to look at[^:]*: (.+)", spec("ready").stdout)
    # a colour written as a value is refused, in a sheet, a prototype and a foundation, and a line that says why is kept
    css = root / "prototypes/assets/css/product.css"
    kept = css.read_text(encoding="utf-8")
    css.write_text(kept + ".x-trial { color: #abcdef; }\n", encoding="utf-8")
    literal = spec("check")
    css.write_text(kept + ".x-trial { color: #abcdef; } /* literal: a trial */\n", encoding="utf-8")
    allowed = spec("check")
    foundation = next(iter(sorted((root / "data/foundations").glob("*.md"))))
    foundation.write_text(foundation.read_text(encoding="utf-8") + "\nA value written here, #654321, by mistake.\n", encoding="utf-8")
    in_text = spec("check")
    css.write_text(kept, encoding="utf-8")
    foundation.write_text(foundation.read_text(encoding="utf-8").replace("\nA value written here, #654321, by mistake.\n", ""), encoding="utf-8")
    # a specification whose styles still hold the values: `tokens.py --apply` moves them, and every page names them
    moved = tmp / "tokened-moved"
    shutil.copytree(SKILL / "examples/shop/specs", moved, ignore=shutil.ignore_patterns(".cache"))
    sheet = moved / "prototypes/assets/css/product.css"
    sheet.write_text(sheet.read_text(encoding="utf-8").replace("var(--color-brand)", "var(--vl-brand)", 2)
                     + ".vl-page { --vl-brand: #2563eb; }\n.x-trial { color: #2563eb; border-color: #0a0b0c; }\n", encoding="utf-8")
    applied = subprocess.run([sys.executable, "-B", str(SKILL / "scripts/tokens.py"), "--apply", str(moved)], capture_output=True, text=True, encoding="utf-8", check=False)
    rewritten = sheet.read_text(encoding="utf-8")
    (root / "prototypes/assets/css/product.css").write_text("a { color: var(--color-nothing); }\n", encoding="utf-8")
    refused = spec("check")
    fresh = tmp / "tokened-new"
    subprocess.run([sys.executable, "-B", str(SKILL / "scripts/new_spec.py"), str(fresh), "--name", "New", "--kind", "application", "--summary", "A new one."], capture_output=True, check=False)
    return [("a token changed in tokens.json reaches every page through the application, with no file written and no step taken",
             "--color-action: #123456;" in served and not (root / "prototypes/assets/css/tokens.css").exists()),
            ("the one-file export carries the tokens as they stand", "--color-action: #123456;" in told),
            ("a value changed in tokens.json lists the prototypes its token reaches, with what moved, and not the others",
             {"SC1", "SC3", "C5", "C6"} <= set(looked) and "--color-action #b0244d -> #123456" in opened and narrowed == ["C6"]),
            ("a prototype looked at and confirmed is told no more", after is None),
            ("a colour written as a value in a sheet is refused at its line, and one with `/* literal: why */` is kept",
             literal.returncode != 0 and "#abcdef is a colour written here" in literal.stdout and allowed.returncode == 0),
            ("a colour written in a foundation's text is refused: a foundation names its token",
             in_text.returncode != 0 and "#654321" in in_text.stdout and "names its token" in in_text.stdout),
            ("tokens.py --apply moves a sheet's values into the tokens, renames their uses, replaces the colours a token holds and lists the rest",
             "var(--vl-brand)" not in rewritten and "--vl-brand:" not in rewritten and "color: var(--color-brand)" in rewritten
             and applied.returncode == 1 and "#0a0b0c" in applied.stdout),
            ("a variable no token holds is a fault at its file and line", refused.returncode != 0 and "--color-nothing is no token" in refused.stdout + refused.stderr),
            ("a new specification's page takes its look from the tokens", "assets/css/tokens.css" in (fresh / "prototypes/page.html").read_text(encoding="utf-8"))]
