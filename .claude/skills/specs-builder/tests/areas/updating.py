"""A specification taking a newer application."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from support import edit, SKILL


def rolled(tmp: Path) -> list[tuple[str, bool]]:
    """The roll-out finds every copy, and names one left behind: on a small skill of its own, and on this one."""
    sys.path.insert(0, str(SKILL / "maintain"))
    import roll_out

    skill = tmp / "a-skill"
    for place in (skill, skill / "examples/one/specs", skill / "examples/two/specs"):
        (place / "app/guide").mkdir(parents=True)
        (place / "app/spec.py").write_text("# the same\n", encoding="utf-8")
        (place / "app/guide/AGENTS.md").write_text("<!-- the block -->\n", encoding="utf-8")
    (skill / "examples/one/specs/AGENTS.md").write_text("<!-- the block -->\nmine\n", encoding="utf-8")
    (skill / "examples/two/specs/AGENTS.md").write_text("<!-- an older block -->\n", encoding="utf-8")
    (skill / "examples/no-specification/specs").mkdir(parents=True)
    alike = len(roll_out.specifications(skill)) == 2
    said = roll_out.behind(skill)
    (skill / "examples/one/specs/app/spec.py").write_text("# left behind\n", encoding="utf-8")
    left = roll_out.behind(skill)
    here = subprocess.run([sys.executable, "-B", str(SKILL / "maintain/roll_out.py"), "--check"], capture_output=True, text=True, encoding="utf-8")
    return [("the roll-out finds each copy, and names a file or an AGENTS.md left behind",
             alike and list(said) == [skill / "examples/two/specs"] and said[skill / "examples/two/specs"] == ["AGENTS.md"]
             and left[skill / "examples/one/specs"] == ["spec.py"]),
            ("every specification beside the skill carries its application and its instructions" + (f" -- {here.stdout.strip()[:300]}" if here.returncode else ""),
             here.returncode == 0)]


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """A specification takes a newer application, and keeps the one it had if it would not check clean under it."""
    root = tmp / "updating"
    shutil.copytree(clean, root)
    tool = str(SKILL / "scripts/new_spec.py")

    def update(*more: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", tool, str(root), "--update-app", *more], capture_output=True, text=True, encoding="utf-8")

    (root / "AGENTS.md").unlink(missing_ok=True)
    (root / "CLAUDE.md").unlink(missing_ok=True)
    first = update()
    instructed = (root / "AGENTS.md").is_file() and (root / "CLAUDE.md").read_text(encoding="utf-8").startswith("@AGENTS.md")
    data = {p: p.read_bytes() for p in (root / "data").rglob("*") if p.is_file()}
    (root / "app/web/engine.js").write_text("// an older one\n", encoding="utf-8")
    (root / "app/left-behind.py").write_text("", encoding="utf-8")
    second = update()
    whole = (root / "app/web/engine.js").read_bytes() == (SKILL / "app/web/engine.js").read_bytes() and not (root / "app/left-behind.py").exists()
    untouched = all(p.read_bytes() == b for p, b in data.items())
    edit(root, "data/requirements/R4.md", "serves: G2, G3", "serves: G99")
    (root / "app/web/engine.js").write_text("// an older one\n", encoding="utf-8")
    third = update()
    kept = (root / "app/web/engine.js").read_text(encoding="utf-8") == "// an older one\n" and (root / "app/spec.py").is_file()
    forced = update("--force")
    took = (root / "app/web/engine.js").read_bytes() == (SKILL / "app/web/engine.js").read_bytes()
    nothing = subprocess.run([sys.executable, "-B", tool, str(tmp / "no-such-folder"), "--update-app"], capture_output=True, text=True)
    roll_out = rolled(tmp)
    return roll_out + [("--update-app says when there is nothing to do, and otherwise takes the skill's application whole, the data untouched",
             first.returncode == 0 and "up to date" in first.stdout and instructed and second.returncode == 0 and "updated" in second.stdout and whole and untouched
             and not (root / "app.new").exists() and not (root / "app.old").exists()),
            ("--update-app keeps the application a specification had if it would not check clean under the new one, and says so; --force takes it",
             third.returncode == 1 and kept and "left as it was" in third.stderr and not (root / "app.old").exists()
             and forced.returncode == 0 and took),
            ("--update-app refuses a folder that holds no specification", nothing.returncode == 2)]
