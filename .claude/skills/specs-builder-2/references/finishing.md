# Review, answer, change, agree

What is done to a specification that exists: read it as an engineer
would, answer what is open in one sitting, work a change through it,
record that it is agreed. Every command below is `python app/spec.py
<command>`, run in the specification's folder; each takes `--json` for an
agent.

## Review: what would an engineer ask?

Asked to review a specification, or what is missing from one:

1. Run `spec.py check`: every file held to the grammar, each problem at
   its file and line. Then `spec.py open`: all that is not settled -- the
   questions, the additions not confirmed, the qualities and risks left
   open, the contradictions, the findings that became nothing, what is
   stale, the requirements and rules on weak ground or documented only,
   and the notes on words a
   review reads for ([writing.md](writing.md), The fixed words). The
   application's Open view shows the same.
2. Read it as part 4 of [aspects.md](aspects.md) describes: as the
   engineer who builds the first release tomorrow and has never met the
   product side -- `spec.py plan` for the order they would build in,
   `spec.py unit <id>` for all one thing needs. Where there are screens,
   read them the same way: could each be built from its prototype, its
   elements, its states and its transitions, and does each flow say what
   happens when a step fails?
3. Report:

   ```
   Check: PASSED | FAILED -- <n> problem(s), <n> note(s)
   | # | where | the question an engineer would ask | resolution |
   Rests on: <the assumptions, and how each could be checked>
   On weak ground: <the requirements and rules inferred, disputed or added, by ID>
   Documented only: <those only documents stand behind, by ID, to check against the product>
   Added and not confirmed: <the additions, by ID>
   Open for the product side: <the open questions and the open qualities>
   Open for engineering: <the open questions for engineering>
   Verdict: ready | not ready -- <the one thing that decides it>
   ```

   `resolution` is `written`, `asked` or `engineering's`, as part 4
   defines them.
4. Offer to write the gaps in, or to ask them.

A specification in another form is read by hand, and the skill offers
to bring it into this one: that is the reverse-engineer mode with the
document as the material, in the role `intent`. One made by specs-builder
is brought over whole by `scripts/import_site.py`.

## Answer: what is open, in one sitting

Asked "what is open", "let's settle the questions", or when a review or a
walk leaves more questions than a round of write-ask can carry:

1. Run `spec.py open`. It lists the open questions a person answers --
   the skill's own, `investigate:`, it finds out itself first -- the most
   deciding first: one about a `must` before one about a `should`, and
   of two, the one more stands on. Each says what it touches.
2. Ask them in rounds of up to four, one topic to a round, each in the
   format [asking.md](asking.md) gives it: a choice with options and a
   recommendation where the options are known, a number where one is
   missing, a scenario for an edge. Say what each touches, so the stakes
   are seen. A question the user cannot answer now stays, and is not
   asked again in the sitting.
3. After each round, write the answers in before asking the next: each
   where it belongs, and what the answer implies for the cases around
   it, as additions. Then settle the question as one operation:

   ```
   do answer Q3 "<what was chosen>" because="<why>" instead="<what was turned down>"
   ```

   It makes a decision of the answer, about what the question was about;
   moves every link to the question onto the decision -- a row that asked
   it is now about it -- and removes the question, its ID retired. It is
   refused while a text still names the question -- a risk's mitigation,
   a screen's `who` -- naming each place: write the answer there first,
   with `set`, in the same change set. A new question is asked with `do
   add question "<a short name>" question="..." why="..." answers=<who>
   about=R6`. Where an answer changes a requirement, it is a change: work
   it as the next section says.
4. Stop when the list is done or the user says so, and report what was
   settled, by ID, and what is left.

## Change: when something moves

A change comes from the user in the conversation, or from the inbox:
`spec.py inbox` lists what waits, each with who asked, what it is about
and what it asks. The application has no forms, so this is the only way a
specification changes, and it is carried all the way through here.

1. Name what changes: a goal, a requirement, a decision -- or a screen,
   a prototype, a component, where the user asks it there. Run
   `spec.py impact <ID>` and tell the user what else moves before
   changing anything: what it stands on, what would be stale at once if
   it changed, and what further if those changed in turn; what is
   unsettled about it, and what is stale already. A change asked in a
   screen or a prototype starts from what its elements stand on: where it
   moves behaviour a requirement states, that requirement changes first,
   or the request contradicts it and is asked. **Show the whole change
   before making it**: each node you would change and how, each screen you
   would redraw, what you would leave and why. Make it once the user says
   so. Nothing is rewritten unseen.
2. Make it through the logic, never by editing a file around it:

   | Operation | Does |
   |---|---|
   | `add <kind> "<name>" key=value ...` | a node, with the next free ID: `add requirement "Keep a wish list" priority=should serves=G2 statement="... shall ..."` |
   | `add-row <id> key=value ...` | a criterion, an element, a part, an entity's state: `add-row R6 says="Given ..."` |
   | `add-line <id> <table> [first] key=value ...` | a line of a screen's, an entity's or an endpoint's table: `add-line SC3 states empty status=likely` |
   | `remove-line <id> <table> <first cell>` | that line taken out |
   | `set <id> <key> <value>` | a field, a text, a cell, a whole table: `set R4 priority should`, `set document status draft` |
   | `tie <id> <relation> <id>`, `untie ...` | one link, where it is written: `tie SC9.3 shows R16`, `tie R6 serves G2`, `tie U1 may R4 "add to the cart"` |
   | `retarget <old> <new>` | every link to the old and every mention of it moved to the new; what defines the old left as it is |
   | `remove <id> [--untie]` | a node and its rows, once nothing links to it -- what does is listed -- or with `--untie`, those links too; additions to it go with it; its ID retired |
   | `answer`, `confirm-added`, `confirm` | below |

   `spec.py kinds <kind>` says what each kind takes. An ID is never
   renumbered and never given twice. A requirement being left out
   becomes `wont`, with why. A name is a field: `set R4 name "..."`
   renames it everywhere, since every link is by ID. Two requirements
   made of one are a change set: `add requirement` the new one,
   `add-row $1` the criteria it takes over, `remove` them from the old.
   Operations that belong together go in a change set, a file of one
   operation to a line, `#` a remark, applied with `do --file <file>`:
   each on what the one before left, so a later one names what an
   earlier one made as `$1`, `$2`; all are done or, at the first refusal
   or at anything that would not load clean, none, with why. `--dry-run`
   says what would change, field by field, and writes nothing; `--because
   D3` and `--who` are logged with it.
3. Record the decision: `add decision "<name>" decision="..."
   because="..." instead="..." about=R4`, or `answer` where it settles a
   question.
4. A specification that was agreed takes no change until it is set back:
   `set document status draft`, first in the same change set or before.
   Every node that stands on what changed is now stale -- `spec.py stale`
   says each, and what moved, before and after: read each against it,
   change what no longer holds, and confirm it, `do confirm <id>`. Never
   confirm what was not read. A prototype is written by hand: `spec.py
   open` lists each one whose screen, or what it shows, moved while its
   file did not. Read it: redraw `prototypes/screens/<ID>.html` where it
   no longer holds, or say it does with `do confirm-drawn <ID>`. Either
   clears it, and only a drawing read may be confirmed.
5. Close what it came from: `spec.py inbox --close <no>`. A request that
   needs a decision first becomes an open question instead,
   `spec.py inbox --raise <no>`, and one that contradicts the specification
   is asked. Where code was built from it, `spec.py changed --target <code>`
   says what to redo.
6. Say what changed, what was confirmed, and what the change left open.
   `spec.py history <id>` tells what changed, when, by whom and why, as
   the node's History view does.

## Agree: is it ready?

A specification is `draft` until the user says it is agreed. Before that:

1. `spec.py check` passes.
2. **Every addition is confirmed or corrected.** Go through the ones left
   with the user, several to a round: `do confirm-added AD3`, or
   `confirm-added R4` for every addition to R4 and its rows.
3. **Challenge it once.** Make the strongest honest case that it fails on
   each of the four risks -- value: who has asked for this, and is today
   really bad enough to change? usability: could the user in the journey
   do this with what they know? feasibility: is there anything whose cost
   nobody has estimated? viability: does the cost fit the worth? Give
   only the objections with substance. One the user answers with what is
   done about it becomes a risk with its mitigation; one they cannot
   answer becomes an assumption with its check, or an open question.
4. `spec.py ready` says nothing stands in the way: nothing stale, no
   addition, every open question one for engineering, no quality or risk
   left open, no contradiction unsettled, no finding that became
   nothing. The logic refuses `agreed` otherwise, saying every reason.

Then, once the user says so, `do set document status agreed`. Only the
user agrees a specification.

To hand the specification to someone without Python, `spec.py export`
writes it as one HTML file.
