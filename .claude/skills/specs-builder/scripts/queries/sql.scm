; What scan_code.py finds in SQL, by tree-sitter: the schema only -- what is kept, its limits and its states -- never
; a row. Each capture is named <lens>.<kind>; a capture whose name starts with _ only tests the match.

; data: what is kept, and the states a thing can be in
(create_table) @data.table
(create_view) @data.view
(create_type (enum_elements)) @data.enum
(enum_elements (literal) @data.member)
(column_definition (keyword_check) (binary_expression operator: (keyword_in) right: (list))) @data.enum
(column_definition (keyword_references)) @data.relation
(constraint (keyword_foreign)) @data.relation

; rule: rules and limits
(column_definition (keyword_not) (keyword_null)) @rule.limit
(column_definition (keyword_unique)) @rule.limit
(column_definition (keyword_check)) @rule.limit
(column_definition (keyword_default)) @rule.default
(constraint (keyword_check)) @rule.limit
(create_index (keyword_unique)) @rule.limit
(create_trigger) @rule.trigger

; action: what can be called
(create_function) @action.procedure

; loose: what looks unfinished
((comment) @loose.todo (#match? @loose.todo "TODO|FIXME|HACK|XXX"))
