"""The specification's application: a local server for its views.

    python app/serve.py --open          start it and open the browser on it
    python app/serve.py --port 8765     on a port of your choosing (default: any that is free)

It listens on 127.0.0.1 only, so nothing outside this computer reaches it. It loads the data and builds the
database when it starts, and again whenever a file under data/ -- or the grammar -- changes; while the data has
problems, every view says which, at their file and line, and the last good database is what is read. It answers
/api/... as JSON and serves the engine from app/web/. Close its window, or press Ctrl+C, to stop it.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 14):
    raise SystemExit(f"specs-builder-2 needs Python 3.14 or later; this is {sys.version.split()[0]}")

import argparse
import html
import json
import mimetypes
import os
import re
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

sys.dont_write_bytecode = True
APP = Path(__file__).resolve().parent
sys.path.insert(0, str(APP))
import api  # noqa: E402
import build  # noqa: E402
import evidence  # noqa: E402
import export as exporting  # noqa: E402
import finish  # noqa: E402
import inbox  # noqa: E402
import load as loading  # noqa: E402
import logic  # noqa: E402
import matrix  # noqa: E402
import prototypes  # noqa: E402
import review  # noqa: E402

WEB = APP / "web"
# what every prototype is given before the product's own head: where its links lead, and the runtime that shows
# its states and variants -- first, so that the product's scripts, deferred after it, find it there
RUNTIME = ('<base href="/prototype/">\n<link rel="stylesheet" href="/runtime/live.css">\n'
           '<script src="/runtime/live.js" defer></script>\n')
DRAWINGS = '<link rel="stylesheet" href="/runtime/drawings.css">\n'
GLANCE = 2.0                          # s: the Matrix's small questions look at every file no oftener than this


class Spec:
    """The specification as the server holds it: loaded again whenever what it was loaded from changes."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.lock = threading.Lock()
        self.stamp: tuple | None = None
        self.version = ""                                   # says which state of the data this is, so a page need not ask again
        self.problems: list = []
        self.stale: list = []
        self.done: loading.Load | None = None
        self.menu_held: tuple | None = None
        self.parts_held: tuple = (None, {})
        self.glanced = 0.0
        self.glancing = False
        self.refresh()

    def files(self) -> tuple:
        """What the data was read from, by folder and not by file: a folder listed says its files' sizes and times at once on
        Windows, where asking each of 7,000 files took 220 ms, and held every other question up behind a busy thread."""
        found = []
        folders = [str(self.root / loading.DATA)]
        while folders:
            try:
                with os.scandir(folders.pop()) as entries:
                    for entry in entries:
                        if entry.is_dir():
                            folders.append(entry.path)
                        elif entry.is_file():
                            said = entry.stat()
                            found.append((entry.path, said.st_size, said.st_mtime_ns))
            except FileNotFoundError:
                continue                                    # no such folder, or one moved as it was read
        for path in (loading.GRAMMAR, self.root / review.REVIEWED, self.root / inbox.INBOX):
            if path.is_file():
                said = path.stat()
                found.append((str(path), said.st_size, said.st_mtime_ns))
        return tuple(sorted(found))

    def refresh(self) -> None:
        with self.lock:
            if (self.root / logic.LOCK).exists():          # a change is being written: read it once it is whole
                return
            stamp = self.files()
            if stamp == self.stamp:
                return
            done = loading.load(self.root)
            self.done = done
            self.version = str(time.time_ns())
            self.problems = done.problems
            if not done.problems:
                loading.build(done)
                logic.notice(self.root, done)              # what was edited by hand, logged as such
                try:
                    self.stale = review.stale(loading.grammar(), done, review.held(self.root))
                except ValueError as wrong:                # said where every view says what is wrong
                    self.problems = [(review.REVIEWED, 0, str(wrong))]
                    self.stale = []
            self.stamp = self.files()

    def glance(self) -> None:
        """As `refresh`, to one side and no oftener than GLANCE: looking at every file is the slowest part of a small
        question, and the Matrix asks many of them as it is scrolled. A change made here sets `stamp` to None, and is read
        before the answer."""
        if self.stamp is None:
            self.refresh()
        elif not self.glancing and time.monotonic() - self.glanced >= GLANCE:
            self.glancing = True
            threading.Thread(target=self.look, daemon=True).start()

    def look(self) -> None:
        try:
            self.refresh()
        finally:
            self.glanced = time.monotonic()
            self.glancing = False

    def held(self, name: str, make) -> object:
        """What looks at everything, worked out once for each state of the data."""
        if self.parts_held[0] != self.stamp:
            self.parts_held = (self.stamp, {})
        parts = self.parts_held[1]
        if name not in parts:
            parts[name] = make()
        return parts[name]

    def troubles(self) -> dict:
        return self.held("troubles", lambda: matrix.problems(self.root, self.stale))

    def grid(self) -> dict | None:
        return self.held("grid", lambda: matrix.grid(self.root, self.stale, self.troubles()))

    def ways(self) -> dict:
        return self.held("ways", lambda: matrix.joins(self.root))

    def menu(self) -> dict:
        """The menu's panels, worked out once for each state of the data: every view asks for them."""
        stamp = self.stamp
        if self.menu_held and self.menu_held[0] == stamp:
            return self.menu_held[1]
        found = api.menu(self.root, self.done, self.stale)
        self.menu_held = (stamp, found)
        return found


def answer(spec: Spec, path: str, query: dict) -> tuple[int, object]:
    """The status and the JSON of one question to /api/."""
    parts = [unquote(p) for p in path.split("/") if p][1:]          # after "api"
    if parts[:1] in (["matrix"], ["map"]):
        spec.glance()
    else:
        spec.refresh()
    root = spec.root
    one = lambda key: (query.get(key) or [""])[0]                    # noqa: E731
    number = lambda key, usual: int(one(key)) if one(key).isdigit() else usual    # noqa: E731
    match parts:
        case ["summary"]:
            return 200, {**api.summary(root, spec.problems, spec.stale), "version": spec.version}
        case ["grammar"]:
            return 200, api.grammar_view()
        case ["names"]:
            return 200, api.names(root)
        case ["design"]:
            return 200, api.design(root)
        case ["prototypes"]:
            return 200, api.prototypes(root)
        case ["menu"]:
            return 200, spec.menu()
        case ["search"]:
            return 200, api.search(root, one("q"))
        case ["history"]:
            return 200, logic.history(root, one("id") or None)
        case ["stale"]:
            return 200, spec.stale
        case ["open"]:
            return 200, api.opened(root)
        case ["built"]:
            return 200, build.built(root)
        case ["evidence"]:
            return 200, evidence.files(root)
        case ["nodes"]:
            return 200, api.nodes(root, one("kind"))
        case ["node", ident]:
            found = api.node(root, ident, spec.stale)
            return (200, found) if found else (404, {"error": f"{ident}: no node has that ID"})
        case ["story", ident]:
            if spec.done is None:
                return 503, {"error": "the specification is being written; ask again"}
            try:
                return 200, finish.story(loading.grammar(), spec.done, ident)
            except KeyError as error:
                return 404, {"error": str(error).strip("'")}
        case ["card", ident]:
            found = api.card(root, ident, spec.stale)
            if found:
                found["linked"] = matrix.linked(root, spec.ways(), ident)
            return (200, found) if found else (404, {"error": f"{ident}: no node has that ID"})
        case ["matrix"]:
            found = spec.grid()
            return (200, found) if found else (404, {"error": "there is no data yet"})
        case ["matrix", "find"]:
            return 200, matrix.find(root, one("q"))
        case ["matrix", "cell"]:
            found = matrix.cell(root, spec.stale, one("from"), one("to"), number("offset", 0), number("limit", matrix.LINKS_FIRST), one("q"))
            return (200, found) if found else (404, {"error": "there is no data yet"})
        case ["matrix", "tree"]:
            within = spec.troubles().get(one("problem"), {}).get(one("kind"), []) if one("problem") else None
            found = matrix.tree(root, one("kind"), one("parent"), number("offset", 0), one("at"), within)
            return (200, found) if found else (404, {"error": "there is no data yet"})
        case ["matrix", "links", ident]:
            found = matrix.links(root, spec.stale, ident, one("way"), one("rel"), number("offset", 0), number("limit", matrix.LINKS_FIRST),
                                 one("q"), one("by") or "sort", one("of"))
            return (200, found) if found else (404, {"error": f"{ident}: no node has that ID"})
        case ["matrix", "path"]:
            found = matrix.path(root, spec.ways(), one("from"), one("to"))
            return (200, found) if found else (404, {"error": f"{one('from')} or {one('to')}: no node has that ID"})
        case ["matrix", "link"]:
            found = matrix.link(root, spec.stale, one("src"), one("rel"), one("dst"))
            return (200, found) if found else (404, {"error": f"{one('src')} {one('rel')} {one('dst')}: no such link"})
        case ["map"]:
            opened = {}                                     # kind:how many@from where
            for part in one("open").split(","):
                kind, _, rest = part.partition(":")
                most, _, start = rest.partition("@")
                if kind and most.isdigit():
                    opened[kind] = (int(most), int(start) if start.isdigit() else 0)
            found = matrix.picture(root, spec.ways(), (spec.grid() or {}).get("cells", []), opened)
            return (200, found) if found else (404, {"error": "there is no data yet"})
        case ["map", "layers"]:
            found = matrix.traced(root, spec.ways(), one("id"), number("steps", 0))
            return (200, found) if found else (404, {"error": f"{one('id')}: no node has that ID"})
        case ["map", "around"]:
            found = matrix.around(root, spec.ways(), one("id"))
            return (200, found) if found else (404, {"error": f"{one('id')}: no node has that ID"})
        case ["map", "stands"]:
            found = matrix.stands(root, spec.ways(), one("id"))
            return (200, found) if found else (404, {"error": f"{one('id')}: no node has that ID"})
        case ["graph"] if not one("around"):
            found = api.whole_graph(root)
            return (200, found) if found else (404, {"error": "there is no data yet"})
        case ["graph"]:
            depth = int(one("depth")) if one("depth").isdigit() else 1
            found = api.graph(root, one("around"), depth)
            return (200, found) if found else (404, {"error": f"{one('around')}: no node has that ID"})
    return 404, {"error": f"/{path.strip('/')}: no such question"}


class Handler(BaseHTTPRequestHandler):
    spec: Spec

    def do_GET(self) -> None:  # noqa: N802 -- the name http.server calls
        url = urlparse(self.path)
        if url.path.startswith("/api/"):
            try:
                status, said = answer(self.spec, url.path, parse_qs(url.query))
            except Exception as wrong:                  # said to the page, never a dropped connection
                status, said = 500, {"error": f"the server failed on {url.path}: {type(wrong).__name__}: {wrong}"}
            self.send(status, json.dumps(said, ensure_ascii=False).encode("utf-8"), "application/json")
            return
        if url.path.startswith("/prototype/"):
            self.prototype(unquote(url.path[len("/prototype/"):]))
            return
        if url.path.startswith("/evidence/"):
            self.evidence(unquote(url.path[len("/evidence/"):]))
            return
        name = "index.html" if url.path in ("", "/") else unquote(url.path).lstrip("/")
        path = (WEB / name).resolve()
        if not path.is_relative_to(WEB) or not path.is_file():              # nothing outside app/web/ is served
            self.send(404, b"not found", "text/plain")
            return
        kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send(200, path.read_bytes(), kind + ("; charset=utf-8" if kind.startswith("text/") or
                                                  kind.endswith("javascript") else ""))

    def do_POST(self) -> None:  # noqa: N802 -- the name http.server calls
        """What the application writes, and neither touches the data: a request for a change, and the export. A change to the
        specification is made with `spec.py do`."""
        path = urlparse(self.path).path
        if path not in ("/api/inbox", "/api/export"):
            self.send(404, b'{"error": "no such question"}', "application/json")
            return
        if self.headers.get("Origin") not in (None, f"http://127.0.0.1:{self.server.server_address[1]}"):
            self.send(403, b'{"error": "a request comes from this application only"}', "application/json")
            return
        if path == "/api/inbox":
            self.request_change()
        else:
            self.exported()

    def exported(self) -> None:
        """The whole specification as one file, written as `spec.py export` writes it and handed to the browser."""
        self.spec.refresh()
        try:
            path = exporting.export(self.spec.root, built=True)
        except ValueError as wrong:
            self.send(409, json.dumps({"refused": str(wrong)}, ensure_ascii=False).encode("utf-8"), "application/json")
            return
        self.send(200, path.read_bytes(), "text/html; charset=utf-8", {"Content-Disposition": f'attachment; filename="{path.name}"'})

    def request_change(self) -> None:
        """A change asked for in the application, {"says": ..., "about": ["R4"], "by": ...}: it waits in inbox.md."""
        try:
            asked = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            entry = inbox.ask(self.spec.root, str(asked.get("says") or ""), [str(i) for i in asked.get("about") or []],
                              str(asked.get("by") or ""), self.spec.done)
        except (ValueError, TypeError, AttributeError) as wrong:
            self.send(400, json.dumps({"error": str(wrong)}).encode("utf-8"), "application/json")
            return
        self.send(200, json.dumps(entry, ensure_ascii=False).encode("utf-8"), "application/json")

    def prototype(self, rest: str) -> None:
        """A screen drawn in the product's shell, a component's drawings in it, or one of the product's assets."""
        self.spec.refresh()
        root = self.spec.root / prototypes.PROTOTYPES
        screen = re.fullmatch(r"(SC\d+)\.html", rest)
        drawing = re.fullmatch(r"components/(C\d+)\.html", rest)
        if screen or drawing:
            ident = (screen or drawing).group(1)
            body = root / ("screens" if screen else "components") / f"{ident}.html"
            shell = self.spec.root / prototypes.SHELL
            if not body.is_file() or not shell.is_file():
                self.send(404, f"{ident}: no prototype".encode("utf-8"), "text/plain; charset=utf-8")
                return
            known = api.names(self.spec.root).get(ident, {})
            page = (shell.read_text(encoding="utf-8")
                    .replace("{{title}}", html.escape(f"{ident} {known.get('name') or ''}".strip()))
                    .replace("{{body}}", body.read_text(encoding="utf-8")))
            head = page.find("<head>")
            given = RUNTIME + (DRAWINGS if drawing else "")
            page = page[:head + 6] + "\n" + given + page[head + 6:] if head >= 0 else given + page
            self.send(200, page.encode("utf-8"), "text/html; charset=utf-8")
            return
        path = (root / rest).resolve()
        if not rest.startswith("assets/") or not path.is_relative_to(root.resolve()) or not path.is_file():
            self.send(404, b"not found", "text/plain")
            return
        kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send(200, path.read_bytes(), kind + ("; charset=utf-8" if kind.startswith("text/") or
                                                  kind.endswith("javascript") or kind.endswith("svg+xml") else ""))

    def evidence(self, rest: str) -> None:
        """A file of the evidence, as it is: nothing outside evidence/ is served, and nothing is run."""
        place = (self.spec.root / evidence.EVIDENCE).resolve()
        path = (place / rest).resolve()
        if not path.is_relative_to(place) or not path.is_file():
            self.send(404, b"not found", "text/plain")
            return
        kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if kind.startswith("text/") or path.suffix in (".md", ".json", ".html", ".js", ".svg"):
            kind = "text/plain"                         # shown as text, never drawn or run
        self.send(200, path.read_bytes(), kind + ("; charset=utf-8" if kind == "text/plain" else ""))

    def send(self, status: int, body: bytes, kind: str, also: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        for key, value in (also or {}).items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A002 -- quiet: the window says only what matters
        pass


class Server(ThreadingHTTPServer):
    """A port held by this server alone: on Windows, the address reused would let it share a port another program
    listens on, and answer that program's visitors -- or they it."""
    allow_reuse_address = sys.platform != "win32"
    request_queue_size = 64                             # the prototype's gallery asks for every screen at once

    def handle_error(self, request, client_address) -> None:
        if not isinstance(sys.exc_info()[1], (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)):
            super().handle_error(request, client_address)   # a page left before its answer came is nothing wrong

    def server_bind(self) -> None:
        if sys.platform == "win32":
            import socket                               # noqa: PLC0415
            self.socket.setsockopt(socket.SOL_SOCKET, getattr(socket, "SO_EXCLUSIVEADDRUSE", -5), 1)
        super().server_bind()


def server(root: Path, port: int = 0) -> ThreadingHTTPServer:
    handler = type("SpecHandler", (Handler,), {"spec": Spec(root)})
    return Server(("127.0.0.1", port), handler)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--open", action="store_true", help="open the browser on it")
    parser.add_argument("--port", type=int, default=0, help="the port (default: any that is free)")
    parser.add_argument("--spec", type=Path, default=APP.parent, help="the specification's folder")
    args = parser.parse_args()
    try:
        httpd = server(args.spec.resolve(), args.port)
    except OSError:
        print(f"port {args.port} is taken by another program: give another with --port, or none, and one free is "
              f"found", file=sys.stderr)
        return 2
    address = f"http://127.0.0.1:{httpd.server_address[1]}/"
    problems = httpd.RequestHandlerClass.spec.problems
    print(f"{api.title(args.spec.resolve())}: {address}")
    if problems:
        print(f"  {len(problems)} problem(s) in the data -- the application lists them")
    print("  close this window, or press Ctrl+C, to stop")
    if args.open:
        webbrowser.open(address)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
