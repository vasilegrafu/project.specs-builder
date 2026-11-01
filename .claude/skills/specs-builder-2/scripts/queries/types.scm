; What scan_code.py finds in TypeScript alone, beside script.scm: the types. Each capture is named <lens>.<kind>; a
; capture whose name starts with _ only tests the match.

; data: what is kept, and the states a thing can be in
(enum_declaration) @data.enum
(enum_body (property_identifier) @data.member)
(enum_body (enum_assignment) @data.member)
(type_alias_declaration value: (union_type (literal_type (string)))) @data.enum
(interface_declaration) @data.model
