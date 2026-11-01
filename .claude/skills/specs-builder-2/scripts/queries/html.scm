; What scan_code.py finds in HTML -- and in the templates written as HTML: Razor, Jinja, htmx -- by tree-sitter. Each
; capture is named <lens>.<kind>, as scout.py names the lenses; a capture whose name starts with _ only tests the
; match. The captured node is the fact: its first line is what a finding quotes.

; action: what a user can do
(start_tag (tag_name) @_t (#eq? @_t "form")) @action.form
(start_tag (tag_name) @_t (#eq? @_t "a") (attribute (attribute_name) @_h (#eq? @_h "href"))) @action.link
(start_tag (tag_name) @_t (#eq? @_t "button")) @action.button
(start_tag (tag_name) @_t (#eq? @_t "input")
  (attribute (attribute_name) @_y (#eq? @_y "type") (quoted_attribute_value (attribute_value) @_v))
  (#match? @_v "^(submit|button|reset)$")) @action.button
(attribute (attribute_name) @_n (#match? @_n "^(hx|data-hx)-(get|post|put|patch|delete)$")) @action.request
(attribute (attribute_name) @_n (#match? @_n "^on[a-z]+$")) @action.handler

; shows: what a user reads
((text) @shows.text (#match? @shows.text "[A-Za-z]"))
(attribute (attribute_name) @_n
  (#match? @_n "^(aria-label|aria-description|placeholder|title|alt|label|data-tooltip|data-title)$")) @shows.label

; rule: rules and limits
(attribute (attribute_name) @_n
  (#match? @_n "^(required|maxlength|minlength|min|max|pattern|accept|step|multiple|readonly)$")) @rule.limit

; data: the choices a user is given
(start_tag (tag_name) @_t (#eq? @_t "select")) @data.choices
(element (start_tag (tag_name) @_t (#eq? @_t "option"))) @data.choice

; system: other systems
(script_element (start_tag (attribute (attribute_name) @_n (#eq? @_n "src")))) @system.script
(attribute (attribute_name) @_n (#match? @_n "^(href|src|action|hx-get|hx-post)$")
  (quoted_attribute_value (attribute_value) @_v (#match? @_v "^(https?|wss?)://"))) @system.address

; loose: what looks unfinished
((comment) @loose.todo (#match? @loose.todo "TODO|FIXME|HACK|XXX"))
