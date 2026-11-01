; What scan_code.py finds in CSS, by tree-sitter: how the product looks, and what it takes from elsewhere. Each capture
; is named <lens>.<kind>; a capture whose name starts with _ only tests the match.

; look: how it looks
(declaration (property_name) @_p (#match? @_p "^--")) @look.token
(color_value) @look.colour
(declaration (property_name) @_p
  (#match? @_p "^(font-family|font-size|font-weight|line-height|border-radius|box-shadow)$")) @look.font
(media_statement) @look.breakpoint

; system: what it takes from elsewhere
(import_statement) @system.import

; loose: what looks unfinished
((comment) @loose.todo (#match? @loose.todo "TODO|FIXME|HACK|XXX"))
