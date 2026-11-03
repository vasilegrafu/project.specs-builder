"""What moved in the drawing between two snapshots: each screen's elements and fields, the style rules, the tokens and the
sample data, and which screens what moved reaches."""
from __future__ import annotations

import re
from types import SimpleNamespace

import prototypes
from answer import short
from cascade import Styles
from drawn import all_pages, forms, outline
from load import natural
from markup import when_said
from samples import sample_values

ELEMENT_KEYS = ("is", "says", "leads to", "opens as", "class")


# --- what a snapshot keeps of them, and what moved ---------------------------------------------------------------------
def drawn_of(model) -> dict:
    """What the prototypes draw, as a snapshot keeps it: each screen's elements and fields, the product's style rules,
    its tokens and its sample data."""
    screens = {}
    for page in all_pages(model):
        asked = SimpleNamespace(id=page.screen, state="", variant="")
        rows = outline(model, asked).data["elements"]
        fields = [f for form in forms(model, asked).data["forms"] for f in form["fields"]]
        screens[page.screen] = {"prototype": page.rel,
                                "elements": [{k: r[k] for k in ELEMENT_KEYS if r.get(k)} | ({"handle": r["owner"]} if r["owner"] else {})
                                             | ({"shows": when_said(r["conditions"])} if r.get("conditions") else {}) for r in rows],
                                "fields": [{k: v for k, v in f.items() if k != "line"} for f in fields]}
    sheet = Styles(model.root)
    return {"screens": screens,
            "styles": [{"selector": s, "media": r.media, "declarations": dict(r.declarations)} for r in sheet.rules for s in r.selectors],
            "tokens": {prototypes.variable(t): str(t["value"]) for t in prototypes.flat_tokens(model.root)},
            "sample": sample_values(model.root)[0]}


def flat(value: object, path: str = "") -> dict:
    """A nested value as its leaves, by their paths: `SAMPLE.cart.0.qty` -- so that what moved is the leaf."""
    if isinstance(value, dict):
        return {k: v for key, inner in value.items() for k, v in flat(inner, f"{path}.{key}" if path else key).items()}
    if isinstance(value, list):
        return {k: v for at, inner in enumerate(value) for k, v in flat(inner, f"{path}.{at}").items()}
    return {path: value}


def compare(was: dict, now: dict) -> dict:
    """What moved in the drawing between two snapshots: each screen's elements and fields, the style rules, the tokens
    and the sample data."""
    screens: dict[str, dict] = {}
    for ref in sorted(set(was.get("screens", {})) | set(now.get("screens", {})), key=natural):
        old, new = was.get("screens", {}).get(ref), now.get("screens", {}).get(ref)
        if old == new:
            continue
        if not old or not new:
            screens[ref] = {"prototype": "new" if new else "gone"}
            continue
        moved = []
        for handle in sorted({e.get("handle", "") for e in old["elements"] + new["elements"]}, key=natural):
            a = [e for e in old["elements"] if e.get("handle", "") == handle]
            b = [e for e in new["elements"] if e.get("handle", "") == handle]
            lost, added = [e for e in a if e not in b], [e for e in b if e not in a]
            for one, other in zip(lost, added):         # an element that changed in place: what of it moved
                moved.append({"handle": handle or "·", "changed": [(k, short(one.get(k, "-"), 70), short(other.get(k, "-"), 70))
                                                                  for k in sorted(set(one) | set(other)) if one.get(k) != other.get(k)]})
            moved += [{"handle": handle or "·", "gone": short(e.get("says") or e.get("is", ""), 70)} for e in lost[len(added):]]
            moved += [{"handle": handle or "·", "new": short(e.get("says") or e.get("is", ""), 70)} for e in added[len(lost):]]
        fields = [("field", short(f.get("label") or f.get("handle"), 50), "gone") for f in old["fields"] if f not in new["fields"]]
        fields += [("field", short(f.get("label") or f.get("handle"), 50), "new or changed") for f in new["fields"] if f not in old["fields"]]
        screens[ref] = {"elements": moved, "fields": fields}

    def rules(held: dict) -> dict:
        """Each selector's declarations under each @media, from every rule it heads, the later winning."""
        out: dict = {}
        for r in held.get("styles", []):
            out.setdefault((r["media"], r["selector"]), {}).update(r["declarations"])
        return out
    r_was, r_now = rules(was), rules(now)
    moved_styles = []
    for key in sorted(set(r_was) | set(r_now)):
        a, b = r_was.get(key, {}), r_now.get(key, {})
        moved_styles += [{"media": key[0], "selector": key[1], "property": p, "was": a.get(p, "-"), "is": b.get(p, "-")}
                         for p in sorted(set(a) | set(b)) if a.get(p) != b.get(p)]
    tokens_was, tokens_now = was.get("tokens", {}), now.get("tokens", {})
    tokens = [(k, tokens_was.get(k, "-"), tokens_now.get(k, "-")) for k in sorted(set(tokens_was) | set(tokens_now))
              if tokens_was.get(k) != tokens_now.get(k)]
    a, b = flat(was.get("sample", {})), flat(now.get("sample", {}))
    sampled = [(k, short(a.get(k, "-"), 60), short(b.get(k, "-"), 60)) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
    return {"screens": screens, "styles": moved_styles, "tokens": tokens, "sample": sampled}


def reached_by(moved: dict, drawn: dict) -> list[str]:
    """The screens a change of the styles or the tokens reaches: those whose elements carry a class its selector names,
    or a class of a rule that uses it; every screen where it names none."""
    screens = drawn.get("screens", {})
    changes = [*moved["styles"], *({"selector": "", "property": t[0]} for t in moved["tokens"])]
    classes: set[str] = set()
    for change in changes:
        classes |= set(re.findall(r"\.([\w-]+)", change["selector"]))
        if change["property"].startswith("--"):
            for rule in drawn.get("styles", []):
                if f"var({change['property']}" in " ".join(rule["declarations"].values()):
                    classes |= set(re.findall(r"\.([\w-]+)", rule["selector"]))
    hit = [ref for ref, s in screens.items() if any(set(e.get("class", "").split()) & classes for e in s["elements"])]
    return sorted(hit or screens, key=natural) if changes else []


def changes_table(screens: dict) -> list[list]:
    """What moved on the screens, a row each: the screen, the element, what, what it was, what it is."""
    drawn: list[tuple] = []
    for ref, held in screens.items():
        if "prototype" in held:
            drawn.append((ref, "-", f"its prototype is {held['prototype']}", "", ""))
            continue
        for e in held["elements"]:
            if "changed" in e:
                drawn += [(ref, e["handle"], k, w, n) for k, w, n in e["changed"]]
            else:
                drawn.append((ref, e["handle"], "new" if "new" in e else "gone", e.get("gone", ""), e.get("new", "")))
        drawn += [(ref, "-", what, label, how) for what, label, how in held["fields"]]
    return [list(r) for r in dict.fromkeys(drawn)]      # a card drawn three times moved once
