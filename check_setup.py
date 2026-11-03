"""Checks that this computer can run specs-builder, and says what to do about anything missing.

Run it with check-setup.cmd on Windows, or `sh check-setup.sh` on macOS and Linux. It changes nothing.
This file runs on an old Python on purpose: its job is to say so.
"""
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLE = HERE / ".claude" / "skills" / "specs-builder" / "examples" / "shop" / "specs"
GUIDE = "GETTING-STARTED.md"
problems = 0


def good(word):
    print("  OK       " + word)


def bad(word, fix):
    global problems
    problems += 1
    print("  MISSING  " + word)
    print("           " + fix)


print("")
print("Checking this computer for specs-builder")
print("")

version = sys.version_info
named = "%d.%d.%d" % (version[0], version[1], version[2])
python_ok = version >= (3, 14)
if python_ok:
    good("Python " + named)
else:
    bad("Python 3.14 or later (this one is " + named + ")", "Install it: see step 2 of " + GUIDE)

if sqlite3.sqlite_version_info >= (3, 8):
    good("Python's database (SQLite)")
else:
    bad("a newer SQLite", "Install Python again from python.org")

if (EXAMPLE / "app" / "spec.py").is_file():
    good("The skill is in this folder")
else:
    bad("the skill's files", "This folder is incomplete: unpack the whole of what you were given, then run this again")

if python_ok and (EXAMPLE / "app" / "spec.py").is_file():
    done = subprocess.run([sys.executable, "app/spec.py", "check"], cwd=str(EXAMPLE), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    last = done.stdout.decode("utf-8", "replace").strip().splitlines()[-1:] or [""]
    if done.returncode == 0:
        good("The example opens and checks clean")
    else:
        bad("a clean example: " + last[0][:90], "The folder may be damaged: unpack it again")

claude = shutil.which("claude")
if claude:
    done = subprocess.run([claude, "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    good("Claude Code " + done.stdout.decode("utf-8", "replace").strip()[:40])
else:
    bad("Claude Code", "Install it: see step 3 of " + GUIDE + ". You can read the example without it, but not write your own")

print("")
if problems:
    print("%d thing(s) to put right. Then run this again." % problems)
else:
    print("All good. Next: open the example, step 5 of " + GUIDE)
print("")
sys.exit(1 if problems else 0)
