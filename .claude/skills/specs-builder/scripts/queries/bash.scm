; What scan_code.py finds in Bash, by tree-sitter: what a script lets someone do, what it talks to, what it says and
; how it fails. Each capture is named <lens>.<kind>; a capture whose name starts with _ only tests the match.

; action: what a user can do
(function_definition) @action.command

; shows: what a user reads
(command name: (command_name) @_n (#match? @_n "^(echo|printf|read)$")
  argument: [(string) (raw_string)]) @shows.message

; rule: rules and limits
(variable_assignment name: (variable_name) @_n (#match? @_n "^_?[A-Z][A-Z0-9_]{2,}$") value: (number)) @rule.constant

; system: other systems
(command name: (command_name) @_n
  (#match? @_n "^(curl|wget|ssh|scp|rsync|aws|az|gcloud|kubectl|helm|docker|psql|mysql|sqlcmd|mongosh|redis-cli|dotnet|terraform|sendmail|mail)$")) @system.call
(string (string_content) @_s (#match? @_s "^(https?|wss?)://")) @system.address
((declaration_command) @system.setting (#match? @system.setting "^export "))

; access: who may do what
(command name: (command_name) @_n (#match? @_n "^(sudo|su|chmod|chown|runuser)$")) @access.check

; failure: what happens when it fails
(redirected_statement
  body: (command name: (command_name) @_n (#match? @_n "^(echo|printf)$"))
  redirect: (file_redirect destination: (number) @_d (#eq? @_d "2"))) @failure.message
(command name: (command_name) @_n (#eq? @_n "exit") argument: (number) @_c (#not-eq? @_c "0")) @failure.exit
(command name: (command_name) @_n (#eq? @_n "trap")) @failure.catch

; loose: what looks unfinished
((comment) @loose.todo (#match? @loose.todo "TODO|FIXME|HACK|XXX"))
