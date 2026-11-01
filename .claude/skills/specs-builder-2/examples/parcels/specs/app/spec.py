"""The specification's command line: check its data, build its database, show a node.

    python app/spec.py check            every file held to the grammar; each problem at its file and line
    python app/spec.py build            check, then write .cache/spec.db -- only when nothing is wrong
    python app/spec.py node R4          a node, what it links to and what links to it, from the database
    python app/spec.py do set R4 priority should --because Q3
                                        one change, made through the logic: checked, written, logged -- or
                                        refused, and nothing changed; `do --file changes.txt` makes one change of
                                        every line of a file, all or none; --dry-run says what it would change
    python app/spec.py history [R4]     what changed, when, by whom and why: all of it, or one node's
    python app/spec.py stale            every node standing on something that changed since it was reviewed
                                        against it, and what moved; `do confirm <id>` once it is read again
    python app/spec.py kinds [question] what each kind holds -- its fields, links, texts and rows -- by the names
                                        `do add`, `add-row` and `set` take

For whoever writes and reviews it -- each with --json for an agent:

    python app/spec.py open             all that is not settled: the questions, the most deciding first; the
                                        additions not confirmed; qualities and risks left open; contradictions;
                                        findings that became nothing; what is stale; requirements and rules on
                                        weak ground, or that only documents stand behind
    python app/spec.py impact R4        before changing it: what it stands on, what would be stale at once, and
                                        further; what is unsettled about it, and what is stale already
    python app/spec.py trace R4         why it is there and where it shows: what it stands on, all the way up; the
                                        findings it came from, with their quotes; what shows it; who may do it
    python app/spec.py ready            whether it may be agreed: exits 1, saying every reason, while it may not
    python app/spec.py inbox            what those building from it asked back, each with its number; --raise N
                                        makes one an open question (with --answers, who answers it), --close N takes
                                        out one the specification now answers
    python app/spec.py story [F1]       a flow as a user story and every requirement it carries, with its priority,
                                        how well it is backed and its criteria; every flow's, without an ID
    python app/spec.py export [--into report.html]
                                        the whole specification as one HTML file that needs nothing beside it, for
                                        whoever has no Python: export/<name>.html, unless --into names another

For reading material -- the agents and the main agent:

    python app/spec.py merge evidence/staging/web.md --check
                                        an agent's own check of its staging file: what the merge would refuse, and why
    python app/spec.py merge evidence/staging/web.md
                                        its findings, coverage and report taken in as one change, or none of it;
                                        `merge` alone, every staging file waiting

For whoever builds from it -- each with --json for an agent:

    python app/spec.py overview         the product, what the specification holds, where to start
    python app/spec.py ask "Does the limit count other devices?" --about R4 --by "the builder"
                                        a question back to the keeper, into inbox.md -- never into the data; build
                                        what does not depend on it meanwhile
    python app/spec.py plan             the order to build in: the foundation, then each requirement after what it
                                        depends on, musts first
    python app/spec.py unit R4          all one thing needs to be built: itself, its rows, every link both ways
                                        with what the node at its end says, its questions, what it owes a review
    python app/spec.py tests R4|all     the acceptance criteria as tests; --gherkin, as scenarios
    python app/spec.py verify           whether it may be built from now: exits 1 on a problem or a stale node
    python app/spec.py snapshot --target <code>
                                        what the code is built from, kept in the code (the newest 3; --keep N)
    python app/spec.py changed --target <code> [--since <stamp>]
                                        what moved since, and what to build and test again, and the tests to take out
    python app/spec.py coverage [R4] [--target <code>]
                                        what the code carries: each requirement, the criteria its tests name and the
                                        files that name it; exits 1 while a must's or a should's criterion has no test

The specification is the folder that holds this app/ folder, unless --spec names another. Python 3.14 or later,
nothing to install.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 14):
    raise SystemExit(f"specs-builder-2 needs Python 3.14 or later; this is {sys.version.split()[0]}")

import argparse
import json
import re
import sqlite3
from pathlib import Path

sys.dont_write_bytecode = True          # nothing is written beside the app's scripts
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
import export as exporting  # noqa: E402
import finish  # noqa: E402
import inbox  # noqa: E402
import merge as merging  # noqa: E402
import load as loading  # noqa: E402
import logic  # noqa: E402
import review  # noqa: E402


def problems(done: loading.Load) -> str:
    lines = [f"{file}:{line}: {message}" if line else f"{file}: {message}" for file, line, message in done.problems]
    count = len(done.nodes)
    lines.append(f"{'FAILED' if done.problems else 'PASSED'} -- {len(done.problems)} problem(s); "
                 f"{count} node(s), {len(done.edges)} link(s)")
    return "\n".join(lines)


def show(root: Path, ident: str) -> int:
    database = root / loading.DATABASE
    if not database.is_file():
        print(f"{database}: not built -- run `spec.py build` first", file=sys.stderr)
        return 2
    con = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    row = con.execute("SELECT kind, name, file, line, fields, fingerprint FROM nodes WHERE id = ?",
                      (ident,)).fetchone()
    if row is None:
        print(f"{ident}: no node has that ID", file=sys.stderr)
        return 2
    kind, name, file, line, fields, print_ = row
    print(f"{ident} {name or ''}  ({kind}, {file}:{line}, fingerprint {print_})")
    for key, value in json.loads(fields).items():
        if key != "name":
            print(f"  {key}: {value}")
    out = con.execute("SELECT e.rel, e.dst, n.name FROM edges e JOIN nodes n ON n.id = e.dst WHERE e.src = ? "
                      "ORDER BY e.rel, e.dst", (ident,)).fetchall()
    back = con.execute("SELECT e.rel, e.src, n.name FROM edges e JOIN nodes n ON n.id = e.src WHERE e.dst = ? "
                       "ORDER BY e.rel, e.src", (ident,)).fetchall()
    for rel, other, other_name in out:
        print(f"  -> {rel} {other} {other_name or ''}".rstrip())
    for rel, other, other_name in back:
        print(f"  <- {other} {other_name or ''} {rel} it".replace("  ", " "))
    return 0


def said(change: dict) -> str:
    """One node's change, in a line or a few."""
    head = f"  {change['id']} {change['change']}"
    out = [head]
    for key, (was, now) in (change.get("fields") or {}).items() if change["change"] == "changed" else []:
        if isinstance(was, list) or isinstance(now, list):      # a table: the lines it lost and gained
            line = lambda r: " | ".join(str(v) for v in r.values()) if isinstance(r, dict) else str(r)  # noqa: E731
            before, after = [line(r) for r in was or []], [line(r) for r in now or []]
            out.append(f"      {key}:")
            out += [f"        - {r}" for r in before if r not in after]
            out += [f"        + {r}" for r in after if r not in before]
            continue
        out.append(f"      {key}: {review.moved(was, now)}")
    for word in ("tied", "untied"):
        if change.get(word):
            out.append(f"      {word}: {', '.join(change[word])}")
    return "\n".join(out)


def do(root: Path, words: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="spec.py do", description=logic.__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--because", default="", help="why: a decision, a question, a few words")
    parser.add_argument("--who", default="", help="who makes it (default: agent)")
    parser.add_argument("--dry-run", action="store_true", help="say what would change, and change nothing")
    parser.add_argument("--file", type=Path, help="a change set: one operation to a line, all or none")
    args, operation = parser.parse_known_args(words)
    if args.file:
        lines = [l for l in args.file.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        operations = [logic.parse(l) for l in lines]
    else:
        operations = [operation]
    if not any(operations):
        parser.error("an operation, or --file: `spec.py do set R4 priority should`")
    try:
        result = logic.apply(root, operations, who=args.who or "agent", because=args.because, dry=args.dry_run)
    except logic.Refused as refused:
        print(f"refused: {refused}", file=sys.stderr)
        return 1
    for line in result.applied:
        print(line)
    if result.problems:
        print("refused -- the result would not load clean, so nothing is changed:", file=sys.stderr)
        for file, line, message in result.problems:
            print(f"  {file}:{line}: {message}" if line else f"  {file}: {message}", file=sys.stderr)
        return 1
    print(("would change:" if result.dry else "changed:") if result.changes else "nothing changed")
    for change in result.changes:
        print(said(change))
    return 0


def show_history(root: Path, ident: str | None) -> int:
    entries = logic.history(root, ident)
    if not entries:
        print("no change is logged" + (f" for {ident}" if ident else ""))
    for entry in entries:
        why = f" -- because {entry['because']}" if entry.get("because") else ""
        print(f"{entry['at']}  {entry['who']}{why}")
        for operation in entry.get("operations", []):
            print(f"    {operation}")
        for change in entry.get("changes", []):
            print(said(change))
    return 0


def kinds(args: argparse.Namespace) -> int:
    """What each kind holds, by the names the operations take."""
    g = loading.grammar()
    wanted = [args.id] if args.id else list(g["kinds"])
    if args.id and args.id not in g["kinds"]:
        print(f"{args.id}: no such kind; they are {', '.join(g['kinds'])}", file=sys.stderr)
        return 2
    answer = {}
    for kind in wanted:
        spec = g["kinds"][kind]
        links = {r["field"]: {"relation": rel, "to": r["to"], **({"least": r["least"]} if "least" in r else {})}
                 for rel, r in g["relations"].items() if kind in r["from"] and "field" in r}
        rows = next(({"kind": d["kind"], "section": t} for t, d in spec.get("sections", {}).items()
                     if d["type"] == "children"), None)
        answer[kind] = {"is": spec["is"], "id": spec["id"], "file": spec.get("folder") or spec.get("single") or "a row",
                        "fields": {k: ("one of " + ", ".join(g["choices"][f["of"]]) if f.get("type") == "choice"
                                       else "text") + (", required" if f.get("required") else "")
                                   for k, f in spec.get("fields", {}).items()},
                        "links": links,
                        "texts": {d["as"]: (t or "(the text under the header)") + (", required" if d.get("required")
                                                                                   else "")
                                  for t, d in spec.get("sections", {}).items() if d["type"] == "text"},
                        "rows": rows,
                        "tables": {d["as"]: [c["name"] + (f" (links: {c['relation']})" if c.get("relation") else "")
                                             for c in d["columns"]]
                                   for d in spec.get("sections", {}).values() if d["type"] == "table"},
                        "columns": [c["name"] + (f" (links: {c['relation']})" if c.get("relation") else "")
                                    for c in spec.get("columns", []) if not c.get("id")]}
    if args.json:
        print(json.dumps(answer, ensure_ascii=False, indent=1))
        return 0
    for kind, a in answer.items():
        print(f"{kind} ({a['id']}, {a['file']}): {a['is']}")
        for k, v in a["fields"].items():
            print(f"    field  {k}: {v}")
        for k, v in a["links"].items():
            print(f"    link   {k}: `{v['relation']}` " + ("anything" if "any" in v["to"] else "a " + " or a ".join(v["to"])) +
                  (f", at least {v['least']}" if v.get("least") else ""))
        for k, v in a["texts"].items():
            print(f"    text   {k}: {v}")
        for k, v in a["tables"].items():
            print(f"    table  {k}: {' | '.join(v)} -- `do add-line <id> {k.split()[0] if ' ' not in k else repr(k)} "
                  f"<{v[0].split(' (')[0]}> key=value`")
        if a["rows"]:
            print(f"    rows   {a['rows']['kind']}, under ## {a['rows']['section']} -- `do add-row {a['id']}... key=value`")
        if a["columns"]:
            print(f"    columns {', '.join(a['columns'])}")
    return 0


def finishing(root: Path, args: argparse.Namespace) -> int:
    """The questions of whoever writes and reviews: each for a person, or as JSON for an agent."""
    g = loading.grammar()
    done = loading.load(root)
    if done.problems:
        print(problems(done))
        return 1
    stamps = review.held(root)

    def say(answer: object, text: list[str], code: int = 0) -> int:
        print(json.dumps(answer, ensure_ascii=False, indent=1) if args.json else "\n".join(text))
        return code

    def ids(items: list[dict]) -> str:
        return ", ".join(f"{n['id']} {n['name']}".strip() for n in items) or "none"

    if args.command == "open":
        o = finish.opened(g, done, stamps)
        lines = [f"{len(o['questions'])} open question(s), the most deciding first:"]
        for q in o["questions"]:
            reach = ", ".join(q["about"] + [a for a in q["asked by"] if a not in q["about"]])
            lines.append(f"  {q['id']} [{q['answers'] or 'nobody named'}] {q['question'][:150]}" +
                         (f"\n      touches {reach}" if reach else ""))
        lines.append(f"{len(o['additions'])} addition(s) not confirmed:")
        for a in o["additions"]:
            lines.append(f"  {a['id']} to {', '.join(a['added to'])}: {a['says'][:150]}")
        for key, said in (("qualities open", "qualities open"), ("risks open", "risks with no mitigation"),
                          ("contradictions", "contradictions unsettled"),
                          ("findings open", "findings that became nothing"),
                          ("weak", "requirements and rules on weak ground"),
                          ("documented", "documented only, to check against the product")):
            lines.append(f"{said}: {ids(o[key])}")
            if key == "qualities open" and o["qualities missing"]:
                lines.append(f"qualities nothing says anything of: {', '.join(o['qualities missing'])}")
        lines.append(f"stale: {', '.join(o['stale']) or 'nothing'}")
        if o["staged"]:
            lines.append(f"waiting to be merged: {', '.join(o['staged'])}")
        if o["disagreements"]:
            lines.append(f"disagreements not reconciled yet: {o['disagreements']}")
        for m in o["material moved"]:
            lines.append(f"read again: {m['source']} {m['part']} changed since it was read ({m['was']} -> {m['now']})")
        for u in o["unaccounted"][:20]:
            lines.append(f"not accounted for: {u['source']} {u['file']} -- no line of its coverage says it was read")
        if len(o["unaccounted"]) > 20:
            lines.append(f"  ... and {len(o['unaccounted']) - 20} more")
        for x in o["sites"]:
            lines.append(f"{'note' if x['note'] else 'capture'}: {x['file']}" + (f":{x['line']}" if x["line"] else "")
                         + f": {x['says']}")
        above = [r for r in o["to investigate"] if r["weight"] >= finish.LINE]
        lines.append(f"to investigate ({len(o['to investigate'])}, {len(above)} at or above the line of "
                     f"{finish.LINE}), the heaviest first:")
        lines += [f"  {r['weight']:>3}  {r['what']}: {r['id']} {r['says'][:110]}" + (f"\n         how: {r['how'][:110]}"
                                                                                   if r["how"] else "")
                  for r in o["to investigate"]]
        said = {"vague": "a vague word", "technology": "a technology word, maybe saying how",
                "opening": "opens with none of the opening words (The, When, While, Where, If)"}
        if o["words"]:
            lines.append(f"notes for a review ({len(o['words'])}):")
            lines += [f"  {w['id']}: {said[w['note']]} -- {', '.join(w['words'])}" for w in o["words"]]
        return say(o, lines)
    if args.command == "story":
        told = [finish.story(g, done, args.id)] if args.id else finish.stories(g, done)
        lines = [] if told else ["no flow yet: a story is told from a flow"]
        for s in told:
            lines += [f"{s['id']} {s['name']}", f"  {s['story']}"]
            if s["untold"]:
                lines.append(f"  not told whole: {'; '.join(s['untold'])}")
            lines.append(f"  carries {len(s['requirements'])} requirement(s), {s['must']} must, {s['criteria']} criteria:")
            for r in s["requirements"]:
                lines.append(f"    {r['id']} {r['name']} [{r['priority'] or '-'}, {r['backed']}]")
                lines += [f"      {c['id']} {c['says']}" for c in r["criteria"]]
            lines.append("")
        return say(told if not args.id else told[0], lines, 1 if any(s["untold"] for s in told) else 0)
    if args.command == "ready":
        held = finish.ready(g, done, stamps)
        agreed = "document" in done.nodes and done.nodes["document"].fields.get("status") == "agreed"
        verdict = ("agreed, but no longer ready: what holds it is above" if agreed else "not ready to be agreed") \
            if held else ("agreed, and nothing stands in the way" if agreed else
                          "ready to be agreed: only the user agrees it, with `do set document status agreed`")
        return say({"ready": not held, "agreed": agreed, "held by": held}, [*held, verdict], 1 if held else 0)
    if not args.id:
        print(f"{args.command} needs an ID: `spec.py {args.command} R4`", file=sys.stderr)
        return 2
    if args.command == "impact":
        i = finish.impact(g, done, stamps, args.id)
        lines = [f"{i['id']} {i['name']} ({i['kind']})" + (f", with its rows {', '.join(i['rows'])}" if i["rows"] else "")]
        lines.append("stands on: " + (", ".join(f"{n['rel']} {n['id']}" for n in i["stands on"]) or "nothing"))
        lines.append(f"stale at once if it changes ({len(i['stale at once'])}):")
        lines += [f"  {n['id']} {n['name']}  -- {'; '.join(n['by'])}" for n in i["stale at once"]]
        lines.append(f"further, if those change too: {ids(i['further'])}")
        lines.append(f"unsettled about it: {ids(i['unsettled'])}")
        lines.append("stale already: " + ("; ".join(f"{s['node']} on {s['on']}" for s in i["stale already"]) or "nothing"))
        in_code(root, args, i, lines)
        return say(i, lines)
    t = finish.trace(g, done, args.id)
    lines = [f"{t['id']} {t['name']} ({t['kind']})", f"  {t['says'][:300]}"]
    if t["backed"]:
        lines.append(f"backed: {t['backed']}")
    if t["stands on"]:
        lines.append("stands on:")
        lines += [f"  {'  ' * (n['depth'] - 1)}{n['from']} {n['rel']} {n['id']} {n['name']}" for n in t["stands on"]]
    if t["came from"]:
        lines.append("came from:")
        for c in t["came from"]:
            lines.append(f"  {c['id']} ({c['seen']}, {', '.join(s['id'] for s in c['sources'])} {c['where']}) became "
                         f"{c['became']}: {c['name']}" + (f'\n      "{c["quote"][:200]}"' if c["quote"] else ""))
    if t["shown by"]:
        lines.append("shown by:")
        lines += [f"  {n['id']} {n['name']}" + (f" on {n['on']}" if n["on"] else "") +
                  (f", passed by {', '.join(n['flows'])}" if n["flows"] else "") +
                  (f" (shows {n['shows']})" if n["shows"] != t["id"] else "") for n in t["shown by"]]
    if t["done by"]:
        lines.append("done by: " + "; ".join(f"{n['id']} {n['name']} ({n['rel']})" for n in t["done by"]))
    if t["spoken of by"]:
        lines.append("spoken of by: " + "; ".join(f"{n['id']} ({n['rel']})" for n in t["spoken of by"]))
    in_code(root, args, t, lines)
    return say(t, lines)


def asking(root: Path, args: argparse.Namespace) -> int:
    """A question back from whoever builds, and the keeper's inbox of them."""
    out = lambda answer, text: print(json.dumps(answer, ensure_ascii=False, indent=1) if args.json else text)  # noqa: E731
    try:
        if args.command == "ask":
            if not args.id:
                print('ask needs the question: `spec.py ask "..." --about R4 --by "the builder"`', file=sys.stderr)
                return 2
            entry = inbox.ask(root, args.id, [i for i in re.split(r"[,\s]+", args.about or "") if i], args.by or "")
            out(entry, f"#{entry['no']} waits in {inbox.INBOX} for the keeper; build what does not depend on it")
            return 0
        if args.raise_no is not None:
            made = inbox.raise_(root, args.raise_no, args.answers, "the keeper")
            out({"raised": args.raise_no, "made": made}, f"#{args.raise_no} is now {made}, an open question")
            return 0
        if args.close_no is not None:
            gone = inbox.take(root, args.close_no)
            out({"closed": gone}, f"#{gone['no']} taken out, answered in the specification")
            return 0
    except (ValueError, KeyError, logic.Refused) as wrong:
        print(str(wrong).strip("'\""), file=sys.stderr)
        return 2
    waiting = inbox.read(root)
    out(waiting, "\n".join([f"{len(waiting)} waiting in the inbox:"] + [
        f"  #{a['no']} [{a['by']}, {a['asked']}] about {', '.join(a['about']) or 'nothing named'}: {a['question']}"
        for a in waiting]))
    return 1 if waiting else 0


def merged(root: Path, args: argparse.Namespace) -> int:
    """A staging file checked, or merged: each said at its line, nothing changed while one stands."""
    given = Path(args.id) if args.id else None
    if given is not None and not given.is_absolute() and not given.exists():
        given = root / given                            # a staging file named from the specification's folder
    paths = [given.resolve()] if given is not None else merging.staged_files(root)
    if not paths:
        print(f"nothing waits in {merging.evidence.STAGING}/")
        return 0
    good = True
    for path in paths:
        ok, said = (merging.check if args.check else merging.merge)(root, path)
        print("\n".join(said))
        good = good and ok
    return 0 if good else 1


def covered(root: Path, args: argparse.Namespace) -> int:
    """What the code carries of the specification, whole or of one requirement."""
    c = build.coverage(root, args.target)
    if args.id:
        found = [r for r in c["requirements"] if r["id"] == args.id]
        if not found:
            raise KeyError(f"{args.id}: no requirement has that ID")
        c["requirements"], c["no test"] = found, [i for i in c["no test"] if i == args.id]
        c["untested"], c["unknown"] = [u for u in c["untested"] if u in found[0]["untested"]], []
        c["whole"] = not found[0]["untested"] or found[0]["priority"] not in ("must", "should")
    lines = [f"{c['tests read']} file(s) of tests and {c['code read']} other file(s) of code read in {c['target']}"]
    for r in c["requirements"]:
        done = len(r["criteria"]) - len(r["untested"])
        lines.append(f"{r['id']} {r['name']} [{r['priority'] or '-'}]: {done} of {len(r['criteria'])} criteria named by a test"
                     + (f"; not {', '.join(r['untested'])}" if r["untested"] and r["priority"] != "wont" else ""))
        if args.id:
            lines += [f"  {t['id']}: {', '.join(t['tests']) or 'no test'}" for t in r["criteria"]]
        if r["tests"]:
            lines.append(f"  tests: {', '.join(r['tests'])}")
        if r["code"]:
            lines.append(f"  code: {', '.join(r['code'])}")
    if c["no test"]:
        lines.append(f"no test names: {', '.join(c['no test'])}")
    if c["unknown"]:
        lines.append("the code names what the specification has not: " +
                     "; ".join(f"{u['id']} ({', '.join(u['files'])})" for u in c["unknown"]))
    lines.append("a test names every criterion of every must and should" if c["whole"] else
                 f"{len(c['untested'])} {'criterion' if len(c['untested']) == 1 else 'criteria'} no test names, "
                 "of what is to be built")
    print(json.dumps(c, ensure_ascii=False, indent=1) if args.json else "\n".join(lines))
    return 0 if c["whole"] else 1


def in_code(root: Path, args: argparse.Namespace, answer: dict, lines: list[str]) -> None:
    """Given the code, or where it is known, what of it names a requirement or a criterion."""
    if answer["kind"] in ("requirement", "criterion"):
        try:
            held = build.named(root, answer["id"], args.target)
        except FileNotFoundError as wrong:
            lines.append(str(wrong))
            return
        if held is not None:
            answer["in the code"] = held
            lines.append(f"tests that name it: {', '.join(held['tests']) or 'none'}")
            lines.append(f"other code that names it: {', '.join(held['code']) or 'none'}")


def builder(root: Path, args: argparse.Namespace) -> int:
    """The builder's questions: each answered for a person, or as JSON for an agent."""
    def say(answer: object, text: list[str]) -> int:
        print(json.dumps(answer, ensure_ascii=False, indent=1) if args.json else "\n".join(text))
        return 0

    if args.command == "overview":
        o = build.overview(root)
        counts = ", ".join(f"{n} {k}" for k, n in o["counts"].items())
        return say(o, [f"{o['name']} ({o['kind']}, {o['status']})", "", o["summary"], "", f"{counts}; {o['links']} links",
                       f"open questions: {', '.join(o['open questions']) or 'none'}",
                       f"stale: {', '.join(o['stale']) or 'nothing'}", "",
                       "Next: `spec.py plan`, then `spec.py unit <id>` for each slice, `spec.py tests <id>` for its tests"])
    if args.command == "plan":
        slices = build.plan(root)
        lines = []
        for s in slices:
            if s["slice"] == "foundation":
                held = "; ".join(f"{k}: {', '.join(v)}" for k, v in s["holds"].items() if v)
                lines.append(f"foundation -- {s['why']}\n    {held}")
            else:
                lines.append(f"{s['slice']} {s['name']} ({s['priority']})" +
                             (f" -- after {', '.join(s['depends on'])}" if s["depends on"] else "") +
                             (f"\n    shown by {', '.join(s['shown by'])}" if s["shown by"] else "") +
                             (f"\n    enforces {', '.join(s['enforces'])}" if s["enforces"] else "") +
                             f"\n    tests {', '.join(s['tests']) or 'none'}")
        return say(slices, lines)
    if args.command == "unit":
        if not args.id:
            print("unit needs an ID: `spec.py unit R4`", file=sys.stderr)
            return 2
        u = build.unit(root, args.id)
        lines = [f"{u['id']} {u['name']} ({u['kind']}, {u['file']})"]
        lines += [f"  {k}: {v}" for k, v in u["fields"].items() if not isinstance(v, list) and k != "name"]
        for r in u["rows"]:
            lines.append(f"  {r['id']} {r['name'] if r['name'] != r['says'] else ''} {r['says']}".rstrip())
        for l in u["links"]:
            lines.append(f"  -> {l['rel']} {l['id']} {l['name']}" + (f" (from {l['from']})" if l.get("from") else "")
                         + (f": {l['says'][:160]}" if l["says"] and l["says"] != l["name"] else ""))
        for l in u["back"]:
            lines.append(f"  <- {l['rel']} {l['id']} {l['name']}")
        if u["questions"]:
            lines.append("  open questions: " + "; ".join(f"{q['id']} {q['says'][:120]}" for q in u["questions"]))
        if u["stale"]:
            lines.append("  stale: " + "; ".join(f"{s['node']} on {s['on']}" for s in u["stale"]))
        return say(u, lines)
    if args.command == "tests":
        found = build.tests(root, args.id)
        if args.gherkin:
            return say(found, [build.gherkin(t) + "\n" for t in found])
        return say(found, [f"{t['id']}  {t['says']}" for t in found])
    if args.command == "verify":
        ok, told = build.verify(root)
        if args.json:
            print(json.dumps({"ready": ok, "said": told}, ensure_ascii=False, indent=1))
        else:
            print("\n".join(told))
        return 0 if ok else 1
    if args.command == "coverage":
        return covered(root, args)
    if not args.target:
        print(f"{args.command} needs the code built from it: --target <folder>", file=sys.stderr)
        return 2
    target = args.target.resolve()
    if args.command == "snapshot":
        if args.list:
            taken = build.snapshots(target)
            return say([p.name for p in taken], [p.name for p in taken] or ["no snapshot is kept there"])
        path = build.snapshot(root, target, args.keep)
        return say({"snapshot": str(path)}, [f"recorded what {target.name} is built from: {path}"])
    c = build.changed(root, target, args.since)
    lines = [f"since {c['since']}:"]
    for change in c["changes"]:
        lines.append(said(change))
    for word in ("new", "gone", "changed"):
        if c["files"][word]:
            lines.append(f"  files {word}: {', '.join(c['files'][word])}")
    if not c["changes"] and not any(c["files"].values()):
        lines.append("  nothing moved")
    for k, v in c["build again"].items():
        lines.append(f"build again -- {k}: {', '.join(v)}")
    if c["tests to run again"]:
        lines.append(f"tests to run again: {', '.join(c['tests to run again'])}")
    if c["tests to remove"]:
        lines.append(f"tests to take out: {', '.join(c['tests to remove'])}")
    return say(c, lines)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):  # read by a program: UTF-8; a console that cannot show a character: ?
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace") if stream.isatty() else stream.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1 and sys.argv[1] == "do":
        spec = Path(__file__).resolve().parent.parent
        words = sys.argv[2:]
        if "--spec" in words:
            at = words.index("--spec")
            spec, words = Path(words[at + 1]), words[:at] + words[at + 2:]
        return do(spec.resolve(), words)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["check", "build", "node", "history", "stale", "kinds", "open", "impact",
                                            "trace", "ready", "story", "ask", "inbox", "merge", "export", "overview", "plan", "unit",
                                            "tests", "verify", "snapshot", "changed", "coverage"])
    parser.add_argument("id", nargs="?", help="with node, history, impact, trace, story, unit, tests or coverage: the node's ID; "
                                              "with kinds, a kind")
    parser.add_argument("--spec", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="the specification's folder (default: the one holding app/)")
    parser.add_argument("--target", type=Path, help="with snapshot, changed, coverage, impact and trace: the code built "
                                                    "from it; a snapshot remembers it, for coverage, impact and trace")
    parser.add_argument("--keep", type=int, default=build.KEEP, help="with snapshot: how many to keep (0: all)")
    parser.add_argument("--since", help="with changed: the snapshot to compare with, by its stamp")
    parser.add_argument("--list", action="store_true", help="with snapshot: list them, and take none")
    parser.add_argument("--gherkin", action="store_true", help="with tests: as scenarios")
    parser.add_argument("--check", action="store_true", help="with merge: judge the file, and write nothing")
    parser.add_argument("--into", type=Path, help="with export: the file to write")
    parser.add_argument("--about", help="with ask: the IDs the question is about, by commas")
    parser.add_argument("--by", help="with ask: who asks it")
    parser.add_argument("--raise", dest="raise_no", type=int, help="with inbox: make this one an open question")
    parser.add_argument("--answers", default="", help="with inbox --raise: who answers it")
    parser.add_argument("--close", dest="close_no", type=int, help="with inbox: take this one out, answered")
    parser.add_argument("--json", action="store_true", help="the answer as JSON, for an agent")
    args = parser.parse_args()
    root = args.spec.resolve()
    if args.command in ("overview", "plan", "unit", "tests", "verify", "snapshot", "changed", "coverage"):
        try:
            return builder(root, args)
        except (ValueError, KeyError, FileNotFoundError) as wrong:
            print(str(wrong).strip("'\""), file=sys.stderr)
            return 2
    if args.command in ("ask", "inbox"):
        return asking(root, args)
    if args.command == "kinds":
        return kinds(args)
    if args.command == "merge":
        return merged(root, args)
    if args.command == "export":
        try:
            path = exporting.export(root, args.into.resolve() if args.into else None)
        except ValueError as wrong:
            print(str(wrong), file=sys.stderr)
            return 2
        print(f"written: {path} ({path.stat().st_size // 1024} KB) -- one file, needing nothing beside it")
        return 0
    if args.command in ("open", "impact", "trace", "ready", "story"):
        try:
            return finishing(root, args)
        except (ValueError, KeyError) as wrong:
            print(str(wrong).strip("'\""), file=sys.stderr)
            return 2
    if args.command == "history":
        return show_history(root, args.id)
    if args.command == "stale":
        done = loading.load(root)
        if done.problems:
            print(problems(done))
            return 1
        owed = review.stale(loading.grammar(), done, review.held(root))
        for s in owed:
            print(f"{s['node']} stands on {s['on']}, which changed since ({s['link']}):")
            for k in sorted(set(s["was"]) | set(s["now"])):
                if s["was"].get(k) != s["now"].get(k):
                    print(f"    {k}: {review.moved(s['was'].get(k), s['now'].get(k))}")
        print(f"{len({s['node'] for s in owed})} node(s) stale" + (" -- `spec.py do confirm <id>` once each is read "
                                                                   "again" if owed else ""))
        return 1 if owed else 0
    if args.command == "node":
        if not args.id:
            parser.error("node needs an ID: `spec.py node R4`")
        return show(root, args.id)
    done = loading.load(root)
    print(problems(done))
    if done.problems:
        return 1
    if args.command == "build":
        print(f"built {loading.build(done).relative_to(root).as_posix()}")
        noticed = logic.notice(root, done)
        if noticed:
            print(f"{len(noticed)} node(s) changed by hand since the last change logged: logged now")
    return 0


if __name__ == "__main__":
    sys.exit(main())
