# The endpoints: what programs call

A product that programs call -- an API, a library, a command line -- has
endpoints beside its requirements, the counterpart of the screens: one
node per endpoint, `A1`, in the application's API menu. The document's
`kind` says when a product has them: `api` or `library`, alone or in a
mix, `application, api`.

## When

- The user asks for them -- "the API", "the endpoints", "what does it
  answer" -- or the kind says `api` or `library`: offer them in one line
  once the requirements are written.
- In reverse-engineer, the API archaeologist's findings become them:
  every endpoint of a description in reach is an endpoint, or is said
  not read, with why.

## One endpoint, one node

```
add endpoint "List the invoices" kind=read surface="GET /invoices" purpose="..." shows=R1 about=N1
add-line $1 "who may call" "the accountant" may="list every invoice" else="403, not allowed"
add-line $1 takes status where=query type="draft | issued" required=no rule="B2"
add-line $1 answers 200 when="always" holds="the invoices, newest first"
add-line $1 fails 401 when="no key" says="sign in"
```

- **Its purpose**, one sentence: what a caller comes here to do.
- **`surface`**: what it is -- a method and a path, `GET
  /invoices/{number}`; a function, `Invoices.download(number)`; or a
  command, `invoices download <number>`. One endpoint per surface.
- **`kind`**: `read`, `write`, `action` or `event`. A read changes
  nothing; a write makes or changes a thing; an action does something
  with no thing to show for it; an event is sent by the product, not
  called.
- **`where`**, on the finding that read it: the description by its line,
  `openapi.json:120`; the route in the code; the call a captured view
  made.
- **Who may call**: a role of the Domain, or `any program with a key`;
  what they may do; and what a caller without the right gets.
- **Takes**: each thing it takes, where -- path, query, header, body --
  its type, whether it is required, and the rule that holds it.
- **Answers**: each status it answers with, when, and what the answer
  holds.
- **Fails**: each status it refuses with, when, and what it says. Every
  endpoint fails somehow; one without it is a gap for a review, and
  `spec.py open` lists it.
- **Limits**, where there are any: rate, size, idempotency, version.
- **Example**, where it helps: one exchange as it is on the wire, or one
  call as it is written, in a block fenced with three backticks. Never a
  real token, key or person's details.

An endpoint stands on a requirement, as an element of a prototype does:
`shows` names the requirements it carries, and `about` what else it
stands on -- a rule that holds a parameter, an entity it takes -- so
that a change to either reaches it. A requirement or a rule named only
in its tables' words ties nothing: tie it.

## Reading a description

Where the material holds an API description, each endpoint is read from
it with the line it stands at, and the finding that became the endpoint
names that line. A description written as YAML is passed with why: ask
for the JSON form.

## Flows through endpoints

A flow that a program takes is tied to the endpoints it calls, `tie F2
calls A1`, as a flow a user takes is to the screens it passes. `spec.py
trace R1` shows each endpoint that shows a requirement, beside the
screens.

## A library or a command line

The same kind. The surface is a function or a command instead of a
method and a path; the statuses of Answers and Fails are what the call
returns or raises, said in words where there is no number.
