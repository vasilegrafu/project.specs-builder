"""Start a new specification: a folder with its document, its application and its launchers, loading clean, ready
for every other part to be written through its operations.

    python .claude/skills/specs-builder-2/scripts/new_spec.py <folder> --name "Invoices" --kind application \\
        --summary "Customers take an invoice out of the portal as a PDF, so that they stop writing to support for one."

The document starts as `draft`, its summary as given. Where the kind holds `application`, the prototypes' page is
written too, grey until the product has a look. A folder that holds a specification already is refused.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 14):
    raise SystemExit(f"specs-builder-2 needs Python 3.14 or later; this is {sys.version.split()[0]}")

import argparse
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import folder  # noqa: E402

KINDS = ("application", "api", "library", "part", "process")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", type=Path, help="the new specification's folder")
    parser.add_argument("--name", required=True, help="the product's name")
    parser.add_argument("--kind", required=True,
                        help=f"what the product is: one of {', '.join(KINDS)}, or a mix, 'application, api'")
    parser.add_argument("--summary", required=True, help="three sentences: what, for whom, for what outcome")
    args = parser.parse_args()
    target = args.target.resolve()
    kinds = [k.strip() for k in args.kind.split(",") if k.strip()]
    wrong = [k for k in kinds if k not in KINDS]
    if wrong or not kinds:
        parser.error(f"--kind {args.kind}: each is one of {', '.join(KINDS)}")
    if (target / "data").exists():
        parser.error(f"{target}: it holds a specification already")
    (target / "data").mkdir(parents=True, exist_ok=True)
    summary = "\n".join(" ".join(line.split()) for line in args.summary.strip().splitlines() if line.strip())
    (target / "data/document.md").write_text(
        f"---\nname: {' '.join(args.name.split())}\nkind: {', '.join(kinds)}\nstatus: draft\n---\n\n{summary}\n",
        encoding="utf-8", newline="\n")
    folder.write_app(target)
    if "application" in kinds:
        folder.write_shell(target)
    sys.path.insert(0, str(target / "app"))
    import load as loading                      # noqa: PLC0415 -- the copy just written, as the folder will run it
    import logic                                # noqa: PLC0415
    done = loading.load(target)
    for file, line, message in done.problems:
        print(f"{file}:{line}: {message}" if line else f"{file}: {message}")
    if done.problems:
        return 1
    loading.build(done)
    logic.notice(target, done)                  # the first stamps: the data as it is
    print(f"{target}: a new specification, {args.name}, draft -- open it with index.cmd (or index.sh); "
          f"write it with `python app/spec.py do ...`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
