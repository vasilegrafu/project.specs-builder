---
id: SC7
name: Remove this feedback
kind: dialog
who: signed-in staff
reached by: Remove on SC6
shows: R12
---

Staff confirm before a piece of feedback is removed.

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The heading | heading | Remove this feedback? |  | Remove this feedback? |  | R12 |  |  |  |
| 2 | The line | text | Says it leaves the list and the monthly figures, and cannot be put back. |  | the line |  | R12 |  |  |  |
| 3 | Could not be removed | message | When the removal failed; the feedback stays. | shown on error | Could not be removed | C6 | R12 |  |  |  |
| 4 | Remove | button | Removes the feedback. Leads back to SC6. | removing | Remove | C3 | R12 |  |  | SC6 |
| 5 | Keep it | button | Closes the dialog; the feedback stays. Leads back to SC6. |  | Keep it | C3 | R12 |  |  | SC6 |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| loading | added | Remove cannot be pressed again. |  |  |
| error | added | Could not be removed; the feedback stays. |  |  |
| hover | added | Its buttons mark themselves under the pointer; a touch screen has nothing in its place. |  |  |
| keyboard | added | The focus starts on Keep it and stays in the dialog; Escape keeps the feedback. |  |  |
| mobile | added | At 375 pixels the dialog fills the width. |  |  |
| navigation | added | It has no address of its own; a reload shows the list. |  |  |
| permissions | added | Only signed-in staff. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Remove is pressed | SC6 | SC6 | R12 |  |
| normal | Keep it is pressed, or Escape | SC6 | SC6 | R12 |  |
| normal | The removal fails | error |  | R12 |  |
