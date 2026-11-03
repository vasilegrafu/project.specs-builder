"""The specification as whoever builds from it reads it: its nodes and links, both ways, and the slices it is built in.

A slice is a piece of work that ends in something that runs. First the foundation everything stands on; then what no
flow passes, the home page among them; then one slice for each flow, in the order of the release plan, a must before a
should where there is none, and a flow after one it depends on. A requirement is completed in the last slice that builds
something showing it, never before the first flow that names it, and never before what it depends on: until then, some
of what its criteria need does not exist, and a test of it could only pretend.
"""
from __future__ import annotations

import difflib
import re
from pathlib import Path

import api
import finish
import load as loading
from load import natural

PRIORITY = {"must": 0, "should": 1, "could": 2, "wont": 3}
EVIDENCE = ("finding", "source", "contradiction")       # what a specification stands on, never what is built
FOUNDATION = ("document", "quality", "constraint", "decision", "foundation", "term", "entity", "rule", "role", "component")
REQUIREMENT_RE = re.compile(r"(?<![A-Za-z0-9])R\d+(?![0-9])")


class Model:
    """The data as loaded, with each node's links found at once rather than searched for."""

    def __init__(self, root: Path, done: loading.Load) -> None:
        self.root, self.done, self.g, self.nodes = root, done, loading.grammar(), done.nodes
        self.outward: dict[str, list[tuple[str, str]]] = {}
        self.inward: dict[str, list[tuple[str, str]]] = {}
        self.held: dict[str, list[str]] = {}
        self.cut: list[dict] | None = None
        for e in done.edges:
            self.outward.setdefault(e.src, []).append((e.rel, e.dst))
            self.inward.setdefault(e.dst, []).append((e.rel, e.src))
        for n in done.nodes.values():
            if n.parent:
                self.held.setdefault(n.parent, []).append(n.id)

    def need(self, ref: str) -> loading.Node:
        """A node by its ID; an ID there is not is answered with the nearest there are."""
        node = self.nodes.get(ref)
        if node is None:
            near = difflib.get_close_matches(ref, [*self.nodes, "foundation", "rest"], n=4, cutoff=0.5)
            raise KeyError(f"{ref}: no node has that ID" + (f"; the nearest are {', '.join(near)}" if near else "")
                           + " -- `spec.py list <kind>` lists them")
        return node

    def kind(self, ref: str) -> str:
        return self.nodes[ref].kind if ref in self.nodes else ""

    def name(self, ref: str) -> str:
        node = self.nodes.get(ref)
        return api.label(self.g, node.kind, node.fields) if node else ""

    def named(self, ref: str) -> str:
        """An ID with its name beside it, as every answer gives it."""
        said = self.name(ref)
        return f"{ref} {said}" if said else ref

    def text(self, ref: str) -> str:
        return finish.text_of(self.g, self.nodes[ref])

    def of_kind(self, kind: str) -> list[str]:
        return sorted((i for i, n in self.nodes.items() if n.kind == kind), key=natural)

    def rows(self, ref: str) -> list[str]:
        """The nodes held inside a node, in order: a screen's elements, a component's parts, a requirement's criteria."""
        return sorted(self.held.get(ref, []), key=natural)

    def top(self, ref: str) -> str:
        return self.nodes[ref].parent or ref if ref in self.nodes else ref

    def out(self, ref: str, *rels: str) -> list[str]:
        return [b for r, b in self.outward.get(ref, []) if r != "has" and (not rels or r in rels)]

    def into(self, ref: str, *rels: str) -> list[str]:
        return [a for r, a in self.inward.get(ref, []) if r != "has" and (not rels or r in rels)]

    def priority(self, ref: str) -> str:
        return str(self.nodes[ref].fields.get("priority") or "") if ref in self.nodes else ""

    def building(self, refs: list[str]) -> list[str]:
        """What is for building among these: the evidence left out."""
        return [r for r in refs if self.kind(r) not in EVIDENCE]

    def carried(self, flow: str) -> list[str]:
        """The requirements a flow's steps and what goes wrong in it name, in the order they name them."""
        f = self.nodes[flow].fields
        named = finish.STORY_ID.findall(f"{f.get('steps') or ''}\n{f.get('goes wrong') or ''}")
        return [r for r in dict.fromkeys(named) if self.kind(r) == "requirement"]

    def shown_by(self, refs: list[str]) -> list[str]:
        """The requirements a set of nodes shows: themselves and what they hold; a flow, what its steps name."""
        found: set[str] = set()
        for ref in refs:
            for node in (ref, *self.rows(ref)):
                found.update(r for r in self.out(node, "shows") if self.kind(r) == "requirement")
            if self.kind(ref) == "flow":
                found.update(self.carried(ref))
        return sorted(found, key=natural)

    def questions_on(self, refs: list[str]) -> list[str]:
        """The open questions that touch these nodes: those about them or what they hold, and those their rows ask."""
        found: set[str] = set()
        for ref in refs:
            for node in (ref, *self.rows(ref)):
                found.update(q for q in self.into(node, "about") if self.kind(q) == "question")
                found.update(q for q in self.out(node, "asks") if self.kind(q) == "question")
        return sorted(found, key=natural)

    def release_of(self) -> dict[str, int]:
        """Each requirement the release plan names, and the place of its release in the plan."""
        plan = str(self.nodes["document"].fields.get("release plan") or "") if "document" in self.nodes else ""
        found: dict[str, int] = {}
        for at, row in enumerate([line for line in plan.splitlines() if line.lstrip().startswith("|")][2:]):
            for ref in REQUIREMENT_RE.findall(row):
                found.setdefault(ref, at)
        return found

    def release_name(self, ref: str) -> str:
        """The release the plan puts a requirement in, as `, release Later`; nothing where there is no plan."""
        plan = str(self.nodes["document"].fields.get("release plan") or "") if "document" in self.nodes else ""
        rows = [line for line in plan.splitlines() if line.lstrip().startswith("|")][2:]
        at = self.release_of().get(ref)
        return "" if at is None or at >= len(rows) else f", release {' '.join(rows[at].strip().strip('|').split('|')[0].split())}"

    def order(self) -> list[str]:
        """The requirements to build, each after what it depends on, the musts first; never a wont."""
        wanted = [n for n in self.nodes.values() if n.kind == "requirement" and n.fields.get("priority") != "wont"]
        ids = {n.id for n in wanted}
        pending = sorted(wanted, key=lambda n: (PRIORITY.get(str(n.fields.get("priority")), 9), natural(n.id)))
        placed: list[str] = []
        done: set[str] = set()
        while pending:
            node = next((n for n in pending if all(d in done or d not in ids for d in self.out(n.id, "depends on"))),
                        pending[0])                     # a cycle is the loader's to refuse; here, the first goes
            placed.append(node.id)
            done.add(node.id)
            pending.remove(node)
        return placed

    def flows_in_order(self, flows: list[dict], release: dict[str, int]) -> list[dict]:
        """The flows by release and priority, each after a flow that carries what it depends on."""
        def rank(piece: dict) -> tuple:
            refs = piece["shows"]
            return (min((release.get(r, 99) for r in refs), default=99),
                    min((PRIORITY.get(self.priority(r), 4) for r in refs), default=4), natural(piece["id"]))
        pending, placed = sorted(flows, key=rank), []
        while pending:
            done = {r for p in placed for r in p["shows"]}

            def waits(piece: dict) -> bool:
                needed = {d for r in piece["carries"] for d in self.out(r, "depends on")} - set(piece["carries"]) - done
                return any(needed & set(other["carries"]) for other in pending if other is not piece)
            piece = next((p for p in pending if not waits(p)), pending[0])
            placed.append(piece)
            pending.remove(piece)
        return placed

    def slices(self) -> list[dict]:
        if self.cut is None:
            self.cut = loading.remembered(self.done, "slices", self.cutting)
        return self.cut

    def cutting(self) -> list[dict]:
        """The order to build the product in, each slice with what it builds, the requirements it completes and those
        it carries on, its rules, how many criteria say it is done, and what is not settled in it."""
        out: list[dict] = [{"id": "foundation", "name": "What everything stands on",
                            "nodes": [r for kind in FOUNDATION for r in self.of_kind(kind)]}]
        passed: set[str] = set()
        made = []
        for flow in self.of_kind("flow"):
            screens, endpoints = self.out(flow, "passes"), self.out(flow, "calls")
            passed.update(screens + endpoints)
            made.append({"id": flow, "name": self.name(flow), "nodes": [*endpoints, *screens, flow],
                         "carries": self.carried(flow), "shows": self.shown_by([flow, *screens, *endpoints])})
        release = self.release_of()
        alone = [r for kind in ("endpoint", "screen") for r in self.of_kind(kind) if r not in passed]
        out.append({"id": "rest", "name": "What no flow passes", "nodes": alone})
        out += self.flows_in_order(made, release)
        first: dict[str, int] = {}                      # each node, and the slice that builds it: the first that holds it
        for at, piece in enumerate(out):
            for ref in piece["nodes"]:
                first.setdefault(ref, at)
        order = self.order()
        home: dict[str, int] = {}
        for ref in order:
            naming = [at for at, piece in enumerate(out) if ref in piece.get("carries", [])]
            showing = {self.top(node) for node in self.into(ref, "shows")}
            places = [first[node] for node in showing if node in first]
            needed = [home[d] for d in self.out(ref, "depends on") if d in home]    # `order` places what it depends on first
            home[ref] = max([*places, *naming[:1], *needed], default=1)
        built: set[str] = set()
        for at, piece in enumerate(out):
            shown = set(self.shown_by(piece["nodes"])) if piece["id"] != "foundation" else set()
            piece["new requirements"] = [r for r in order if home[r] == at]
            piece["requirements"] = [r for r in order if r in shown or home[r] == at]
            piece["new"] = [r for r in piece["nodes"] if r not in built]
            piece["earlier"] = [r for r in piece["nodes"] if r in built]
            built.update(piece["nodes"])
            piece["rules"] = sorted({b for r in piece["new requirements"] for b in self.out(r, "enforces")}
                                    | {r for r in piece["new"] if self.kind(r) == "rule"}, key=natural)
            piece["criteria"] = sum(len(self.rows(r)) for r in piece["new requirements"])
            piece["later"] = [r for r in piece["new requirements"] if release.get(r, 0) > 0
                              or self.priority(r) in ("should", "could")]
            piece["blocked by"] = self.questions_on([*piece["new"], *piece["new requirements"]])
            piece["needs first"] = sorted({d for r in piece["new requirements"] for d in self.out(r, "depends on")
                                           if home.get(d, 0) > at}, key=natural)
            piece.pop("carries", None)
            piece.pop("shows", None)
        return [p for p in out if p["nodes"] or p["new requirements"]]

    def slice(self, ref: str) -> dict | None:
        return next((p for p in self.slices() if p["id"] == ref), None)
