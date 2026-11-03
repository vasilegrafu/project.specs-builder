"""specs-builder's selftest: the whole skill proved on copies of the shop example, each check planting the fault it is
about. Each area of it is a file of `tests/areas/`.

    python .claude/skills/specs-builder/tests/selftest.py                    every area, in a few minutes
    python .claude/skills/specs-builder/tests/selftest.py --only building    one area, or several
    python .claude/skills/specs-builder/tests/selftest.py --list             the areas

An area that crashes fails, says where, and the others still run. A check that fails says which of its conditions did.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 14):
    raise SystemExit(f"specs-builder needs Python 3.14 or later; this is {sys.version.split()[0]}")

import argparse
import shutil
import tempfile
import time
import traceback
from pathlib import Path

import support

AREAS = ("data", "served", "operations", "staleness", "building", "procedures", "documents", "reading", "readers", "guarded",
         "accounted", "updating", "tokened", "walked", "examples", "runner")


def run(name: str, clean: Path, bad: list[str]) -> None:
    """One area, in a folder of its own, each check said as it stands."""
    began = time.perf_counter()
    count = 0
    print(f"== {name}", flush=True)
    try:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            checks = support.area(name).run(Path(tmp), clean)
    except Exception:                                   # one area's crash is that area's failure, and no other's
        frames = traceback.format_exc().strip().splitlines()
        print(f"FAIL {name} crashed:", *(f"     {line}" for line in frames[-5:]), sep="\n", flush=True)
        bad.append(f"{name} crashed: {frames[-1]}")
        return
    for title, held in checks:
        count += 1
        print(f"{'ok  ' if held else 'FAIL'} {title}", flush=True)
        if not held:
            failed = getattr(held, "failed", "")
            if failed:
                print(f"     failed: {failed}", flush=True)
            bad.append(f"{name}: {title}" + (f" -- failed: {failed}" if failed else ""))
    print(f"   {count} check(s) in {time.perf_counter() - began:.1f}s", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", nargs="+", choices=AREAS, metavar="AREA", help="only these areas")
    parser.add_argument("--list", action="store_true", help="list the areas")
    args = parser.parse_args()
    if args.list:
        print("\n".join(AREAS))
        return 0
    started = time.perf_counter()
    bad: list[str] = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        clean = Path(tmp) / "clean"
        shutil.copytree(support.EXAMPLE, clean, ignore=shutil.ignore_patterns(".cache", "__pycache__"))
        for name in args.only or AREAS:
            run(name, clean, bad)
    for line in bad:
        print(f"ERROR {line}")
    print(f"{'PASSED' if not bad else 'FAILED'} -- {len(bad)} problem(s) in {time.perf_counter() - started:.1f}s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
