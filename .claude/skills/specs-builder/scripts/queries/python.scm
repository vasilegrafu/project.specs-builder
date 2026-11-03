; What scan_code.py finds in Python, by tree-sitter. Each capture is named <lens>.<kind>, as scout.py names the
; lenses; a capture whose name starts with _ only tests the match. The captured node is the fact: its first line is
; what a finding quotes. FastAPI, Flask, Django, Dash and pydantic are what these patterns know.

; action: what a user can do
(decorator
  (call function: (attribute attribute: (identifier) @_n)
    (#match? @_n "^(route|get|post|put|delete|patch|websocket|api_route|callback|command)$"))) @action.route
(decorator
  (call function: (identifier) @_n (#match? @_n "^(callback|route|command|api_view|action)$"))) @action.route
(call function: (identifier) @_n (#match? @_n "^(Input|State)$")
  arguments: (argument_list . (string))) @action.input
(call function: (identifier) @_n (#match? @_n "^(path|re_path|url)$")
  arguments: (argument_list . (string))) @action.route

; shows: what a user reads
(call function: (attribute object: (identifier) @_m)
  (#match? @_m "^(html|dbc|dcc|dmc|ui|st|gr|ft)$")
  arguments: (argument_list . (string) @shows.text))
(keyword_argument name: (identifier) @_k
  (#match? @_k "^(title|label|placeholder|children|header|tooltip|message|headerName|subtitle|description|help_text|help|verbose_name|error_message|error_messages)$")
  value: (string) @shows.label)
(call function: (identifier) @_n (#match? @_n "^(flash|alert|gettext|_)$")
  arguments: (argument_list . (string) @shows.message))
(call function: (attribute object: (identifier) @_o attribute: (identifier) @_n)
  (#match? @_o "^(st|messages|messagebox|toast|ui)$")
  (#match? @_n "^(error|warning|info|success|toast|notify|showerror|showwarning|showinfo|add_message)$")
  arguments: (argument_list . (string) @shows.message))

; rule: rules and limits
(assignment left: (identifier) @_n (#match? @_n "^_?[A-Z][A-Z0-9_]{2,}$")
  right: [(integer) (float) (unary_operator)]) @rule.constant
(call function: (identifier) @_f (#match? @_f "^(Field|constr|conint|confloat|condecimal|conlist|Query|Path|Body|Form)$")
  arguments: (argument_list (keyword_argument name: (identifier) @_k)
    (#match? @_k "^(ge|gt|le|lt|min_length|max_length|pattern|regex|max_digits|decimal_places|multiple_of)$"))) @rule.limit
(call function: (attribute attribute: (identifier) @_f)
  (#match? @_f "Field$")
  arguments: (argument_list (keyword_argument name: (identifier) @_k)
    (#match? @_k "^(max_length|min_length|max_digits|decimal_places|validators|choices|unique|null|blank)$"))) @rule.limit
(call function: (identifier) @_f (#match? @_f "^(MinValueValidator|MaxValueValidator|MinLengthValidator|MaxLengthValidator|RegexValidator)$")) @rule.limit

; data: what is kept, and the states a thing can be in
(class_definition superclasses: (argument_list (_) @_b)
  (#match? @_b "(Enum|IntEnum|StrEnum|Flag|IntFlag|TextChoices|IntegerChoices|Choices)$")) @data.enum
(class_definition superclasses: (argument_list (_) @_b)
  (#match? @_b "(Enum|IntEnum|StrEnum|Flag|IntFlag|TextChoices|IntegerChoices|Choices)$")
  body: (block (expression_statement (assignment left: (identifier)) @data.member)))
(class_definition superclasses: (argument_list (_) @_b)
  (#match? @_b "(BaseModel|Model|Base|Schema|TypedDict|SQLModel|DeclarativeBase)$")) @data.model
(decorated_definition
  (decorator [(identifier) (attribute) (call)] @_d (#match? @_d "dataclass"))
  definition: (class_definition) @data.model)
(call function: (attribute attribute: (identifier) @_n)
  (#match? @_n "^(read_csv|to_csv|read_sql|to_sql|read_json|to_json|read_parquet|to_parquet|read_excel|to_excel|read_pickle|to_pickle)$")) @data.file
(assignment left: (identifier) @_n (#eq? @_n "__tablename__")) @data.table

; system: other systems
(call function: (attribute object: (identifier) @_o attribute: (identifier) @_n)
  (#match? @_o "^(requests|httpx|aiohttp|urllib|session|client|http|smtplib|boto3)$")
  (#match? @_n "^(get|post|put|delete|patch|request|urlopen|stream|send|sendmail|client|resource)$")) @system.call
(string (string_content) @_s (#match? @_s "^(https?|wss?)://")) @system.address
(call function: (attribute object: (attribute object: (identifier) @_o attribute: (identifier) @_e))
  (#eq? @_o "os") (#eq? @_e "environ")) @system.setting
(subscript value: (attribute object: (identifier) @_o attribute: (identifier) @_e)
  (#eq? @_o "os") (#eq? @_e "environ")) @system.setting
(call function: (attribute attribute: (identifier) @_n) (#eq? @_n "getenv")) @system.setting

; access: who may do what
(decorator (identifier) @_n (#match? @_n "(login|permission|role|auth|admin|staff|superuser)")) @access.check
(decorator (call function: [(identifier) (attribute)] @_n)
  (#match? @_n "(login|permission|role|auth|admin|staff|superuser)")) @access.check
(call function: (identifier) @_d (#match? @_d "^(Depends|Security)$")
  arguments: (argument_list (_) @_a)
  (#match? @_a "(role|permission|auth|admin|current_user|scope)")) @access.check

; failure: what happens when it fails
(raise_statement) @failure.raise
(except_clause) @failure.catch

; look: how it looks
(string (string_content) @_c (#match? @_c "^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?([0-9a-fA-F]{2})?$")) @look.colour

; loose: what looks unfinished
((comment) @loose.todo (#match? @loose.todo "TODO|FIXME|HACK|XXX"))
((decorator) @loose.skip (#match? @loose.skip "skip|xfail"))

; rule: a feature flag read -- what is on for whom is a rule of the product
(call function: [(identifier) @_n (attribute attribute: (identifier) @_n)]
  (#match? @_n "^(is_enabled|is_active|feature_enabled|is_feature_enabled|flag_is_active|switch_is_active|get_flag|variation|bool_variation)$")
  arguments: (argument_list . (string))) @rule.flag

; test: what the tests pin down -- read only with --tests, in the files the rest leaves out
(function_definition name: (identifier) @_n (#match? @_n "^test_")) @test.case
(class_definition name: (identifier) @_n (#match? @_n "^Test[A-Z]")) @test.case
((decorator) @test.fixture (#match? @test.fixture "fixture"))
((decorator) @test.skip (#match? @test.skip "skip|xfail"))
(call function: [(identifier) @_n (attribute attribute: (identifier) @_n)]
  (#match? @_n "^(patch|MagicMock|Mock|AsyncMock|create_autospec|monkeypatch|mocker|stub|fake)$")) @test.mock
(call function: (attribute object: (identifier) @_o attribute: (identifier) @_n)
  (#match? @_o "^(mock|mocker|monkeypatch|responses|respx|httpretty|freezegun)$")
  (#match? @_n "^(patch|setattr|add|get|post|freeze_time|object|dict)$")) @test.mock
