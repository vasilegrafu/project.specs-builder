"""After a change to the skill's `app/`: every specification beside the skill takes it, and each is told apart.

    python .claude/skills/specs-builder/maintain/roll_out.py            every example and target takes `app/`
    python .claude/skills/specs-builder/maintain/roll_out.py --check    says which are behind, and changes nothing
    python .claude/skills/specs-builder/maintain/roll_out.py --force    takes it though one does not check clean

`app/` is the one to edit: the tests and new_spec.py both read it, and every copy is made from it. A specification that
would not check clean under the new application keeps the one it had, and the run exits 1: mend its data, or use --force.
Close any specification that is open first, as its window holds its folder.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 14):
    raise SystemExit(f"specs-builder needs Python 3.14 or later; this is {sys.version.split()[0]}")

import argparse
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import folder  # noqa: E402

SKILL = HERE.parent


def specifications(skill: Path = SKILL) -> list[Path]:
    """Each folder that carries a copy of the application: the examples, and the targets of the repository around the skill."""
    places = sorted((skill / "examples").glob("*/specs"))
    if len(skill.parents) > 2:
        places += sorted(skill.parents[2].glob("targets/*/specs"))
    return [p for p in places if (p / "app" / "spec.py").is_file()]


def behind(skill: Path = SKILL) -> dict[Path, list[str]]:
    """What differs from the skill's `app/`, and an AGENTS.md whose block is not the skill's, for each that is behind."""
    block = (skill / "app/guide/AGENTS.md").read_text(encoding="utf-8").strip()
    found = {}
    for place in specifications(skill):
        said = folder.differing(place / "app", skill / "app")
        agents = place / "AGENTS.md"
        if not agents.is_file() or block not in agents.read_text(encoding="utf-8"):
            said.append("AGENTS.md")
        if said:
            found[place] = said
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="say which are behind, and change nothing")
    parser.add_argument("--force", action="store_true", help="take the application though a specification does not check clean")
    args = parser.parse_args()
    if not args.check:
        failed = [place for place in specifications() if folder.update_app(place, args.force)]
        if failed:
            print(f"{len(failed)} kept what they had: {', '.join(str(p) for p in failed)}", file=sys.stderr)
    left = behind()
    for place, said in left.items():
        print(f"{place}: behind: {', '.join(sorted(said)[:6])}" + (f" and {len(said) - 6} more" if len(said) > 6 else ""))
    if not left:
        print(f"{len(specifications())} specification(s) carry the skill's application")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
