; What scan_code.py finds in C#, by tree-sitter. Each capture is named <lens>.<kind>, as scout.py names the lenses;
; a capture whose name starts with _ only tests the match. The captured node is the fact: its first line is what a
; finding quotes. ASP.NET Core -- controllers and minimal APIs -- data annotations and Entity Framework are what
; these patterns know.

; action: what a user can do
(attribute name: (identifier) @_n
  (#match? @_n "^(Http(Get|Post|Put|Delete|Patch|Head|Options)|Route|AcceptVerbs)$")) @action.route
(invocation_expression function: (member_access_expression name: (identifier) @_n)
  (#match? @_n "^Map(Get|Post|Put|Delete|Patch|Methods|Group|Hub|Controller|ControllerRoute|RazorPages|Fallback)$")) @action.route
(method_declaration name: (identifier) @_n
  (#match? @_n "^On(Get|Post|Put|Delete|Patch)(Async)?$")) @action.handler

; shows: what a user reads
(attribute_argument name: (identifier) @_n
  (#match? @_n "^(ErrorMessage|Name|Description|Prompt|DisplayName|ShortName|GroupName)$")) @shows.label
(attribute name: (identifier) @_n (#match? @_n "^(Display|DisplayName|Description)$")) @shows.label
(assignment_expression
  left: (element_access_expression expression: (identifier) @_v)
  (#match? @_v "^(ViewData|ViewBag|TempData)$")
  right: (string_literal)) @shows.text

; rule: rules and limits
(attribute name: (identifier) @_n
  (#match? @_n "^(Required|Range|StringLength|MaxLength|MinLength|Length|RegularExpression|EmailAddress|Phone|Url|Compare|CreditCard|AllowedValues|DeniedValues|Base64String|FileExtensions)$")) @rule.limit
(field_declaration (modifier) @_m (#eq? @_m "const")
  (variable_declaration (variable_declarator [(integer_literal) (real_literal) (prefix_unary_expression)]))) @rule.constant
(invocation_expression function: (member_access_expression name: (identifier) @_n)
  (#match? @_n "^(NotEmpty|NotNull|MaximumLength|MinimumLength|Length|GreaterThan|GreaterThanOrEqualTo|LessThan|LessThanOrEqualTo|InclusiveBetween|ExclusiveBetween|Matches|EmailAddress|Must|HasMaxLength|IsRequired|HasPrecision)$")) @rule.limit

; data: what is kept, and the states a thing can be in
(enum_declaration) @data.enum
(enum_member_declaration) @data.member
(property_declaration type: (generic_name (identifier) @_t) (#eq? @_t "DbSet")) @data.table
(record_declaration) @data.model
(class_declaration (base_list (_) @_b) (#match? @_b "^(DbContext|IdentityDbContext|IEntity|Entity|AggregateRoot)")) @data.model

; system: other systems
(object_creation_expression type: (identifier) @_t
  (#match? @_t "^(HttpClient|SmtpClient|WebClient|ServiceBusClient|BlobServiceClient|SqlConnection|NpgsqlConnection)$")) @system.client
(invocation_expression function: (member_access_expression name: (identifier) @_n)
  (#match? @_n "^(GetAsync|PostAsync|PutAsync|DeleteAsync|PatchAsync|SendAsync|GetFromJsonAsync|PostAsJsonAsync|PutAsJsonAsync|GetStringAsync|GetStreamAsync|AddHttpClient)$")) @system.call
(string_literal (string_literal_content) @_s (#match? @_s "^(https?|wss?)://")) @system.address
(invocation_expression function: (member_access_expression expression: (identifier) @_e name: (identifier) @_n)
  (#eq? @_e "Environment") (#eq? @_n "GetEnvironmentVariable")) @system.setting
(element_access_expression expression: (identifier) @_c (#match? @_c "^(Configuration|configuration|config|_configuration)$")) @system.setting

; access: who may do what
(attribute name: (identifier) @_n (#match? @_n "^(Authorize|AllowAnonymous|RequireHttps|ValidateAntiForgeryToken)$")) @access.check
(invocation_expression function: (member_access_expression name: (identifier) @_n)
  (#match? @_n "^(IsInRole|RequireAuthorization|RequireRole|RequireClaim|HasClaim|AuthorizeAsync|AllowAnonymous|AddPolicy)$")) @access.check

; failure: what happens when it fails
(throw_statement) @failure.throw
(throw_expression) @failure.throw
(catch_clause) @failure.catch
(invocation_expression function: (identifier) @_n
  (#match? @_n "^(Problem|BadRequest|NotFound|Conflict|Unauthorized|Forbid|UnprocessableEntity|ValidationProblem|StatusCode)$")) @failure.refuse
(invocation_expression function: (member_access_expression expression: (identifier) @_r name: (identifier) @_n)
  (#match? @_r "^(Results|TypedResults)$")
  (#match? @_n "^(Problem|BadRequest|NotFound|Conflict|Unauthorized|Forbid|UnprocessableEntity|ValidationProblem|StatusCode)$")) @failure.refuse
(invocation_expression function: (member_access_expression name: (identifier) @_n) (#eq? @_n "AddModelError")) @failure.message

; look: how it looks
(string_literal (string_literal_content) @_c (#match? @_c "^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?([0-9a-fA-F]{2})?$")) @look.colour

; loose: what looks unfinished
((comment) @loose.todo (#match? @loose.todo "TODO|FIXME|HACK|XXX"))
(attribute name: (identifier) @_n (#match? @_n "^(Ignore|Skip|Obsolete)$")) @loose.skip
(attribute_argument name: (identifier) @_n (#eq? @_n "Skip")) @loose.skip

; rule: a feature flag read, or an action behind one
(attribute name: (identifier) @_n (#match? @_n "^FeatureGate$")) @rule.flag
(invocation_expression function: (member_access_expression name: (identifier) @_n)
  (#match? @_n "^(IsEnabledAsync|IsEnabled|IsFeatureEnabled)$")) @rule.flag

; test: what the tests pin down -- read only with --tests, in the files the rest leaves out
(attribute name: (identifier) @_n (#match? @_n "^(Fact|Theory|Test|TestCase|TestMethod|DataTestMethod|InlineData|TestCaseSource)$")) @test.case
(attribute name: (identifier) @_n (#match? @_n "^(Ignore|Skip|Explicit)$")) @test.skip
(attribute_argument name: (identifier) @_n (#eq? @_n "Skip")) @test.skip
(object_creation_expression type: (generic_name (identifier) @_n (#match? @_n "^(Mock|Fake|Stub)$"))) @test.mock
(invocation_expression function: (member_access_expression expression: (identifier) @_o name: (identifier) @_n)
  (#match? @_o "^(Substitute|A|Mock|NSubstitute)$") (#match? @_n "^(For|Fake|Of|Setup)$")) @test.mock
(attribute name: (identifier) @_n (#match? @_n "^(SetUp|TearDown|OneTimeSetUp|TestInitialize|ClassInitialize|AssemblyInitialize)$")) @test.fixture
(base_list (generic_name (identifier) @_n (#match? @_n "^(IClassFixture|ICollectionFixture|IAsyncLifetime)$"))) @test.fixture
