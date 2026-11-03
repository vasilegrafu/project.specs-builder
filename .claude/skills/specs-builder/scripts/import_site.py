"""Import a specification of the earlier form -- a site of pages from which a graph is read -- into this skill's
form: one file per node, the prototypes held to them, the application beside them.

    python .claude/skills/specs-builder/scripts/import_site.py <the earlier specification> <the new folder>
    python .claude/skills/specs-builder/scripts/import_site.py <earlier> <new> --replace     over a folder there

The earlier specification is read through what its own folder carries -- its reading, in tools/, asked for the model
it keeps -- and, where that model does not hold a thing whole, through its pages: a requirement's whole statement, a
screen's states, a flow's steps gone wrong, a component's drawings, each prototype. Nothing of the earlier skill is
used. What the new form keeps as text rather than as nodes -- the lines of code, the views of a live site and the
index of an API that the reading of evidence went through -- is not carried as nodes, and every link to one of them
is counted and said. The new folder is written whole, then checked: its problems, if any, are the importer's to
mend, and are said at their lines.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 14):
    raise SystemExit(f"specs-builder needs Python 3.14 or later; this is {sys.version.split()[0]}")

import argparse
import json
import re
import shutil
import subprocess
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import folder  # noqa: E402

SKILL = folder.SKILL
sys.path.insert(0, str(folder.APP))
import evidence  # noqa: E402
ASK = ("import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); import spec_cache; "
       "print(spec_cache.current(Path(sys.argv[2])))")


def natural(text: str) -> list:
    return [int(x) if x.isdigit() else x for x in re.findall(r"\d+|\D+", str(text))]


class Earlier:
    """The earlier specification: its model, asked of its own reading, and its pages."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        done = subprocess.run([sys.executable, "-I", "-B", "-c", ASK, str(folder / "tools"), str(folder)],
                              capture_output=True, text=True, encoding="utf-8")
        if done.returncode:
            raise SystemExit(f"{folder}: its own reading could not be asked for its model -- "
                             f"{(done.stderr or done.stdout).strip().splitlines()[-1:]}")
        self.model = Path(done.stdout.strip()) / "model"
        self.edges = [l.split("\t") for l in (self.model / "edges.tsv").read_text(encoding="utf-8").splitlines()[1:]
                      if l.count("\t") == 2]

    def kind(self, folder: str) -> list[dict]:
        place = self.model / folder
        if not place.is_dir():
            return []
        return sorted((json.loads(p.read_text(encoding="utf-8")) for p in place.glob("*.json")),
                      key=lambda n: natural(n["id"]))

    def json(self, name: str) -> dict:
        path = self.model / name
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    def page(self, at: str) -> str:
        """The markdown a page holds, by the `at` the model gives it."""
        path = self.folder / at.split("#", 1)[0]
        if not path.is_file():
            return ""
        text = path.read_text(encoding="utf-8")
        start = text.find('<script type="text/markdown"')
        if start < 0:
            return ""
        return text[start:].split(">", 1)[1].split("</script>", 1)[0]


def section(markdown: str, title: str) -> str:
    """The text of a `## title` section of a page's markdown."""
    found = re.search(rf"^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", markdown, flags=re.M | re.S)
    return found.group(1).strip() if found else ""


def table_rows(text: str) -> list[list[str]]:
    rows = [l.strip() for l in text.splitlines() if l.strip().startswith("|")]
    out = []
    for raw in rows[2:]:
        inner = raw.strip().strip("|")
        out.append([c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", inner)])
    return out


def state_id(earlier: str) -> str:
    """A state's ID as the new form names it: its entity's, then its name as one word -- `N2.in the cart`
    becomes `N2.in-the-cart`, as the loader names the row."""
    head, _, name = earlier.partition(".")
    return f"{head}.{re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')}"


def escaped(text: str) -> str:
    """A text whose lines read as headings in a node's file -- `# x`, `## x` -- kept as text, not as a heading."""
    return "\n".join("\\" + line if re.match(r"#{1,6} ", line) else line for line in text.splitlines())


def cell(text: object) -> str:
    return " ".join(str(text or "").split()).replace("|", "\\|")


def table(head: list[str], rows: Sequence[Sequence[object]]) -> str:
    line = lambda cells: "| " + " | ".join(cell(c) for c in cells) + " |"        # noqa: E731
    return "\n".join([line(head), "|" + "---|" * len(head), *(line(r) for r in rows)])


class Importer:
    def __init__(self, earlier: Earlier, target: Path) -> None:
        self.e = earlier
        self.t = target
        self.written = Counter()
        self.dropped = Counter()
        self.lost: dict[str, set] = {}
        self.notes: list[str] = []
        self.rename: dict[str, str] = {}
        index = earlier.json("index.json")
        self.kinds = {n["id"]: n["kind"] for n in index.get("nodes", [])}
        for n, q in enumerate(self.quality_order(), 1):
            self.rename[q] = f"Y{n}"
        for n, f in enumerate(earlier.json("design/foundations.json").get("nodes", []), 1):
            self.rename[f["id"]] = f"FD{n}"
        self.ids = {self.rename.get(i, i) for i, k in self.kinds.items() if k not in ("api", "view", "code")}
        for entity in earlier.kind("entities"):           # its states are rows of its own, named: N2.open
            for state in entity.get("holds", []):
                named = state_id(state["id"])
                self.rename[state["id"]] = named
                self.kinds[state["id"]] = self.kinds[named] = "state"
                self.ids.add(named)
        self.ids.add("document")

    def quality_order(self) -> list[str]:
        prd = self.e.page("site/requirements/prd.html")
        words = [r[0] for r in table_rows(section(prd, "Quality requirements")) if r]
        found = [q["id"] for q in self.e.kind("qualities")]
        return [w for w in words if w in found] + sorted(set(found) - set(words))

    def keep(self, ids: list[str] | None) -> list[str]:
        """The IDs of a link the new form has; each one dropped counted by what it named."""
        out = []
        for i in ids or []:
            i = self.rename.get(i, i)
            if i in self.ids:
                if i not in out:
                    out.append(i)
            else:
                self.dropped[self.kinds.get(i, "unknown")] += 1
                self.lost.setdefault(self.kinds.get(i, "unknown"), set()).add(i)
        return out

    def out(self, node: dict, rel: str) -> list[str]:
        return self.keep((node.get("out") or {}).get(rel, []))

    def write(self, folder: str, ident: str, header: list[tuple[str, object]], sections: list[tuple[str, str]],
              kind: str) -> None:
        lines = ["---", *(f"{k}: {' '.join(str(v).split())}" for k, v in header if v not in (None, "", [])), "---"]
        for title, body in sections:
            body = escaped((body or "").strip())
            if body:
                lines += ["", body] if not title else ["", f"## {title}", "", body]
        path = self.t / "data" / folder / f"{ident}.md" if folder else self.t / "data" / f"{ident}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
        self.written[kind] += 1

    # the kinds, one by one
    def document(self) -> None:
        prd = self.e.page("site/requirements/prd.html")
        doc = self.e.json("document.json")
        head = re.search(r"^# (.+?)(?::\s*product requirements)?\s*$", prd, flags=re.M)
        status = re.search(r"\*\*Status:\*\*\s*(\w+)", prd)
        kind = re.search(r"\*\*Kind:\*\*\s*(.+)", prd)
        said = {t: section(prd, t) for t in ("Boundary", "Interface", "More")}
        self.write("", "document", [("name", head.group(1) if head else self.t.parent.name),
                                    ("kind", kind.group(1).strip() if kind else ""),
                                    ("status", status.group(1) if status else "")],
                   [("", doc.get("summary", "")), ("Problem", doc.get("problem", "")), ("Users", doc.get("users", "")),
                    ("Journey", doc.get("journey", "")), ("Non-goals", doc.get("non-goals", "")),
                    ("Assumptions", doc.get("assumptions", "")), ("Boundary", said["Boundary"]),
                    ("Interface", said["Interface"]), ("Release plan", doc.get("release plan", "")),
                    ("More", said["More"])], "document")

    def goals(self) -> None:
        prd = self.e.page("site/requirements/prd.html")
        rows = {r[0]: r for r in table_rows(section(prd, "Goals")) if r and re.fullmatch(r"G\d+", r[0])}
        for g in self.e.kind("goals"):
            r = rows.get(g["id"], [])
            self.write("goals", g["id"], [("id", g["id"]), ("name", g["name"]),
                                          ("measured by", r[2] if len(r) > 2 else ""),
                                          ("today", r[3] if len(r) > 3 else ""),
                                          ("target", r[4] if len(r) > 4 else "")], [], "goal")

    def statement(self, r: dict) -> str:
        """A requirement's whole statement, from its page: every line between its heading and its first key line."""
        page = self.e.page(r.get("at", ""))
        lines = page.strip().splitlines()[1:] if page.strip().startswith("#") else []
        out = []
        for line in lines:
            if re.match(r"^[A-Z][A-Za-z ]+:(\s|$)", line):
                break
            out.append(line)
        return "\n".join(out).strip() or r.get("says", "")

    def requirements(self) -> None:
        for r in self.e.kind("requirements"):
            body = [("", self.statement(r)), ("Why", self.left_out(r))]
            if r.get("holds"):
                body.append(("Accepted when", "\n".join(f"- {c['id']} {' '.join(c['says'].split())}" for c in r["holds"])))
            self.write("requirements", r["id"], [
                ("id", r["id"]), ("name", r["name"]), ("priority", r.get("priority", "")),
                ("serves", ", ".join(self.out(r, "serves"))), ("enforces", ", ".join(self.out(r, "enforces"))),
                ("depends on", ", ".join(self.out(r, "depends on"))), ("refines", ", ".join(self.out(r, "refines"))),
                ("conflicts with", ", ".join(self.out(r, "conflicts with"))), ("from", r.get("from", ""))],
                body, "requirement")

    def left_out(self, r: dict) -> str:
        """Why a wont is left out: the `Left out:` line of its page."""
        found = re.search(r"^Left out:\s*(.+?)\s*$", self.e.page(r.get("at", "")), flags=re.M)
        return found.group(1) if found else ""

    def simple(self, folder: str, kind: str, text_key: str, extra: list[tuple[str, str]],
               sections: list[tuple[str, str]], about: str | None = "about") -> None:
        for n in self.e.kind(folder):
            ident = self.rename.get(n["id"], n["id"])
            header = [("id", ident), *((k, n.get(v, "")) for k, v in extra)]
            if about:
                header.append((about, ", ".join(self.out(n, "about" if about == "about" else about))))
            self.write(folder, str(ident), header, [("", n.get(text_key, "")), *((t, n.get(k, "")) for t, k in sections)],
                       kind)

    def rules(self) -> None:
        for b in self.e.kind("rules"):
            self.write("rules", b["id"], [("id", b["id"]), ("name", b["name"]),
                                          ("applies to", ", ".join(self.out(b, "governs")))],
                       [("", b.get("says", "")), ("Except", b.get("except", ""))], "rule")

    def roles(self) -> None:
        for u in self.e.kind("roles"):
            lines = []
            for a in u.get("actions", []):
                found = re.match(r"([A-Z]+\d+)\s+(.*)", a.get("action", ""))
                if not found or self.rename.get(found.group(1), found.group(1)) not in self.ids:
                    self.notes.append(f"{u['id']}: the action `{a.get('action')}` names no requirement; left out")
                    continue
                answer = {"yes": "yes", "no": "no"}.get(a.get("may"), "?")
                lines.append(f"- {answer}: {found.group(1)} {found.group(2)}")
            self.write("roles", u["id"], [("id", u["id"]), ("name", u["name"]), ("who", u.get("who", ""))],
                       [("Actions", "\n".join(lines))], "role")

    def entities(self) -> None:
        for n in self.e.kind("entities"):
            fields = table(["Field", "Meaning", "From"], [[f.get("name", ""), f.get("means", ""), ""]
                                                          for f in n.get("fields", [])]) if n.get("fields") else ""
            states = table(["State", "Means", "Moves to", "Seen in"],
                           [[state_id(s["id"]).split(".", 1)[1], "", ", ".join(self.keep((s.get("out") or {}).get("moves"))),
                             ", ".join(i for i in self.keep((s.get("out") or {}).get("moves as seen in"))
                                       if i[0] in "EXB")] for s in n.get("holds", [])]) if n.get("holds") else ""
            life = table(["State", "Event", "Guard", "Effect", "Next"],
                         [[l.get("state", ""), l.get("event", ""), l.get("guard", ""), l.get("effect", ""), l.get("next", "")]
                          for l in n.get("lifecycle", [])]) if n.get("lifecycle") else ""
            self.write("entities", n["id"], [("id", n["id"]), ("name", n["name"])],
                       [("", n.get("purpose", "")), ("Fields", fields), ("States", states), ("Lifecycle", life)], "entity")

    def rows(self, holds: list[dict]) -> list[list[str]]:
        out = []
        for e in holds:
            links = e.get("out") or {}
            out.append([e["id"].rsplit(".", 1)[1], e.get("name", ""), e.get("is", ""), e.get("does", ""),
                        e.get("states", ""), e.get("heard as", ""), ", ".join(self.keep(links.get("is"))),
                        ", ".join(self.keep(links.get("shows"))), ", ".join(self.keep(links.get("about"))),
                        ", ".join(self.keep(links.get("asks"))), ", ".join(self.keep(links.get("leads to")))])
        return out

    def split(self, stands: str) -> tuple[str, str]:
        ids = self.keep(re.findall(r"[A-Z]+\d+(?:\.[\w-]+)?|foundation:[\w-]+", stands or ""))
        return ", ".join(i for i in ids if self.kinds.get(i) == "requirement"), \
            ", ".join(i for i in ids if self.kinds.get(i) != "requirement")

    @staticmethod
    def shot(path: str) -> str:
        """A screenshot's path from the specification's folder, as a page's was from its own."""
        return path[path.index("evidence/"):] if "evidence/" in path else path

    def screens(self) -> None:
        head = ["#", "Element", "Kind", "What it shows and does", "States", "Heard as", "Component", "Shows", "About",
                "Asks", "Leads to"]
        for s in self.e.kind("screens"):
            page = self.e.page(s.get("at", ""))
            data = table(["What it shows or changes", "Shows", "About"],
                         [[d.get("what it shows or changes", ""), *self.split(d.get("stands on", ""))]
                          for d in s.get("data", [])]) if s.get("data") else ""
            evidence = lambda ids: ", ".join(i for i in self.keep(ids) if self.kinds.get(i) in ("finding", "contradiction", "rule"))  # noqa: E731
            states = []
            for r in table_rows(section(page, "States")) + table_rows(section(page, "Behaviour")):
                if len(r) >= 5:                         # a screenshot stands in what it shows: Evidence holds IDs alone
                    shots = [self.shot(s) for s in re.findall(r"[\w./-]+\.(?:png|jpe?g|gif|webp)", r[3], re.I)]
                    shown = " ".join([r[2], *(f"Seen in {s}." for s in shots)]).strip()
                    states.append([r[0], r[1], shown, evidence(re.findall(r"[A-Z]+\d+", r[3])), r[4]])
            transitions = [[t.get("from", ""), t.get("event", ""), t.get("to", ""),
                            ", ".join(i for i in self.keep([t["to"]] if re.fullmatch(r"SC\d+", t.get("to", "")) else [])),
                            ", ".join(self.keep(t.get("requirements"))), evidence(t.get("evidence"))]
                           for t in s.get("transitions", [])]
            variants = [[v.get("what differs, and for whom", ""), ", ".join(self.keep(re.findall(r"[A-Z]+\d+", v.get("stands on", ""))))]
                        for v in s.get("variants", [])]
            layout = [[l.get("what", ""), l.get("must be", ""), l.get("from", "")] for l in s.get("layout", [])]
            shown = sorted({p[2] for p in s.get("from parts", []) if len(p) == 3 and p[1] == "displays"}, key=natural)
            self.write("screens", s["id"], [
                ("id", s["id"]), ("name", s["name"]), ("kind", s.get("screen kind", "")), ("address", s.get("address", "")),
                ("who", s.get("who", "")), ("reached by", s.get("reached by", "")),
                ("displays", ", ".join(self.keep(shown)))], [
                ("", s.get("purpose", "")), ("Data", data),
                ("Elements", table(head, self.rows(s.get("holds", []))) if s.get("holds") else ""),
                ("States", table(["State", "Status", "What it shows", "Evidence", "Investigation"], states) if states else ""),
                ("Transitions", table(["From", "Event", "To", "Leads to", "Shows", "Evidence"], transitions) if transitions else ""),
                ("Variants", table(["What differs, and for whom", "About"], variants) if variants else ""),
                ("Layout", table(["What", "Must be", "From"], layout) if layout else "")], "screen")

    def drawings(self, c: dict) -> list[tuple[str, str, str]]:
        page = (self.e.folder / c.get("at", "").split("#", 1)[0])
        if not page.is_file():
            return []
        out = []
        for line in page.read_text(encoding="utf-8").splitlines():
            if line.startswith("| ") and "<" in line and not line.startswith("| Variant"):
                parts = [p.strip() for p in line.strip().strip("|").split(" | ")]
                if len(parts) >= 3:
                    out.append((parts[0], parts[-1], " | ".join(parts[1:-1])))
        return out

    def components(self) -> None:
        head = ["#", "Part", "Kind", "What it shows and does", "States", "Heard as", "Component", "Shows", "About",
                "Asks", "Leads to"]
        for c in self.e.kind("components"):
            drawn = self.drawings(c)
            rules = "\n".join(f"- {r['rule']}" + (f" ({r['stands on']})" if r.get("stands on") else "")
                              for r in c.get("rules", []))
            self.write("components", c["id"], [("id", c["id"]), ("name", c["name"]),
                                               ("made of", ", ".join(self.out(c, "made of")))], [
                ("", c.get("purpose", "")),
                ("Parts", table(head, self.rows(c.get("holds", []))) if c.get("holds") else ""),
                ("Variants", table(["Variant", "When"], [[n, w] for n, w, _ in drawn]) if drawn else ""),
                ("Rules", rules)], "component")
            figures = []
            for name, _, html in drawn:
                html = re.sub(r'data-variant="[^"]*"', f'data-variant="{name}"', html, count=1)
                if "data-variant=" not in html:
                    html = f'<span class="stage" data-variant="{name}">{html}</span>'
                figures.append(f"<figure>\n<figcaption>{name}</figcaption>\n{html}\n</figure>\n")
            path = self.t / "prototypes/components" / f"{c['id']}.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("".join(figures), encoding="utf-8", newline="\n")

    def foundations(self) -> None:
        for f in self.e.json("design/foundations.json").get("nodes", []):
            ident = self.rename[f["id"]]
            self.write("foundations", ident, [("id", ident), ("name", f.get("name", ""))], [("", f.get("says", ""))],
                       "foundation")

    def flows(self) -> None:
        for f in self.e.kind("flows"):
            page = self.e.page(f.get("at", ""))
            steps = "\n".join(f"{n}. {' '.join(s.split())}" for n, s in enumerate(f.get("steps", []), 1))
            self.write("flows", f["id"], [
                ("id", f["id"]), ("name", f["name"]), ("user", f.get("user", "")), ("trigger", f.get("trigger", "")),
                ("serves", ", ".join(self.out(f, "serves"))), ("passes", ", ".join(self.out(f, "passes"))),
                ("calls", ", ".join(self.out(f, "calls")))],
                [("", f.get("purpose", "")), ("Steps", steps), ("When it goes wrong", section(page, "When it goes wrong"))],
                "flow")

    def endpoints(self) -> None:
        tables = [("Who may call", "who may call", ["Caller", "May", "Else"], ["caller", "may", "else"]),
                  ("Takes", "takes", ["Name", "Where", "Type", "Required", "Rule"], ["name", "where", "type", "required", "rule"]),
                  ("Answers", "answers", ["Status", "When", "Holds"], ["status", "when", "holds"]),
                  ("Fails", "fails", ["Status", "When", "Says"], ["status", "when", "says"]),
                  ("Limits", "limits", ["What", "Is"], ["what", "is"])]
        for a in self.e.kind("endpoints"):
            body = [("", a.get("purpose", ""))]
            for title, key, head, keys in tables:
                rows = a.get(key) or []
                body.append((title, table(head, [[r.get(k, "") for k in keys] for r in rows]) if rows else ""))
            body.append(("Example", re.sub(r"<!--.*?-->\s*", "", section(self.e.page(a.get("at", "")), "Example"), flags=re.S).strip()))
            self.write("endpoints", a["id"], [("id", a["id"]), ("name", a["name"]), ("kind", a.get("endpoint kind", "")),
                                              ("surface", a.get("surface", "")), ("shows", ", ".join(self.out(a, "shows"))),
                                              ("about", ", ".join(self.out(a, "about")))], body, "endpoint")

    def evidence_files(self) -> None:
        """The earlier evidence's files, kept in evidence/: each page as the Markdown it holds, under the same
        name ending .md, every other file -- a screenshot, an API's description -- as it is. The page of every
        finding and the Evidence page were the earlier form's own: their findings and coverage are nodes now."""
        earlier = self.e.folder / "site/evidence"
        self.converted: dict[str, str] = {}             # an earlier page's name -> the new file's
        if not earlier.is_dir():
            return
        for path in sorted(earlier.rglob("*")):
            rel = path.relative_to(earlier).as_posix()
            if not path.is_file() or rel in ("index.html", "findings.html") or rel.startswith("staging/"):
                continue
            if path.suffix == ".html" and self.e.page(path.relative_to(self.e.folder).as_posix()):
                self.converted[path.name] = path.with_suffix(".md").name
        for path in sorted(earlier.rglob("*")):
            rel = path.relative_to(earlier).as_posix()
            if not path.is_file() or rel in ("index.html", "findings.html") or rel.startswith("staging/"):
                continue
            target = self.t / evidence.EVIDENCE / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if path.name in self.converted:
                text = self.e.page(path.relative_to(self.e.folder).as_posix())
                target.with_suffix(".md").write_text(self.renamed(text).strip("\n") + "\n", encoding="utf-8",
                                                     newline="\n")
            else:
                shutil.copyfile(path, target)
            self.written["evidence file"] += 1

    def renamed(self, text: str) -> str:
        """A text naming the earlier pages of the evidence by their new names: `V3-x.html` as `V3-x.md`, and
        `site/evidence/` as `evidence/`."""
        text = text.replace("site/evidence/", f"{evidence.EVIDENCE}/")
        return re.sub(r"[\w.-]+\.html\b", lambda m: self.converted.get(m.group(0), m.group(0)), text)

    def evidence(self) -> None:
        self.evidence_files()
        found = self.e.page("site/evidence/findings.html")
        covered: dict[str, list[list[str]]] = {}
        for row in table_rows(section(found, "Coverage")):
            if row and re.fullmatch(r"S\d+", row[0]):
                covered.setdefault(row[0], []).append((row + [""] * 5)[1:5])
        for s in self.e.kind("sources"):
            where = self.renamed(s.get("where", ""))
            there = evidence.source_place(self.t, where)
            rows = []
            for part, read, note, _held in covered.get(s["id"], []):
                part = self.renamed(part)
                printed = evidence.print_of(there, part) if there is not None and read != "not read" else ""
                rows.append([part, read, note, printed])
            self.write("sources", s["id"], [("id", s["id"]), ("name", s.get("material", "")), ("role", s.get("role", "")),
                                            ("where", where), ("version", s.get("version", ""))],
                       [("Coverage", table(["Part", "Read", "Note", "Print"], rows) if rows else "")], "source")
        for f in self.e.kind("findings"):
            words = [w for w in f.get("became", []) if not re.fullmatch(r"[A-Z]+\d+(?:\.[\w-]+)?", w)]
            self.write("findings", f["id"], [
                ("id", f["id"]), ("source", ", ".join(self.out(f, "from"))), ("where", self.renamed(f.get("where", ""))),
                ("lens", f.get("lens", "")), ("seen", f.get("seen", "")), ("became", ", ".join(self.out(f, "became"))),
                ("became in", ", ".join(words))],
                [("", f.get("found", "")), ("Quote", f.get("quote", "")), ("Limits", f.get("limits", ""))], "finding")
        for x in self.e.kind("contradictions"):
            words = [w for w in x.get("became", []) if not re.fullmatch(r"[A-Z]+\d+(?:\.[\w-]+)?", w)]
            self.write("contradictions", x["id"], [
                ("id", x["id"]), ("between", ", ".join(self.out(x, "between"))),
                ("became", ", ".join(self.out(x, "became"))), ("became in", ", ".join(words)),
                ("settled", "yes" if x.get("settled") is True else "no" if x.get("settled") is False else x.get("settled") or "")],
                [("", x.get("says", ""))], "contradiction")

    def prototypes(self) -> None:
        site = self.e.folder / "site"
        pages = sorted((site / "prototype").glob("SC*.html"))
        if not pages:
            return
        body_class = ""
        for page in pages:
            text = page.read_text(encoding="utf-8")
            found = re.search(r"<body([^>]*)>", text)
            body_class = body_class or (found.group(1) if found else "")
            body = text[text.index("<body"):]
            body = body[body.index(">") + 1:body.rindex("</body>")]
            body = re.sub(r"<!--.*?-->\s*", "", body, flags=re.S)
            body = body.replace("data-spec-element=", "data-el=").replace("data-spec-part=", "data-part=")
            body = re.sub(r'\s+data-spec-[a-z-]+="[^"]*"', "", body)
            body = re.sub(r"\b(SC\d+)-[a-z0-9-]+\.html", r"\1.html", body)
            body = body.replace("../assets/", "assets/")
            path = self.t / "prototypes/screens" / f"{page.name.split('-', 1)[0]}.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body.strip() + "\n", encoding="utf-8", newline="\n")
        assets = self.t / "prototypes/assets"
        for name in ("css/product.css", "js/sample.js", "js/prototype.js"):
            if (site / "assets" / name).is_file():
                (assets / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(site / "assets" / name, assets / name)
                if name.endswith(".js"):                # what it finds its elements by has a shorter name here
                    held = (assets / name).read_text(encoding="utf-8")
                    (assets / name).write_text(held.replace("data-spec-element", "data-el").replace("data-spec-part", "data-part"), encoding="utf-8", newline="\n")
        for img in (site / "assets/img").glob("*") if (site / "assets/img").is_dir() else []:
            if img.is_file() and not img.name.startswith("how-it-flows"):
                (assets / "img").mkdir(parents=True, exist_ok=True)
                shutil.copyfile(img, assets / "img" / img.name)
        if (site / "design-system/tokens.json").is_file():
            (self.t / "prototypes/tokens.json").write_text(
                self.renamed((site / "design-system/tokens.json").read_text(encoding="utf-8")), encoding="utf-8",
                newline="\n")
        folder.write_shell(self.t, body_class)

    def run(self) -> None:
        self.document()
        self.goals()
        self.requirements()
        self.simple("qualities", "quality", "requirement", [("name", "quality"), ("status", "status")], [],
                    about="met by")
        self.simple("constraints", "constraint", "says", [], [])
        self.simple("decisions", "decision", "decision", [], [("Because", "because"), ("Instead of", "instead")])
        self.simple("questions", "question", "question", [("answers", "answers")], [("Why", "why")])
        self.simple("risks", "risk", "risk", [("of", "of"), ("likelihood", "likelihood")],
                    [("If it happens", "if"), ("Mitigation", "mitigation")])
        self.simple("terms", "term", "means", [("name", "term"), ("also", "also")], [], about="names")
        self.rules()
        self.roles()
        self.entities()
        self.screens()
        self.components()
        self.foundations()
        self.flows()
        self.endpoints()
        self.evidence()
        self.prototypes()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("earlier", type=Path, help="the earlier specification's folder: the one holding site/")
    parser.add_argument("target", type=Path, help="the new specification's folder")
    parser.add_argument("--replace", action="store_true", help="write over a folder that holds a specification")
    args = parser.parse_args()
    earlier, target = args.earlier.resolve(), args.target.resolve()
    if not (earlier / "site").is_dir() or not (earlier / "tools").is_dir():
        parser.error(f"{earlier}: not a specification of the earlier form -- it holds no site/ and tools/")
    if (target / "data").exists() and not args.replace:
        parser.error(f"{target}: it holds a specification already; --replace writes over it")
    for name in ("data", "prototypes", "stamps", "evidence", "app", ".cache"):
        shutil.rmtree(target / name, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    importer = Importer(Earlier(earlier), target)
    importer.run()
    folder.write_app(target)
    print(f"{target}: " + ", ".join(f"{n} {k}" for k, n in sorted(importer.written.items())))
    if importer.dropped:
        print("links not carried, to what the new form keeps as text: " +
              ", ".join(f"{n} to {k}" for k, n in importer.dropped.most_common()))
        for kind, lost in sorted(importer.lost.items()):
            print(f"  {kind}: {', '.join(sorted(lost, key=natural)[:12])}" + (" ..." if len(lost) > 12 else ""))
    for note in importer.notes:
        print(f"note: {note}")
    sys.path.insert(0, str(target / "app"))
    import load as loading                      # noqa: PLC0415 -- the copy just written, as the folder will run it
    done = loading.load(target)
    for file, line, message in done.problems:
        print(f"{file}:{line}: {message}" if line else f"{file}: {message}")
    print(f"{'PASSED' if not done.problems else 'FAILED'} -- {len(done.problems)} problem(s); "
          f"{len(done.nodes)} node(s), {len(done.edges)} link(s)")
    return 1 if done.problems else 0


if __name__ == "__main__":
    sys.exit(main())
