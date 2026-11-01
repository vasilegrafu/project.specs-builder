#!/usr/bin/env python3
"""Scout material before reading it: what is there, and what each file seems to hold.

    python scripts/scout.py <folder or file>                    # the map: every file, and its signals
    python scripts/scout.py <folder> --list shows                # each place one lens points at, with its line
    python scripts/scout.py <folder> --coverage S1               # rows for the Coverage table of the evidence
    python scripts/scout.py --plan <material> ... --into evidence/scout.md   # what can be built: the scout's report
    python scripts/scout.py --selftest

A specification written from material -- code, documents, screenshots -- is
only as good as what was read. This lists everything that is there, so that
what was read and what was not can be said for every file, and points at
the places where each kind of fact is likely to be found, so that reading
starts where it pays.

The map has one row per file: its path, its kind (code, markup, style,
document, data, image, other), its size, and how many places in it each
lens points at. The lenses are the kinds of fact a specification needs:

    action    what a user can do: routes, handlers, commands, buttons
    shows     what a user reads: messages, labels, titles
    rule      rules and limits: named constants, thresholds, timeouts
    data      what is kept: models, tables, files written and read
    system    other systems: addresses, clients, settings from outside
    access    who may do what: roles, permissions, sign-in
    failure   what happens when it fails: caught errors, refusals
    look      how it looks: colours, sizes, fonts
    loose     what looks unfinished: TODO, FIXME, skipped tests
    test      what the tests pin down: a case, a skip, a mock, a fixture

The signals are pattern matches, not understanding: they say where to look
first, never what is there. A file with no signal still has to be accounted
for. Folders that hold no material of the product are left out (.git,
node_modules, virtual environments, caches, build output) and named in the
map. A data file is never opened: its rows may be private. An image is
listed by name and size.

A live site read in a browser is a folder of captures beside an
`inventory.md` (references/reading-a-live-site.md). Each capture is a
page that holds a view's text, one element to a line with its role --
`button: Download`, `message: Enter an amount` -- and is listed as the kind
`capture`, its text read with lenses of their own: the role of a line, and
the words a site uses for a limit, a refusal or a sign-in.

`--list <lens>` prints each place a lens points at as `path:line: text`.
`--coverage <source ID>` prints one table row per file, to paste under
coverage of the source and fill in. Exits 2 when the path cannot be read.
`--selftest` builds a small tree and checks the map of it. Standard library
only.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textfile  # noqa: E402

LEFT_OUT = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv", "env", ".idea", ".vscode",
            ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build", "bin", "obj", ".next", ".cache",
            "coverage", ".tox"}
KINDS = {
    "code": {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".cs", ".java", ".kt", ".go", ".rb", ".php", ".rs",
             ".swift", ".vue", ".svelte", ".sql", ".sh", ".ps1", ".bat", ".c", ".cpp", ".h"},
    "markup": {".html", ".htm", ".cshtml", ".razor", ".liquid", ".jinja", ".j2", ".xml", ".svg"},
    "style": {".css", ".scss", ".sass", ".less"},
    "document": {".md", ".txt", ".rst", ".adoc", ".pdf", ".docx", ".doc", ".pptx"},
    "data": {".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".db", ".sqlite", ".sqlite3", ".jsonl", ".ndjson", ".pkl",
             ".dat", ".feather"},
    "image": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico"},
    "settings": {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".config", ".properties"},
}
READ = ("code", "markup", "style", "settings")      # the kinds whose lines are looked at; a document only where it is text
TEXT_DOCUMENTS = {".md", ".txt", ".rst", ".adoc"}

LENSES: dict[str, re.Pattern[str]] = {
    "action": re.compile(
        r"@\w*\.?(route|get|post|put|delete|patch|callback|command)\b|\[Http(Get|Post|Put|Delete|Patch)|\[Route\(|"
        r"addEventListener\(|\bon[A-Z]\w*\s*[:=]|\bonclick\b|<form\b|<button\b|<Route\b|"
        r"router\.(get|post|put|delete)\(|app\.(get|post|put|delete)\(|__main__|def main\(|n_clicks|"
        r"dagcomponentfuncs\.\w+\s*="),
    "shows": re.compile(
        r"\b(alert|confirm|prompt)\(|\b(title|label|placeholder|subtitle|tooltip|headerName|textContent|innerHTML|"
        r"innerText|message)\b\s*[:=]\s*[fr]?['\"`]|html\.(Div|Span|H\d|P|Th|Td|A|Button|Label)\(\s*[fr]?['\"]|"
        r"<(h\d|label|title|th|button)\b[^>]*>[^<{]+"),
    "rule": re.compile(
        r"^\s*_?[A-Z][A-Z0-9_]{2,}\s*=\s*[-+]?\d|\b(timeout|max_\w+|min_\w+|limit|threshold|retries|interval|"
        r"ttl|expires?|rate)\w*\s*[:=]\s*[-+]?\d|[<>]=?\s*-?\d+(\.\d+)?\b(?!\s*[;)]?\s*$)", re.IGNORECASE),
    "data": re.compile(
        r"\bCREATE TABLE\b|@dataclass|class \w+\([^)]*(Model|Base|Schema)\)|\b(read|to)_(csv|json|sql|parquet)\(|"
        r"\.(csv|json|sqlite|db)['\"]|\binterface \w+|\benum \w+|localStorage|sessionStorage", re.IGNORECASE),
    "system": re.compile(
        r"https?://[\w.-]+|\b(requests|httpx|urllib|axios|aiohttp)\.|\bfetch\(|os\.environ|getenv\(|process\.env|"
        r"\bconnect\(", re.IGNORECASE),
    "access": re.compile(
        r"\b(role|permission|is_admin|authori[sz]e|login_required|authenticated|password|token|api_?key)\w*\b|"
        r"\[Authorize", re.IGNORECASE),
    "failure": re.compile(
        r"^\s*except\b|\bcatch\s*\(|\braise \w|\bthrow \w|\.onerror\b|on_error|\b(failed|not found|invalid|"
        r"cannot|could not|unable)\b", re.IGNORECASE),
    "look": re.compile(
        r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\(|\bfont-?[sS]ize\b|\bfont-?[fF]amily\b|--[\w-]+\s*:"),
    "loose": re.compile(r"\b(TODO|FIXME|HACK|XXX)\b|\.skip\(|@skip|mark\.skip|@Ignore|@Disabled"),
    "test": re.compile(r"^\s*(def test_|async def test_|class Test[A-Z]|\[(Fact|Theory|Test|TestCase|TestMethod)\b|"
                       r"(it|test|describe)(\.(skip|only|todo|each))?\()|@pytest\.fixture|\b(patch|jest\.mock|vi\.mock|"
                       r"new Mock<|Substitute\.For<|beforeEach|\[SetUp\])\b"),
}


# A live site's captures (references/reading-a-live-site.md): a folder with an inventory, each other page in it the
# capture of one view, one element to a line with its role. Each is a page that holds its text, as every file of
# text the evidence holds is; one written before that as the text alone, `.md`, is read the same way until it is
# made a page.
SITE_INVENTORY = "inventory.md"
OLD_SITE_INVENTORY = "inventory.html"
SITE_LENSES: dict[str, re.Pattern[str]] = {
    # a capture's own line, `button: Download`, or a line of its accessibility tree, `- button "Download"`
    "action": re.compile(r"^(\s*- )?(button|link|field|menu|menuitem|tab|option|checkbox|radio|select|form|search|"
                         r"searchbox|textbox|combobox|switch|slider|spinbutton|hidden)\b[:\s\"]", re.IGNORECASE),
    "shows": re.compile(r"^(\s*- )?(heading|text|label|message|tooltip|title|placeholder|dialog|image|img|notice|"
                        r"paragraph|alert|status|region|frame|cell|columnheader)\b[:\s\"]", re.IGNORECASE),
    "rule": re.compile(r"\b(at most|at least|maximum|minimum|required|up to|no more than|must be|between \d)|"
                       r"\d+\s*(characters|items|days|hours|minutes|MB|KB|GB)\b", re.IGNORECASE),
    "data": re.compile(r"^(stored|kept|saved):|\b(saved|draft|history|recent)\b", re.IGNORECASE),
    "system": re.compile(r"^request:|https?://[\w.-]+", re.IGNORECASE),
    "access": re.compile(r"\b(sign in|log in|signed in|logged in|permission|not allowed|access denied|forbidden|"
                         r"admin|upgrade|subscribe)\b", re.IGNORECASE),
    "failure": re.compile(r"\b(error|failed|not found|invalid|cannot|could not|unable|try again|went wrong)\b",
                          re.IGNORECASE),
    "look": re.compile(r"^style:|#[0-9a-fA-F]{6}\b|rgba?\(", re.IGNORECASE),
    "loose": re.compile(r"\b(coming soon|beta|lorem ipsum|todo|placeholder text)\b", re.IGNORECASE),
}


def site_inventory(folder: Path) -> Path | None:
    """The inventory of a site's captures, where the folder holds one: a page, or the text alone as it was."""
    for name in (SITE_INVENTORY, OLD_SITE_INVENTORY):
        if (folder / name).is_file():
            return folder / name
    return None


def is_capture(path: Path) -> bool:
    """Whether a file is the capture of one view: a page or a text beside a site's inventory, not the inventory."""
    return (path.suffix.lower() in (".html", ".md") and path.name not in (SITE_INVENTORY, OLD_SITE_INVENTORY)
            and site_inventory(path.parent) is not None)


def captures_in(site: Path) -> list[Path]:
    """The captures of a site's folder, in order of their names."""
    return sorted((p for p in site.iterdir() if p.is_file() and is_capture(p)), key=lambda p: p.name.lower())


@dataclass
class Entry:
    path: str                    # relative to the root, with forward slashes
    kind: str
    size: int                    # lines where the file is read, bytes otherwise
    counted: str                 # "lines" or "bytes"
    places: dict[str, list[tuple[int, str]]] = field(default_factory=dict)    # per lens: (line, its text)
    by: str = ""                 # how its lines were read: tree-sitter or ast for code a parser reads; else patterns


def kind_of(path: Path) -> str:
    suffix = path.suffix.lower()
    for kind, suffixes in KINDS.items():
        if suffix in suffixes:
            return kind
    return "other"


def walk(root: Path) -> tuple[list[Path], list[str]]:
    """Every file under the root that could be material, and the folders left out."""
    if root.is_file():
        return [root], []
    found: list[Path] = []
    skipped: list[str] = []
    stack = [root]
    while stack:
        folder = stack.pop()
        for child in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
            if child.is_dir():
                if child.name in LEFT_OUT:
                    skipped.append(child.relative_to(root).as_posix() + "/")
                else:
                    stack.append(child)
            elif child.is_file():
                found.append(child)
    return sorted(found, key=lambda p: p.relative_to(root).as_posix().lower()), sorted(skipped)


def paths(root: Path) -> list[str]:
    """The path of every file of the material, as the Coverage table names it."""
    base = root.parent if root.is_file() else root
    return [path.relative_to(base).as_posix() for path in walk(root)[0]]


def scan(root: Path, syntax: bool = True) -> tuple[list[Entry], list[str]]:
    import scan_code             # here, not at the top: scan_code imports this module
    engine = scan_code.Engine(syntax)
    files, skipped = walk(root)
    base = root.parent if root.is_file() else root
    entries: list[Entry] = []
    for path in files:
        kind = "capture" if is_capture(path) else kind_of(path)
        name = path.relative_to(base).as_posix()
        readable = kind in READ or kind == "capture" or (kind == "document" and path.suffix.lower() in TEXT_DOCUMENTS)
        if not readable:                 # a data file is never opened; an image has no lines
            entries.append(Entry(name, kind, path.stat().st_size, "bytes"))
            continue
        try:
            # a capture is read as its text, each line where it stands in the file
            lines = (textfile.held(path) if kind == "capture"
                     else path.read_text(encoding="utf-8-sig", errors="replace")).splitlines()
        except OSError:
            entries.append(Entry(name, kind, path.stat().st_size, "bytes"))
            continue
        entry = Entry(name, kind, len(lines), "lines")
        if kind != "capture" and path.suffix.lower() in scan_code.LANGUAGES:   # what a parser reads is pointed at by
                                                                               # its syntax: what is there, not what
                                                                               # looks so; a capture is a view's text
            facts, by = scan_code.facts_in(path, name, engine)
            if by in ("tree-sitter", "ast"):
                entry.by = by
                for fact in facts:
                    entry.places.setdefault(fact.lens, []).append((fact.line, f"{fact.kind}: {fact.text}"))
                entries.append(entry)
                continue
        if kind != "document":
            lenses = SITE_LENSES if kind == "capture" else LENSES
            for number, line in enumerate(lines, start=1):
                if len(line) > 2000:     # a minified or generated line: nothing a person wrote to be read
                    continue
                if kind == "capture" and line.startswith(("#", "- **")):    # the capture's own heads, not the view
                    continue
                for lens, pattern in lenses.items():
                    if pattern.search(line):
                        entry.places.setdefault(lens, []).append((number, " ".join(line.split())[:140]))
        entries.append(entry)
    return entries, skipped


def render_map(root: Path, entries: list[Entry], skipped: list[str]) -> str:
    out = [f"{root}: {len(entries)} file(s)"]
    by_kind: dict[str, int] = {}
    for entry in entries:
        by_kind[entry.kind] = by_kind.get(entry.kind, 0) + 1
    out.append("  " + ", ".join(f"{kind} {count}" for kind, count in sorted(by_kind.items())))
    import scan_code
    code = [e for e in entries if Path(e.path).suffix.lower() in scan_code.LANGUAGES]
    if code:
        parsed = sum(1 for e in code if e.by)
        if parsed == len(code):
            out.append(f"  code read by its syntax: all {len(code)} file(s)")
        else:
            out.append(f"  code read by its syntax: {parsed} of {len(code)} file(s); the rest by patterns, which say "
                       f"where to look and not what is there -- `scan_code.py --languages` says why")
    if skipped:
        out.append("  left out, as holding nothing of the product: " + ", ".join(skipped))
    width = max((len(e.path) for e in entries), default=4)
    for entry in sorted(entries, key=lambda e: (-sum(len(p) for p in e.places.values()), e.path.lower())):
        signals = ", ".join(f"{lens} {len(entry.places[lens])}" for lens in LENSES if lens in entry.places)
        if entry.kind == "data":
            signals = "not opened: a data file"
        out.append(f"  {entry.path:<{width}}  {entry.kind:<8} {entry.size:>7} {entry.counted}  {signals}")
    return "\n".join(out)


def render_list(entries: list[Entry], lens: str) -> str:
    out = []
    for entry in entries:
        out.extend(f"{entry.path}:{number}: {text}" for number, text in entry.places.get(lens, []))
    return "\n".join(out) or f"nothing found for '{lens}'"


def render_coverage(entries: list[Entry], source: str) -> str:
    out = ["| Source | Part | Read | Note |", "|---|---|---|---|"]
    out.extend(f"| {source} | {entry.path} | <<full, part or not read>> | <<what of it, or why not>> |"
               for entry in entries)
    return "\n".join(out)


def run_selftest() -> int:
    bad: list[str] = []
    with tempfile.TemporaryDirectory(prefix="specs-builder-inventory-") as tmp:
        root = Path(tmp) / "app"
        (root / "pages").mkdir(parents=True)
        (root / "node_modules" / "lib").mkdir(parents=True)
        (root / "pages" / "orders.py").write_text(
            'MAX_ORDER = 5000\n\n@app.route("/orders")\ndef orders():\n    # TODO: paging\n'
            '    if amount > MAX_ORDER:\n        raise ValueError("The amount is above the limit")\n',
            encoding="utf-8")
        (root / "style.css").write_text(".gain { color: #36d399; font-size: 14px; }\n", encoding="utf-8")
        (root / "holdings.csv").write_text("ticker,shares\nSECRET,100\n", encoding="utf-8")
        (root / "notes.md").write_text("# Notes\n\nCustomers ask for a file.\n", encoding="utf-8")
        (root / "node_modules" / "lib" / "index.js").write_text("alert('x')\n", encoding="utf-8")
        entries, skipped = scan(root)
        by_path = {entry.path: entry for entry in entries}

        if set(by_path) != {"pages/orders.py", "style.css", "holdings.csv", "notes.md"} or skipped != ["node_modules/"]:
            bad.append(f"the map should hold the four files and leave node_modules out: {sorted(by_path)}, {skipped}")
        print(f"{'FAILED' if bad else 'ok'}  every file is listed, and folders that hold no material are left out")

        before = len(bad)
        wanted = {"action": 3, "rule": 1, "loose": 5, "failure": 7}
        for syntax in (True, False):     # by its syntax, as tree-sitter or ast reads it; and with neither installed
            read = {entry.path: entry for entry in scan(root, syntax)[0]}
            orders = read.get("pages/orders.py")
            for lens, line in wanted.items():
                if not orders or line not in [n for n, _ in orders.places.get(lens, [])]:
                    bad.append(f"'{lens}' should point at line {line} of pages/orders.py, read "
                               f"{'by tree-sitter where it is installed' if syntax else 'without tree-sitter'}")
            if orders and orders.by != ("ast" if not syntax else orders.by or "a parser"):
                bad.append(f"pages/orders.py should be read by its syntax, and was read by '{orders.by}'")
        if "look" not in by_path["style.css"].places:
            bad.append("'look' should point at the colour in style.css")
        print(f"{'FAILED' if len(bad) > before else 'ok'}  each lens points at the lines that hold its kind of fact")

        before = len(bad)
        data = by_path["holdings.csv"]
        text = render_map(root, entries, skipped) + render_list(entries, "shows") + render_coverage(entries, "S1")
        if data.places or data.counted != "bytes" or "SECRET" in text:
            bad.append("a data file must not be opened, and nothing of it may be printed")
        if "| S1 | holdings.csv |" not in text or paths(root) != sorted(by_path, key=str.lower):
            bad.append("the coverage rows should name every file")
        print(f"{'FAILED' if len(bad) > before else 'ok'}  a data file is never opened, and coverage names every file")

        before = len(bad)
        site = Path(tmp) / "site"
        site.mkdir()
        (site / SITE_INVENTORY).write_text(textfile.document(
            "# A shop: inventory\n\n- **Address:** https://shop.example.com\n"), encoding="utf-8")
        page = textfile.document(
            "# V1 · The checkout\n\n- **Address:** https://shop.example.com/checkout\n\n## On the page\n\n"
            "heading: Checkout\nfield: Card number (required)\nbutton: Pay now\n"
            "message: Something went wrong. Try again.\nrequest: GET payments.example.com\n"
            "style: Pay now: background #0969da\n\n## Accessibility tree\n\n```yaml\n- main:\n"
            "  - button \"Pay now\"\n  - heading \"Checkout\" [level=1]\n```\n")
        (site / "V1-the-checkout.md").write_text(page, encoding="utf-8")
        captures, _ = scan(site)
        found = {entry.path: entry for entry in captures}
        checkout = found.get("V1-the-checkout.md")
        if not checkout or checkout.kind != "capture" or found.get(SITE_INVENTORY, Entry("", "", 0, "")).kind != "document":
            bad.append("a view's page beside an inventory should be a capture, and the inventory a document")
        else:
            # each lens points at the line of the file, the page's own lines counted
            first = page.split("\n").index("# V1 · The checkout") + 1
            wanted = {"shows": 7, "action": 8, "rule": 8, "failure": 10, "system": 11, "look": 12}
            tree = {"action": 18, "shows": 19}           # the accessibility tree's lines are read by their role too
            for lens, line in tree.items():
                if line + first - 1 not in [n for n, _ in checkout.places.get(lens, [])]:
                    bad.append(f"'{lens}' should point at line {line + first - 1} of the capture, in its accessibility "
                               f"tree: {checkout.places.get(lens)}")
            for lens, line in wanted.items():
                if line + first - 1 not in [n for n, _ in checkout.places.get(lens, [])]:
                    bad.append(f"'{lens}' should point at line {line + first - 1} of the capture")
            if first + 2 in [n for places in checkout.places.values() for n, _ in places]:
                bad.append("the capture's own Address line is not the view's text, and no lens should point at it")
            if any(n < first for places in checkout.places.values() for n, _ in places):
                bad.append("the page around the capture's text is not the view's, and no lens should point at it")
        print(f"{'FAILED' if len(bad) > before else 'ok'}  a site's captures are read by the role and the words of "
              f"each line")

    for message in bad:
        print("ERROR " + message)
    print(f"{'FAILED' if bad else 'PASSED'} -- {len(bad)} problem(s)")
    return 1 if bad else 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Scout material before reading it.")
    parser.add_argument("path", nargs="?", type=Path, help="the folder or file that holds the material")
    parser.add_argument("--list", metavar="LENS", choices=sorted(LENSES), help="print each place this lens points at")
    parser.add_argument("--coverage", metavar="SOURCE", help="print Coverage rows for the evidence, for this source ID")
    parser.add_argument("--plan", nargs="+", metavar="MATERIAL",
                        help="say what can be built from these -- folders, files, a site's captures, a site's address "
                             "-- and what reading them would take: the scout's report")
    parser.add_argument("--into", type=Path, help="with --plan, write the report here: evidence/scout.md")
    parser.add_argument("--selftest", action="store_true", help="check this script against a small tree it builds")
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    if args.plan:
        import material_plan    # noqa: PLC0415 -- it reads code by scan_code.py, which reads files by this script
        return material_plan.main([*args.plan, *(["--into", str(args.into)] if args.into else [])])
    if args.path is None:
        parser.error("the folder or file of the material is required unless --selftest is given")
    if not args.path.exists():
        print(f"{args.path}: not found", file=sys.stderr)
        return 2
    try:
        entries, skipped = scan(args.path)
    except OSError as problem:
        print(f"{args.path}: cannot be read -- {problem}", file=sys.stderr)
        return 2
    if args.list:
        print(render_list(entries, args.list))
    elif args.coverage:
        print(render_coverage(entries, args.coverage))
    else:
        print(render_map(args.path, entries, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
