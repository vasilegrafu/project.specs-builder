"""What the product means, as whoever builds it needs it: each entity as a JSON Schema, an entity's lifecycle as a state
machine, who may do what as one table, the rules to enforce, the words to name things by, the qualities and constraints
to hold to, and the API's description.

Each is read from the data and nothing is added. What the specification does not say, a field's type or whether it is
required, is said to be not said, to ask.
"""
from __future__ import annotations

import json
import re

from answer import Answer, table

STATUS_FIELDS = ("status", "state")                     # a field that holds the lifecycle's state, by its name
SURFACE_RE = re.compile(r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(\S+)", re.IGNORECASE)


def entities_of(model, ref: str | None) -> list[str]:
    if not ref:
        return model.of_kind("entity")
    if model.need(ref).kind != "entity":
        raise KeyError(f"{ref}: no entity has that ID -- `spec.py list entity` lists them")
    return [ref]


def state_names(model, ref: str) -> list[str]:
    return [str(model.nodes[s].fields.get("name") or s.split(".", 1)[1]) for s in model.rows(ref)]


def schema(model, args) -> Answer:
    refs = entities_of(model, args.id)
    a = Answer("The entities as JSON Schema" if not args.id else f"{model.named(args.id)} as JSON Schema")
    schemas = {}
    for entity in refs:
        node = model.nodes[entity]
        states = state_names(model, entity)
        properties = {}
        for field in node.fields.get("fields", []):
            for name in (n.strip() for n in str(field.get("field", "")).split(",")):
                if not name:
                    continue
                prop: dict = {"description": field.get("meaning", "")}
                if name.lower() in STATUS_FIELDS and states:
                    prop |= {"enum": states, "x-from": "its lifecycle's states"}
                properties[name] = prop
        unsettled = model.questions_on([entity])
        schemas[entity] = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": entity,
                           "title": model.name(entity), "description": node.fields.get("about", ""), "type": "object",
                           "properties": properties, **({"x-states": states} if states else {}),
                           **({"x-unsettled": unsettled} if unsettled else {}),
                           "x-governed-by": model.into(entity, "governs")}
        a.add(model.named(entity), ["```json", json.dumps(schemas[entity], indent=1, ensure_ascii=False), "```"], 7)
    if not refs:
        a.add("", ["The specification holds no entity: what the product keeps is not specified. Ask."], 10)
    a.add("", ["Each field as the entity names it, with what it means. The specification does not say a field's type, "
               "nor which are required: where the meaning does not settle it, ask, and never decide it in code. A field "
               "that holds the state takes the lifecycle's states; `x-states` holds them where no field says it does; "
               "the rules that govern an entity are `rules`."], 9)
    a.data = {"schemas": schemas}
    a.next = [f"lifecycle {refs[0]}" if refs else "rules"]
    return a


def lifecycle(model, args) -> Answer:
    ref = entities_of(model, args.id)[0]
    node = model.nodes[ref]
    a = Answer(f"{model.named(ref)}: its lifecycle")
    rows = node.fields.get("lifecycle", [])
    a.add("Moves", table(["State", "On", "Only if", "Then", "To"],
                         [[r.get("state"), r.get("event"), r.get("guard"), r.get("effect"), r.get("next")] for r in rows]), 8)
    held, drawing = [], ["```mermaid", "stateDiagram-v2"]
    states = model.rows(ref)
    if states:
        drawing.append(f"  [*] --> {states[0].split('.', 1)[1].replace('-', '_')}")
    for state in states:
        name = state.split(".", 1)[1]
        onward = model.out(state, "moves")
        held.append([name, ", ".join(s.split(".", 1)[1] for s in onward) or "none: it ends here",
                     ", ".join(model.into(state, "displays")) or "-"])
        drawing += [f"  {name.replace('-', '_')} --> {to.split('.', 1)[1].replace('-', '_')}" for to in onward]
        if not onward:
            drawing.append(f"  {name.replace('-', '_')} --> [*]")
    a.add("States", table(["State", "Moves to", "Shown on"], held), 7)
    a.add("As a diagram", drawing + ["```"], 4)
    rules = model.into(ref, "governs")
    a.add("The rules that govern it", [f"- {model.named(r)}" for r in rules], 7)
    if rows or states:
        a.add("", ["A move the table does not have is not allowed: build the machine with exactly these moves, each only "
                   "where its condition holds."], 9)
    else:
        a.add("", [f"{ref} has no lifecycle: nothing says it moves between states."], 9)
    a.data = {"lifecycle": rows, "states": held, "rules": rules}
    a.next = [f"schema {ref}", "rules"]
    return a


def permissions(model, args) -> Answer:
    roles = model.of_kind("role")
    a = Answer("Who may do what")
    actions: dict[str, dict[str, str]] = {}
    for role in roles:
        for row in model.nodes[role].fields.get("actions", []):
            actions.setdefault(f"{row.get('about')} {row.get('action', '')}".strip(), {})[role] = str(row.get("answer", "?"))
    a.add("", ["Each action as the role words it, and for each role yes, no or ?. A ? is not known, so ask; a - is an "
               "action the specification does not ask of that role. What a role may not do, the product refuses, and "
               "a test shows it refused."], 9)
    a.add("Permissions", table(["What", *[model.named(r) for r in roles]],
                               [[action, *[held.get(r, "-") for r in roles]] for action, held in actions.items()]), 8)
    a.add("Who each is", [f"- {model.named(r)}: {model.nodes[r].fields.get('who', '')}" for r in roles], 6)
    if not roles:
        a.add("", ["The specification holds no role: nothing says who may do what. Ask."], 10)
    a.data = {"roles": {r: model.name(r) for r in roles}, "may": actions}
    a.next = ["rules"]
    return a


def rules(model, args) -> Answer:
    ref = args.id
    if ref and model.need(ref).kind != "rule":
        raise KeyError(f"{ref}: no rule has that ID -- `spec.py list rule` lists them")
    refs = [ref] if ref else model.of_kind("rule")
    a = Answer("The rules to enforce" if not ref else model.named(ref))
    data = []
    for rule in refs:
        f = model.nodes[rule].fields
        governs, enforced = model.out(rule, "governs"), model.into(rule, "enforces")
        lines = [str(f.get("says", ""))] + (["", f"Except: {f['except']}"] if f.get("except") else [])
        lines += ["", f"Governs: {', '.join(model.named(g) for g in governs) or '-'}",
                  f"Made true by: {', '.join(model.named(r) for r in enforced) or 'no requirement yet: ask'}",
                  f"Stands: {f.get('confidence', '-')}"]
        a.add("" if ref else model.named(rule), lines, 7)
        data.append({"rule": rule, "says": f.get("says", ""), "except": f.get("except", ""), "governs": governs,
                     "enforced by": enforced})
    a.add("", ["A rule holds everywhere it applies: enforce it once, where every way in passes, and test it from each "
               "requirement that makes it true." if refs else "The specification holds no rule."], 9)
    a.data = {"rules": data}
    a.next = [f"trace {refs[0]}"] if refs else []
    return a


def glossary(model, args) -> Answer:
    a = Answer("The words of the product")
    rows = [[model.name(t), model.nodes[t].fields.get("means", ""), model.nodes[t].fields.get("also", "") or "-", t]
            for t in model.of_kind("term")]
    a.add("", ["Name things in the code, the tests and the messages by these words, and by nothing the glossary lists "
               "as another name for them."], 9)
    a.add("Terms", table(["Term", "Means", "Also called", "ID"], rows), 8)
    named = [[ref, model.name(ref), kind] for kind in ("entity", "role", "rule") for ref in model.of_kind(kind)]
    a.add("Named things", table(["ID", "Name", "Kind"], named), 6)
    a.data = {"terms": rows, "named": named}
    return a


def qualities(model, args) -> Answer:
    a = Answer("What the product must hold to, beyond what it does")
    rows = [[model.named(q), model.nodes[q].fields.get("status", ""), model.nodes[q].fields.get("says", ""),
             ", ".join(model.out(q, "met by")) or "-"] for q in model.of_kind("quality")]
    a.add("Qualities", table(["Quality", "Status", "What it must be", "Met by"], rows), 8)
    constraints = [[c, model.nodes[c].fields.get("says", "")] for c in model.of_kind("constraint")]
    a.add("Constraints", table(["ID", "Fixed from outside"], constraints), 7)
    a.add("", ["A quality that is met has its number to test against. One that is open is not settled: ask."
               if rows or constraints else "The specification holds no quality and no constraint: ask if there are any."], 9)
    a.data = {"qualities": rows, "constraints": constraints}
    return a


def api_of(model) -> dict | None:
    """The API's description, OpenAPI 3, from each endpoint whose surface is a method and a path: what it takes, from
    Takes, and each status it answers, from Answers and Fails. The data is the source; this is written from it."""
    paths: dict[str, dict] = {}
    for ref in model.of_kind("endpoint"):
        f = model.nodes[ref].fields
        found = SURFACE_RE.match(str(f.get("surface") or "").strip())
        if not found:
            continue
        operation: dict = {"operationId": ref, "summary": model.name(ref), "description": f.get("purpose", ""),
                           "x-requirements": model.out(ref, "shows")}
        parameters, fields, needed = [], {}, []
        for row in f.get("takes", []):
            where = str(row.get("where", "")).lower()
            required = str(row.get("required", "")).lower().startswith("y")
            said = ": ".join(part for part in (row.get("type"), row.get("rule")) if part)
            if where == "body":
                fields[row.get("name")] = {"description": said}
                if required:
                    needed.append(row.get("name"))
            elif where in ("path", "query", "header", "cookie"):
                parameters.append({"name": row.get("name"), "in": where, "required": where == "path" or required,
                                   "description": said, "schema": {"type": "string"}})
        if parameters:
            operation["parameters"] = parameters
        if fields:
            body: dict = {"type": "object", "properties": fields} | ({"required": needed} if needed else {})
            operation["requestBody"] = {"required": bool(needed), "content": {"application/json": {"schema": body}}}
        responses: dict[str, dict] = {}
        for row in [*f.get("answers", []), *f.get("fails", [])]:
            status = str(row.get("status", ""))
            if re.fullmatch(r"\d{3}", status):
                said = " -- ".join(str(row[k]) for k in ("when", "holds", "says") if row.get(k))
                before = responses.get(status)
                responses[status] = {"description": f"{before['description']}; or {said}" if before else said}
        operation["responses"] = responses or {"default": {"description": f.get("purpose", "")}}
        paths.setdefault(found.group(2), {})[found.group(1).lower()] = operation
    return {"openapi": "3.0.3", "info": {"title": model.name("document"), "version": "1"}, "paths": paths} if paths else None


def openapi(model, args) -> Answer:
    a = Answer("The API's description")
    held = api_of(model)
    if held is None:
        a.add("", ["No endpoint has a method and a path, so there is no OpenAPI description: `list endpoint` lists what "
                   "programs call."], 10)
        return a
    a.add("", ["OpenAPI 3, written from the endpoints: each operation names the requirements it carries in "
               "`x-requirements`. `export --model` writes it as `openapi.json`."], 9)
    a.add("openapi.json", ["```json", json.dumps(held, indent=1, ensure_ascii=False), "```"], 8)
    a.data = {"openapi": held}
    return a
