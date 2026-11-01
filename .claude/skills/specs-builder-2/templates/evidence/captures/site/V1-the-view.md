# V1 · <<the view's name, as its users would say it>>

- **Address:** <<the address it was captured at>>
- **Title:** <<the page's title>>
- **Captured:** <<YYYY-MM-DD HH:MM, at widths 1280, 768 and 375>>
- **Screenshots:** <<the screenshots, from this file: shots/V1-1280.png, ...; or `none` and why>>
- **Redacted:** <<what kind of thing was replaced by [redacted]; or `nothing`>>

## On the page

<<one element to a line, with its role, its words as they stand, and its state; scripts/capture.js writes it:>>
region: <<a part of the page: header, navigation, main, footer>>
heading: <<the heading>>
text: <<a paragraph>>
link: <<the words of a link>> → <<where it leads: /a/path on this host, or host/path on another>>
button: <<the words on a button, and its state: (expanded), (disabled)>>
form: <<its name>> · <<its method and where it sends: POST /invoices>> · fields: <<their labels>> · submit: <<its button>>
field: <<a field's label, its limits: (required, maxlength 80)>> · placeholder: <<its placeholder>>
message: <<a message the view shows>>

## Hidden on the page

hidden: <<what the page holds and does not show yet -- a closed dialog, a menu -- and what it offers>>

## After actions

### <<what was done: Left Amount empty and moved on>>

message: <<what the view then showed>>

## Requests

request: <<fetch GET /api/a/{id} → 200 {its shape}, where watch.js ran first; the host of another site>>

## Styles

style: <<the element: the property and its value, as the page holds it>>

## Accessibility tree

```yaml
<<the browser's own tree of the view, written by scripts/a11y_tree.py from the browser tool's snapshot>>
```
