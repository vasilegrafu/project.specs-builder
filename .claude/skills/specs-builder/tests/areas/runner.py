"""The selftest itself: a check that fails names its condition, and an area that crashes takes nothing else with it."""
from __future__ import annotations

import contextlib
import io
import types
from pathlib import Path

import selftest
import support


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    source = """
def run(tmp, clean):
    one, two, reached = 1, 2, []
    checks = [("each holds", one == 1 and two == 2)]
    checks.append(("the second does not", one == 1 and two == 3 and reached.append("third") is None))
    checks.append(("a plain truth", one == 2))
    return checks + list_of(one) + [("what was reached", not reached)]


def list_of(one):
    return [("in a returned list", one == 1 and one == 9)]
"""
    held = dict(support.watched("sample", source, tmp / "sample.py").run(tmp, clean))
    checks = [("a check's conditions are watched: all true is true, and the first that fails is named, the rest not run",
               bool(held["each holds"]) and not held["the second does not"] and held["the second does not"].failed == "two == 3"
               and held["what was reached"] and held["in a returned list"].failed == "one == 9"),
              ("a plain truth stays as it was", held["a plain truth"] is False)]

    def crashing() -> types.ModuleType:
        return support.watched("crashing", "def run(tmp, clean):\n    raise OSError('nothing there')\n", tmp / "crashing.py")

    def quiet() -> types.ModuleType:
        return support.watched("quiet", "def run(tmp, clean):\n    return [('fine', 1 == 1 and 2 == 2), ('not fine', 1 == 1 and 2 == 3)]\n", tmp / "quiet.py")

    bad: list[str] = []
    said = io.StringIO()
    real = support.area
    support.area = lambda name: crashing() if name == "crashing" else quiet()
    try:
        with contextlib.redirect_stdout(said):
            selftest.run("crashing", clean, bad)
            selftest.run("quiet", clean, bad)
    finally:
        support.area = real
    told = said.getvalue()
    checks.append(("an area that crashes fails, says why, and the next area still runs",
                   "FAIL crashing crashed:" in told and "OSError: nothing there" in told and "ok   fine" in told and bad[0].startswith("crashing crashed")))
    checks.append(("a failure says its condition, on screen and in the list at the end",
                   "FAIL not fine" in told and "failed: 2 == 3" in told and bad[1] == "quiet: not fine -- failed: 2 == 3"))
    return checks
