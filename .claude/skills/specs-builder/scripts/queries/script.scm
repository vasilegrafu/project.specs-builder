; What scan_code.py finds in JavaScript and TypeScript, by tree-sitter: what the two share, with or without JSX.
; jsx.scm adds the markup, types.scm what only TypeScript has. Each capture is named <lens>.<kind>, as scout.py names
; the lenses; a capture whose name starts with _ only tests the match. The captured node is the fact: its first line
; is what a finding quotes. Express, React Router, zod, yup, fetch and axios are what these patterns know.

; action: what a user can do
(call_expression
  function: (member_expression object: (identifier) @_o property: (property_identifier) @_n)
  (#match? @_o "^(app|router|server|api|routes|fastify)$")
  (#match? @_n "^(get|post|put|delete|patch|all|route|use)$")
  arguments: (arguments . [(string) (template_string)])) @action.route
(pair key: [(property_identifier) (string)] @_k (#match? @_k "^\"?path\"?$") value: (string)) @action.route
(call_expression function: (identifier) @_n (#match? @_n "^(addEventListener)$")) @action.handler
(call_expression function: (member_expression property: (property_identifier) @_n)
  (#eq? @_n "addEventListener")) @action.handler

; shows: what a user reads
(call_expression function: (identifier) @_n (#match? @_n "^(alert|confirm|prompt|t|i18n)$")
  arguments: (arguments . [(string) (template_string)] @shows.message))
(call_expression
  function: (member_expression object: (identifier) @_o property: (property_identifier) @_n)
  (#match? @_o "^(toast|message|notification|notify|snackbar|enqueueSnackbar|Swal|window)$")
  (#match? @_n "^(error|warning|warn|info|success|show|open|alert|confirm|fire|loading)$")
  arguments: (arguments . [(string) (template_string)] @shows.message))
(assignment_expression
  left: (member_expression property: (property_identifier) @_p)
  (#match? @_p "^(textContent|innerText|title|placeholder|value)$")
  right: [(string) (template_string)] @shows.text)
(pair key: [(property_identifier) (string)] @_k
  (#match? @_k "^\"?(title|label|placeholder|message|description|headerName|tooltip|helperText|errorMessage|emptyText)\"?$")
  value: [(string) (template_string)] @shows.label)

; rule: rules and limits
(call_expression
  function: (member_expression object: (_) @_o property: (property_identifier) @_n)
  (#not-match? @_o "^Math$")
  (#match? @_n "^(min|max|length|gte|lte|gt|lt|minLength|maxLength|multipleOf|positive|nonnegative|negative|int|email|url|uuid|regex|matches|nonempty|required|oneOf)$")
  arguments: (arguments)) @rule.limit
(lexical_declaration (variable_declarator name: (identifier) @_n (#match? @_n "^_?[A-Z][A-Z0-9_]{2,}$")
  value: [(number) (unary_expression)])) @rule.constant
(pair key: [(property_identifier) (string)] @_k
  (#match? @_k "^\"?(required|maxLength|minLength|min|max|pattern|maxSize|maxFiles|validate)\"?$")) @rule.limit

; data: what is kept
(call_expression function: (member_expression object: (identifier) @_o property: (property_identifier) @_n)
  (#match? @_o "^(z|yup|Joi)$") (#match? @_n "^(object|enum|nativeEnum|union|literal)$")) @data.model
(member_expression object: (identifier) @_o (#match? @_o "^(localStorage|sessionStorage|indexedDB)$")) @data.store
(new_expression constructor: (identifier) @_n (#match? @_n "^(Schema|Model)$")) @data.model

; system: other systems
(call_expression function: (identifier) @_n (#match? @_n "^(fetch|axios|ky|ofetch|\\$fetch|useFetch|useSWR)$")) @system.call
(call_expression
  function: (member_expression object: (identifier) @_o property: (property_identifier) @_n)
  (#match? @_o "^(axios|http|api|client|ky|request|superagent|apiClient|httpClient|\\$http)$")
  (#match? @_n "^(get|post|put|delete|patch|request|head)$")) @system.call
(new_expression constructor: (identifier) @_n (#match? @_n "^(WebSocket|EventSource|XMLHttpRequest)$")) @system.call
(string (string_fragment) @_s (#match? @_s "^(https?|wss?)://")) @system.address
(member_expression object: (member_expression object: (identifier) @_p property: (property_identifier) @_e)
  (#eq? @_p "process") (#eq? @_e "env")) @system.setting

; access: who may do what
(call_expression function: [(identifier) (member_expression)] @_n
  (#match? @_n "(hasRole|hasPermission|hasAuthority|isAdmin|authori[sz]e|requireAuth|isAuthenticated|checkPermission|useAuth|usePermission|canAccess|ensureLoggedIn)$")) @access.check

; failure: what happens when it fails
(throw_statement) @failure.throw
(catch_clause) @failure.catch
(call_expression function: (member_expression property: (property_identifier) @_n) (#eq? @_n "catch")) @failure.catch

; look: how it looks
(string (string_fragment) @_c (#match? @_c "^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?([0-9a-fA-F]{2})?$")) @look.colour

; loose: what looks unfinished
((comment) @loose.todo (#match? @loose.todo "TODO|FIXME|HACK|XXX"))
(call_expression function: (member_expression object: (identifier) @_o property: (property_identifier) @_n)
  (#match? @_o "^(it|test|describe)$") (#match? @_n "^(skip|todo)$")) @loose.skip

; rule: a feature flag read
(call_expression function: [(identifier) @_n (member_expression property: (property_identifier) @_n)]
  (#match? @_n "^(useFlag|useFeatureFlag|useFeature|useFeatureIsOn|isEnabled|isFeatureEnabled|getFlag|variation|boolVariation)$")
  arguments: (arguments . (string))) @rule.flag

; test: what the tests pin down -- read only with --tests, in the files the rest leaves out
(call_expression function: (identifier) @_n (#match? @_n "^(it|test|describe|context|specify)$")
  arguments: (arguments . [(string) (template_string)])) @test.case
(call_expression function: (member_expression object: (identifier) @_o property: (property_identifier) @_n)
  (#match? @_o "^(it|test|describe)$") (#match? @_n "^(only|each|concurrent)$")) @test.case
(call_expression function: (member_expression object: (identifier) @_o property: (property_identifier) @_n)
  (#match? @_o "^(it|test|describe)$") (#match? @_n "^(skip|todo)$")) @test.skip
(call_expression function: (member_expression object: (identifier) @_o property: (property_identifier) @_n)
  (#match? @_o "^(jest|vi|sinon|td|nock|msw|cy)$")
  (#match? @_n "^(mock|fn|spyOn|stub|replace|useFakeTimers|intercept|doMock|unstable_mockModule)$")) @test.mock
(call_expression function: (identifier) @_n (#match? @_n "^(beforeEach|beforeAll|afterEach|afterAll|fixture|setup|setupFiles)$")) @test.fixture
