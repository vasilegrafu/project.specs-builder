"""What the prototypes draw, read from them: a screen's elements as a tree, every word it shows, its fields and their
limits, where each element leads and what leads to it, what each state and variant changes and the widths it changes
at, the values an element is drawn with -- the product's styles and tokens, resolved -- the sample data, the messages,
and the cases a test of the screen checks.

A prototype is a picture to build to, never code to copy: each answer says what is drawn, so that it is built in the
product's own technology. What an element means is its row in the data; only what it looks like and says is read here.
"""
from __future__ import annotations

import html
import json
import posixpath
import re

import prototypes
from answer import Answer, short, table
from load import natural
from cascade import matches, Styles
from markup import CONDITIONS, FIELD_RULES, HANDLE_RE, HEADINGS, INLINE, INTERACTIVE, Mark, Page, SCREEN_FILE_RE, shows, UNSEEN, when_said, WORD_ATTRIBUTES
from samples import SAMPLE, sample_values

# what a property a parent sets reaches its children with, as CSS says
INHERITED = {"color", "font", "font-family", "font-size", "font-weight", "font-style", "line-height", "letter-spacing",
             "text-align", "text-transform", "white-space", "visibility", "cursor", "list-style", "word-spacing"}
SUMMARY = ("display", "color", "background", "background-color", "font-size", "font-weight", "padding", "margin",
           "border", "border-left", "border-radius", "gap", "grid-template-columns", "width", "max-width")


def prototype_of(model, ref: str) -> str:
    """The prototype file of a screen or a component, from the specification's folder."""
    folder = model.g["kinds"].get(model.kind(ref), {}).get("prototype")
    return f"{prototypes.PROTOTYPES}/{folder}/{ref}.html" if folder else ""


def page_of(model, ref: str) -> Page:
    """The prototype of a screen or a component, parsed."""
    rel = prototype_of(model, model.need(ref).id)
    if not rel:
        raise KeyError(f"{ref} is a {model.kind(ref)}: this answers for a screen or a component -- `spec.py list screen` lists them")
    if not (model.root / rel).is_file():
        raise KeyError(f"{ref}: it has no prototype yet, {rel}")
    return Page(model.root, rel, ref)


def all_pages(model) -> list[Page]:
    return [Page(model.root, prototype_of(model, ref), ref) for ref in model.of_kind("screen")
            if (model.root / prototype_of(model, ref)).is_file()]


def target_of(href: str) -> tuple[str, str]:
    """Where a link leads: a screen with how it opens, a place on the page, or elsewhere."""
    if not href:
        return "", ""
    path, _, rest = href.partition("?")
    path, _, anchor = path.partition("#")
    if re.match(r"[a-z]+:|//", href):
        return "elsewhere", href
    if not path and anchor:
        return "this page", f"#{anchor}"
    found = SCREEN_FILE_RE.match(posixpath.basename(path))
    return (found.group(1), rest) if found else ("a file", href)


def significant(page: Page, node: Mark) -> bool:
    return bool(page.handle(node)) or node.tag in INTERACTIVE or node.tag in HEADINGS or node.tag == "img" \
        or any(node.attrs.get(a) for a in CONDITIONS) or node.attrs.get("role") in ("alert", "status", "dialog")


def what_it_is(node: Mark) -> str:
    kind = f"input[{node.attrs.get('type', 'text')}]" if node.tag == "input" else node.tag
    return kind + (f" role={node.attrs['role']}" if node.attrs.get("role") else "")


def stands_on(model, handle: str) -> list[str]:
    """What an element's row in the data says it is, shows, is about, asks and leads to; the evidence left out."""
    out = []
    for rel in ("is", "shows", "about", "asks", "leads to"):
        ends = model.building(model.out(handle, rel)) if handle else []
        if ends:
            out.append(f"{rel} {', '.join(ends)}")
    return out


# --- outline ----------------------------------------------------------------------------------------------------------
def outline(model, args) -> Answer:
    ref, state, variant = args.id, args.state or "", args.variant or ""
    page = page_of(model, ref)
    a = Answer(f"{model.named(ref)}: its prototype as a tree" + (f", in the state {state}" if state else "")
               + (f", as {variant}" if variant else ""))
    lines: list[str] = []
    rows: list[dict] = []

    def visit(node: Mark, depth: int) -> None:
        for child in node.children:
            if isinstance(child, str) or child.tag in UNSEEN:
                continue
            conditions = page.conditions(child)
            if (state or variant) and not shows(conditions, state or "normal", variant):
                continue
            if not significant(page, child):
                visit(child, depth)
                continue
            inner = any(significant(page, n) for n in child.walk() if n is not child)
            handle = page.handle(child)
            name = model.name(handle) if handle else ""
            words = short((child.own_text() if inner else child.text()) or child.attrs.get("aria-label", "")
                          or child.attrs.get("alt", "") or child.attrs.get("placeholder", ""), 70)
            kind, how = target_of(child.attrs.get("href", "") or child.attrs.get("action", ""))
            extras = stands_on(model, handle)
            if kind and (how or kind not in model.out(handle, "leads to")):
                extras.append(f"goes to {kind}" + (f" ?{how}" if how and kind.startswith("SC") else f" {how}" if how else ""))
            own = {k: v for k, v in (conditions if not state and not variant else {}).items() if child.attrs.get(k)}
            if own:
                extras.append(when_said(own))
            if child.attrs.get("class"):
                extras.append("class " + child.attrs["class"])
            lines.append("  " * depth + f"- {handle or '·'}{' ' + name if name else ''} `{what_it_is(child)}`"
                         + (f' "{words}"' if words else "") + (f" -- {'; '.join(extras)}" if extras else ""))
            rows.append({"handle": handle, "owner": page.owner(child), "name": name, "is": what_it_is(child), "says": words, "line": child.line,
                         "depth": depth, "conditions": conditions, **({"leads to": kind, "opens as": how} if kind else {}),
                         **({"class": child.attrs["class"]} if child.attrs.get("class") else {})})
            visit(child, depth + 1)

    visit(page.main, 0)
    a.add("", [f"`{page.rel}`, line by line as drawn: an element with a handle -- `{ref}.4`, a component's part `C9.2` -- "
               f"is a row of the data; `·` is what has none and a person still reads or acts on. Build it in the "
               f"product's technology: this is the picture, not the code."], 9)
    a.add("Elements", lines, 8)
    a.data = {"prototype": page.rel, "elements": rows}
    a.next = [f"words {ref}", f"forms {ref}", f"states {ref}", f"styles {ref}"]
    return a


# --- words ------------------------------------------------------------------------------------------------------------
def words_of(page: Page) -> list[dict]:
    """Every word a prototype shows -- its text, and what it says in attributes a person meets -- each with whose it
    is and when it shows."""
    out, seen, within = [], set(), set()

    def one_line(node: Mark) -> bool:
        """Whether a node's words are one sentence, a link in the middle of it perhaps: told whole, not cut at the link."""
        marks = [n for n in node.walk() if n is not node]
        return (any(isinstance(c, str) and c.strip() for c in node.children) and bool(marks)
                and all(n.tag in INLINE and not page.handle(n) and not any(n.attrs.get(c) for c in CONDITIONS) for n in marks))

    for node in page.elements():
        owner = page.owner(node)
        held = page.conditions(node)
        conditions = when_said(held)
        alert = any(at.attrs.get("role") in ("alert", "status") or "aria-live" in at.attrs
                    for at in [node, *page.ancestors(node)])
        if id(node) in within:
            pieces = []
        elif one_line(node):
            pieces = [(node.text(), "text")]
            within |= {id(n) for n in node.walk()}
        else:
            pieces = [(" ".join(c.split()), "text") for c in node.children if isinstance(c, str) and c.strip()]
        pieces += [(node.attrs[a], a) for a in WORD_ATTRIBUTES if node.attrs.get(a)]
        if node.tag == "input" and node.attrs.get("type") in ("submit", "button") and node.attrs.get("value"):
            pieces.append((node.attrs["value"], "value"))
        for words, where in pieces:
            key = (owner, words, where, conditions)
            if words and key not in seen:
                seen.add(key)
                out.append({"handle": owner, "words": words, "as": where, "shows": conditions or "always",
                            "line": node.line, "in a state": "data-when" in held, "alert": alert})
    return out


def words(model, args) -> Answer:
    ref = args.id
    page = page_of(model, ref)
    found = words_of(page)
    a = Answer(f"{model.named(ref)}: every word it shows")
    a.add("", ["The copy of the screen, word for word as the prototype draws it: use these words, and ask before "
               "changing one. Sample data -- a name, a price -- stands for what the product shows there."], 9)
    a.add("Words", table(["Element", "Words", "As", "Shows"],
                         [[w["handle"] or "-", w["words"], w["as"], w["shows"]] for w in found]), 8)
    a.data = {"prototype": page.rel, "words": found}
    a.next = [f"states {ref}", f"forms {ref}"]
    return a


# --- forms ------------------------------------------------------------------------------------------------------------
def label_of(page: Page, field: Mark) -> str:
    ident = field.attrs.get("id", "")
    for node in page.tree.walk():
        if node.tag == "label" and ident and node.attrs.get("for") == ident:
            return node.text()
    for at in page.ancestors(field):
        if at.tag == "label":
            return at.text()
    if field.attrs.get("aria-labelledby"):
        named = [n.text() for n in page.tree.walk() if n.attrs.get("id") in field.attrs["aria-labelledby"].split()]
        if named:
            return " ".join(named)
    return field.attrs.get("aria-label", "") or field.attrs.get("placeholder", "")


def field_rules(field: Mark) -> str:
    return ", ".join(rule if field.attrs[rule] in ("", rule) else f"{rule} {field.attrs[rule]}"
                     for rule in FIELD_RULES if rule in field.attrs)


def forms(model, args) -> Answer:
    ref = args.id
    page = page_of(model, ref)
    a = Answer(f"{model.named(ref)}: its fields and what refuses them")
    fields = [n for n in page.elements() if n.tag in ("input", "select", "textarea")
              and n.attrs.get("type") not in ("hidden", "submit", "button", "reset", "image")]
    buttons = [n for n in page.elements() if n.tag == "button"
               or (n.tag == "input" and n.attrs.get("type") in ("submit", "button", "reset", "image"))]
    groups: dict[int, tuple] = {}
    for node in fields + buttons:
        form = next((up for up in page.ancestors(node) if up.tag == "form"), None)
        groups.setdefault(id(form) if form is not None else 0, (form, [], []))[1 if node in fields else 2].append(node)
    data = []
    for form, held_fields, held_buttons in groups.values():
        if form is not None:
            kind, how = target_of(form.attrs.get("action", ""))
            named = (page.handle(form) or form.attrs.get("aria-label") or form.attrs.get("id")
                     or (f"in {page.owner(form)}" if page.owner(form) else ""))
            heading = (f"Form {named}".strip() + (f", sent to {kind}" + (f" ?{how}" if how else "") if kind else "")
                       + (f" by {form.attrs['method'].upper()}" if form.attrs.get("method") else ""))
        else:
            heading = "Fields outside a form"
        rows, held = [], []
        for field in held_fields:
            options = [o.text() for o in field.walk() if o.tag == "option"]
            kind = field.tag if field.tag != "input" else field.attrs.get("type", "text")
            owner = page.owner(field)
            rows.append([owner or "-", label_of(page, field), kind, field_rules(field) or "-",
                         ", ".join(options) or field.attrs.get("value", "") or "-",
                         "; ".join(stands_on(model, owner)) or "-", when_said(page.conditions(field)) or "always"])
            held.append({"handle": owner, "label": label_of(page, field), "type": kind,
                         "rules": {r: field.attrs[r] for r in FIELD_RULES if r in field.attrs}, "options": options,
                         "value": field.attrs.get("value", ""), "name": field.attrs.get("name", ""),
                         "stands on": stands_on(model, owner), "line": field.line})
        acts = [[page.owner(b) or "-", b.text() or b.attrs.get("value", ""), b.attrs.get("type", "submit"),
                 "; ".join(stands_on(model, page.owner(b))) or "-", when_said(page.conditions(b)) or "always"]
                for b in held_buttons]
        scope = form if form is not None else page.main
        messages = [[page.owner(n) or "-", n.text(), when_said(page.conditions(n)) or "always"]
                    for n in scope.walk() if n.attrs.get("role") in ("alert", "status") or "aria-live" in n.attrs
                    or any(w in n.attrs.get("data-when", "") for w in ("error", "failing", "invalid", "refused"))]
        a.add(heading, table(["Element", "Label", "Type", "Rules", "Options or value", "Stands on", "Shows"], rows)
              + ([""] if acts else []) + table(["Element", "Button", "Type", "Stands on", "Shows"], acts)
              + ([""] if messages else []) + table(["Element", "Message", "Shows"], messages), 8)
        data.append({"form": heading, "fields": held, "buttons": [x[1] for x in acts], "messages": [m[1] for m in messages]})
    a.add("", [f"{ref} has no field and no button."] if not data else [
        "Each rule above is only what the prototype's field says: required, a lowest, a highest, a length, a pattern. "
        "The requirements below hold the rest, a limit among it. What a refusal says is theirs too: where they do not "
        "say it, ask, and never write one."], 9)
    behind = sorted({r for n in fields + buttons for r in model.out(page.owner(n), "shows")}, key=lambda r: (len(r), r))
    for r in behind:
        details = model.nodes[r].fields.get("details")
        a.add(f"What {model.named(r)} says of them", [str(model.nodes[r].fields.get("statement", "")).strip()]
              + ([str(details).strip()] if details else [])
              + [f"- `{c}` {model.nodes[c].fields.get('says', '')}" for c in model.rows(r)], 7, f"tests {r}")
    a.data["requirements"] = {r: {"says": model.nodes[r].fields.get("statement", ""), "details": model.nodes[r].fields.get("details", ""),
                                  "criteria": {c: model.nodes[c].fields.get("says", "") for c in model.rows(r)}} for r in behind}
    a.data = {"prototype": page.rel, "forms": data, **a.data}
    a.next = [f"tests {ref} --ui", f"links {ref}"]
    return a


# --- links ------------------------------------------------------------------------------------------------------------
def links(model, args) -> Answer:
    ref = args.id
    page = page_of(model, ref)
    a = Answer(f"{model.named(ref)}: where it leads, and what leads to it")
    out = []
    for node in page.elements():
        href = node.attrs.get("href") or (node.attrs.get("action") if node.tag == "form" else "")
        always = when_said(page.conditions(node)) or "always"
        if node.attrs.get("data-open"):
            out.append([page.owner(node) or "-", short(node.text(), 50), f"opens the dialog #{node.attrs['data-open']}", "", always])
        elif href:
            kind, how = target_of(href)
            out.append([page.owner(node) or "-", short(node.text() or node.attrs.get("aria-label", ""), 50),
                        f"{kind} {model.name(kind)}".strip() if kind.startswith("SC") else f"{kind} {how}".strip(),
                        how if kind.startswith("SC") else "", always])
    a.add("Leads to", table(["Element", "Words", "To", "Opens as", "Shows"], out), 8)
    into = []
    for other in all_pages(model):
        for node in other.elements():
            kind, how = target_of(node.attrs.get("href") or (node.attrs.get("action", "") if node.tag == "form" else ""))
            if kind == ref:
                into.append([other.screen, other.owner(node) or "-", short(node.text(), 50), how])
    a.add("Led to from", table(["Screen", "Element", "Words", "Opens as"], into), 7)
    moves = [[m.get("from"), m.get("event"), m.get("to"), m.get("shows")] for m in model.nodes[ref].fields.get("transitions", [])]
    a.add("Its transitions, as the data states them", table(["From", "On", "To", "Requirements"], moves), 6)
    if not (out or into or moves):
        a.add("", [f"Nothing on {ref} leads anywhere, and nothing leads to it."], 9)
    a.data = {"prototype": page.rel, "leads to": out, "led to from": into, "transitions": moves}
    a.next = [f"states {ref}"]
    return a


def element_of(model, ref: str) -> tuple[Page, Mark]:
    """The page and node of a handle: a screen's element, or a component's part as its own drawing or a screen draws it."""
    found = HANDLE_RE.match(ref)
    if not found:
        raise KeyError(f"{ref}: give an element, `SC3.4`, a part, `C2.1`, a screen, `SC3`, or a class, `.btn`")
    pages = [page_of(model, found.group(1))]
    if ref.startswith("C"):
        pages += all_pages(model)
    for page in pages:
        for node in page.elements():
            if page.handle(node) == ref:
                return page, node
    raise KeyError(f"{ref}: no prototype draws it -- `spec.py outline <screen>` lists what each draws")


def styles(model, args) -> Answer:
    ref = args.id
    sheet = Styles(model.root)
    a = Answer(f"{ref}: the values it is drawn with")
    named = ", ".join(f"`{f}`" for f in sheet.files) or "no sheet"
    if not sheet.rules:
        a.add("", ["The product has no styles of its own yet: its prototypes are drawn grey, and the look is not decided."], 10)
        return a
    if re.fullmatch(r"(SC|C)\d+", ref):
        page = page_of(model, ref)
        rows, data = [], {}
        for node in page.elements():
            handle = page.handle(node)
            if not handle or handle in data:
                continue
            variables, plain = sheet.variables(page, node), sheet.plain(page, node)
            values = {p: sheet.resolve(plain[p][0], variables) for p in SUMMARY if p in plain}
            data[handle] = values
            rows.append([handle, model.name(handle) or what_it_is(node), "; ".join(f"{p}: {v}" for p, v in values.items()) or "-"])
        a.add("", [f"Each element's own values from {named}, variables resolved. `styles <element>` gives one whole: what "
                   f"it inherits, its states and its widths."], 9)
        a.add("Elements", table(["Element", "Name", "Values"], rows), 8)
        a.data = {"styles": sheet.files, "elements": data}
        a.next = [f"states {ref}"]
        return a
    if ref.startswith("."):
        rows = [[r.media or "-", s, "; ".join(f"{p}: {v}" for p, v in r.declarations), r.line]
                for r in sheet.rules for s in r.selectors if re.search(rf"{re.escape(ref)}(?![\w-])", s)]
        a.add("Rules", table(["Under", "Selector", "Declarations", "Line"], rows) or [f"No rule names {ref}."], 8)
        a.data = {"styles": sheet.files, "rules": rows}
        return a
    page, node = element_of(model, ref)
    variables, plain = sheet.variables(page, node), sheet.plain(page, node)

    def inherits(prop: str) -> str:
        """What a property written `inherit` takes: its value on the nearest element above that sets it."""
        for up in page.ancestors(node):
            held = sheet.plain(page, up)
            if prop in held and held[prop][0] != "inherit":
                return f"{sheet.resolve(held[prop][0], variables)}, from {held[prop][1]}"
        return "the browser's own"
    own = [[p, sheet.resolve(v, variables) if v != "inherit" else f"inherit: {inherits(p)}", v if "var(" in v else "",
            sheet.token_of(v, sheet.resolve(v, variables)), f"{s} (line {line})"]
           for p, (v, s, _, line) in plain.items() if not p.startswith("--")]
    inherited = []
    for prop in sorted(INHERITED - set(plain)):
        for up in page.ancestors(node):
            held = sheet.plain(page, up)
            if prop in held:
                value = sheet.resolve(held[prop][0], variables)
                inherited.append([prop, value, sheet.token_of(held[prop][0], value), f"{held[prop][1]}, on `{up.tag}`"])
                break
    conditioned: dict[tuple, list] = {}
    for _, _, prop, value, selector, media, notes, _ in sheet.reaching(page, node):
        if media or notes:
            conditioned.setdefault((media, notes), []).append([prop, sheet.resolve(value, variables), selector])
    a.add("", [f"`{ref}` in `{page.rel}`, line {node.line}: `{what_it_is(node)}`"
               + (f' "{short(node.text(), 60)}"' if node.text() else "")
               + f". From {named}, as a browser would apply it; build it as the product's own theme, the tokens named "
                 f"where a value is one."], 10)
    a.add("Its own values", table(["Property", "Value", "Written", "Token", "From"], own), 9)
    a.add("What it inherits", table(["Property", "Value", "Token", "From"], inherited), 7)
    for (media, notes), rows in conditioned.items():
        heading = " and ".join([f"at {media}"] if media else []) + (" " if media and notes else "") \
            + (f"when {' '.join(notes)}" if notes else "")
        a.add(heading[0].upper() + heading[1:], table(["Property", "Value", "From"], rows), 6)
    a.data = {"styles": sheet.files, "element": ref, "own": own, "inherited": inherited,
              "conditioned": [{"media": m, "when": list(n), "declarations": r} for (m, n), r in conditioned.items()]}
    a.next = [f"states {page.screen}"]
    return a


def tokens(model, args) -> Answer:
    held = prototypes.flat_tokens(model.root)
    a = Answer("The product's design tokens")
    if not held:
        a.add("", ["The product has no tokens yet: its look is not decided, or it keeps its values in its own styles."], 10)
        return a
    a.add("", [f"`{prototypes.TOKENS}`, each value with the variable a page knows it by. The page links "
               f"`{prototypes.TOKENS_CSS}`: no such file is kept, it is made from the tokens, and it is the block below."], 9)
    named: dict[str, list[str]] = {}                    # each token, and the foundations that name it
    for node in model.of_kind("foundation"):
        for name in re.findall(r"(?<![\w-])(--[A-Za-z][\w-]*)", str(model.nodes[node].fields.get("says", ""))):
            named.setdefault(name, []).append(node)
    reaching = prototypes.tokens_reaching(model.root)
    a.add("Tokens", table(["Variable", "Value", "Type", "What it is for", "Named by", "Reaches"],
                          [[prototypes.variable(t), t["value"], t["type"], t["about"],
                            ", ".join(dict.fromkeys(named.get(prototypes.variable(t), []))),
                            ", ".join(sorted({p.rsplit("/", 1)[1][:-5] for p, held in reaching.items() if prototypes.variable(t) in held}, key=natural))]
                           for t in held]), 8)
    a.add("As CSS", ["```css", prototypes.tokens_css(model.root).rstrip(), "```"], 7)
    shell = model.root / prototypes.SHELL
    outside = [html.unescape(h) for h in re.findall(r'<link[^>]*href="(https?:[^"]+)"', shell.read_text(encoding="utf-8"))] if shell.is_file() else []
    a.add("What the page links from elsewhere", [f"- `{href}`" for href in outside], 6)
    a.data = {"tokens": [{"variable": prototypes.variable(t), **t, "named by": list(dict.fromkeys(named.get(prototypes.variable(t), []))),
                          "reaches": sorted({p.rsplit("/", 1)[1][:-5] for p, held in reaching.items() if prototypes.variable(t) in held}, key=natural)}
                         for t in held], "css": prototypes.tokens_css(model.root), "linked": outside}
    a.next = ["styles <element>"]
    return a


# --- states, variants and widths -------------------------------------------------------------------------------------
def states(model, args) -> Answer:
    ref = args.id
    page = page_of(model, ref)
    fields = model.nodes[ref].fields
    a = Answer(f"{model.named(ref)}: what each state and variant shows, and the widths it changes at")
    named_states: dict[str, None] = {}
    named_variants: dict[str, None] = {}
    for at in page.elements():
        for attribute in CONDITIONS:
            for word in at.attrs.get(attribute, "").split():
                (named_states if attribute in ("data-when", "data-unless") else named_variants).setdefault(word, None)
        if at.attrs.get("data-variant"):
            named_variants.setdefault(at.attrs["data-variant"], None)
    for word in page.main.attrs.get("data-states", "").split():
        named_states.setdefault(word, None)
    for word in page.main.attrs.get("data-variants", "").split():
        named_variants.setdefault(word, None)
    a.add("As the data says them", table(
        ["State", "Status", "What it shows", "Evidence or how to find out"],
        [[r.get("state"), r.get("status"), r.get("what it shows"), r.get("evidence") or r.get("investigation") or "-"]
         for r in fields.get("states", [])]), 7)
    a.add("Variants, as the data says them", table(
        ["What differs, and for whom", "About"], [[r.get("what differs, and for whom"), r.get("about")] for r in fields.get("variants", []) if "what differs, and for whom" in r])
        or table(["Variant", "When"], [[r.get("variant"), r.get("when")] for r in fields.get("variants", [])]), 7)
    data: dict = {"prototype": page.rel, "states": {}, "variants": {}}
    for held, is_state in ((named_states, True), (named_variants, False)):
        for word in held:
            shown, hidden = [], []
            for at in page.elements():
                own = {c: at.attrs[c].split() for c in CONDITIONS if at.attrs.get(c)}
                if not own:
                    continue
                state, variant = (word, "") if is_state else ("normal", word)
                before, after = shows(own, "normal", ""), shows(own, state, variant)
                if after and not before:
                    shown.append([page.owner(at) or "-", short(at.text(), 70)])
                elif before and not after:
                    hidden.append([page.owner(at) or "-", short(at.text(), 70)])
            how = f"?state={word}" if is_state else f"?as={word}"
            script = word in page.main.attrs.get("data-states" if is_state else "data-variants", "").split()
            a.add(f"{'State' if is_state else 'Variant'} {word} (`/prototype/{ref}.html{how}`)",
                  (["Shown by the product's own script, prototype.js, beyond what the page marks."] if script else [])
                  + (["Shows:", ""] + table(["Element", "Words"], shown) + [""] if shown else [])
                  + (["Hides:", ""] + table(["Element", "Words"], hidden) if hidden else []), 6)
            data["states" if is_state else "variants"][word] = {"opens": how, "shows": shown, "hides": hidden, "by script": script}
    sheet = Styles(model.root)
    widths: dict[str, list] = {}
    for rule in sheet.rules:
        if "width" not in rule.media:
            continue
        for selector in rule.selectors:
            reached = [page.owner(n) or n.tag for n in page.elements() if matches(page, n, selector) is not None]
            if reached:
                widths.setdefault(rule.media, []).append([selector, "; ".join(f"{p}: {v}" for p, v in rule.declarations),
                                                          ", ".join(dict.fromkeys(reached))])
    for media, rows in widths.items():
        a.add(f"At {media}", table(["Selector", "Declarations", "Reaches"], rows), 5)
    a.add("Its layout, as the data states it", table(["What", "Must be", "From"], [[r.get("what"), r.get("must be"), r.get("from")]
                                                                                   for r in fields.get("layout", [])]), 7)
    data["widths"] = widths
    a.data = data
    a.next = [f"tests {ref} --ui", f"styles {ref}"]
    return a


def sample(model, args) -> Answer:
    a = Answer("The sample data the prototypes show")
    if not (model.root / SAMPLE).is_file():
        a.add("", ["The prototypes have no sample data of their own: what they show is written in each."], 10)
        return a
    values, failed = sample_values(model.root)
    a.add("", [f"`{SAMPLE}`, as JSON: what each prototype shows in place of a server's answers. These are fixtures for "
               f"tests, never the product's data."] if values else [f"`{SAMPLE}` holds no sample data yet."], 9)
    for name, value in values.items():
        a.add(name, ["```json", json.dumps(value, indent=1, ensure_ascii=False), "```"], 8)
    a.add("Not read as data", [f"- {f}" for f in failed], 5)
    a.data = {"file": SAMPLE, "values": values, "not read": failed}
    return a


# --- messages --------------------------------------------------------------------------------------------------------
def messages(model, args) -> Answer:
    """Every message the product shows: what a prototype says in a state other than its normal one, an alert, and what
    each endpoint answers when it fails."""
    a = Answer("Every message the product shows")
    held: dict[tuple, dict] = {}                        # each message once, with every screen that shows it
    for page in all_pages(model):
        for word in words_of(page):
            if word["in a state"] or word["alert"]:
                own = word["handle"] if word["handle"].startswith("C") else ""
                held.setdefault((own, word["words"], word["shows"]), {"screens": [], **word})["screens"].append(page.screen)
    rows = [[", ".join(dict.fromkeys(m["screens"])), m["handle"] or "-", m["words"], m["shows"] + ("; an alert" if m["alert"] else "")]
            for m in held.values()]
    a.add("On the screens, beyond their normal state", table(["Screens", "Element", "Words", "Shows"], rows), 8)
    fails = [[ref, model.name(ref), row.get("status"), row.get("when"), row.get("says")]
             for ref in model.of_kind("endpoint") for row in model.nodes[ref].fields.get("fails", [])]
    a.add("What the endpoints answer when they fail", table(["Endpoint", "Name", "Status", "When", "Says"], fails), 7)
    a.add("", ["Use these words as they are. A message the product needs that is not here is asked, never written in code."
               if rows or fails else "No screen says anything beyond its normal state, and no endpoint says how it fails."], 9)
    a.data = {"screens": list(held.values()), "endpoints": fails}
    return a


# --- the cases a test of a screen checks -----------------------------------------------------------------------------
def ui_cases(model, refs: list[str]) -> Answer:
    a = Answer(f"What a test of {', '.join(refs)} checks on the screen")
    data = []
    for ref in refs:
        page = page_of(model, ref)
        cases: list[list] = []
        for word in words_of(page):
            if word["handle"] and word["as"] == "text":
                cases.append([word["handle"], f'shows "{short(word["words"], 60)}"', word["shows"],
                              ", ".join(model.out(word["handle"], "shows")) or "-"])
        for move in model.nodes[ref].fields.get("transitions", []):
            cases.append([f"{ref}", f"on {move.get('event', '')}, goes to {move.get('to', '')}",
                          f"from {move.get('from', '')}", move.get("shows") or "-"])
        bounds = []
        for node in page.elements():
            if node.tag not in ("input", "textarea", "select"):
                continue
            rules = []
            if "required" in node.attrs:
                rules.append("unticked is refused" if node.attrs.get("type") in ("checkbox", "radio") else "empty is refused")
            if node.attrs.get("min") and node.attrs.get("max"):
                rules.append(f"{node.attrs['min']} and {node.attrs['max']} are taken; one step outside each is refused")
            elif node.attrs.get("min"):
                rules.append(f"{node.attrs['min']} is taken; one step below is refused")
            elif node.attrs.get("max"):
                rules.append(f"{node.attrs['max']} is taken; one step above is refused")
            if node.attrs.get("maxlength"):
                rules.append(f"{node.attrs['maxlength']} characters are taken, one more is not")
            if node.attrs.get("pattern"):
                rules.append(f"what does not match {node.attrs['pattern']} is refused")
            if node.attrs.get("type") == "email":
                rules.append("what is not an address is refused")
            if rules:
                owner = page.owner(node)
                bounds.append([owner or "-", label_of(page, node), "; ".join(rules), "; ".join(stands_on(model, owner)) or "-"])
        a.add(model.named(ref), [f"Open `/prototype/{ref}.html` -- `?state=<state>` and `?as=<variant>` show the others -- "
                                 f"and find each element by `[data-el]` or `[data-part]`: the product's own tests find it "
                                 f"their own way.", ""] + table(["Element", "Checks that it", "When", "Requirement"], cases)
              + ([""] + table(["Field", "Label", "Boundaries", "Stands on"], bounds) if bounds else []), 7)
        data.append({"screen": ref, "prototype": page.rel, "cases": cases, "boundaries": bounds})
    a.add("", ["Each case is what the prototype draws: a requirement's own criteria come first, in `tests`, and what a "
               "refusal says is the requirement's or the rule's, never the test's."], 9)
    a.data = {"screens": data}
    return a
