"""What whoever builds from a specification asks of it, what the code carries of it, and what moved since."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from support import edit, loading, natural, SKILL


def _raised(act) -> Exception | None:
    try:
        act()
    except (KeyError, ValueError) as wrong:
        return wrong
    return None


def questions(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """What an agent that builds asks: every command the earlier form of this skill's specifications answered, answered here from the data
    and the prototypes, and the instructions it finds in the folder by itself."""
    import json
    from types import SimpleNamespace

    sys.path.insert(0, str(SKILL / "scripts"))
    import build
    import drawn
    import markup
    import folder
    import logic
    import model as modelling
    import query

    root = tmp / "asked"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")

    def fresh() -> modelling.Model:
        return modelling.Model(root, loading.load(root))

    def asked(command: str, ident: str | None = None, **more: object):
        said = {"id": ident, "json": False, "depth": 1, "rel": "", "evidence": False, "ui": False, "gherkin": False, "state": "",
                "variant": "", "since": None, "until": None, "target": None, "command": command, **more}
        args = SimpleNamespace(**said)
        return query.opened(model, args) if command == "open" else query.COMMANDS[command](model, args)

    def text(command: str, ident: str | None = None, **more: object) -> str:
        return asked(command, ident, **more).markdown()

    def refused(command: str, ident: str) -> str:
        try:
            asked(command, ident)
        except KeyError as wrong:
            return str(wrong)
        return ""

    def run(*words: str, cwd: Path = root) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(root / "app/spec.py"), *words], cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False)

    checks = []
    model = fresh()
    # the plan
    slices = model.slices()
    ids = [s["id"] for s in slices]
    wanted = [n.id for n in model.nodes.values() if n.kind == "requirement" and n.fields.get("priority") != "wont"]
    homes = [r for s in slices for r in s["new requirements"]]
    checks.append(("the plan is slices: the foundation, what no flow passes, then each flow, and each requirement completed in exactly one",
                   ids[:2] == ["foundation", "rest"] and {f"F{i}" for i in range(1, 6)} <= set(ids) and sorted(homes) == sorted(wanted)
                   and "R1" in model.slice("F1")["new requirements"] and "R4" in model.slice("F2")["new requirements"]
                   and "SC17" in model.slice("rest")["nodes"]))
    checks.append(("a slice names what it builds, what it uses from an earlier one, its rules, its criteria and what blocks it",
                   "B1" in model.slice("foundation")["nodes"] and "SC7" in model.slice("F2")["earlier"] and "B1" in model.slice("F2")["rules"]
                   and model.slice("F2")["criteria"] == sum(len(model.rows(r)) for r in model.slice("F2")["new requirements"]) > 0
                   and model.slice("F1")["blocked by"] == ["Q1"]))
    plan_said, over = text("plan"), asked("overview")
    checks.append(("the plan and the overview tell it, and the overview says what binds every slice and how to build",
                   "Blocked by: Q1" in plan_said and "Never build" in plan_said
                   and all(f"## {h}" in over.markdown() for h in ("Quality requirements", "Constraints", "Decisions", "Risks", "Users",
                                                                  "The slices, in the order to build them", "Where the look is", "How to build it"))
                   and over.data["name"] == "Voltline" and over.data["open questions"] == ["Q1"] and over.data["slices"][0]["id"] == "foundation"))
    # one piece of work
    of_screen, of_requirement = text("unit", "SC3"), text("unit", "R4")
    checks.append(("a unit takes a slice or a node, and holds what it needs: rows, rules, who may, what is not settled, where it shows and its look",
                   "F1 Buy a product" in text("unit", "F1", budget=0) and "B1" in text("unit", "foundation") and "SC17" in text("unit", "rest")
                   and "Add to cart" in of_screen and "prototypes/screens/SC3.html" in of_screen and "up to five" in of_requirement
                   and "## Who may" in of_requirement and "U1 visitor" in of_requirement and "⚠ Not settled" in of_requirement
                   and "## Where it shows" in of_requirement and "SC3.13" in of_requirement))
    shown_later = [(r, s["id"]) for s in slices for r in s["new requirements"]
                   if any(model.top(x) in {n for later in slices[slices.index(s) + 1:] for n in later["new"]} for x in model.into(r, "shows"))]
    checks.append((f"a requirement is completed once all that shows it is built, and not before a flow names it{': ' + str(shown_later) if shown_later else ''}",
                   not shown_later))
    told_once = text("unit", "foundation", budget=0)
    checks.append(("the foundation's unit leaves out what the overview says, and look what node says",
                   "Y1 " not in told_once.split("What holds over the whole product")[1].split("##")[1] and "**D1" not in told_once
                   and "Foundation:" not in text("look", "SC3")))
    checks.append(("a unit leaves the evidence out unless it is asked for",
                   "E13" not in of_screen and "E13 " not in of_requirement and "moves as seen in" not in text("unit", "N1")
                   and "The evidence behind it" in text("unit", "R4", evidence=True)
                   and not [x for x in asked("unit", "R4").data["back"] if x["kind"] == "finding"]))
    cut = asked("unit", "foundation").markdown(1500)
    checks.append(("an answer stays within its budget, says what it left out and how to ask for it; JSON holds it all",
                   len(cut) < 4000 and "Left out, to keep this answer within its budget" in cut and "`node " in cut
                   and "foundation" in asked("unit", "foundation").json()))
    # the tests
    of_flow, of_rule = text("tests", "F2"), text("tests", "B1")
    checks.append(("tests take a slice, a requirement, a screen, a rule, an entity or all, with the rules and transitions, and name where a carried requirement is tested",
                   "`R4.1`" in of_flow and "Carried on" in of_flow and "`B1`" in of_flow and "R4.2" in text("tests", "SC3") and "R4.1" in of_rule
                   and "`N1` in -- the stock falls" in text("tests", "N1") and "R16." in text("tests", "all")))
    of_gherkin = text("tests", "R4", gherkin=True)
    of_ui = text("tests", "SC3", ui=True)
    checks.append(("tests read as features, and as what a test of a screen checks, the fields' boundaries among it",
                   "Feature: R4 Add a product to the cart" in of_gherkin and "Scenario: R4.1" in of_gherkin and "Given " in of_gherkin
                   and 'shows "Add to cart"' in of_ui and "1 and 5 are taken; one step outside each is refused" in of_ui
                   and "no screen in it" in str(_raised(lambda: asked("tests", "B1", ui=True)))))
    # what is drawn
    seen = text("look", "SC3")
    checks.append(("look names each element's selector, the components, where to see it drawn, and refuses what is not drawn",
                   '[data-el="13"]' in seen and "C1 Primary button" in seen and "/prototype/SC3.html" in seen and "prototypes/tokens.json" in seen
                   and "[data-part=" in text("look", "C9") and "is a requirement" in refused("look", "R4")))
    normal, out_of_stock, signed_in = text("outline", "SC3"), text("outline", "SC3", state="out-of-stock"), text("outline", "SC3", variant="signed-in")
    checks.append(("outline is the prototype as a tree, and shows what a state or a variant shows",
                   "SC3.13 Add to cart" in normal and "C9.7" in normal and "not as signed-in" in normal and "SC3.14" in out_of_stock
                   and "SC3.14" not in text("outline", "SC3", state="few-left") and "C9.7" in signed_in and "C9.4" not in signed_in
                   and "goes to SC1;" not in normal and "goes to SC5 ?state=empty" in normal))
    reader = markup.Reader()
    reader.feed('<main><p>Please ring <a href="tel:1">01632 960123</a>.</p><ul><li>one</li><li>two</li></ul></main>')
    sentence = reader.root.children[0]
    (root / "prototypes/screens/SC17.html").write_text((root / "prototypes/screens/SC17.html").read_text(encoding="utf-8").replace("</main>", '<p role="alert">Please ring <a href="tel:1">01632 960123</a>.</p></main>'), encoding="utf-8", newline="\n")
    whole_line = [w["words"] for w in drawn.words_of(drawn.page_of(model, "SC17"))]
    checks.append(("words are spaced as a browser spaces them, and a sentence with a link in it stays one sentence",
                   sentence.children[0].text() == "Please ring 01632 960123." and sentence.children[1].text() == "one two"
                   and "Please ring 01632 960123." in whole_line))
    checks.append(("forms says what the requirements say of the fields, whole, where a limit may be kept alone",
                   "What R4 Add a product to the cart says of them" in text("forms", "SC3") and "`R4.2`" in text("forms", "SC3")
                   and "up to five of each product" in text("forms", "SC3") and "R4.2" in asked("forms", "SC3").data["requirements"]["R4"]["criteria"]))
    checks.append(("words, forms and links read the prototype: its copy, its fields and their limits, where it leads and what leads to it",
                   "Add to cart" in text("words", "SC3") and "Tell me when it is back" in text("words", "SC3") and "max 5" in text("forms", "SC3")
                   and "Full name" in text("forms", "SC6") and "required" in text("forms", "SC6") and "SC1 The home page" in text("links", "SC3")
                   and "Led to from" in text("links", "SC5")))
    of_states, of_styles = text("states", "SC3"), text("styles", "SC3.13")
    checks.append(("states says what each changes and how to open it, and styles resolves values as a browser would, tokens and inherited ones too",
                   "?state=out-of-stock" in of_states and "Out of stock" in of_states and "?as=signed-in" in of_states and "#2563eb" in of_styles
                   and "var(--color-brand)" in of_styles and "--color-surface" in of_styles and "When :hover" in of_styles
                   and "from .vl-page" in of_styles and "SC3.13" in text("styles", "SC3") and ".vl-btn" in text("styles", ".vl-btn")))
    of_tokens = asked("tokens")
    checks.append(("tokens give what the page links as CSS, which no file holds, and look says so",
                   ":root {" in of_tokens.markdown() and of_tokens.data["tokens"] and "--color-brand" in of_tokens.data["css"]
                   and "`spec.py tokens`" in seen))
    helped_one = run("coverage", "--help")
    checks.append(("a command's --help is its row of the guide, and coverage says it reads names",
                   helped_one.returncode == 0 and "It reads names" in helped_one.stdout and len(helped_one.stdout) < 1000))
    checks.append(("sample reads the sample data, and messages what the product says beyond the normal, its endpoints' failures too",
                   asked("sample").data["values"]["SAMPLE"]["mostOfOne"] == 5 and "Nothing matches." in text("messages")
                   and asked("messages").data["endpoints"]))
    # what it means
    schema = asked("schema", "N1").data["schemas"]["N1"]
    moves = asked("lifecycle", "N1").data
    checks.append(("schema and lifecycle are read from the entity, a type never added, and lifecycle draws its moves",
                   {"price", "old price", "slug"} <= set(schema["properties"]) and schema["x-states"] == ["in", "low", "out"]
                   and "type" not in schema["properties"]["slug"] and len(moves["lifecycle"]) == 4 and "stateDiagram-v2" in text("lifecycle", "N1")
                   and "no entity" in refused("lifecycle", "R4")))
    may = asked("permissions").data["may"]
    checks.append(("permissions, rules, glossary and qualities say who may, what holds, the words and the numbers",
                   may["R6 place an order"] == {"U1": "no", "U2": "yes", "U3": "yes"} and may["R11 delete another customer's account"]["U3"] == "?"
                   and "Made true by: R4 " in text("rules", "B1") and "A deal holds" in text("rules") and "## Terms" in text("glossary")
                   and "## Qualities" in text("qualities")))
    api_of = asked("openapi").data["openapi"]
    checks.append(("openapi is written from the endpoints, each operation naming what it carries",
                   api_of["openapi"].startswith("3.") and api_of["paths"]["/api/v1/products"]["get"]["operationId"] == "A1"
                   and "R1" in api_of["paths"]["/api/v1/products"]["get"]["x-requirements"]
                   and any(p["name"] == "category" and p["in"] == "query" for p in api_of["paths"]["/api/v1/products"]["get"]["parameters"])))
    # finding one's way
    near = refused("unit", "R999")
    checks.append(("an ID it does not know is answered with the nearest, and a kind with the kinds",
                   "the nearest are" in near and "R9" in near and "the kinds are" in refused("list", "nothing")))
    checks.append(("node reaches as far as it is asked, edges take a relation, list every kind, and find reads every node without accents",
                   len(asked("node", "R4", depth=2).data["around"]) > len(asked("node", "R4").data["around"])
                   and asked("edges", "B1", rel="enforces").data["in"] and not asked("edges", "B1", rel="enforces").data["out"]
                   and "criterion" in text("list", "kinds") and "R4 " in text("list", "requirement") and "B1 " in text("find", "at most five")
                   and "Karl-Liebknecht" in text("find", "strasse") + text("find", "Karl-Liebknecht")))
    of_open = asked("open", "F1")
    checks.append(("open takes a slice or a node, says what it blocks, and exits 1 while it lists anything; open alone stays the keeper's",
                   of_open.exit == 1 and "Q1" in of_open.markdown() and "Blocks: " in of_open.markdown() and asked("open", "FD1").exit == 0
                   and "open question(s), the most deciding first" in run("open").stdout and run("open").returncode == 1))
    # the command line itself
    bare = tmp / "no-database"
    shutil.copytree(root, bare, ignore=shutil.ignore_patterns(".cache"))
    told = subprocess.run([sys.executable, "-B", "app/spec.py", "node", "R4"], cwd=bare, capture_output=True, text=True, encoding="utf-8", check=False)
    words_apart = run("find", "at", "most", "five")
    away = run("overview", "--json", cwd=tmp)
    checks.append(("node answers from a fresh clone, words a shell splits are one question, and it answers from anywhere as JSON",
                   told.returncode == 0 and "R4 Add a product" in told.stdout and "B1 " in words_apart.stdout
                   and json.loads(away.stdout)["name"] == "Voltline"))
    logic.apply(root, [logic.parse('set R4 statement "When a visitor selects Add to cart on a product in stock, the shop shall add it to their cart, one to six."')])
    warned = run("unit", "R4").stdout
    checks.append(("every answer says first what is stale", "stale" in warned[:300] and "Say so before building" in warned))
    code = tmp / "built-code"
    code.mkdir()
    model = fresh()
    build.snapshot(root, code)
    old = build.snapshots(code)[0]
    held = json.loads(old.read_text(encoding="utf-8"))
    checks.append(("a snapshot keeps what the prototypes draw, element by element, with the styles, tokens and sample data",
                   "SC3.13" in {e.get("handle") for e in held["drawn"]["screens"]["SC3"]["elements"]} and held["drawn"]["styles"]
                   and held["drawn"]["tokens"] and held["drawn"]["sample"]["SAMPLE"]["mostOfOne"] == 5))
    screen = root / "prototypes/screens/SC3.html"
    screen.write_text(screen.read_text(encoding="utf-8").replace(">Tell me when it is back<", ">Tell me when it returns<"), encoding="utf-8", newline="\n")
    sample = root / "prototypes/assets/js/sample.js"
    sample.write_text(sample.read_text(encoding="utf-8").replace("mostOfOne: 5", "mostOfOne: 6"), encoding="utf-8", newline="\n")
    tokens = root / "prototypes/tokens.json"
    first_value = re.search(r'"hex": "(#[0-9a-fA-F]+)"|"\$value": "(#[0-9a-fA-F]+)"', tokens.read_text(encoding="utf-8"))
    was = first_value.group(1) or first_value.group(2)
    tokens.write_text(tokens.read_text(encoding="utf-8").replace(was, "#123456", 1), encoding="utf-8", newline="\n")
    sheet = root / "prototypes/assets/css/product.css"
    sheet.write_text(sheet.read_text(encoding="utf-8").replace(".vl-btn {", ".vl-btn {\n  outline-offset: 2px;", 1), encoding="utf-8", newline="\n")
    moved = build.changed(root, code)
    said = run("changed", "--target", str(code)).stdout
    checks.append(("changed tells what the prototypes draw, element by element, the styles, the tokens, the sample, and the slices and screens it reaches",
                   any(e.get("changed") and e["handle"] == "SC3.14" for e in moved["drawn"]["screens"]["SC3"]["elements"])
                   and any(s["property"] == "outline-offset" for s in moved["drawn"]["styles"]) and any(t[2] == "#123456" for t in moved["drawn"]["tokens"])
                   and any("mostOfOne" in t[0] for t in moved["drawn"]["sample"]) and "SC3" in moved["ui tests"] and "F1" in moved["slices"]
                   and moved["screens reached"] and "tell me when it returns" in said.lower() and "## Slices to build again" in said))
    build.snapshot(root, code)
    stamps = [p.stem.removeprefix("spec_") for p in build.snapshots(code)]
    between = build.changed(root, code, stamps[0], stamps[1])
    gone = json.loads(old.read_text(encoding="utf-8"))
    gone.pop("drawn")
    old.write_text(json.dumps(gone), encoding="utf-8")
    older = build.changed(root, code, stamps[0])
    checks.append(("changed compares two snapshots with --until, and takes one from before snapshots kept what is drawn",
                   between["until"] == stamps[1] and "SC3" in between["drawn"]["screens"] and older["drawn"] is None
                   and "prototypes/screens/SC3.html" in older["files"]["changed"]))
    wrote = run("export", "--model")
    place = root / "export/model"
    index = json.loads((place / "index.json").read_text(encoding="utf-8")) if (place / "index.json").is_file() else {}
    checks.append(("export --model writes the data for a program: every node, every link, the slices and the API",
                   wrote.returncode == 0 and len(index.get("nodes", [])) == len(list((place / "nodes").glob("*.json")))
                   and index.get("slices") and "R4\tenforces\tB1" in (place / "edges.tsv").read_text(encoding="utf-8")
                   and "SC3.13\tshows\tR4" in (place / "stands.tsv").read_text(encoding="utf-8")
                   and (place / "openapi.json").is_file() and json.loads((place / "nodes/R4.json").read_text(encoding="utf-8"))["kind"] == "requirement"))
    # many questions of data that stands still
    kept = tmp / "kept-load"
    shutil.copytree(clean, kept, ignore=shutil.ignore_patterns(".cache"))
    read = loading.load(kept)
    first_read, again = loading.held(kept), loading.held(kept)
    was_kept = (kept / loading.HELD).is_file()
    same = (list(again.nodes) == list(read.nodes) and {i: (n.kind, n.file, n.line, n.parent, n.fields) for i, n in again.nodes.items()}
            == {i: (n.kind, n.file, n.line, n.parent, n.fields) for i, n in read.nodes.items()} and again.edges == read.edges and not first_read.problems)
    edit(kept, "data/rules/B1.md", "at most five", "at most six")
    told_new = "six" in str(loading.held(kept).nodes["B1"].fields)
    (kept / loading.HELD).write_text("not what it was\n{", encoding="utf-8")
    edit(kept, "data/rules/B1.md", "at most six", "at most seven")
    mended = "seven" in str(loading.held(kept).nodes["B1"].fields)
    edit(kept, "data/rules/B1.md", "at most seven", "at most five")
    edit(kept, "data/requirements/R4.md", "serves: G2, G3", "serves: G99")
    wrong = bool(loading.held(kept).problems)
    edit(kept, "data/requirements/R4.md", "serves: G99", "serves: G2, G3")
    worked: list[int] = []

    def counted() -> int:
        worked.append(1)
        return len(worked)
    first_time, second_time = loading.remembered(loading.held(kept), "counted", counted), loading.remembered(loading.held(kept), "counted", counted)
    edit(kept, "data/rules/B1.md", "at most five", "at most four")
    third_time = loading.remembered(loading.held(kept), "counted", counted)
    checks.append(("what was loaded is kept while no file changes, whole; a change is read, a spoiled file is ignored, and data with a problem is never kept",
                   was_kept and same and told_new and mended and wrong))
    checks.append(("what takes long is kept the same way, and worked out again when a file changes", (first_time, second_time, third_time) == (1, 1, 2)))
    asked_two = run("ask", "Is this one question?", "--about", "R4", "SC3", "--by", "a test")
    checks.append(("ask takes its IDs by spaces as well as by commas",
                   asked_two.returncode == 0 and "SC3" in (root / "inbox.md").read_text(encoding="utf-8")))
    # what an agent finds by itself
    made = tmp / "agents-find"
    shutil.copytree(clean, made)
    (made / "AGENTS.md").write_text("# Our own notes\n", encoding="utf-8")
    folder.write_agents(made)
    (made / "AGENTS.md").write_text((made / "AGENTS.md").read_text(encoding="utf-8").replace("Follow `app/guide/build.md`", "An old line"), encoding="utf-8")
    folder.write_agents(made)
    kept = (made / "AGENTS.md").read_text(encoding="utf-8")
    block = (SKILL / "app/guide/AGENTS.md").read_text(encoding="utf-8").strip()
    checks.append(("a folder's instructions are written whole, the notes beside the block kept, and CLAUDE.md sends Claude Code to them",
                   block in kept and "# Our own notes" in kept and "An old line" not in kept and "@AGENTS.md" in (made / "CLAUDE.md").read_text(encoding="utf-8")))
    folders = [p / "specs" for p in sorted((SKILL / "examples").iterdir()) if (p / "specs/data").is_dir()]
    bare_folders = [p.parent.name for p in folders if block not in (p / "AGENTS.md").read_text(encoding="utf-8")] if all((p / "AGENTS.md").is_file() for p in folders) else ["some"]
    checks.append((f"every example carries the instructions{': ' + ', '.join(bare_folders) if bare_folders else ''}", not bare_folders))
    helped = subprocess.run([sys.executable, str(SKILL / "app/spec.py"), "--help"], capture_output=True, text=True, check=False).stdout
    known = set(re.search(r"\{([a-z,]+)\}", helped).group(1).split(","))
    first_skill = {"overview", "plan", "unit", "look", "tests", "open", "node", "edges", "list", "find", "trace", "coverage", "changed", "verify",
                   "export", "ask", "snapshot", "outline", "words", "forms", "links", "states", "styles", "sample", "messages", "schema",
                   "lifecycle", "permissions", "rules", "glossary", "qualities", "openapi"}
    guide = (SKILL / "app/guide/query.md").read_text(encoding="utf-8")
    forms = (SKILL / "app/guide/model.md").read_text(encoding="utf-8")
    g = loading.grammar()
    checks.append(("every command the earlier query tool had is here, the guide says each, and the data's guide every kind and link",
                   first_skill <= known and len(first_skill) == 32 and all(f"`{c}" in guide for c in first_skill)
                   and all(f"| {k} |" in forms for k in g["kinds"]) and all(f"| {r} |" in forms for r in g["relations"])))
    return checks


def carried(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """What a builder asks, answered from a copy of the example; a snapshot taken, the data changed, and told."""
    import build
    import logic

    root = tmp / "built-from"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")    # changed: an agreed one takes none
    code = tmp / "the-code"
    checks = []
    o = build.overview(root)
    checks.append(("the overview names the product and counts what it holds",
                   o["name"] == "Voltline" and o["counts"].get("requirement") == 16 and o["open questions"] == ["Q1"]))
    checks.append(("a specification with nothing stale may be built from", build.verify(root)[0]))
    logic.apply(root, [logic.parse("tie R1 depends on R16")])
    import model as modelling
    in_order = modelling.Model(root, loading.load(root))
    order = in_order.order()
    home = {r: at for at, s in enumerate(in_order.slices()) for r in s["new requirements"]}
    built = sorted((i for i, n in loading.load(root).nodes.items()
                    if n.kind == "requirement" and n.fields.get("priority") != "wont"), key=natural)
    checks.append(("the plan starts with the foundation and builds a requirement after what it depends on, "
                   "and none it will not",
                   build.plan(root)[0]["id"] == "foundation" and order.index("R16") < order.index("R1") and home["R16"] <= home["R1"]
                   and sorted(order, key=natural) == built and len(built) == 15))
    u = build.unit(root, "R4")
    checks.append(("a unit holds its criteria, what it enforces with what that says, what shows it, its questions",
                   [r["id"] for r in u["rows"]] == ["R4.1", "R4.2", "R4.3", "R4.4"]
                   and any(l["id"] == "B1" and "five" in l["says"] for l in u["links"])
                   and any(l["id"] == "SC3.13" and l["rel"] == "shown by" for l in u["back"])
                   and [q["id"] for q in u["questions"]] == ["Q1"]))
    found = build.tests(root, "R4")
    scenario = build.gherkin(found[0])
    checks.append(("a requirement's criteria are its tests, and read as scenarios",
                   [t["id"] for t in found] == ["R4.1", "R4.2", "R4.3", "R4.4"]
                   and scenario.startswith("Scenario: R4.1\n  Given ") and "\n  When " in scenario and "\n  Then " in scenario))
    # what the code carries: read from the names in it, criterion by criterion
    try:
        build.coverage(root)
        checks.append(("coverage with no code known says so", False))
    except FileNotFoundError as wrong:
        checks.append(("coverage with no code known says so", "no code is known" in str(wrong)))
    for name, text in (("tests/test_cart.py", "def test_R4_1_adds(): pass\ndef test_R4_2(): pass\ndef test_R99(): pass\n"
                                              "def test_R5_only_the_requirement(): pass\n"),
                       ("src/Shop.Tests/Browse.cs", "// R1.1\n"), ("src/app/CartTests.cs", "// R6.1\n"),
                       ("src/app/latest.py", "# carries R2\nname = 'R2D2 R7x'\n"), ("node_modules/lib/test.js", "// R8.1\n"),
                       ("features/search.feature", scenario.replace("R4.1", "R3.1"))):
        (code / name).parent.mkdir(parents=True, exist_ok=True)
        (code / name).write_text(text, encoding="utf-8")
    cover = build.coverage(root, code)
    held = {r["id"]: r for r in cover["requirements"]}
    inside = shutil.copytree(root, code / "the-spec", ignore=shutil.ignore_patterns(".cache", "__pycache__"))
    (inside / "tests").mkdir()
    (inside / "tests" / "test_own.py").write_text("# R10.1\n", encoding="utf-8")
    of_inside = build.coverage(inside, code)
    shutil.rmtree(inside)
    checks.append(("coverage counts a requirement by the criteria its tests name, not by being named, and tells tests "
                   "by their place and their name",
                   [c["id"] for c in held["R4"]["criteria"] if c["tests"]] == ["R4.1", "R4.2"]
                   and held["R4"]["untested"] == ["R4.3", "R4.4"] and held["R5"]["tests"] == ["tests/test_cart.py"]
                   and len(held["R5"]["untested"]) == len(held["R5"]["criteria"])
                   and held["R1"]["tests"] == ["src/Shop.Tests/Browse.cs"] and held["R6"]["tests"] == ["src/app/CartTests.cs"]
                   and held["R2"]["code"] == ["src/app/latest.py"] and not held["R2"]["tests"]
                   and held["R3"]["tests"] == ["features/search.feature"] and "R5" not in cover["no test"]
                   and "R2" in cover["no test"]))
    checks.append(("coverage leaves out what is not the product's, and the specification's own folder, says what the "
                   "code names that the specification has not, and is not whole while a must has a criterion untested",
                   not held["R8"]["tests"] and "R7" not in {r for r, h in held.items() if h["code"]}
                   and [u["id"] for u in cover["unknown"]] == ["R99"] and not cover["whole"] and "R15" not in cover["no test"]
                   and "the-spec" not in str(of_inside["requirements"]) and of_inside["code read"] == cover["code read"]))
    checks.append(("the application says so where no code is known", "none" in build.built(root)))
    try:
        build.coverage(root, root)
        checks.append(("coverage refuses the specification's own folder as its code", False))
    except FileNotFoundError as wrong:
        checks.append(("coverage refuses the specification's own folder as its code", "is the specification itself" in str(wrong)))
    try:
        build.changed(root, code)
        checks.append(("changed with no snapshot says so", False))
    except FileNotFoundError as wrong:
        checks.append(("changed with no snapshot says so", "no snapshot" in str(wrong)))
    build.snapshot(root, code)
    checks.append(("a snapshot leaves where the code is, for coverage and the application to need no telling",
                   build.coverage(root)["requirements"][3]["tests"] == ["tests/test_cart.py"]
                   and build.named(root, "R4.1")["tests"] == ["tests/test_cart.py"] and "none" not in build.built(root)))
    logic.apply(root, [logic.parse('set R4 statement "When a visitor selects Add to cart on a product in stock, the '
                                   'shop shall add it to their cart, one to six."'), logic.parse("remove R4.4")])
    (root / "prototypes/assets/img/new-badge.svg").write_text("<svg/>", encoding="utf-8")
    c = build.changed(root, code)
    ids = {x["id"]: x["change"] for x in c["changes"]}
    checks.append(("changed tells each node new, gone or changed since the snapshot",
                   ids.get("R4") == "changed" and ids.get("R4.4") == "removed"))
    checks.append(("changed tells every file of the prototypes, an image too",
                   "prototypes/assets/img/new-badge.svg" in c["files"]["new"]))
    checks.append(("changed says what to build again and the tests to take out",
                   "R4" in c["build again"].get("requirements", []) and "SC3" in c["build again"].get("screens", [])
                   and c["tests to remove"] == ["R4.4"]))
    checks.append(("a change makes the specification not ready to build from until it is reviewed",
                   not build.verify(root)[0]))
    for _ in range(3):
        build.snapshot(root, code)
    checks.append(("snapshots kept in the code, the newest three", len(build.snapshots(code)) == 3))
    return checks


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    return questions(tmp, clean) + carried(tmp, clean)
