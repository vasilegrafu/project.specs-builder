"""Reading material: staging files merged, what was read held to what it is now, the evidence served."""
from __future__ import annotations

import shutil
from pathlib import Path

from support import edit, loading, SKILL


def staging(root: Path, fault: str = "") -> Path:
    """An agent's staging file, as rules.md shapes it, with one fault planted where `fault` names it."""
    import json

    facets = json.loads((SKILL / "app/agents.json").read_text(encoding="utf-8"))["facets"]["web"]
    facets = facets[1:] if fault == "facet" else facets
    quote = "link: Cart 9 → /cart.html" if fault == "quote" else "link: Cart 2 → /cart.html"
    where = "x.csv" if fault == "data" else "V21-the-cart.md"
    lens = "touch" if fault == "lens" else "action"
    twin = "| S2 | V5-aero-14-a-product-with-a-deal.md | rule | Five at most | `field: Quantity (number, min 1, max 5)` | run | | |\n" \
        if fault == "twin" else ""
    rows = "\n".join(f"| {f} | none | | the cart's views |" for f in facets)
    text = f"""# Web: the cart, walked again

- **Role:** web
- **Read:** S2, the cart's views
- **Version:** 2026-10-26
- **New source:** S9 | evidence/captures/the-brief.md | the brief, read again as its own source

## Findings

| Source | Where | Lens | Found | Quote | Seen | Became | Limits |
|---|---|---|---|---|---|---|---|
| S2 | {where} | {lens} | The header's cart link says how many lines the cart holds | `{quote}` | run | | seen as Ana only |
| S9 | the-brief.md | need | The shop must behave as it does today | `the shop must behave on the new one as it does today` | said | | |
{twin}
## Coverage

| Source | Part | Read | Note |
|---|---|---|---|
| S2 | V21-the-cart.md | full | |
| S9 | the-brief.md | full | |

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
{rows}

## Disagreements

- V21 says Cart 2 while the cart lists three lines.

## Report

Walked the cart again.
"""
    path = root / "evidence/staging/web.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def run(tmp: Path, clean: Path) -> list[tuple[str, bool]]:
    """Reading material: an agent's staging file judged and merged, all or nothing; what was read held to what it
    is now; the captured sites held whole; the evidence served, and nothing beside it."""
    import threading
    import urllib.error
    import urllib.request

    import evidence
    import finish
    import load as fresh
    import logic
    import merge
    import review
    import serve

    root = tmp / "reading"
    shutil.copytree(clean, root)
    edit(root, "data/document.md", "status: agreed", "status: draft")
    (root / "evidence/captures/site/x.csv").write_text("name,email\nAna,ana@example.com\n", encoding="utf-8")
    edit(root, "data/sources/S2.md", "| inventory.md | full |", "| x.csv | not read | private rows |  |\n| inventory.md | full |")
    loading.build(loading.load(root))
    logic.notice(root, loading.load(root))
    checks = []
    said = lambda fault: " ".join(merge.check(root, staging(root, fault))[1])   # noqa: E731
    checks.append(("a staging file with a facet of its role unanswered is refused, the facet named",
                   "facet views: no row" in said("facet")))
    checks.append(("a quote not in the file its Where names is refused", "the quote is not in V21-the-cart.md" in said("quote")))
    checks.append(("a lens that is none of the grammar's is refused", "`touch` is no lens" in said("lens")))
    checks.append(("a quote from a file of data is refused, the file never opened", "file of data" in said("data")))
    checks.append(("a finding the specification holds already is refused, naming it", "the same place and quote as E14" in said("twin")))
    before = sorted(p.name for p in (root / "data/findings").glob("*.md"))
    ok, _ = merge.merge(root, staging(root, "quote"))
    checks.append(("a refused staging file merges nothing and stays", not ok and (root / "evidence/staging/web.md").is_file()
                   and sorted(p.name for p in (root / "data/findings").glob("*.md")) == before))
    ok, told = merge.merge(root, staging(root))
    done = fresh.load(root)
    made = [n for n in done.nodes.values() if n.kind == "finding" and n.id not in {b[:-3] for b in before}]
    source = next((n for n in done.nodes.values() if n.kind == "source" and n.fields.get("where") == "evidence/captures/the-brief.md"), None)
    s2 = done.nodes["S2"].fields.get("coverage") or []
    checks.append(("a good staging file merges whole: each finding a node, a declared source added with the next free ID",
                   ok and len(made) == 2 and source is not None and source.id == "S4"
                   and any(e.src == made[1].id and e.rel == "from" and e.dst == "S4" for e in done.edges)))
    checks.append(("each part read is a line of its source's coverage, with the print of what it is now",
                   any(r["part"] == "V21-the-cart.md" and r["print"] == evidence.print_of(root / "evidence/captures/site",
                                                                                          "V21-the-cart.md") for r in s2)
                   and sum(1 for r in s2 if r["part"] == "V21-the-cart.md") == 1))
    checks.append(("the agent's report is kept, its disagreements gathered, its staging file gone",
                   (root / "evidence/reports/web.md").is_file() and (root / evidence.DISAGREEMENTS).is_file()
                   and not (root / "evidence/staging/web.md").exists()))
    g = loading.grammar()
    o = finish.opened(g, done, review.held(root))
    checks.append(("disagreements not reconciled keep the specification from being agreed",
                   any("disagreements" in r for r in finish.ready(g, done, review.held(root))) and o["disagreements"]))
    # what was read, held to what it is now
    edit(root, "evidence/captures/site/V22-checkout.md", "# V22", "# V22 ")
    (root / "evidence/captures/site/V99-a-new-view.md").write_text("# V99 · A new view\n", encoding="utf-8")
    (root / "evidence/captures/site/shots/V1-375.jpg").unlink()
    done = fresh.load(root)
    o = finish.opened(g, done, review.held(root))
    checks.append(("a part changed since it was read is told, and to be investigated with the findings resting on it",
                   any(m["part"] == "V22-checkout.md" for m in o["material moved"])
                   and any(r["what"] == "material changed since it was read" and r["says"] == "V22-checkout.md"
                           for r in o["to investigate"])))
    checks.append(("a file of a source no line of coverage accounts for is told",
                   any(u["file"] == "site/V99-a-new-view.md" or u["file"].endswith("V99-a-new-view.md") for u in o["unaccounted"])))
    checks.append(("a capture not in the inventory, and a screenshot gone, are faults of the site",
                   any("V99" in x["file"] and "not in the inventory" in x["says"] for x in o["sites"])
                   and any("V1-375.jpg" in x["says"] for x in o["sites"])))
    checks.append(("what is to investigate is ranked, the heaviest first",
                   [r["weight"] for r in o["to investigate"]] == sorted((r["weight"] for r in o["to investigate"]), reverse=True)
                   and any(r["what"] == "state" for r in o["to investigate"])))
    # the evidence served, and nothing beside it
    httpd = serve.server(root, 0)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/evidence/captures/site/V21-the-cart.md") as answer:
            served = answer.status == 200 and answer.headers["Content-Type"].startswith("text/plain") \
                and b"V21" in answer.read()
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/evidence/..%2Fdata%2Fdocument.md")
            outside = False
        except urllib.error.HTTPError as wrong:
            outside = wrong.code == 404
        checks.append(("the evidence is served as text, and nothing outside it", served and outside))
        try:
            serve.server(root, port)
            checks.append(("a port another server holds is refused, not shared", False))
        except OSError:
            checks.append(("a port another server holds is refused, not shared", True))
    finally:
        httpd.shutdown()
    return checks
