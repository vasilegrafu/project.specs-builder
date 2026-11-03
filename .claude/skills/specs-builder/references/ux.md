# How it is used and how it looks: flows, screens, prototypes, design

Beside the requirements, the specification says how the product is used
and how it looks. The requirements say what it must do; these say where,
in what order and in what form. They are the **UX** of the application's
menu.

| Kind | Answers | Holds |
|---|---|---|
| a flow, `F1` | in what order is this piece of work done? | who does it or what starts it, its steps, what goes wrong; the screens it passes and the endpoints it calls |
| a screen, `SC1` | what is it built from, beyond what it looks like? | where it opens and who may see it; its data; each element as a row, `SC1.3`; its states, transitions, variants and layout |
| its prototype | how does it look, and what does it say? | `prototypes/screens/SC1.html`: the screen's markup in the product's look, every word it shows, one anchor per element |
| a foundation, `FD1` | how does it look, everywhere? | one rule of the look -- colours and what they mean, text, spacing, layout, shape, motion, icons, patterns, words, accessibility |
| a component, `C1` | what is this building block, in each of its states? | its parts as rows, `C1.2`; its variants, each drawn in `prototypes/components/C1.html`; its rules |

Each is optional. Work with no interface has none; a change inside an
interface whose patterns are settled may need one flow and nothing else;
a visual change only the design. Write them when the user asks for them,
or offer them once the requirements for anything with an interface are
written. A screen, once written, has its prototype: `add screen` starts
one.

The application draws them: a screen with its elements and its preview;
the prototype view, with its states, variants, widths and each element's
links; a component with its drawings; the design system, from the
foundations and `prototypes/tokens.json`. `index.cmd` (or `index.sh`)
opens it.

## Four rules

- **Nothing is restated.** Behaviour is in the requirements and nowhere
  else. A flow carries the requirements its steps name, a link the loader makes from the IDs, so that a requirement changed reaches the flow. An element, a step or a transition names its requirement by ID
  -- in its Shows column, the one place that ties it. If writing a
  screen turns up behaviour no requirement holds, the requirement is
  written first.
- **Three kinds of content.** What the user said; what was found in
  material -- the screen's `from` names the source, and the findings it
  was seen in stand in its States' and Transitions' Evidence; and what
  the skill added, an addition `added to` the screen or the row.
- **Never invent a fact, or a look.** A colour, a size or a wording the
  user did not give and the material does not show is asked. A grey
  prototype needs no look at all.
- **Through the logic.** Flows, screens, elements, components and parts
  are written with `spec.py do` -- `add`, `add-row`, `add-line`, `set`,
  `tie` -- and each change is held to the grammar whole. The prototypes'
  markup is the one thing written by hand, as HTML; `spec.py check`
  holds it to the data both ways, and the application shows a fault at
  its line.

## Flows

A flow is one piece of work from what starts it to what counts as done,
in the product as it will be -- not as it is walked today, which is the
document's Journey. Write one for each thing the user comes to do:

```
add flow "Send an invoice to the accountant" user="the customer" purpose="The customer sends an invoice to their accountant and has it sent when it is done." serves=G1 passes="SC3, SC4" calls=A2
```

- **`user`**, who does it, as the document's Users names them; or, for a
  flow no user drives, **`trigger`**, what starts it: a schedule, an
  event, a call from another system.
- **`serves`**, the goals it serves.
- **Steps**, its text: a numbered list or a table, one step each -- who
  does what and what the product shows, and the screen, the endpoint and
  the requirement it uses, by ID. A step outside the product -- "he places
  the order at the broker" -- names none, and says so. The screens it
  passes are tied, `passes`, and the endpoints it calls, `calls`: an ID
  named only in the steps' words ties nothing.
- **Show the branches that matter**: where it can fail, where the user
  is refused, where they can turn back. A flow with only the happy path
  is half a flow.
- **When it goes wrong**, for a flow with a trigger: what fails, what
  the product does then, and how anyone sees it.

### A flow is a user story

Every flow is told as a user story, from what it already holds, and
nothing is written for the story itself:

> As **the visitor**, I want to **buy a product**, so that **customers
> place their orders on the site, not by phone; and fewer checkouts are
> abandoned**.

-- its `user`, its name and the goals it `serves`. A flow no user drives
is told as a job: "Started by **the timer, every night at 02:30**: **the
nightly run**, so that ...". Under the story comes **what it carries**:
every requirement its steps and its "When it goes wrong" name, in the
order the steps first name them, each with its priority, how well it is
backed (`confidence`) and its criteria. That table is what a team plans
a piece of work from. So write a flow for its story:

- **Name it as what the user does**, a verb first, as it reads after "I
  want to": "Buy a product", "Cancel a visit", "Send an invoice to the
  accountant" -- not "Checkout" or "The cart". A job's flow is named as
  what runs: "The nightly run", "A rerun by hand".
- **Give it a `user`** as the document's Users names them, or a
  **`trigger`** -- one or the other, always.
- **Tie it to the goals it serves**, at least one: they are the story's
  "so that".
- **Name, in its steps, every requirement it carries** -- the step that
  does what the requirement says ends with its ID. A requirement named in
  no flow's steps is carried by none; one named in the wrong step makes
  the table wrong.

The application shows the story and its table at the head of the flow's
page; the export carries them under the flow; `spec.py story [F1]` says
them, every flow's without an ID, `--json` for an agent. `spec.py ready`
holds the specification while a flow's story cannot be told -- no user
and no trigger, no goal served, or steps that name no requirement.

## Screens

A screen is what the user sees at one point: a page, a dialog, a popup,
a message that arrives. Name it as the users would. How it looks and
every word it shows are its prototype; its node says what a prototype
cannot:

- **Its purpose**, one sentence under its header: what the user comes
  here to do. Then its **`kind`** -- one of the kinds below -- its
  **`address`**, **`who`** may see it, what it is **`reached by`**, and
  its **`from`**, where it was read from material.
- **What it is about**: `shows` the requirements the screen as a whole
  carries, `about` an entity, a rule, a finding, and `displays` the
  entities' states it shows (`N2.open`).
- **Data**: a line per thing it shows or changes -- `add-line SC3 data
  "the order's lines" shows=R4 about=N2`.
- **Elements**: a row per element its prototype anchors -- `add-row SC3
  name="Add to cart" is=button does="Adds the product in that quantity"
  component=C1 shows=R4` -- numbered `SC3.13`, the 13 its prototype's
  `data-el="13"`. Every element that shows, says or does something has a
  row of its own: a heading, a mark, a button, a link, a field, a table
  and each of its cells, the names of its columns too, each item of a
  list, each name and value of a list of facts, the legend of a group of
  fields, a line of text, a message, a dialog; only a wrapper that lays
  out has none, and a label is its field's when it names a field that
  has one. A region -- the page heading, a list, a form, a table -- is a
  row too, and is the anchor of nothing inside it: the elements inside it
  are rows each, or the parts of the component it is. A thing that
  repeats -- a card, a row, an item -- carries the same number each time,
  and is one row. A number is never reused: a new element takes the next
  free one. Its columns say what it is, its kind, what it shows and does,
  its states, the name a screen reader hears, its component, and what it
  stands on -- the requirement it shows, what it is about, the question
  it asks, the screen it leads to.
- **States, every time**: a line for every state the screen's kind likely
  has -- a form's empty, validation, error, loading, success, disabled and
  unauthorized -- and for each of its own -- submitting, confirmed --
  `add-line SC3 states empty status=observed "what it shows"="..."
  evidence=E20`. Each says what was established of it, in its Status:
  - `observed`: seen in the material, and its Evidence names the finding
    it was seen in;
  - `likely`: the kind has it, nobody has seen it, and its Investigation
    says how it would be reached without harm -- the network slowed, the
    form sent empty, the page opened signed out;
  - `n/a`: it cannot occur, and What it shows says why;
  - `stated` or `added`: the user said it, or the skill added it (and an
    addition says so), and no material shows it.
  This is the part engineers otherwise guess, and where a specification
  that looked complete turns out not to be. The prototype shows each
  state that is settled, by the same name (`data-when="empty"`), and no
  state the screen does not list; a `likely` state needs no drawing until
  it is known.
- **Behaviour, every time**: what is true of the whole screen beyond its
  states -- under the pointer, with the keyboard alone, at a phone's width,
  in its navigation (back, a deep link, a reload) and for each kind of
  user -- one state line each, `hover`, `keyboard`, `mobile`,
  `navigation`, `permissions`, with the same Status, Evidence and
  Investigation.
- **Transitions**: what moves the screen from one state to another, a
  line per event: From -- `normal`, a state above, or `any` -- the Event,
  To -- a state, or another screen -- and what it leads to, the
  requirement it shows and the findings it was seen in, each by ID in
  its column. A finding of what a user does or what fails, that became a
  requirement the screen shows and that no transition names, is
  behaviour the screen may have left out: a review asks it.
- **Variants**, where it differs for another kind of user: a line per
  difference, with what it is about.
- **Layout**, where a number must hold: a width, a height, a space, an
  order, each with what fixes it -- a requirement or a finding by ID, or
  the foundations.

Large or dense screens: number the regions, then one representative row
or item, and say in its row that the rest repeat. A grid of forty
columns is numbered as its groups, not as forty headings.

### Screen kinds

What a screen of each kind likely has, which its States account for.

| Kind | Is | The states it likely has |
|---|---|---|
| `page` | a page that shows what the product holds | empty, loading, error |
| `list` | a list, a table, a grid of things, searched or filtered | empty, loading, error, no-results |
| `form` | where a user enters something and sends it | empty, validation, error, loading, success, disabled, unauthorized |
| `detail` | one thing, opened by its address | loading, error, not-found, unauthorized |
| `dialog` | a dialog, a panel or a popup over another screen | loading, error |
| `wizard-step` | one step of several, toward one end | empty, validation, error, loading, success |
| `message` | what arrives: a notification, an email, a toast | none |

### Behaviours

| Behaviour | What it says |
|---|---|
| `hover` | what changes under the pointer, and what a touch screen has in its place |
| `keyboard` | the order Tab reaches the elements in, how the focus shows, what Enter and Escape do |
| `mobile` | what the screen does at 375 pixels: what moves, what hides, what folds into a menu |
| `navigation` | where back leads, whether the address opens the screen as it was, what a reload keeps |
| `permissions` | what each kind of user sees, and what someone without the right sees |

### States that are one

A state written by another name is that state.

| State | Also written |
|---|---|
| `error` | failing, failed, failure |
| `unauthorized` | refused, forbidden, signed out |
| `no-results` | nothing found, no match, filtered |
| `not-found` | unknown address, missing |
| `success` | sent, saved, confirmed, done, placed |

## Prototypes

A prototype is the screen drawn: what a person looks through, and what
an engineer takes the layout and the words from. It holds how the
screen looks at each width and every word it shows, so that neither is
written twice. It is `prototypes/screens/SC3.html`, the markup of the
screen's body, `<main data-prototype="SC3">` around it; the application
serves it inside the product's page, `prototypes/page.html`, which holds
`{{title}}` and `{{body}}` and links the product's styles and scripts
from `prototypes/assets/`.

- **One anchor per element, and nothing else of what it means.** Each
  element of the screen's Elements carries `data-el="13"`, its number;
  each part of a component, `data-part="C3.1"`, its row of the
  component's Parts, on every screen it is on. What the element shows,
  what it is about, what component it is, what question it asks, is its
  row: never an attribute. Every anchor has its row and every element's
  row its anchor: the check holds both ways, and a part's row may stand
  without one, on a screen that does not draw that part. A `data-spec-*` attribute, how links
  were written in markup before, is refused. `spec.py open` says what
  else falls short, and `ready` will not pass while it does: anything
  shown with no anchor; a state the prototype draws and its States do not
  list; a link its row's Leads to does not say, or one the row says and
  the prototype does not draw; markup that is not strict -- a tag left
  open, an id used twice, an image with no `alt`, styles or a script of
  its own.
- **`add-row` draws a placeholder.** An element added through the logic
  puts `<div data-el="14" class="spec-new">… -- to be drawn</div>` at the
  end of the prototype, so that it is seen until someone draws it where
  it belongs; `remove` takes its anchor out of the markup.
- **A piece the screens share is written once.** A header or a footer
  every screen holds alike goes in `prototypes/shared/C1.html`, named for
  its component: what goes inside the element, each thing in it carrying
  its `data-part`. Each screen holds the element, its class and its
  anchor, marked `data-stamp="C1"`, and `spec.py stamp` writes the piece
  into every one. A copy changed by hand holds an agreement, and a piece
  that differs from screen to screen stays in each screen.
- **Grey until there is a look.** A look nobody gave is not invented.
  Until there is one, `<main>` keeps `class="wire"`, and the grey classes
  of `live.css` draw it -- region, row, spread, col, card, btn, tiny,
  pill, field, msg, popup, list, small, box, new, a grid table, pin --
  with the real labels and real sample values: it shows structure, and
  is not taken for the design.
- **One look, once.** Once the product has a look, the prototype is drawn
  with `prototypes/assets/css/product.css` and the classes the components
  are drawn with, so that the design and the prototype cannot disagree;
  `wire` comes off.
- **The values live in `tokens.json`, and nowhere else.** The page shell
  links `assets/css/tokens.css`, which is not a file: the application makes
  it from `tokens.json` whenever it is asked for, and the export does the
  same, each token as the variable `--<group>-<name>`. So `color.action` is
  `var(--color-action)`, a screen types no value of its own, and a value
  changed in `tokens.json` changes every screen, component and drawing. `spec.py check`
  refuses a variable no token holds. Never write a `tokens.css` or a script
  for it. CSS can't read a variable in a media query, so a breakpoint
  repeats its token there.
- **States and variants** come from `live.js`, which the application
  serves to every prototype: blocks marked `data-when="empty"` or
  `data-unless="empty"`, variants with `data-as` and `data-unless-as`, and
  on `<main>`, `data-states` and `data-variants` for those only the
  product's script shows; dialogs with `data-open="id"` on a `<dialog
  id>` and `data-close` in it. The prototype view offers each in its
  toolbar, with the width, and shows each element's links in its
  inspector.
- **Sample data** is `prototypes/assets/js/sample.js`: records taken from
  the material, or the requirements' own examples, never a fact made up.
  What the product does beyond showing -- a cart that adds, a list that
  pages -- is `prototypes/assets/js/prototype.js`, the product's: only
  what the requirements say, each piece naming its requirement.
- **Alike where the screen exists.** Rebuilding a site, set the prototype
  beside the captured screenshot at each width and correct what differs
  until they are alike. What still differs, and why, is said in the
  screen's purpose or a Layout line. Pictures are grey placeholders
  unless the user allows the site's own.
- **A reference, never the code.** Whoever builds the product takes the
  layout, the look and the words from the prototype, and the behaviour
  from the requirements.

## Asking for the look

**This is a must, every time.** Before the first screen, prototype or
component is drawn, stop and ask. The session never chooses a look on its
own, and a word in the brief such as "modern" or "warm" opens these
questions and doesn't answer them. Where material shows the product's look,
say what was found and ask whether to keep it.

Ask these together, in one round, and say why they matter: every screen is
built from the answers.

| Ask | Why, and what to do with the answer |
|---|---|
| **Is there a design system already?** A brand book, a style guide, a Figma file, a component library, an existing product, a stylesheet | It's the source, and is followed rather than reinvented. Read it, take its values into `prototypes/tokens.json`, and name it |
| **Is there a brand?** A logo, colours, fonts, a tone of voice | These are facts only the user has. Ask for the files |
| **What do you like?** Sites, apps, images, screenshots, a mood board, anything to point at, and what you like in each | The best way to get a look from someone who can't describe one. Open or read each, and note what it shows |
| **What should it never look like?** A competitor, a style to avoid | Saves a wrong first draft |
| **What should it feel like?** Three words, and who it's for | Decides between directions |
| **Which theme?** Light, dark or both, the main colours, and a colour for each meaning such as success and error | Becomes the tokens. Each theme is a full set of values |
| **Type and shape:** fonts, how dense, rounded or square corners, shadows or flat | Becomes the foundations. A font must be free to use, or the user's own licence |
| **Pictures:** photos they own, drawn illustrations, icons | Says what the prototype can show. Nothing is taken from a site without the right to use it |
| **Who must it work for?** Which devices, what level of accessibility | Sets the breakpoints and the contrast to hold, 4.5:1 for text at the least |

**When the user has no answers,** offer two or three directions, each a
named idea with its colours, type and a small sample, and recommend one.
What they choose becomes a decision, with the directions turned down. "You
decide" still gets a recommendation and a yes, as [asking.md](asking.md)
says.

**When the user doesn't want a look yet,** the prototype stays grey, and one
foundation says so, with who decides and when. That's a choice they made,
not a gap.

**Keep what was given.** A design system or an inspiration is a source, `add
source`, kept in `evidence/`, and what was taken from it a finding with its
quote or description, so each foundation shows where it came from. Never
copy a site's own logo, pictures or words into the prototype.

**What a professional design system holds** before screens are drawn in the
look: colours with their meanings and contrast, a type scale, a spacing
scale, the grid and breakpoints, shape and elevation, the states every
control has (under the pointer, focus, disabled, error), and all of it in
`prototypes/tokens.json`, so that no screen types a value of its own. A
token is named by its meaning -- `color.brand`, `color.bad-soft`,
`shadow.card` -- never by the number a capture gave it (`text-1`); the
foundations' tables name the tokens, and a value changed in `tokens.json`
lists every prototype it reaches as one to look at, with what moved. A
specification whose styles still write values is moved over by
`scripts/tokens.py --apply <folder>`: each custom property with a colour
becomes a token named after it, every page names the token, and the
colours no token holds are listed to be named.

**Every later time** screens are added or redrawn, say which design system
they will use and ask whether it still holds, in one line. A new source or
theme goes through this section again.

## Design: foundations and components

Together they are the product's design system, as far as a specification
can hold one: the decisions every screen is built from, written once.
There is no code library and no design file behind them, and they record
decisions; they do not make them. Where there is a designer, or the team
builds on a library that exists, they are short: which library, which of
its values are changed, and the few components that are the product's
own.

**The foundations** are a node each, `add foundation "Colours and what
they mean" says="..."`, and the values in `prototypes/tokens.json`, which
the design-system view draws. A foundation's table names a token, never a
value -- `| swatch brand | --color-brand | it can be pressed | ... |` -- and
the page shows the value beside the name; a colour written in a foundation
is refused by `check`. Every screen and component says which foundations
it is drawn by, `follows: FD1, FD2, FD5` in its header, so that a
foundation changed reaches each of them as stale; one following none,
where foundations exist, is a fault `open` lists:

- **Colours and what they mean**: a rule is "green means a gain", not
  "use #36d399". The value is there so the rule can be applied.
- **Text**: the sizes and weights in use.
- **Density and spacing**: the spacing scale, row heights, what is
  grouped, how much room.
- **Layout**: the grid, the breakpoints, the widths a page may have, its
  margins.
- **Shape and elevation**: corner radii, border widths, shadows, each
  with where it applies.
- **Motion**: what moves, how long and how it eases; and what never
  moves.
- **Icons**: the set, the sizes, the stroke, and whether a word always
  stands beside one.
- **Patterns**: what is done the same way everywhere -- a failure, an
  empty screen, loading, the confirmation of what cannot be undone, a
  form and its validation, search and filtering, how money, numbers and
  dates are written, what is shown by colour and what else carries it.
- **Words**: the voice; how a button, a label and an error are worded;
  capitalisation; the terms, which are the Domain's.
- **Accessibility**: contrast, focus, the keyboard and what a screen
  reader is told, as rules that cut across every screen; a screen's own
  are in its rows and states.

**A component** is a building block used in more than one place, or with
more than one state: a button, a card, a cell, a message, a popup.

- **What it is for**, its purpose, and when to use it and when not.
- **Its variants**, each a line of its Variants -- `add-line C1 variants
  disabled when="the product is out of stock"` -- and each drawn in
  `prototypes/components/C1.html`, one element with `data-variant="disabled"`
  each, in the product's look: default, under the pointer, with the
  keyboard's focus, disabled, in error, on and off -- those it really
  has. A state it cannot be in is left out; one nobody decided is asked,
  never guessed. To draw a state that needs the pointer, give it a class
  of its own, with a class such as `.ml-hover` beside the real one (`.is-hover` is taken: the prototype's runtime strips it). Every variant has its
  drawing, and every drawing its variant: the check holds both.
- **Its rules**: what holds wherever it is used -- its sizes, what it may
  contain, where it sits, what it must never do.
- **Its parts**, where a user meets it piece by piece -- the mark, the
  search, each link of a menu, the price of a card -- a row each, `add-row
  C9 name="Search" is=field does="..." shows=R7`, defined once and carried
  as `data-part="C9.2"` on every screen it is on, so that a header on
  eighteen screens is written once and says the same everywhere.
- An element that is a component names it in its Component column, `is`:
  the engineer then builds it once, and the component's node says which
  elements use it.
- **Made of others.** A toolbar of buttons, a row of cards: a combination
  that is a region of a screen is a component too, `made of` the
  components it combines, its drawing the combination whole, its rules
  the arrangement.

What is a component and what is only part of one screen: if it appears
on two screens, or has states of its own, it is a component. Do not make
one of everything; a prototype already says what is on a screen.

Where the product exists, take the values and the components from its
stylesheet, its code, the styles captured from it as a live site, or its
screenshots, and name the source. Where it does not, ask, as "Asking for
the look" says: a look nobody chose is not written.

## Three levels of fidelity

Use the cheapest that answers the question at hand.

| Level | Is | Use it |
|---|---|---|
| a text sketch | a few lines of boxes in the conversation | to offer the user layouts to choose between, while asking |
| screens with grey prototypes | flows and screens beside the requirements, each drawn in grey | to hand over with the requirements before there is a look |
| the prototype in the product's look | each screen drawn with the design's classes | to talk it through, to judge an interaction, and to give engineers the layout and the look to build from |

## Keeping them in step

An element, a step, a transition points at a requirement by ID, so a
change to the requirement reaches them by itself: `spec.py impact R4`
says, before the change, every element, screen, part and endpoint that
would be stale; after it, each is stale until it is read against what
changed and confirmed, `do confirm SC3.13 <print>`, the print `stale` shows. A change asked in a screen
or a prototype starts from what its elements stand on: where it moves
behaviour a requirement states, that requirement changes first, or the
request contradicts it and is asked. Once screens are written, the
document's Interface section goes: states live in one place.
