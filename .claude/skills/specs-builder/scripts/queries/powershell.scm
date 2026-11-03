; What scan_code.py finds in PowerShell, by tree-sitter: what a script lets someone do, its parameters and their
; limits, what it talks to, what it says and how it fails. Each capture is named <lens>.<kind>; a capture whose name
; starts with _ only tests the match. Command names are matched in any case, as PowerShell reads them.

; action: what a user can do
(function_statement) @action.command

; shows: what a user reads
(command command_name: (command_name) @_n
  (#match? @_n "(?i)^(Write-Host|Write-Output|Write-Warning|Write-Information|Read-Host)$")) @shows.message

; rule: rules and limits
(attribute (attribute_name) @_n
  (#match? @_n "^(Parameter|ValidateRange|ValidateLength|ValidatePattern|ValidateNotNull|ValidateNotNullOrEmpty|ValidateCount|ValidateScript)$")) @rule.limit

; data: what is kept, and the states a thing can be in
(enum_statement) @data.enum
(enum_member) @data.member
(attribute (attribute_name) @_n (#eq? @_n "ValidateSet")) @data.enum
(class_statement) @data.model

; system: other systems
(command command_name: (command_name) @_n
  (#match? @_n "(?i)^(Invoke-RestMethod|Invoke-WebRequest|Invoke-Sqlcmd|Invoke-Command|New-PSSession|Send-MailMessage|Start-BitsTransfer|curl|az|aws|docker|kubectl|dotnet|git)$")) @system.call
((variable) @system.setting (#match? @system.setting "(?i)^\\$env:"))
((expandable_string_literal) @system.address (#match? @system.address "^\"(https?|wss?)://"))
((verbatim_string_characters) @system.address (#match? @system.address "^'(https?|wss?)://"))

; access: who may do what
((comment) @access.check (#match? @access.check "(?i)^#Requires\\s+-RunAsAdministrator"))

; failure: what happens when it fails
((flow_control_statement) @failure.throw (#match? @failure.throw "(?i)^throw"))
(catch_clause) @failure.catch
(command command_name: (command_name) @_n (#match? @_n "(?i)^Write-Error$")) @failure.message

; loose: what looks unfinished
((comment) @loose.todo (#match? @loose.todo "TODO|FIXME|HACK|XXX"))
