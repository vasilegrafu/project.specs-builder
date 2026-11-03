"""What the tests of specs-builder share: where things are, the small edits that plant a fault, and how a test file is
loaded so that a check that fails says which of its conditions did.

A check is a title and a truth, `checks.append(("the plan starts with the foundation", a and b and c))`. Loaded from here,
each `and` of such a truth is watched: the check that fails names the condition that failed, with no change to the test.
"""
from __future__ import annotations

import ast
import sys
import types
from pathlib import Path

sys.dont_write_bytecode = True
TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
sys.path.insert(0, str(SKILL / "app"))
sys.path.insert(0, str(SKILL / "scripts"))
import load as loading  # noqa: E402

EXAMPLE = SKILL / "examples" / "shop" / "specs"


natural = loading.natural


STYLES = ("style.css", "maps.css", "prototype.css", "views.css")
ENGINE = ("engine.js", "evidence.js", "prototype.js")


def web_text(names: tuple[str, ...]) -> str:
    """What the application loads as one, in its order: a rule or a function is held wherever of these it stands."""
    return "\n".join((SKILL / "app/web" / name).read_text(encoding="utf-8") for name in names)


def edit(root: Path, name: str, old: str, new: str) -> None:
    path = root / name
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise AssertionError(f"the seed for {name} expects one {old!r}, and finds {text.count(old)}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


def remove(root: Path, name: str) -> None:
    (root / name).unlink()


def add(root: Path, name: str, text: str) -> None:
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(text, encoding="utf-8", newline="\n")


WISH = ('add requirement "Keep a wish list" priority=should serves=G2 statement="When a customer selects Save, '
        'the shop shall keep the product in their wish list."')


WISH_TEST = 'add-row $1 says="Given a signed-in customer on a product, when Save is selected, then it is kept."'


class Held:
    """A check's truth: false when a condition failed, and which."""

    def __init__(self, failed: str = "") -> None:
        self.failed = failed

    def __bool__(self) -> bool:
        return not self.failed


def all_of(*conditions: tuple) -> Held:
    """Each condition in turn, as `and` would, stopping at the first that fails."""
    for said, holds in conditions:
        if not holds():
            return Held(said)
    return Held()


class Watched(ast.NodeTransformer):
    """A check's `a and b and c` written as `all_of(("a", lambda: a), ...)`, in the file as it is loaded."""

    def __init__(self, source: str) -> None:
        self.source = source

    def watch(self, pair: ast.expr) -> None:
        if not (isinstance(pair, ast.Tuple) and len(pair.elts) == 2 and isinstance(pair.elts[1], ast.BoolOp) and isinstance(pair.elts[1].op, ast.And)):
            return
        truth = pair.elts[1]
        if any(isinstance(n, ast.NamedExpr) for n in ast.walk(truth)):      # a name bound in one and read in the next
            return
        no_args = ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[])
        conditions = [ast.Tuple([ast.Constant(" ".join(ast.get_source_segment(self.source, c).split())), ast.Lambda(no_args, c)], ast.Load())
                      for c in truth.values]
        pair.elts[1] = ast.copy_location(ast.Call(ast.Name("all_of", ast.Load()), conditions, []), truth)
        ast.fix_missing_locations(pair)

    def visit_Call(self, node: ast.Call) -> ast.Call:
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "append" and len(node.args) == 1:
            self.watch(node.args[0])
        return node

    def visit_Return(self, node: ast.Return) -> ast.Return:
        self.generic_visit(node)
        if isinstance(node.value, ast.List):
            for pair in node.value.elts:
                self.watch(pair)
        return node


def watched(name: str, source: str, path: Path) -> types.ModuleType:
    """A file of tests, loaded with each check's conditions watched."""
    module = types.ModuleType(f"areas.{name}")
    module.__file__ = str(path)
    module.__dict__["all_of"] = all_of
    exec(compile(Watched(source).visit(ast.parse(source)), path, "exec"), module.__dict__)
    return module


def area(name: str) -> types.ModuleType:
    """The tests of one area, from `tests/areas/<name>.py`."""
    path = TESTS / "areas" / f"{name}.py"
    return watched(name, path.read_text(encoding="utf-8"), path)

