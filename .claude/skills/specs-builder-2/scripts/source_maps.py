#!/usr/bin/env python3
"""Fetch the source code a live site publishes in its source maps, so that scan_code.py can read it as code.

    python scripts/source_maps.py <site's captures folder>                  # read the maps; say what it would write
    python scripts/source_maps.py <site's captures folder> --fetch          # and write it, into <folder>/source/
    python scripts/source_maps.py --selftest

Only when the user has said yes for this site, with --fetch or without:
either way the scripts and their maps are requested of the site, which is
the one request of the skill's own a reader of a live site makes besides
the walk (references/reading-a-live-site.md). Without --fetch nothing is
written.

A site built from code ships its scripts bundled and minified, and many
publish beside each a source map -- `main.js.map` -- that holds the code it
was built from, file by file. Where a site does, the product's own front
end can be read as code: its routes, its messages, its limits, its states.

The scripts are those the captures list, `request: script /static/main.js`
-- capture.js lists every script of the site's own host -- at the host of
the inventory's Address. For each, the script is fetched and its last
line read for `//# sourceMappingURL=`; where it names none, `<script>.map`
is tried. A map's sources that carry their text (`sourcesContent`) are
written under `source/<the path the map gives>`, without the bundler's
prefixes (`webpack://`, `../`); what is the bundler's own or a library's --
`node_modules/`, `webpack/` -- is left out. Nothing of another host is
fetched, nothing but GET, nothing with a cookie or a key, at most
MOST_FILES files and MOST_BYTES bytes.

Give `source/` its own row under Sources in the evidence -- `S4 |
evidence/captures/<site>/source/` -- so that it is covered and read as the
code it is, and its captures' folder does not have to cover it. Standard
library only.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import re
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textfile  # noqa: E402
import scout  # noqa: E402

SOURCE = "source"
INVENTORY = "inventory.md"
MOST_FILES = 5000
MOST_BYTES = 50_000_000
LEFT_OUT = re.compile(r"(^|/)(node_modules|bower_components|webpack|\(webpack\)|vite|\.pnpm|external)(/|$)|"
                      r"^webpack/bootstrap|^\x00|^\(")
MAP_RE = re.compile(r"//[#@]\s*sourceMappingURL=(\S+)\s*$")
AGENT = "specs-builder source_maps.py (reading a site the user asked to have read)"


def scripts_of(site: Path) -> tuple[str, list[str]]:
    """The site's origin, from its inventory, and the paths of its own scripts its captures list."""
    held = scout.site_inventory(site)
    inventory = textfile.text_of(held.read_text(encoding="utf-8-sig", errors="replace")) if held else ""
    found = re.search(r"^- \*\*Address:\*\* *(\S+)", inventory, re.MULTILINE)
    origin = ""
    if found:
        parts = urlsplit(found.group(1))
        origin = f"{parts.scheme}://{parts.netloc}"
    paths: list[str] = []
    for capture in scout.captures_in(site):
        for line in textfile.text_of(capture.read_text(encoding="utf-8-sig", errors="replace")).splitlines():
            script = re.match(r"^request: script (/\S+)", line)
            if script and script.group(1) not in paths:
                paths.append(script.group(1))
    return origin, paths


def get(url: str) -> bytes | None:
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as answer:   # noqa: S310 -- http(s) of the site, asked for
            return answer.read(MOST_BYTES)
    except (urllib.error.URLError, OSError, ValueError):
        return None


def map_of(script_url: str, origin: str) -> tuple[str, dict | None]:
    """Where a script's source map is, and the map; nothing where it has none or it is on another host."""
    body = get(script_url)
    if body is None:
        return "", None
    tail = body[-2000:].decode("utf-8", "replace").strip().splitlines()
    named = MAP_RE.search(tail[-1]) if tail else None
    where = named.group(1) if named else script_url + ".map"
    if where.startswith("data:"):
        try:
            return "inline", json.loads(base64.b64decode(where.split(",", 1)[1]))
        except (ValueError, IndexError):
            return "inline", None
    where = urljoin(script_url, where)
    if urlsplit(where).netloc != urlsplit(origin).netloc:
        return where, None
    raw = get(where)
    if raw is None:
        return where, None
    try:
        return where, json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return where, None


def path_of(source: str) -> str:
    """A map's name for a file, as a path under source/: without the bundler's prefixes and the climbs out."""
    name = re.sub(r"^[a-z-]+://", "", source).split("?", 1)[0]
    parts = [part for part in PurePosixPath(name.replace("\\", "/")).parts if part not in ("..", ".", "/", "")]
    return "/".join(re.sub(r"[<>:\"|?*]", "_", part) for part in parts)


def fetch(site: Path, write: bool) -> list[str]:
    origin, paths = scripts_of(site)
    said: list[str] = []
    if not origin:
        return [f"{site / INVENTORY}: it says no Address, so the site's host is not known"]
    if not paths:
        return [f"{site}: no capture lists a script of the site's own host (`request: script /...`): capture the views "
                f"again with the current capture.js"]
    files = size = 0
    for path in paths:
        where, found = map_of(origin + path, origin)
        if found is None:
            said.append(f"{path}: no source map" + (f" at {where}" if where else ""))
            continue
        sources, texts = found.get("sources") or [], found.get("sourcesContent") or []
        kept = [(path_of(name), text) for name, text in zip(sources, texts)
                if isinstance(text, str) and not LEFT_OUT.search(path_of(name)) and path_of(name)]
        said.append(f"{path}: a map with {len(sources)} source(s), {len(kept)} of the product's own")
        for name, text in kept:
            if files >= MOST_FILES or size + len(text) > MOST_BYTES:
                said.append(f"stopped at {files} file(s): more than this script fetches at once")
                return said
            files, size = files + 1, size + len(text)
            if write:
                target = site / SOURCE / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8", newline="\n")
    said.append(f"{'written' if write else 'would write'}: {files} file(s) under {site / SOURCE}" +
                ("" if write else " -- run again with --fetch, once the user has said yes"))
    return said


def run_selftest() -> int:
    bad: list[str] = []
    with tempfile.TemporaryDirectory(prefix="specs-builder-maps-") as tmp:
        served = Path(tmp) / "served"
        (served / "static").mkdir(parents=True)
        bundle = {"version": 3, "sources": ["webpack://shop/./src/App.tsx", "webpack://shop/node_modules/react/index.js",
                                            "webpack://shop/../src/api/invoices.ts", "webpack/bootstrap"],
                  "sourcesContent": ['export const App = () => <h1>Your invoices</h1>;\n', "module.exports = 1;\n",
                                     'fetch("/api/invoices");\n', "(()=>{})();\n"]}
        (served / "static" / "main.js").write_text("var a=1;\n//# sourceMappingURL=main.js.map\n", encoding="utf-8")
        (served / "static" / "main.js.map").write_text(json.dumps(bundle), encoding="utf-8")
        (served / "static" / "plain.js").write_text("var b=2;\n", encoding="utf-8")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(served)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            site = Path(tmp) / "site"
            site.mkdir()
            (site / INVENTORY).write_text(textfile.document(
                f"# Shop: inventory\n\n- **Address:** http://127.0.0.1:{server.server_port}/\n"), encoding="utf-8")
            (site / "V1-home.md").write_text(textfile.document(
                "# V1 · Home\n\n## Requests\n\nrequest: script /static/main.js\n"
                "request: script /static/plain.js\nrequest: script cdn.example.com\n"), encoding="utf-8")
            dry = fetch(site, write=False)
            if (site / SOURCE).exists() or not any("would write: 2 file(s)" in line for line in dry):
                bad.append(f"without --fetch nothing is written, and what would be is said: {dry}")
            said = fetch(site, write=True)
            written = sorted(p.relative_to(site / SOURCE).as_posix() for p in (site / SOURCE).rglob("*") if p.is_file())
            if written != ["shop/src/App.tsx", "shop/src/api/invoices.ts"]:
                bad.append(f"the product's own sources are written, without the bundler's and the libraries': {written}")
            if not any("/static/plain.js: no source map" in line for line in said):
                bad.append(f"a script with no map should be said so: {said}")
        finally:
            server.shutdown()
    print(f"{'FAILED' if bad else 'ok'}  a map's own sources are written under source/, and only with --fetch")
    for message in bad:
        print("ERROR " + message)
    print(f"{'FAILED' if bad else 'PASSED'} -- {len(bad)} problem(s)")
    return 1 if bad else 0


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002 -- the name the base class gives it
        pass


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Fetch the source code a live site publishes in its source maps.")
    parser.add_argument("site", nargs="?", type=Path, help="the folder of the site's captures, with its inventory.md")
    parser.add_argument("--fetch", action="store_true", help="fetch and write the sources; without it, only say what")
    parser.add_argument("--selftest", action="store_true", help="check this script against a server it starts")
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    if args.site is None:
        parser.error("the site's folder of captures is required unless --selftest is given")
    if scout.site_inventory(args.site) is None:
        print(f"{args.site}: no {INVENTORY} -- give the folder of a site's captures", file=sys.stderr)
        return 2
    print("\n".join(fetch(args.site, args.fetch)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
