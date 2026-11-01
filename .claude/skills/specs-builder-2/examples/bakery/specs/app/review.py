"""What each node was last reviewed against, so that a change reaches every node that stands on what changed.

Every link remembers the node it stands on as it was when the link was last reviewed: in stamps/reviewed.json,
each link's stamp is that node's print then, and each print keeps what the node meant -- so a node made stale is
shown what moved, before and after, not only that something did. Which end of a link stands on which is the
relation's `stale` in the grammar: `to`, the node a link leaves stands on the one it reaches (an element on the
requirement it shows); `from`, the other way; `both`; `none`.

A node's print is what it means, the links it states, and -- for a kind whose `print` says so, as a requirement
does its criteria -- the prints of its rows: a criterion changed changes its requirement, a screen's element does
not change the screen. A stamp is kept when its link goes, and found again when the link comes back: untying and
tying again never clears what was owed. Only confirming does: `confirm SC3.13` stamps SC3.13's links with what they
reach now, and is logged as a change of its own. A link new since the last stamping is stamped as it is -- whoever
made it made it against what is there.

A drawing is held the same way, for its words are in its file and no link reaches them: `drawn` keeps, for each node
with a prototype, what it and all it stands on were, and its file, when the two were last in step. What moved under a
file that did not is told by `undrawn`, until the file is redrawn or `confirm-drawn` says it still holds.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

import load as loading
import prototypes

REVIEWED = "stamps/reviewed.json"


def prints(g: dict, done: loading.Load) -> dict[str, str]:
    """Each node's print: its meaning, its own links, and its rows' prints where its kind counts them."""
    links: dict[str, list[str]] = {}
    rows: dict[str, list[str]] = {}
    for e in done.edges:
        if e.rel == "has":
            rows.setdefault(e.src, []).append(e.dst)
        else:
            links.setdefault(e.src, []).append(f"{e.rel} {e.dst}")
    out: dict[str, str] = {}

    def of(ident: str) -> str:
        if ident not in out:
            node = done.nodes[ident]
            said = {"meaning": loading.meaning(g, node), "links": sorted(links.get(ident, []))}
            if g["kinds"][node.kind].get("print rows"):
                said["rows"] = [of(r) for r in sorted(rows.get(ident, []), key=natural)]
            raw = json.dumps(said, sort_keys=True, ensure_ascii=False)
            out[ident] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return out[ident]

    for ident in done.nodes:
        of(ident)
    return out


def natural(ident: str) -> list:
    return [int(x) if x.isdigit() else x for x in re.findall(r"\d+|\D+", ident)]


def ends(g: dict, edge: loading.Edge) -> list[tuple[str, str]]:
    """Each (node that stands, node it stands on) a link makes, by its relation's `stale`."""
    way = g["relations"][edge.rel].get("stale", "to")
    return {"to": [(edge.src, edge.dst)], "from": [(edge.dst, edge.src)],
            "both": [(edge.src, edge.dst), (edge.dst, edge.src)], "none": []}[way]


def key(edge: loading.Edge, far: str) -> str:
    return f"{edge.src} {edge.rel} {edge.dst} @{far}"


def held(root: Path) -> dict:
    try:
        said = json.loads((root / REVIEWED).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except ValueError as wrong:
        raise ValueError(f"{REVIEWED} cannot be read ({wrong}): mend it by hand, or take it out to start every "
                         f"stamp again -- nothing is guessed in its place") from None
    return said if isinstance(said.get("links"), dict) else {}


def stale(g: dict, done: loading.Load, stamps: dict, now: dict | None = None) -> list[dict]:
    """Each node standing on something that changed since it was last reviewed against it: what it stands on, by
    which link, and what that meant then and means now. `now` is the prints, where the asker holds them."""
    now = prints(g, done) if now is None else now
    seen = stamps.get("seen", {})
    out = []
    for edge in done.edges:
        for near, far in ends(g, edge):
            was = stamps.get("links", {}).get(key(edge, far))
            if was is None or was == now.get(far):
                continue
            out.append({"node": near, "on": far, "link": f"{edge.src} {edge.rel} {edge.dst}",
                        "was": seen.get(was, {}), "now": loading.meaning(g, done.nodes[far])})
    return sorted(out, key=lambda s: (natural(s["node"]), natural(s["on"])))


def standing(g: dict, done: loading.Load, now: dict) -> dict[str, str]:
    """For each node with a prototype, one print of what its drawing depends on: itself, its rows, and all they stand on."""
    held = {i: [now[i]] for i, n in done.nodes.items() if g["kinds"][n.kind].get("prototype")}
    if not held:
        return {}
    for ident, node in done.nodes.items():
        if node.parent in held:
            held[node.parent].append(now[ident])
    for edge in done.edges:
        for near, far in ends(g, edge):
            top = done.nodes[near].parent or near if near in done.nodes else None
            if top in held and far in now:
                held[top].append(now[far])
    return {i: hashlib.sha256("|".join(sorted(said)).encode("utf-8")).hexdigest()[:16] for i, said in held.items()}


def file_print(g: dict, done: loading.Load, ident: str) -> str:
    """A print of a node's drawing, as the file stands."""
    path = done.root / prototypes.PROTOTYPES / g["kinds"][done.nodes[ident].kind]["prototype"] / f"{ident}.html"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.is_file() else ""


def undrawn(g: dict, done: loading.Load, stamps: dict, now: dict | None = None) -> list[str]:
    """Each node whose drawing has not moved though something it shows has, and so may say what is no longer so. Only those
    the prints set apart have their files read."""
    marks = stamps.get("drawn", {})
    if not marks:
        return []
    now = prints(g, done) if now is None else now
    return sorted((i for i, s in standing(g, done, now).items()
                   if i in marks and marks[i]["stands"] != s and marks[i]["file"] == file_print(g, done, i)), key=natural)


def redrawn(g: dict, done: loading.Load, stamps: dict) -> dict:
    """The stamps with each drawing whose file moved taken as in step with `done`: read before a change, so that the change
    is measured from the drawing as it stands."""
    marks = stamps.get("drawn", {})
    if not marks:
        return stamps
    stands = standing(g, done, prints(g, done))
    fresh = {i: ({"stands": stands[i], "file": file_print(g, done, i)} if i in stands and mark["file"] != file_print(g, done, i) else mark)
             for i, mark in marks.items()}
    return {**stamps, "drawn": fresh}


def stamped(g: dict, done: loading.Load, stamps: dict, confirm: set[str] | None = None,
            gone: set[str] | None = None, drawn: set[str] | None = None) -> dict:
    """The stamps after a change: every link with none stamped as it is; the links of each node in `confirm`
    stamped again with what they reach now; the stamps of nodes `gone` taken out. Every other stamp is kept, its
    link there or not. A drawing is stamped when it is new, when its file moved, or when `drawn` names it."""
    now = prints(g, done)
    links = dict(stamps.get("links", {}))
    seen = dict(stamps.get("seen", {}))
    for edge in done.edges:
        for near, far in ends(g, edge):
            k = key(edge, far)
            if k not in links or (confirm and near in confirm):
                links[k] = now[far]
                seen[now[far]] = loading.meaning(g, done.nodes[far])
    if gone:
        links = {k: v for k, v in links.items() if not ({k.split(" ", 1)[0], k.rsplit("@", 1)[1]} & gone)}
    used = set(links.values())
    marks = dict(stamps.get("drawn", {}))
    for ident, stands in standing(g, done, now).items():
        file = file_print(g, done, ident)
        if ident not in marks or marks[ident]["file"] != file or (drawn and ident in drawn):
            marks[ident] = {"stands": stands, "file": file}
    return {"links": dict(sorted(links.items())), "seen": {p: m for p, m in sorted(seen.items()) if p in used},
            "drawn": {i: m for i, m in sorted(marks.items()) if i in done.nodes}}


def moved(was: object, now: object, around: int = 4) -> str:
    """What moved between two texts, cut to the words that differ with a few either side: `...one to [five, or
    raise ... already -> six]`. Anything else, both said whole."""
    if not (isinstance(was, str) and isinstance(now, str)):
        return f"{was!r} -> {now!r}"
    a, b = was.split(), now.split()
    head = 0
    while head < min(len(a), len(b)) and a[head] == b[head]:
        head += 1
    tail = 0
    while tail < min(len(a), len(b)) - head and a[-1 - tail] == b[-1 - tail]:
        tail += 1
    before = " ".join(a[max(0, head - around):head])
    after = " ".join(a[len(a) - tail:len(a) - tail + around]) if tail else ""
    lost, gained = " ".join(a[head:len(a) - tail]), " ".join(b[head:len(b) - tail])
    return (("..." if head > around else "") + (before + " " if before else "") + f"[{lost} -> {gained}]"
            + (" " + after if after else "") + ("..." if tail > around else ""))


def save(root: Path, stamps: dict) -> None:
    path = root / REVIEWED
    path.parent.mkdir(parents=True, exist_ok=True)
    fresh = path.with_name(path.name + ".new")
    fresh.write_text(json.dumps(stamps, ensure_ascii=False, indent=0, sort_keys=True) + "\n",
                     encoding="utf-8", newline="\n")
    os.replace(fresh, path)
