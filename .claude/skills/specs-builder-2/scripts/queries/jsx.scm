; What scan_code.py finds in JSX markup, in JavaScript and in TSX, beside script.scm. Each capture is named
; <lens>.<kind>; a capture whose name starts with _ only tests the match.

; action: what a user can do
(jsx_attribute (property_identifier) @_n (#match? @_n "^on[A-Z]")) @action.handler
(jsx_opening_element name: (identifier) @_t (#match? @_t "^(form|Form)$")) @action.form
(jsx_self_closing_element name: (identifier) @_t (#match? @_t "^(Route|Redirect|Navigate)$")) @action.route
(jsx_opening_element name: (identifier) @_t (#match? @_t "^(Route)$")) @action.route
(jsx_opening_element name: (identifier) @_t (#match? @_t "^(Link|NavLink|a)$")
  (jsx_attribute (property_identifier) @_h (#match? @_h "^(to|href)$"))) @action.link
(jsx_self_closing_element name: (identifier) @_t (#match? @_t "^(Link|NavLink|a)$")
  (jsx_attribute (property_identifier) @_h (#match? @_h "^(to|href)$"))) @action.link

; shows: what a user reads
((jsx_text) @shows.text (#match? @shows.text "[A-Za-z]"))
(jsx_attribute (property_identifier) @_n
  (#match? @_n "^(aria-label|aria-description|placeholder|title|alt|label|helperText|tooltip|description|emptyText|errorMessage|confirmText|cancelText|okText)$")
  (string)) @shows.label

; rule: rules and limits
(jsx_attribute (property_identifier) @_n
  (#match? @_n "^(required|maxLength|minLength|min|max|pattern|accept|maxlength|minlength|step|multiple)$")) @rule.limit

; access: who may do what
(jsx_opening_element name: (identifier) @_t
  (#match? @_t "(Protected|Private|Require|Auth|Guard|Authorized|Can|Permission)")) @access.check
(jsx_self_closing_element name: (identifier) @_t
  (#match? @_t "(Protected|Private|Require|Auth|Guard|Authorized|Can|Permission)")) @access.check
(jsx_attribute (property_identifier) @_n (#match? @_n "^(disabled|hidden|readOnly)$") (jsx_expression)) @access.state

; look: a component of the interface -- a function or an arrow function named with a capital that returns markup
(function_declaration name: (identifier) @_n (#match? @_n "^[A-Z][A-Za-z0-9]*$")
  body: (statement_block (return_statement [(jsx_element) (jsx_self_closing_element)
                                            (parenthesized_expression [(jsx_element) (jsx_self_closing_element)])]))) @look.component
(variable_declarator name: (identifier) @_n (#match? @_n "^[A-Z][A-Za-z0-9]*$")
  value: (arrow_function body: [(jsx_element) (jsx_self_closing_element)
                                (parenthesized_expression [(jsx_element) (jsx_self_closing_element)])
                                (statement_block (return_statement [(jsx_element) (jsx_self_closing_element)
                                  (parenthesized_expression [(jsx_element) (jsx_self_closing_element)])]))])) @look.component
