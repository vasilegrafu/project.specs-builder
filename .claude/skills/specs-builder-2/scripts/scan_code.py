#!/usr/bin/env python3
"""List the facts in code by its syntax: each route, message, limit, state and check, with its line.

    python scripts/scan_code.py <folder or file>                    # every fact, lens by lens
    python scripts/scan_code.py <folder> --lens action              # the facts of one lens
    python scripts/scan_code.py <folder> --tests --lens test        # the tests too: each case, skip, mock, fixture
    python scripts/scan_code.py <folder> --json                     # the same, for a tool
    python scripts/scan_code.py --languages                         # each language, and whether it is read by syntax
    python scripts/scan_code.py --selftest

scout.py says where each kind of fact is likely to be, by patterns over
lines. This reads code as a parser does, so that what it lists is what the
code holds: a route with its method and its path, an enum with each of its
members, a limit on the field it limits, the message a user is shown -- and
never a word in a comment or a string that only looks like one. Each fact
is one line:

    api/InvoicesController.cs:9  route  HttpGet("{id}/pdf")  · InvoicesController.Download

the file and the line, the kind, the code's own words -- the first line of
what was found, so that a finding can quote it as it stands -- and the
class or function it is in. The lenses are scout.py's: action, shows,
rule, data, system, access, failure, look, loose.

It reads with tree-sitter -- the package `tree-sitter` and one package
per language, each holding its grammar, so nothing is fetched when it
runs (GRAMMARS below): C#, Python, JavaScript and JSX, TypeScript and
TSX, HTML and the templates written as HTML, CSS, Bash, PowerShell and
SQL. The grammars are the tree-sitter project's own, but for PowerShell
and SQL, which it has none of: those are their authors', the ones every
tool uses. What each language is asked is in queries/<language>.scm, one
pattern per kind of fact; what a framework is known by -- ASP.NET Core,
FastAPI, Flask, Django, Dash, pydantic, React, Express, zod, htmx -- is
written there, and a new one is a pattern more. A language whose
package is not installed is read as if there were no tree-sitter:
Python with the standard library's ast, the others by scout.py's
patterns; the output says which it was, and --languages says it for
each.

Tests are left out, and so is generated or minified code: what they hold
is not what the product does. With --tests the tests are read as well,
for the test archaeologist: the lens `test` lists each test case, each
one skipped, each mock -- a system outside -- and each fixture, beside
whatever else a test holds. A data file is never opened. Standard
library only, but for tree-sitter where it is there.
"""
from __future__ import annotations

import argparse
import ast
import importlib
import io
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scout  # noqa: E402

QUERIES = Path(__file__).resolve().parent / "queries"
LANGUAGES = {".py": "python", ".cs": "csharp", ".ts": "typescript", ".mts": "typescript", ".cts": "typescript",
             ".tsx": "tsx", ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
             ".html": "html", ".htm": "html", ".cshtml": "html", ".razor": "html", ".jinja": "html", ".j2": "html",
             ".css": "css", ".sh": "bash", ".bash": "bash", ".ps1": "powershell", ".psm1": "powershell",
             ".sql": "sql"}
# Each language's grammar: the package that holds it, the function that gives it, and where it is from.
GRAMMARS = {
    "python": ("tree-sitter-python", "tree_sitter_python", "language"),
    "csharp": ("tree-sitter-c-sharp", "tree_sitter_c_sharp", "language"),
    "javascript": ("tree-sitter-javascript", "tree_sitter_javascript", "language"),
    "typescript": ("tree-sitter-typescript", "tree_sitter_typescript", "language_typescript"),
    "tsx": ("tree-sitter-typescript", "tree_sitter_typescript", "language_tsx"),
    "html": ("tree-sitter-html", "tree_sitter_html", "language"),
    "css": ("tree-sitter-css", "tree_sitter_css", "language"),
    "bash": ("tree-sitter-bash", "tree_sitter_bash", "language"),
    "powershell": ("tree-sitter-powershell", "tree_sitter_powershell", "language"),     # airbus-cert's
    "sql": ("tree-sitter-sql", "tree_sitter_sql", "language"),                          # DerekStride's
}
QUERY_FILES = {"python": ("python",), "csharp": ("csharp",), "javascript": ("script", "jsx"),
               "typescript": ("script", "types"), "tsx": ("script", "jsx", "types"), "html": ("html",),
               "css": ("css",), "bash": ("bash",), "powershell": ("powershell",), "sql": ("sql",)}
INSTALL = "pip install tree-sitter " + " ".join(sorted({package for package, _, _ in GRAMMARS.values()}))
LENS_SAYS = {"action": "what a user can do", "shows": "what a user reads", "rule": "rules and limits",
             "data": "what is kept, and the states a thing can be in", "system": "other systems",
             "access": "who may do what", "failure": "what happens when it fails", "look": "how it looks",
             "loose": "what looks unfinished", "test": "what the tests pin down"}
# What a specification has to account for, one by one: each route, and each set of states (spec.py).
ACCOUNTED = {"action.route": "route", "data.enum": "set of states", "test.case": "test case"}
# The nodes whose name says where a fact is: a class, a function, a method, an enum, a table, a CSS rule.
SCOPES = {"class_definition", "function_definition", "class_declaration", "method_declaration",
          "constructor_declaration", "enum_declaration", "interface_declaration", "record_declaration",
          "struct_declaration", "function_declaration", "method_definition", "abstract_class_declaration",
          "variable_declarator", "function_statement", "class_statement", "enum_statement", "create_table",
          "create_type", "create_view", "create_function", "rule_set"}
# Where a scope keeps its name, where it is not in a field called name: a child of one of these types.
NAMED_BY = ("function_name", "simple_name", "object_reference", "selectors")
TESTS = re.compile(r"(^|/)(tests?|__tests__|spec|e2e|cypress|playwright|[^/]*_tests?)/|(^|/)(test_[^/]*|[^/]*_test)\.py$|"
                   r"(^|/)conftest\.py$|\.(test|spec|stories)\.[cm]?[jt]sx?$|Tests?\.cs$", re.IGNORECASE)
LONGEST_LINE = 2000          # a longer line is minified or generated: nothing a person wrote to be read
LONGEST_TEXT = 200           # what of a fact's first line is kept


@dataclass(frozen=True)
class Fact:
    path: str                # from the root, with forward slashes
    line: int
    end: int                 # the last line of what was found
    lens: str
    kind: str
    text: str                # its first line, as the code has it
    symbol: str              # the class, function or enum it is in
    by: str                  # tree-sitter, ast or pattern
    reach: int = 0           # the last line of the code it governs: the function a decorator or an attribute is on
    lead: int = 0            # the first line of the comments right above that code, which say what it is for

    @property
    def name(self) -> str:
        return f"{self.lens}.{self.kind}"

    @property
    def first(self) -> int:
        """The first line that belongs to the fact: the comments above what it governs, or what it is."""
        return min(self.lead or self.line, self.line)

    @property
    def last(self) -> int:
        """The last line that belongs to the fact: what it governs, or what it is."""
        return max(self.reach, self.end)


@dataclass
class Scan:
    facts: list[Fact] = field(default_factory=list)
    read: dict[str, dict[str, int]] = field(default_factory=dict)    # how each file was read: by, language, count
    tests: int = 0
    with_tests: bool = False       # whether the test files were read, not left out
    generated: int = 0
    why_not_syntax: str = ""


class Engine:
    """tree-sitter, where it is installed: a parser and the queries for each language, made once."""

    def __init__(self, syntax: bool = True) -> None:
        self.ts: Any = None
        self.problem = "" if syntax else "asked not to"
        self.missing: list[str] = []             # the grammar packages a language read asked for, not installed
        self.made: dict[str, tuple[Any, list[Any]] | None] = {}
        if syntax:
            try:
                import tree_sitter  # type: ignore[import-not-found]
                self.ts = tree_sitter
            except ImportError:
                self.problem = "tree-sitter is not installed"

    def ready(self, language: str) -> tuple[Any, list[Any]] | None:
        if self.ts is None:
            return None
        if language not in self.made:
            package, module, function = GRAMMARS[language]
            try:
                grammar = self.ts.Language(getattr(importlib.import_module(module), function)())
            except ImportError:
                if package not in self.missing:
                    self.missing.append(package)
                self.problem = f"not installed: {', '.join(self.missing)}"
                self.made[language] = None
                return None
            queries = []
            for name in QUERY_FILES[language]:              # a query the grammar refuses is this skill's error
                try:
                    queries.append(self.ts.Query(grammar, (QUERIES / f"{name}.scm").read_text(encoding="utf-8")))
                except self.ts.QueryError as problem:
                    raise SystemExit(f"queries/{name}.scm, for {language}: {problem}") from problem
            self.made[language] = (self.ts.Parser(grammar), queries)
        return self.made[language]


def first_line(text: str) -> str:
    line = text.split("\n", 1)[0].rstrip("\r").strip()
    return line[:LONGEST_TEXT]


def symbol_of(node: Any) -> str:
    """The names of the scopes around a node, outermost first: InvoicesController.Download."""
    names: list[str] = []
    came, current = node, node.parent
    while current is not None:
        if current.type == "decorated_definition":          # a decorator speaks of what it decorates
            definition = current.child_by_field_name("definition")
            if definition is not None and definition.id != came.id:
                named = definition.child_by_field_name("name")
                if named is not None and named.text:
                    names.append(named.text.decode("utf-8", "replace"))
        elif current.type in SCOPES:
            named = current.child_by_field_name("name")
            if named is None:
                named = next((child for child in current.named_children if child.type in NAMED_BY), None)
            if named is not None and named.type == "object_reference":
                named = named.child_by_field_name("name") or named
            top = current.type != "variable_declarator" or (
                current.parent is not None and current.parent.parent is not None
                and current.parent.parent.type in ("program", "export_statement"))
            if named is not None and named.text and top:
                names.append(named.text.decode("utf-8", "replace"))
        came, current = current, current.parent
    return ".".join(reversed(names))


def syntax_facts(engine: Engine, language: str, name: str, text: str) -> list[Fact] | None:
    made = engine.ready(language)
    if made is None:
        return None
    parser, queries = made
    tree = parser.parse(text.encode("utf-8"))
    facts: list[Fact] = []
    for query in queries:
        for capture, nodes in engine.ts.QueryCursor(query).captures(tree.root_node).items():
            if capture.startswith("_") or "." not in capture:
                continue
            lens, kind = capture.split(".", 1)
            for node in nodes:
                said = first_line(node.text.decode("utf-8", "replace")) if node.text else ""
                if said:
                    facts.append(Fact(name, node.start_point[0] + 1, node.end_point[0] + 1, lens, kind, said,
                                      symbol_of(node), "tree-sitter", *span_of(node)))
    return facts


def span_of(node: Any) -> tuple[int, int]:
    """For a decorator or an attribute: the last line of what it is on -- a route's handler -- and the first line of
    the comments right above that, which say what it is for. (0, 0) for anything else."""
    above = node.parent
    if above is not None and above.type == "attribute_list":
        above = above.parent
    elif above is None or above.type != "decorated_definition":
        return 0, 0
    if above is None:
        return 0, 0
    lead, before = above.start_point[0], above.prev_sibling
    while before is not None and before.type == "comment" and before.end_point[0] >= lead - 1:
        lead, before = before.start_point[0], before.prev_sibling
    return above.end_point[0] + 1, lead + 1


# --- Python without tree-sitter: the standard library's ast ------------------------------------------------------

AST_ROUTE = re.compile(r"^(route|get|post|put|delete|patch|websocket|api_route|callback|command)$")
AST_ACCESS = re.compile(r"login|permission|role|auth|admin|staff|superuser")
AST_ENUM = re.compile(r"(Enum|IntEnum|StrEnum|Flag|IntFlag|TextChoices|IntegerChoices|Choices)$")
AST_MODEL = re.compile(r"(BaseModel|Model|Base|Schema|TypedDict|SQLModel|DeclarativeBase)$")
AST_LIMITS = {"ge", "gt", "le", "lt", "min_length", "max_length", "pattern", "regex", "max_digits", "multiple_of"}
AST_FLAGS = {"is_enabled", "is_active", "feature_enabled", "is_feature_enabled", "flag_is_active", "switch_is_active",
             "get_flag", "variation", "bool_variation"}           # a feature flag read, as queries/python.scm knows it
AST_LABELS = {"title", "label", "placeholder", "children", "header", "tooltip", "message", "headerName", "subtitle",
              "description", "help_text", "help", "verbose_name", "error_message"}
AST_UI = {"html", "dbc", "dcc", "dmc", "ui", "st", "gr", "ft"}
COLOUR = re.compile(r"^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?([0-9a-fA-F]{2})?$")
TODO = re.compile(r"#.*\b(TODO|FIXME|HACK|XXX)\b")
WORDS = re.compile(r"[^\W\d_]{2,}")


def dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{dotted(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return dotted(node.func)
    return ""


def ast_facts(name: str, text: str) -> list[Fact] | None:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return None
    facts: list[Fact] = []
    scope: list[str] = []

    lines = text.splitlines()

    def put(node: ast.AST, lens: str, kind: str, reach: int = 0) -> None:
        said = ast.get_source_segment(text, node) or ""
        line_of, column = getattr(node, "lineno", 0), getattr(node, "col_offset", 0)
        if said and 0 < line_of <= len(lines) and column and lines[line_of - 1][column - 1] == "@":
            said = "@" + said            # a decorator, quoted as it stands in the file, as tree-sitter quotes it
        if said:
            line = getattr(node, "lineno", 1)
            facts.append(Fact(name, line, getattr(node, "end_lineno", line) or line, lens, kind, first_line(said),
                              ".".join(scope), "ast", reach))

    def visit(node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                called = dotted(decorator)
                last = called.rsplit(".", 1)[-1]
                scope.append(node.name)
                if isinstance(decorator, ast.Call) and AST_ROUTE.match(last):
                    put(decorator, "action", "route", getattr(node, "end_lineno", 0) or 0)
                elif AST_ACCESS.search(called):
                    put(decorator, "access", "check")
                elif "skip" in called or "xfail" in called:
                    put(decorator, "loose", "skip")
                    put(decorator, "test", "skip")
                elif "fixture" in called:
                    put(decorator, "test", "fixture")
                if "dataclass" in called and isinstance(node, ast.ClassDef):
                    put(node, "data", "model")
                for inner in ast.iter_child_nodes(decorator):       # what the decorator is given: a callback's Inputs
                    visit(inner)
                scope.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                put(node, "test", "case")
            if isinstance(node, ast.ClassDef) and re.match(r"Test[A-Z]", node.name):
                put(node, "test", "case")
            if isinstance(node, ast.ClassDef):
                bases = [dotted(base) for base in node.bases]
                if any(AST_ENUM.search(base) for base in bases):
                    put(node, "data", "enum")
                    scope.append(node.name)
                    for item in node.body:
                        if isinstance(item, ast.Assign) and all(isinstance(t, ast.Name) for t in item.targets):
                            put(item, "data", "member")
                    scope.pop()
                elif any(AST_MODEL.search(base) for base in bases):
                    put(node, "data", "model")
            scope.append(node.name)
            for child in ast.iter_child_nodes(node):
                if child not in node.decorator_list:
                    visit(child)
            scope.pop()
            return
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            value = node.value.operand if isinstance(node.value, ast.UnaryOp) else node.value
            if re.fullmatch(r"_?[A-Z][A-Z0-9_]{2,}", node.targets[0].id) and isinstance(value, ast.Constant) \
                    and isinstance(value.value, (int, float)) and not isinstance(value.value, bool):
                put(node, "rule", "constant")
        elif isinstance(node, ast.Raise):
            put(node, "failure", "raise")
        elif isinstance(node, ast.ExceptHandler):
            put(node, "failure", "catch")
        elif isinstance(node, ast.Call):
            called = dotted(node.func)
            head, _, last = called.rpartition(".")
            if last in ("Field", "constr", "conint", "confloat", "Query", "Path", "Body") and \
                    any(k.arg in AST_LIMITS for k in node.keywords):
                put(node, "rule", "limit")
            elif last in ("Input", "State") and not head and node.args and isinstance(node.args[0], ast.Constant):
                put(node, "action", "input")
            elif head in ("requests", "httpx", "aiohttp", "urllib", "session", "client") and \
                    last in ("get", "post", "put", "delete", "patch", "request", "urlopen"):
                put(node, "system", "call")
            elif called in ("os.environ.get", "os.getenv", "getenv"):
                put(node, "system", "setting")
            elif last in AST_FLAGS and node.args and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                put(node, "rule", "flag")
            elif last in ("flash", "alert") and not head and node.args:
                put(node.args[0], "shows", "message")
            elif last in ("patch", "MagicMock", "Mock", "AsyncMock", "create_autospec") \
                    or (head in ("mock", "mocker", "monkeypatch") and last in ("patch", "setattr", "object", "dict")):
                put(node, "test", "mock")
            if head in AST_UI and node.args and isinstance(node.args[0], ast.Constant) and \
                    isinstance(node.args[0].value, str):
                put(node.args[0], "shows", "text")
            for keyword in node.keywords:
                if keyword.arg in AST_LABELS and isinstance(keyword.value, ast.Constant) and \
                        isinstance(keyword.value.value, str):
                    put(keyword.value, "shows", "label")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if re.match(r"^(https?|wss?)://", node.value):
                put(node, "system", "address")
            elif COLOUR.match(node.value):
                put(node, "look", "colour")
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    for number, line in enumerate(text.splitlines(), start=1):
        found = TODO.search(line)
        if found:
            facts.append(Fact(name, number, number, "loose", "todo", first_line(line[found.start():]), "", "ast"))
    return facts


def pattern_facts(name: str, text: str) -> list[Fact]:
    """scout.py's patterns, where no parser reads the language: where to look, not what is there."""
    facts: list[Fact] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for lens, pattern in scout.LENSES.items():
            if pattern.search(line):
                facts.append(Fact(name, number, number, lens, "signal", first_line(line), "", "pattern"))
    return facts


def tidy(facts: list[Fact]) -> list[Fact]:
    """One fact once: of two of a kind on one line, the one whose words the other holds goes."""
    kept: list[Fact] = []
    by_place: dict[tuple[str, int, str], list[Fact]] = {}
    for fact in facts:
        by_place.setdefault((fact.path, fact.line, fact.name), []).append(fact)
    for group in by_place.values():
        group = sorted(set(group), key=lambda f: (-len(f.text), -f.end))
        for fact in group:
            if fact.lens == "shows" and not WORDS.search(fact.text):
                continue                         # a sign, a number, a space: nothing a user reads as words
            if not any(fact.text in other.text and other != fact for other in kept if other in group):
                kept.append(fact)
    order = {lens: n for n, lens in enumerate(LENS_SAYS)}
    return sorted(kept, key=lambda f: (order.get(f.lens, 99), f.path.lower(), f.line, f.kind, f.text))


def facts_in(path: Path, name: str, engine: Engine) -> tuple[list[Fact], str]:
    """The facts of one file of code, and how it was read; nothing for a file no parser and no pattern is for."""
    language = LANGUAGES.get(path.suffix.lower())
    if language is None:
        return [], ""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if any(len(line) > LONGEST_LINE for line in text.splitlines()):
        return [], "generated"
    found = syntax_facts(engine, language, name, text)
    if found is not None:
        return tidy(found), "tree-sitter"
    if language == "python":
        found = ast_facts(name, text)
        if found is not None:
            return tidy(found), "ast"
    return pattern_facts(name, text), "pattern"


def is_test(name: str) -> bool:
    return bool(TESTS.search(name))


def scan(root: Path, engine: Engine | None = None, tests: bool = False) -> Scan:
    """The facts of the code under the root: the product's own files, and with `tests` its tests as well."""
    engine = engine or Engine()
    result = Scan()
    base = root.parent if root.is_file() else root
    for path in scout.walk(root)[0]:
        name = path.relative_to(base).as_posix()
        if path.suffix.lower() not in LANGUAGES:
            continue
        if is_test(name):
            result.tests += 1
            if not tests:
                continue
        facts, by = facts_in(path, name, engine)
        if by == "generated":
            result.generated += 1
            continue
        language = LANGUAGES[path.suffix.lower()]
        counts = result.read.setdefault(by, {})
        counts[language] = counts.get(language, 0) + 1
        result.facts.extend(facts)
    result.with_tests = tests
    if any(by != "tree-sitter" for by in result.read):
        result.why_not_syntax = engine.problem
    return result


def render(root: Path, result: Scan, lens: str | None = None) -> str:
    files = sum(sum(counts.values()) for counts in result.read.values())
    out = [f"{root}: {files} file(s) of code"]
    for by in ("tree-sitter", "ast", "pattern"):
        if by in result.read:
            how = {"tree-sitter": "by syntax, tree-sitter", "ast": "by syntax, Python's ast",
                   "pattern": "by pattern only: where to look, not what is there"}[by]
            out.append(f"  read {how}: " + ", ".join(f"{language} {count}" for language, count
                                                      in sorted(result.read[by].items())))
    if result.why_not_syntax:
        out.append(f"  not read by tree-sitter: {result.why_not_syntax}; `{INSTALL}`")
    left = [some for some in (f"{result.tests} test file(s)" if result.tests and not result.with_tests else "",
                              f"{result.generated} generated or minified" if result.generated else "") if some]
    if left:
        out.append("  left out: " + ", ".join(left))
    if result.with_tests and result.tests:
        out.append(f"  read with the tests: {result.tests} test file(s)")
    counts = {name: sum(1 for f in result.facts if f.lens == name) for name in LENS_SAYS}
    out.append("  " + " · ".join(f"{name} {count}" for name, count in counts.items() if count))
    for name, says in LENS_SAYS.items():
        if lens and name != lens:
            continue
        facts = [f for f in result.facts if f.lens == name]
        if not facts:
            continue
        out += ["", f"## {name}: {says} ({len(facts)})"]
        for fact in facts:
            more = " …" if fact.end > fact.line else ""
            where = f"  · {fact.symbol}" if fact.symbol else ""
            out.append(f"{fact.path}:{fact.line}  {fact.kind}  {fact.text}{more}{where}")
    return "\n".join(out)


def as_json(root: Path, result: Scan) -> str:
    return json.dumps({"root": str(root), "read": result.read, "tests": result.tests, "generated": result.generated,
                       "why_not_syntax": result.why_not_syntax, "facts": [asdict(f) for f in result.facts]},
                      indent=1, ensure_ascii=False)


# --- Selftest ---------------------------------------------------------------------------------------------------

SAMPLES = {
    "api/invoices.py": '''import os
from enum import Enum

MAX_LINES = 100
PDF_URL = os.environ.get("PDF_URL")


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"


class Line(BaseModel):
    amount: int = Field(ge=1, le=10000)


# the invoice as a PDF, for the accountant
@app.get("/invoices/{invoice_id}/pdf")
@login_required
def download(invoice_id: int):
    try:
        pass
    except KeyError:
        raise HTTPException(status_code=409, detail="A draft cannot be downloaded")
    # TODO: watermark
    return httpx.get("https://pdf.example.com/render")


@callback(Output("table", "data"), Input("refresh", "n_clicks"))
def refresh(n):
    flash("Refreshed")
    return html.Div([html.Button("Refresh", id="refresh")], title="Trades", style={"color": "#36d399"})


if flags.is_enabled("new_checkout"):
    pass
''',
    "Controllers/InvoicesController.cs": '''public enum InvoiceStatus { Draft, Issued, Paid }

[ApiController]
[Route("api/invoices")]
public class InvoicesController : ControllerBase
{
    private const int MaxLines = 100;

    [HttpGet("{id}/pdf")]
    [Authorize(Roles = "Accountant")]
    public IActionResult Download(int id)
    {
        if (invoice.Status == InvoiceStatus.Draft)
            return Problem("A draft cannot be downloaded", statusCode: 409);
        // TODO: watermark
        throw new InvalidOperationException("The invoice is not found");
    }
}

public class Line
{
    [Required, Range(1, 10000)]
    public int Amount { get; set; }
    [StringLength(80, ErrorMessage = "At most 80 characters")]
    public string Note { get; set; }
}

public static class Endpoints
{
    public static void Map(WebApplication app)
    {
        app.MapGet("/health", () => "ok").RequireAuthorization("Admin");
        new HttpClient().GetAsync("https://pdf.example.com/render");
        features.IsEnabledAsync("NewCheckout");
    }
}

[FeatureGate("NewCheckout")]
public class CheckoutController : ControllerBase { }
''',
    "web/InvoicePage.tsx": '''import { z } from "zod";

export enum InvoiceStatus { Draft = "draft", Issued }
type Status = "draft" | "issued" | "paid";
const Line = z.object({ amount: z.number().min(1).max(10000) });

export function InvoicePage() {
  return (
    <main>
      <h1>Your invoice</h1>
      <button aria-label="Download PDF" onClick={download}>Download</button>
      <input placeholder="Search invoices" required maxLength={80} />
      <Route path="/invoices/:id" element={<RequireAuth><InvoicePage /></RequireAuth>} />
    </main>
  );
}

async function download() {
  const res = await fetch("/api/invoices/1/pdf");
  if (!res.ok) throw new Error("The download failed");
  toast.error("Try again later");
}
// TODO: retry
export const Banner = () => <p>Free delivery</p>;
function Checkout() { return useFlag("new_checkout") ? <InvoicePage /> : null; }
''',
    "web/server.js": '''const express = require("express");
const app = express();
app.post("/invoices/:id/send", (req, res) => { throw new Error("Not sent"); });
''',
    "templates/invoices.html": '''<!DOCTYPE html>
<html lang="en">
<head><title>Invoices</title><script src="https://cdn.example.com/htmx.js"></script></head>
<body>
  <h1>Your invoices</h1>
  <form action="/invoices/search" method="post">
    <input name="q" placeholder="Invoice number" required maxlength="20">
    <select name="status"><option>Draft</option><option>Issued</option></select>
    <button type="submit" hx-post="/invoices/search">Search</button>
  </form>
  <a href="/invoices/new" aria-label="New invoice">New</a>
  <!-- TODO: paging -->
</body>
</html>
''',
    "web/site.css": ''':root {
  --accent: #0969da;
}
/* TODO: dark mode */
.btn-primary { color: #ffffff; font-family: "Inter", sans-serif; }
@media (max-width: 768px) {
  .grid { display: block; }
}
''',
    "deploy/deploy.sh": '''#!/usr/bin/env bash
MAX_RETRIES=3
export API_URL="https://api.example.com"
deploy() {
  if [ -z "${TOKEN:-}" ]; then
    echo "TOKEN is not set" >&2
    exit 1
  fi
  sudo systemctl restart shop
  curl -fsS "$API_URL/deploy"
  echo "Deployed"
}
trap 'echo "Failed"' ERR
# TODO: rollback
''',
    "deploy/Deploy.ps1": '''#Requires -RunAsAdministrator
enum Stage { Draft; Live }
function Invoke-Deploy {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("dev", "prod")]
        [string]$Environment,
        [ValidateRange(1, 10)]
        [int]$Count = 1
    )
    if (-not $env:DEPLOY_TOKEN) { throw "DEPLOY_TOKEN is not set" }
    try {
        Invoke-RestMethod -Uri "https://api.example.com/deploy" -Method Post
        Write-Host "Deployed to $Environment"
    } catch {
        Write-Error "The deploy failed"
    }
}
# TODO: rollback
''',
    "database/schema.sql": '''CREATE TYPE invoice_status AS ENUM ('draft', 'issued', 'paid');

CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    number VARCHAR(20) NOT NULL UNIQUE,
    status invoice_status NOT NULL DEFAULT 'draft',
    amount NUMERIC(10, 2) CHECK (amount > 0),
    kind TEXT CHECK (kind IN ('sale', 'refund')),
    customer_id INT REFERENCES customers(id)
);

CREATE VIEW open_invoices AS SELECT * FROM invoices WHERE status <> 'paid';
-- TODO: archive
''',
    "logic_tests/invoices.py": "def test_two():\n    assert True\n",
    "tests/test_invoices.py": ('import pytest\nfrom unittest.mock import patch\n\n@pytest.fixture\ndef client():\n'
                              '    return make_client()\n\n@pytest.mark.skip(reason="flaky")\ndef test_download():\n'
                              '    with patch("api.invoices.render") as render:\n'
                              '        assert get("/invoices/1/pdf").status_code == 200\n'),
    "web/__tests__/invoice.test.tsx": ('import { vi } from "vitest";\nvi.mock("../api");\n'
                                      'describe("the invoice page", () => {\n'
                                      '  beforeEach(() => { reset(); });\n'
                                      '  it("downloads a PDF", () => { expect(1).toBe(1); });\n'
                                      '  it.skip("prints", () => {});\n});\n'),
    "Api.Tests/InvoicesTests.cs": ('public class InvoicesTests : IClassFixture<Db>\n{\n'
                               '    private readonly Mock<IRenderer> renderer = new Mock<IRenderer>();\n'
                               '    [Fact]\n    public void Downloads() { }\n'
                               '    [Fact(Skip = "slow")]\n    public void Prints() { }\n}\n'),
    "web/vendor.min.js": "var a=1;" * 400 + "\n",
    "holdings.csv": "ticker,shares\nSECRET,100\n",
}

# (file, fact, words it holds): what the reading must find in the samples, by tree-sitter
WANTED = [
    ("api/invoices.py", "action.route", 'app.get("/invoices/{invoice_id}/pdf")'),
    ("api/invoices.py", "action.route", "callback("),
    ("api/invoices.py", "action.input", 'Input("refresh", "n_clicks")'),
    ("api/invoices.py", "access.check", "login_required"),
    ("api/invoices.py", "data.enum", "class InvoiceStatus(str, Enum):"),
    ("api/invoices.py", "data.member", 'DRAFT = "draft"'),
    ("api/invoices.py", "rule.constant", "MAX_LINES = 100"),
    ("api/invoices.py", "rule.limit", "Field(ge=1, le=10000)"),
    ("api/invoices.py", "failure.raise", "raise HTTPException"),
    ("api/invoices.py", "system.call", 'httpx.get("https://pdf.example.com/render")'),
    ("api/invoices.py", "system.setting", 'os.environ.get("PDF_URL")'),
    ("api/invoices.py", "shows.text", '"Refresh"'),
    ("api/invoices.py", "shows.label", '"Trades"'),
    ("api/invoices.py", "shows.message", '"Refreshed"'),
    ("api/invoices.py", "look.colour", '"#36d399"'),
    ("api/invoices.py", "loose.todo", "TODO: watermark"),
    ("api/invoices.py", "rule.flag", 'flags.is_enabled("new_checkout")'),
    ("Controllers/InvoicesController.cs", "rule.flag", 'FeatureGate("NewCheckout")'),
    ("Controllers/InvoicesController.cs", "rule.flag", 'features.IsEnabledAsync("NewCheckout")'),
    ("web/InvoicePage.tsx", "rule.flag", 'useFlag("new_checkout")'),
    ("web/InvoicePage.tsx", "look.component", "function InvoicePage()"),
    ("web/InvoicePage.tsx", "look.component", "Banner = () =>"),
    ("Controllers/InvoicesController.cs", "action.route", 'HttpGet("{id}/pdf")'),
    ("Controllers/InvoicesController.cs", "action.route", 'app.MapGet("/health"'),
    ("Controllers/InvoicesController.cs", "access.check", 'Authorize(Roles = "Accountant")'),
    ("Controllers/InvoicesController.cs", "access.check", "RequireAuthorization"),
    ("Controllers/InvoicesController.cs", "data.enum", "public enum InvoiceStatus"),
    ("Controllers/InvoicesController.cs", "data.member", "Issued"),
    ("Controllers/InvoicesController.cs", "rule.limit", "Range(1, 10000)"),
    ("Controllers/InvoicesController.cs", "rule.constant", "private const int MaxLines = 100;"),
    ("Controllers/InvoicesController.cs", "shows.label", 'ErrorMessage = "At most 80 characters"'),
    ("Controllers/InvoicesController.cs", "failure.refuse", 'Problem("A draft cannot be downloaded"'),
    ("Controllers/InvoicesController.cs", "failure.throw", "throw new InvalidOperationException"),
    ("Controllers/InvoicesController.cs", "system.client", "new HttpClient()"),
    ("Controllers/InvoicesController.cs", "loose.todo", "// TODO: watermark"),
    ("web/InvoicePage.tsx", "data.enum", "enum InvoiceStatus { Draft"),
    ("web/InvoicePage.tsx", "data.enum", 'type Status = "draft" | "issued" | "paid";'),
    ("web/InvoicePage.tsx", "data.member", "Issued"),
    ("web/InvoicePage.tsx", "data.model", "z.object("),
    ("web/InvoicePage.tsx", "rule.limit", "z.number().min(1).max(10000)"),
    ("web/InvoicePage.tsx", "shows.text", "Your invoice"),
    ("web/InvoicePage.tsx", "shows.label", 'aria-label="Download PDF"'),
    ("web/InvoicePage.tsx", "shows.label", 'placeholder="Search invoices"'),
    ("web/InvoicePage.tsx", "rule.limit", "maxLength={80}"),
    ("web/InvoicePage.tsx", "action.handler", "onClick={download}"),
    ("web/InvoicePage.tsx", "action.route", '<Route path="/invoices/:id"'),
    ("web/InvoicePage.tsx", "access.check", "<RequireAuth>"),
    ("web/InvoicePage.tsx", "system.call", 'fetch("/api/invoices/1/pdf")'),
    ("web/InvoicePage.tsx", "failure.throw", 'throw new Error("The download failed")'),
    ("web/InvoicePage.tsx", "shows.message", '"Try again later"'),
    ("web/InvoicePage.tsx", "loose.todo", "// TODO: retry"),
    ("web/server.js", "action.route", 'app.post("/invoices/:id/send"'),
    ("templates/invoices.html", "action.form", '<form action="/invoices/search" method="post">'),
    ("templates/invoices.html", "action.link", '<a href="/invoices/new"'),
    ("templates/invoices.html", "action.button", '<button type="submit"'),
    ("templates/invoices.html", "action.request", 'hx-post="/invoices/search"'),
    ("templates/invoices.html", "shows.text", "Your invoices"),
    ("templates/invoices.html", "shows.label", 'placeholder="Invoice number"'),
    ("templates/invoices.html", "shows.label", 'aria-label="New invoice"'),
    ("templates/invoices.html", "rule.limit", 'maxlength="20"'),
    ("templates/invoices.html", "rule.limit", "required"),
    ("templates/invoices.html", "data.choices", '<select name="status">'),
    ("templates/invoices.html", "data.choice", "<option>Issued</option>"),
    ("templates/invoices.html", "system.script", '<script src="https://cdn.example.com/htmx.js">'),
    ("templates/invoices.html", "loose.todo", "<!-- TODO: paging -->"),
    ("web/site.css", "look.token", "--accent: #0969da"),
    ("web/site.css", "look.colour", "#ffffff"),
    ("web/site.css", "look.font", 'font-family: "Inter", sans-serif'),
    ("web/site.css", "look.breakpoint", "@media (max-width: 768px)"),
    ("web/site.css", "loose.todo", "/* TODO: dark mode */"),
    ("deploy/deploy.sh", "action.command", "deploy() {"),
    ("deploy/deploy.sh", "rule.constant", "MAX_RETRIES=3"),
    ("deploy/deploy.sh", "system.setting", 'export API_URL="https://api.example.com"'),
    ("deploy/deploy.sh", "system.address", "https://api.example.com"),
    ("deploy/deploy.sh", "system.call", 'curl -fsS "$API_URL/deploy"'),
    ("deploy/deploy.sh", "access.check", "sudo systemctl restart shop"),
    ("deploy/deploy.sh", "failure.message", 'echo "TOKEN is not set" >&2'),
    ("deploy/deploy.sh", "failure.exit", "exit 1"),
    ("deploy/deploy.sh", "failure.catch", "trap"),
    ("deploy/deploy.sh", "shows.message", 'echo "Deployed"'),
    ("deploy/deploy.sh", "loose.todo", "# TODO: rollback"),
    ("deploy/Deploy.ps1", "action.command", "function Invoke-Deploy {"),
    ("deploy/Deploy.ps1", "rule.limit", "Parameter(Mandatory = $true)"),
    ("deploy/Deploy.ps1", "rule.limit", "ValidateRange(1, 10)"),
    ("deploy/Deploy.ps1", "data.enum", 'ValidateSet("dev", "prod")'),
    ("deploy/Deploy.ps1", "data.enum", "enum Stage { Draft; Live }"),
    ("deploy/Deploy.ps1", "data.member", "Live"),
    ("deploy/Deploy.ps1", "system.setting", "$env:DEPLOY_TOKEN"),
    ("deploy/Deploy.ps1", "system.call", 'Invoke-RestMethod -Uri "https://api.example.com/deploy"'),
    ("deploy/Deploy.ps1", "shows.message", 'Write-Host "Deployed to $Environment"'),
    ("deploy/Deploy.ps1", "failure.throw", 'throw "DEPLOY_TOKEN is not set"'),
    ("deploy/Deploy.ps1", "failure.message", 'Write-Error "The deploy failed"'),
    ("deploy/Deploy.ps1", "access.check", "#Requires -RunAsAdministrator"),
    ("deploy/Deploy.ps1", "loose.todo", "# TODO: rollback"),
    ("database/schema.sql", "data.enum", "CREATE TYPE invoice_status AS ENUM ('draft', 'issued', 'paid')"),
    ("database/schema.sql", "data.member", "'issued'"),
    ("database/schema.sql", "data.table", "CREATE TABLE invoices ("),
    ("database/schema.sql", "data.enum", "kind TEXT CHECK (kind IN ('sale', 'refund'))"),
    ("database/schema.sql", "data.relation", "customer_id INT REFERENCES customers(id)"),
    ("database/schema.sql", "data.view", "CREATE VIEW open_invoices"),
    ("database/schema.sql", "rule.limit", "number VARCHAR(20) NOT NULL UNIQUE"),
    ("database/schema.sql", "rule.limit", "amount NUMERIC(10, 2) CHECK (amount > 0)"),
    ("database/schema.sql", "rule.default", "status invoice_status NOT NULL DEFAULT 'draft'"),
    ("database/schema.sql", "loose.todo", "-- TODO: archive"),
]
# the class, function, table or rule a fact says it is in: (file, fact, words it holds, symbol)
WANTED_SYMBOLS = [
    ("Controllers/InvoicesController.cs", "action.route", "HttpGet", "InvoicesController.Download"),
    ("Controllers/InvoicesController.cs", "data.member", "Issued", "InvoiceStatus"),
    ("deploy/Deploy.ps1", "rule.limit", "ValidateRange", "Invoke-Deploy"),
    ("database/schema.sql", "rule.limit", "number VARCHAR", "invoices"),
    ("web/site.css", "look.colour", "#ffffff", ".btn-primary"),
]
# what Python's ast must find in the same file, where tree-sitter is not there
WANTED_BY_AST = [w for w in WANTED if w[0] == "api/invoices.py" and w[1] not in ("shows.message",)]


def run_selftest() -> int:
    bad: list[str] = []
    with tempfile.TemporaryDirectory(prefix="specs-builder-scan-") as tmp:
        root = Path(tmp) / "app"
        for name, text in SAMPLES.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text, encoding="utf-8")

        engine = Engine()
        ready = [language for language in GRAMMARS if engine.ready(language) is not None]
        if engine.ts is None or len(ready) < len(GRAMMARS):
            print(f"skip  tree-sitter or a grammar is not installed ({engine.problem}): only the reading without "
                  f"them is checked")
        else:
            before = len(bad)
            result = scan(root, engine)
            if result.why_not_syntax or set(result.read) != {"tree-sitter"}:
                bad.append(f"every sample should be read by tree-sitter: {result.read}, {result.why_not_syntax}")
            for file, name, words in WANTED:
                if not any(f.path == file and f.name == name and words in f.text for f in result.facts):
                    bad.append(f"tree-sitter should find {name} '{words}' in {file}")
            print(f"{'FAILED' if len(bad) > before else 'ok'}  tree-sitter finds each kind of fact in C#, Python, "
                  f"JavaScript, TypeScript, TSX, HTML, CSS, Bash, PowerShell and SQL")

            before = len(bad)
            for fact in result.facts:
                held = (root / fact.path).read_text(encoding="utf-8").splitlines()
                if fact.text not in held[fact.line - 1]:
                    bad.append(f"{fact.path}:{fact.line}: '{fact.text}' is not that line's own words")
                    break
            for file, words, first, last in (("api/invoices.py", 'app.get("/invoices', 17, 26),
                                             ("Controllers/InvoicesController.cs", 'HttpGet("{id}/pdf")', 9, 17)):
                route = [f for f in result.facts if f.path == file and f.name == "action.route" and words in f.text]
                if not route or (route[0].first, route[0].last) != (first, last):
                    bad.append(f"the route '{words}' in {file} should hold its handler and the comments above it, "
                               f"lines {first} to {last}: {route[:1]}")
            for file, name, words, symbol in WANTED_SYMBOLS:
                found = [f for f in result.facts if f.path == file and f.name == name and words in f.text]
                if not found or found[0].symbol != symbol:
                    bad.append(f"{name} '{words}' in {file} should say it is in {symbol}: {found[:1]}")
            if any("ok" == f.text.strip('"') for f in result.facts if f.lens == "shows"):
                bad.append("a string that is only returned is not something a user reads")
            print(f"{'FAILED' if len(bad) > before else 'ok'}  each fact quotes its line as it stands, and says "
                  f"where it is")

        before = len(bad)
        bare = scan(root, Engine(syntax=False))
        if set(bare.read) != {"ast", "pattern"} or bare.read["ast"] != {"python": 1}:
            bad.append(f"without tree-sitter, Python is read by ast and the rest by pattern: {bare.read}")
        for file, name, words in WANTED_BY_AST:
            if not any(f.path == file and f.name == name and words in f.text for f in bare.facts):
                bad.append(f"ast should find {name} '{words}' in {file}")
        if not any(f.by == "pattern" and f.path == "Controllers/InvoicesController.cs" and f.lens == "action"
                   for f in bare.facts):
            bad.append("without tree-sitter, C# should still be pointed at by pattern")
        if "asked not to" not in render(root, bare):
            bad.append("the output should say why it was not read by tree-sitter")
        print(f"{'FAILED' if len(bad) > before else 'ok'}  without tree-sitter, Python is read by ast and the rest "
              f"by pattern, and it says so")

        before = len(bad)
        result = scan(root, Engine(syntax=engine.ts is not None))
        text = render(root, result) + as_json(root, result)
        if result.tests != 4 or result.generated != 1 or "SECRET" in text or "test_invoices" in text:
            bad.append(f"tests, minified code and data should be left out: tests {result.tests}, "
                       f"generated {result.generated}")
        print(f"{'FAILED' if len(bad) > before else 'ok'}  tests, generated code and data files are left out")

        before = len(bad)
        with_tests = scan(root, Engine(syntax=engine.ts is not None), tests=True)
        found = {(f.path, f.name, f.text) for f in with_tests.facts if f.lens == "test"}
        wanted_tests = [("tests/test_invoices.py", "test.case", "def test_download"),
                        ("tests/test_invoices.py", "test.fixture", "@pytest.fixture"),
                        ("tests/test_invoices.py", "test.skip", "skip"), ("tests/test_invoices.py", "test.mock", "patch(")]
        if engine.ts is not None and len(ready) == len(GRAMMARS):
            wanted_tests += [("web/__tests__/invoice.test.tsx", "test.case", 'it("downloads a PDF"'),
                             ("web/__tests__/invoice.test.tsx", "test.skip", "it.skip"),
                             ("web/__tests__/invoice.test.tsx", "test.mock", 'vi.mock("../api")'),
                             ("web/__tests__/invoice.test.tsx", "test.fixture", "beforeEach"),
                             ("Api.Tests/InvoicesTests.cs", "test.case", "Fact"), ("Api.Tests/InvoicesTests.cs", "test.skip", "Skip"),
                             ("Api.Tests/InvoicesTests.cs", "test.mock", "new Mock<IRenderer>()"),
                             ("Api.Tests/InvoicesTests.cs", "test.fixture", "IClassFixture")]
        for file, name, words in wanted_tests:
            if not any(p == file and n == name and words in t for p, n, t in found):
                bad.append(f"--tests should find {name} '{words}' in {file}: {sorted(f for f in found if f[0] == file)}")
        if not any(f.lens == "action" for f in with_tests.facts) or "read with the tests: 4" not in render(root, with_tests):
            bad.append("--tests reads the product's files as well as its tests, and says so")
        print(f"{'FAILED' if len(bad) > before else 'ok'}  with --tests, each test case, skip, mock and fixture is listed")

    for message in bad:
        print("ERROR " + message)
    print(f"{'FAILED' if bad else 'PASSED'} -- {len(bad)} problem(s)")
    return 1 if bad else 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="List the facts in code by its syntax.")
    parser.add_argument("path", nargs="?", type=Path, help="the folder or file of code")
    parser.add_argument("--lens", choices=sorted(LENS_SAYS), help="print the facts of this lens only")
    parser.add_argument("--json", action="store_true", help="print the facts as JSON")
    parser.add_argument("--tests", action="store_true", help="read the tests as well: the lens test lists what they hold")
    parser.add_argument("--languages", action="store_true", help="say how each language is read here")
    parser.add_argument("--selftest", action="store_true", help="check this script against samples it writes")
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    if args.languages:
        engine = Engine()
        for language, (package, _, _) in GRAMMARS.items():
            suffixes = " ".join(s for s, named in LANGUAGES.items() if named == language)
            how = ("by syntax" if engine.ready(language) is not None else
                   "by Python's ast; " if language == "python" else "by patterns; ") + \
                  ("" if engine.ready(language) is not None else f"`pip install {package}` reads it by syntax")
            print(f"{language:<11} {suffixes:<38} {how}")
        if engine.ts is None:
            print(f"tree-sitter is not installed: `{INSTALL}`")
        return 0
    if args.path is None:
        parser.error("the folder or file of code is required unless --selftest or --languages is given")
    if not args.path.exists():
        print(f"{args.path}: not found", file=sys.stderr)
        return 2
    result = scan(args.path, tests=args.tests)
    print(as_json(args.path, result) if args.json else render(args.path, result, args.lens))
    return 0


if __name__ == "__main__":
    sys.exit(main())
