#!/usr/bin/env python3
"""List what an API description says: each endpoint, what it takes, what it answers, and who may call it.

    python scripts/api_spec.py <file or folder>            # every endpoint, one to a block
    python scripts/api_spec.py <file or folder> --json     # the same, for a tool
    python scripts/api_spec.py --selftest

The API archaeologist reads an API by three things: its description, the
routes of its code (scan_code.py), and the calls a running application
makes (the captures of a live walk). This reads the description: an
OpenAPI 3 or Swagger 2 document written as JSON. For each endpoint it gives
the method and the path, the line of the file it stands at -- so that a
finding can name it, `openapi.json:120` -- its summary, the parameters it
takes and which are required, the body it takes, each status it answers
with what it holds, and the security it asks for.

A folder is searched for files named `openapi*.json` or `swagger*.json`,
outside dependencies and builds; a file named is read whatever its name. A
description written as YAML is not read: Python's standard library has no
reader for it, and this skill takes nothing else. Ask for the JSON form --
every tool that writes OpenAPI writes it -- and the output says so of each
YAML file it passes. No other file is opened. Standard library only.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")
NOT_THE_PRODUCTS = {"node_modules", ".git", ".venv", "venv", "bin", "obj", "dist", "build", "__pycache__"}
NAME_RE = re.compile(r"^(openapi|swagger)[\w.-]*\.(json|ya?ml)$", re.IGNORECASE)


@dataclass
class Endpoint:
    """One operation of an API description."""
    file: str                  # from the folder read, with forward slashes
    line: int                  # where its method stands in the file
    end: int                   # the last line before the next operation
    method: str
    path: str
    summary: str
    parameters: list[str] = field(default_factory=list)     # `id in path, required`
    request: str = ""          # what its body holds
    responses: dict[str, str] = field(default_factory=dict)  # each status: what it says and holds
    security: str = ""         # what it asks of the caller; "none" where it says it asks nothing

    @property
    def name(self) -> str:
        return f"{self.method.upper()} {self.path}"


def schema_said(schema: object, depth: int = 0) -> str:
    """A schema in a few words: a named schema by its name, a list by what it holds, an object by its fields."""
    if not isinstance(schema, dict):
        return ""
    if "$ref" in schema:
        return str(schema["$ref"]).rsplit("/", 1)[-1]
    for either in ("oneOf", "anyOf", "allOf"):
        if isinstance(schema.get(either), list):
            parts = [schema_said(s, depth + 1) for s in schema[either]]
            return (" or " if either != "allOf" else " and ").join(p for p in parts if p and p != "null")
    kind = schema.get("type")
    if kind == "array":
        return f"a list of {schema_said(schema.get('items'), depth + 1) or 'items'}"
    if kind == "object" or "properties" in schema:
        fields = list((schema.get("properties") or {}).keys())
        if fields and depth < 2:
            return "{" + ", ".join(fields[:8]) + (", ..." if len(fields) > 8 else "") + "}"
        return str(schema.get("title") or "an object")
    if isinstance(kind, list):
        return " or ".join(str(k) for k in kind if k != "null")
    return str(kind or schema.get("title") or "")


def content_said(holder: object) -> str:
    """What a request body or a response holds: the schema of its first content type, or of Swagger's `schema`."""
    if not isinstance(holder, dict):
        return ""
    if "schema" in holder:
        return schema_said(holder["schema"])
    content = holder.get("content")
    if isinstance(content, dict) and content:
        first = next(iter(content.values()))
        return schema_said(first.get("schema")) if isinstance(first, dict) else ""
    return ""


def security_said(asked: object) -> str:
    if asked is None:
        return ""
    if isinstance(asked, list) and not asked:
        return "none"
    if isinstance(asked, list):
        return " or ".join(" and ".join(sorted(item)) for item in asked if isinstance(item, dict)) or "none"
    return ""


def operation_lines(text: str) -> list[int]:
    """The line of each operation, in the order the document holds them: a method's key inside a path's object.
    A description written on one line has every operation on line 1."""
    out: list[int] = []
    in_path = False
    for number, line in enumerate(text.splitlines(), start=1):
        if re.match(r'^\s*"/[^"]*"\s*:\s*\{', line):
            in_path = True
        elif in_path and re.match(rf'^\s*"({"|".join(METHODS)})"\s*:\s*\{{', line, re.IGNORECASE):
            out.append(number)
    return out


def read(file: Path, name: str) -> tuple[list[Endpoint], str]:
    """The endpoints of one description, and why it could not be read, where it could not."""
    if file.suffix.lower() in (".yaml", ".yml"):
        return [], "written as YAML, which is not read here: ask for the JSON form"
    try:
        text = file.read_text(encoding="utf-8-sig")
        held = json.loads(text)
    except (OSError, UnicodeDecodeError, ValueError) as problem:
        return [], f"not JSON: {problem}"
    if not isinstance(held, dict) or not ("openapi" in held or "swagger" in held) or \
            not isinstance(held.get("paths"), dict):
        return [], "not an OpenAPI or Swagger description: no `openapi` or `swagger`, or no `paths`"
    lines = operation_lines(text)
    endpoints: list[Endpoint] = []
    for path, operations in held["paths"].items():
        if not isinstance(operations, dict):
            continue
        shared = operations.get("parameters", [])
        for method, operation in operations.items():
            if method.lower() not in METHODS or not isinstance(operation, dict):
                continue
            at = lines[len(endpoints)] if len(endpoints) < len(lines) else 1
            point = Endpoint(name, at, at, method.lower(), path,
                             str(operation.get("summary") or operation.get("operationId") or ""))
            for parameter in [*shared, *operation.get("parameters", [])]:
                if isinstance(parameter, dict) and "$ref" not in parameter:
                    point.parameters.append(f"{parameter.get('name', '?')} in {parameter.get('in', '?')}"
                                            + (", required" if parameter.get("required") else ""))
                    if parameter.get("in") == "body":           # Swagger 2's body
                        point.request = schema_said(parameter.get("schema"))
                elif isinstance(parameter, dict):
                    point.parameters.append(str(parameter["$ref"]).rsplit("/", 1)[-1])
            if "requestBody" in operation:
                point.request = content_said(operation["requestBody"]) or "a body"
            for status, answer in (operation.get("responses") or {}).items():
                said = answer.get("description", "") if isinstance(answer, dict) else ""
                holds = content_said(answer)
                point.responses[str(status)] = f"{said}: {holds}" if said and holds else said or holds
            point.security = security_said(operation.get("security", held.get("security")))
            endpoints.append(point)
    ordered = sorted(endpoints, key=lambda e: e.line)
    for here, after in zip(ordered, ordered[1:]):
        here.end = max(here.line, after.line - 1)
    if ordered:
        ordered[-1].end = max(ordered[-1].line, len(text.splitlines()))
    return endpoints, ""


def scan(where: Path) -> tuple[list[Endpoint], list[tuple[str, str]]]:
    """Every endpoint of the descriptions under `where`, and each description not read, with why."""
    if where.is_file():
        files = [(where, where.name)]
    else:
        files = [(p, p.relative_to(where).as_posix()) for p in sorted(where.rglob("*"))
                 if p.is_file() and NAME_RE.match(p.name)
                 and not NOT_THE_PRODUCTS & set(p.relative_to(where).parts)]
    found: list[Endpoint] = []
    passed: list[tuple[str, str]] = []
    for file, name in files:
        endpoints, why = read(file, name)
        found += endpoints
        if why:
            passed.append((name, why))
    return found, passed


def render(endpoints: list[Endpoint], passed: list[tuple[str, str]]) -> str:
    out = []
    for e in endpoints:
        out.append(f"{e.file}:{e.line}  {e.name}" + (f"  · {e.summary}" if e.summary else ""))
        if e.parameters:
            out.append(f"    takes: {'; '.join(e.parameters)}")
        if e.request:
            out.append(f"    body: {e.request}")
        for status, said in e.responses.items():
            out.append(f"    {status}: {said}")
        if e.security:
            out.append(f"    asks: {e.security}")
    for name, why in passed:
        out.append(f"{name}: not read -- {why}")
    out.append(f"{len(endpoints)} endpoint(s)" + (f", {len(passed)} file(s) not read" if passed else ""))
    return "\n".join(out) + "\n"


SAMPLE = {
    "openapi": "3.0.3",
    "info": {"title": "Invoices", "version": "1"},
    "security": [{"cookie": []}],
    "paths": {
        "/invoices/{number}/pdf": {
            "parameters": [{"name": "number", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {
                "summary": "The invoice as a PDF",
                "responses": {
                    "200": {"description": "The PDF", "content": {"application/pdf": {"schema": {"type": "string"}}}},
                    "404": {"description": "No such invoice"},
                    "409": {"description": "A draft", "content": {"application/json": {
                        "schema": {"$ref": "#/components/schemas/Problem"}}}},
                },
            },
        },
        "/health": {"get": {"summary": "Health", "security": [], "responses": {"200": {"description": "OK"}}}},
        "/invoices": {"post": {
            "summary": "A new invoice",
            "requestBody": {"content": {"application/json": {"schema": {
                "type": "object", "properties": {"customer": {"type": "string"}, "lines": {
                    "type": "array", "items": {"$ref": "#/components/schemas/Line"}}}}}}},
            "responses": {"201": {"description": "Made", "content": {"application/json": {"schema": {
                "type": "array", "items": {"$ref": "#/components/schemas/Invoice"}}}}}},
        }},
    },
}


def run_selftest() -> int:
    bad: list[str] = []

    def check(label: str, holds: bool, detail: object) -> None:
        print(f"{'ok' if holds else 'FAILED'}  {label}")
        if not holds:
            bad.append(f"{label}: {detail!r}")

    with tempfile.TemporaryDirectory(prefix="specs-builder-api-") as tmp:
        root = Path(tmp) / "app"
        (root / "docs").mkdir(parents=True)
        (root / "docs/openapi.json").write_text(json.dumps(SAMPLE, indent=2), encoding="utf-8")
        (root / "docs/openapi.yaml").write_text("openapi: 3.0.3\n", encoding="utf-8")
        (root / "node_modules/x").mkdir(parents=True)
        (root / "node_modules/x/openapi.json").write_text(json.dumps(SAMPLE), encoding="utf-8")
        (root / "data.json").write_text('{"rows": [1, 2]}', encoding="utf-8")
        endpoints, passed = scan(root)
        named = {e.name: e for e in endpoints}
        text = (root / "docs/openapi.json").read_text(encoding="utf-8").splitlines()
        check("the three endpoints of the description are read, and none of a dependency's",
              sorted(named) == ["GET /health", "GET /invoices/{number}/pdf", "POST /invoices"], sorted(named))
        pdf = named.get("GET /invoices/{number}/pdf")
        check("an endpoint carries its line, its parameters, its answers and its security",
              pdf is not None and '"get"' in text[pdf.line - 1] and pdf.parameters == ["number in path, required"]
              and pdf.responses.get("409") == "A draft: Problem" and pdf.security == "cookie", pdf)
        health = named.get("GET /health")
        check("an endpoint that asks no security says so", health is not None and health.security == "none", health)
        made = named.get("POST /invoices")
        check("a body's fields, and a list of a named schema, are read",
              made is not None and made.request == "{customer, lines}"
              and made.responses.get("201") == "Made: a list of Invoice", made)
        check("an endpoint's lines end before the next one's",
              pdf is not None and made is not None and not (pdf.end >= made.line and pdf.line < made.line),
              (pdf, made))
        check("a YAML description is passed, with why, and a file of data is never opened",
              passed == [("docs/openapi.yaml", "written as YAML, which is not read here: ask for the JSON form")],
              passed)
        flat = Path(tmp) / "flat.json"
        flat.write_text(json.dumps(SAMPLE), encoding="utf-8")
        one, _ = scan(flat)
        check("a file named is read whatever its name, and on one line every endpoint is at line 1",
              len(one) == 3 and all(e.line == 1 for e in one), one)
    for message in bad:
        print("ERROR " + message)
    print(f"{'FAILED' if bad else 'PASSED'} -- {len(bad)} problem(s)")
    return 1 if bad else 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="List the endpoints an OpenAPI or Swagger description holds.")
    parser.add_argument("where", nargs="?", type=Path, help="a description, or a folder to search for them")
    parser.add_argument("--json", action="store_true", help="the endpoints as JSON, for a tool")
    parser.add_argument("--selftest", action="store_true", help="check this script")
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    if args.where is None or not args.where.exists():
        parser.error("a description or a folder that is there is required, unless --selftest is given")
    endpoints, passed = scan(args.where)
    if args.json:
        print(json.dumps({"endpoints": [asdict(e) | {"name": e.name} for e in endpoints],
                          "not read": [{"file": n, "why": w} for n, w in passed]}, indent=2, ensure_ascii=False))
    else:
        print(render(endpoints, passed), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
