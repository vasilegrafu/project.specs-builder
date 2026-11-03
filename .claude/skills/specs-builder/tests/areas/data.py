"""The data: the example loads clean, each fault planted in a copy is told at its file and line, the database, what a node means."""
from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

from support import add, edit, loading, remove


# Each seed: what it plants, the change, and the problem expected -- its file, where in it (a line's number, 0 for
# none, or words on the line, found in the file as planted), and words in the problem.
R4, B1, SC3, C1 = "data/requirements/R4.md", "data/rules/B1.md", "data/screens/SC3.md", "data/components/C1.md"
SEEDS = [
    ("an unknown key in a header",
     lambda r: edit(r, R4, "priority: must\n", "priority: must\nowner: U1\n"), (R4, "owner: U1", "`owner:` is no field of a requirement")),
    ("a misspelled link key, read as nothing in the old form",
     lambda r: edit(r, R4, "serves: G2, G3", "serve: G2, G3"), (R4, "serve: G2", "`serve:` is no field")),
    ("a link to an ID that is not there",
     lambda r: edit(r, R4, "enforces: B1, B5", "enforces: B1, B99"), (R4, "enforces:", "B99 is not defined")),
    ("a link to a node of the wrong kind",
     lambda r: edit(r, R4, "serves: G2, G3", "serves: G2, R3"), (R4, "serves:", "and R3 is a requirement")),
    ("a link that is not an ID",
     lambda r: edit(r, R4, "serves: G2, G3", "serves: G2, the conversion goal"), (R4, "serves:", "is not an ID")),
    ("a link said twice",
     lambda r: edit(r, R4, "serves: G2, G3", "serves: G2, G2"), (R4, "serves:", "is said twice")),
    ("a requirement that serves no goal",
     lambda r: edit(r, R4, "serves: G2, G3\n", ""), (R4, "id: R4", "R4 serves nothing")),
    ("a requirement with no criterion",
     lambda r: edit(r, R4, "## Accepted when", "## Except"), (R4, "id: R4", "R4 has nothing")),
    ("a line in a list section that is no item",
     lambda r: edit(r, R4, "- R4.1 ", "R4.1 "), (R4, "R4.1 Given", "holds only its list")),
    ("a criterion under the wrong requirement",
     lambda r: edit(r, R4, "- R4.3 ", "- R5.3 "), (R4, "- R5.3", "R5.3 is not R4's")),
    ("a criterion defined twice",
     lambda r: edit(r, R4, "- R4.3 ", "- R4.2 "), (R4, "R4.2 Given a product out of stock", "R4.2 is defined twice")),
    ("a value outside its choices",
     lambda r: edit(r, R4, "priority: must", "priority: urgent"), (R4, "priority: urgent", "`priority: urgent` is not one of")),
    ("a required field missing",
     lambda r: edit(r, R4, "name: Add a product to the cart\n", ""), (R4, "id: R4", "R4 has no `name:`")),
    ("a statement that says nothing the product shall do",
     lambda r: edit(r, R4, "the shop shall add", "the shop adds"), (R4, "the shop adds", "says what the product `shall` do")),
    ("a section the kind does not have",
     lambda r: edit(r, R4, "## Accepted when", "## Notes\n\nsee R5\n\n## Accepted when"),
     (R4, "## Notes", "`## Notes` is no section of a requirement")),
    ("a `# ` heading in place of the name",
     lambda r: edit(r, B1, "A cart holds at most five", "# Up to five\n\nA cart holds at most five"),
     (B1, "# Up to five", "not a `# ` heading")),
    ("a key said twice",
     lambda r: edit(r, B1, "name: Up to five of a product\n", "name: Up to five of a product\nname: Five at most\n"),
     (B1, "name: Five at most", "`name` is said twice")),
    ("a header never closed",
     lambda r: add(r, "data/goals/G9.md", "---\nid: G9\nname: Open-ended\n"), ("data/goals/G9.md", 1, "the header is never closed")),
    ("an ID that does not match its file",
     lambda r: edit(r, "data/goals/G3.md", "id: G3", "id: G7"), ("data/goals/G3.md", "id: G7", "the file of G7 is named G7.md")),
    ("an ID of the wrong kind for its folder",
     lambda r: edit(r, "data/goals/G3.md", "id: G3", "id: R3"), ("data/goals/G3.md", "id: R3", "`R3` is no goal's ID")),
    ("a file where no node belongs",
     lambda r: add(r, "data/notes/todo.md", "---\nid: X1\n---\n"), ("data/notes/todo.md", 0, "not a node's file")),
    ("a self-link",
     lambda r: edit(r, "data/requirements/R5.md", "serves:", "depends on: R5\nserves:"),
     ("data/requirements/R5.md", "depends on: R5", "R5 depends on itself")),
    ("a cycle across two requirements",
     lambda r: (edit(r, "data/requirements/R5.md", "serves:", "depends on: R6\nserves:"),
                edit(r, "data/requirements/R6.md", "serves:", "depends on: R5\nserves:")),
     ("data/requirements/R5.md", "depends on: R6", "R5 depends on R6 depends on R5: a cycle")),
    ("an action that is not `yes`, `no` or `?`",
     lambda r: edit(r, "data/roles/U1.md", "- yes: R1 browse", "- maybe: R1 browse"),
     ("data/roles/U1.md", "- maybe: R1", "each action is `- yes: R1")),
    ("an action about a goal",
     lambda r: edit(r, "data/roles/U1.md", "- yes: R1 browse", "- yes: G1 browse"), ("data/roles/U1.md", "- yes: G1", "and G1 is a goal")),
    # tables, and rows that are nodes of their own
    ("a row a cell short",
     lambda r: edit(r, SC3, "| 8 | The SKU | text |", "| 8 | The SKU |"), (SC3, "| 8 | The SKU", "this row has 10 cells")),
    ("a table with columns its kind does not have",
     lambda r: edit(r, SC3, "| Asks | Leads to |\n", "| Asks | Goes to |\n"), (SC3, "| # | Element", "has the columns")),
    ("an element that shows a goal",
     lambda r: edit(r, SC3, "| C4 | R2 |", "| C4 | G1 |"), (SC3, "| 9 | The price", "and G1 is a goal")),
    ("an element that is two components",
     lambda r: edit(r, SC3, "| C4 | R2 |", "| C4, C5 | R2 |"), (SC3, "| 9 | The price", "no more than 1")),
    ("a line in a table's section that is not the table",
     lambda r: edit(r, C1, "a product out of stock |\n", "a product out of stock |\nand more\n"), (C1, "and more", "holds only its table")),
    # the prototypes, held to the data both ways
    ("an anchor in the markup with no row",
     lambda r: edit(r, "prototypes/screens/SC3.html", 'data-el="9"', 'data-el="99"'),
     ("prototypes/screens/SC3.html", 'data-el="99"', '`data-el="99"` has no row')),
    ("a row drawn nowhere in the markup",
     lambda r: edit(r, "prototypes/screens/SC3.html", ' data-el="9"', ""), (SC3, "| 9 | The price", "SC3.9 is drawn nowhere")),
    ("a link written in the markup, as it was before",
     lambda r: edit(r, "prototypes/screens/SC3.html", 'data-el="9"', 'data-el="9" data-spec-req="R2"'),
     ("prototypes/screens/SC3.html", "data-spec-req", "`data-spec-req` in the markup")),
    ("a part the markup names that no component has",
     lambda r: edit(r, "prototypes/screens/SC3.html", 'data-part="C9.1"', 'data-part="C9.99"'),
     ("prototypes/screens/SC3.html", 'data-part="C9.99"', "names no part")),
    ("a variant drawn nowhere",
     lambda r: edit(r, "prototypes/components/C1.html", 'data-variant="disabled"', 'data-variant="off"'),
     (C1, "| disabled |", "variant `disabled` is drawn nowhere")),
    ("a screen with no prototype",
     lambda r: remove(r, "prototypes/screens/SC17.html"), ("data/screens/SC17.md", "id: SC17", "SC17 has no prototype")),
    ("a prototype of no screen",
     lambda r: add(r, "prototypes/screens/SC99.html", "<main></main>\n"), ("prototypes/screens/SC99.html", 0, "a prototype of no screen")),
    ("a page shell without its body's place",
     lambda r: edit(r, "prototypes/page.html", "{{body}}", ""), ("prototypes/page.html", 0, "holds {{body}} 0 times")),
    # the kinds the earlier form held, now nodes of their own
    ("an endpoint with no surface",
     lambda r: edit(r, "data/endpoints/A1.md", "surface: GET /api/v1/products\n", ""),
     ("data/endpoints/A1.md", "id: A1", "A1 has no `surface:`")),
    ("a finding read in no source there is",
     lambda r: edit(r, "data/findings/E1.md", "source: S1", "source: S9"), ("data/findings/E1.md", "source: S9", "S9 is not defined")),
    ("a state that moves to one its entity does not have",
     lambda r: edit(r, "data/entities/N2.md", "| empty |  | N2.open |", "| empty |  | N2.gone |"),
     ("data/entities/N2.md", "| empty |  | N2.gone", "N2.gone is not defined")),
    ("a document that says nothing",
     lambda r: edit(r, "data/document.md", "Voltline is a small electronics shop", "## More\n\nVoltline is a small electronics shop"),
     ("data/document.md", 1, "says nothing in its text")),
]


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    done = loading.load(clean)
    checks = [(f"the shop example loads clean: {len(done.nodes)} nodes, {len(done.edges)} links" + (f" -- {done.problems[:3]}" if done.problems else ""),
               not done.problems)]
    for at, (title, plant, (file, line, words)) in enumerate(SEEDS):
        root = tmp / f"seed{at}"
        shutil.copytree(clean, root)
        plant(root)
        found = loading.load(root).problems
        if isinstance(line, str):           # the line that holds those words, as the file now stands
            held = (root / file).read_text(encoding="utf-8").splitlines()
            line = next((i + 1 for i, text in enumerate(held) if line in text), -1)
        hit = [p for p in found if p[0] == file and p[1] == line and words in p[2]]
        checks.append((title + ("" if hit else f": expected {file}:{line} with {words!r}; got {found[:3]}"), bool(hit)))

    # the database: built whole, its joins held by a trigger, its old copy kept when a load fails
    database = loading.build(done)
    con = sqlite3.connect(database)
    con.execute("PRAGMA foreign_keys = ON")
    counts = (con.execute("SELECT count(*) FROM nodes").fetchone()[0],
              con.execute("SELECT count(*) FROM edges").fetchone()[0])
    checks.append(("the database holds every node and link", counts == (len(done.nodes), len(done.edges))))
    try:
        con.execute("INSERT INTO edges VALUES ('R4', 'serves', 'R3', 'x', 1)")
        checks.append(("the database refuses a join the grammar does not allow", False))
    except sqlite3.DatabaseError:
        checks.append(("the database refuses a join the grammar does not allow", True))
    try:
        con.execute("INSERT INTO edges VALUES ('R4', 'serves', 'G99', 'x', 1)")
        checks.append(("the database refuses a link to a node that is not there", False))
    except sqlite3.DatabaseError:
        checks.append(("the database refuses a link to a node that is not there", True))
    con.close()
    checks.append(("a build leaves no half-written file", not database.with_name(database.name + ".new").exists()))
    before = database.stat().st_mtime_ns
    broken = loading.load(tmp / "seed2")
    try:
        loading.build(broken, database)
        checks.append(("a load with problems builds nothing", False))
    except ValueError:
        checks.append(("a load with problems builds nothing, and the last database stays",
                       database.stat().st_mtime_ns == before))

    # what a node means: spacing is no change, wording is
    g = loading.grammar()
    r4 = done.nodes["R4"]
    same = loading.Node(r4.id, r4.kind, r4.file, r4.line,
                        {**r4.fields, "statement": "  " + str(r4.fields["statement"]).replace(" ", "   ")})
    moved = loading.Node(r4.id, r4.kind, r4.file, r4.line,
                         {**r4.fields, "statement": str(r4.fields["statement"]).replace("one to five", "one to six")})
    checks.append(("a change of spacing leaves the fingerprint", loading.fingerprint(g, same) == loading.fingerprint(g, r4)))
    checks.append(("a change of wording moves the fingerprint", loading.fingerprint(g, moved) != loading.fingerprint(g, r4)))
    # a table's rows by what they say: moved down its file it is the same, its words changed it is not
    shifted = tmp / "shifted"
    shutil.copytree(clean, shifted)
    edit(shifted, "data/components/C1.md", "## Variants", "\n\n## Variants")
    worded = tmp / "worded"
    shutil.copytree(clean, worded)
    edit(worded, "data/components/C1.md", "a darker blue", "a darker green")
    c1 = loading.fingerprint(g, done.nodes["C1"])
    checks.append(("a table moved down its file leaves the fingerprint", loading.fingerprint(g, loading.load(shifted).nodes["C1"]) == c1))
    checks.append(("a table's words changed move the fingerprint", loading.fingerprint(g, loading.load(worded).nodes["C1"]) != c1))
    return checks
