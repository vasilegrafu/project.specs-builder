# What to ask about

The aspects of a product that a requirements document must settle, in the
order to ask them. In ask-write, take the first unanswered ones each
round, and treat the list as the floor: [asking.md](asking.md) says how to
go beyond it. In write-ask, use the list to find what the user's words
left out: complete what can be completed, and ask about the rest.

Ask only what applies. Everything here is general practice, never a fact
about the user's product.

## How deep to go

Ask-write offers three depths at the start, and the user picks one.

| Depth | Covers | About |
|---|---|---|
| short | part 1 | ten questions |
| standard | parts 1 and 2, and one question for each area of part 3 that applies | twenty to thirty |
| full | all of standard; each area that applies gone through from its own entry; parts 4 and 5 | as many as the product needs |

For a change to a product that already exists, only the areas the change
touches apply.

## 1. What every product must settle

| Aspect | The question | Why it matters | It becomes |
|---|---|---|---|
| the problem | What goes wrong today, and for whom? When did it last happen? | without it the team builds a copy of what already exists | Problem |
| how it is known | How do you know: something counted, someone who said it, your own experience? | it tells the reader how far to trust the problem | Problem; an assumption where nothing shows it |
| what they do today | What do they use now, and where exactly does it fail them? | that tool is the real competitor; the gap is the product | Users; Journey; Problem |
| who it is for | Whose hands is it in first? Who is it not for? | "everyone" produces several half-products | Users; a non-goal |
| the cost | What does the problem cost them, and how often? | the cost becomes the goal's baseline | Goals |
| why now | What changed, or will, that makes this worth doing now? | it shows what the first release must address, and how much effort it deserves | Problem |
| if nothing is built | What happens, to whom, by when? | "nothing much" is an answer that bears on whether to build | Problem |
| the main outcome | Of everything it could do, which outcome comes first and best? | it decides what the first release contains | Summary; Goals; Decisions |
| success | What will you count to know it worked, what value, by when? | a goal with no number cannot be tested | Goals |
| what must not get worse | While that improves, what has to stay as good as it is? | a product can meet its goal and do damage elsewhere | a guard-rail goal |
| the limit | How much time or money may the first release cost? | without a limit scope grows one cheap feature at a time | Constraints; Decisions |
| what is out | What will people expect that you do not want built now? | silence is read as inclusion | Non-goals |
| what could go wrong | What could make this fail or cost more than planned, and what would you do about it? | a danger everyone knows and nobody wrote down arrives as a surprise | Risks |
| who could stop it | Who, if they said no, would stop this? Have they been asked? | an unasked veto arrives after the work is done | an open question for that person |

## 2. Walking the main journey

Take the user's main piece of work one step at a time.

| Aspect | The question | It becomes |
|---|---|---|
| the step | At this step, what must the product do, and what does the user see afterwards? | a requirement and its ordinary criterion |
| a real case | Give me a real case, with the actual values. | a criterion with real values |
| the boundaries | What is the smallest, the largest, the first, the last, none at all? | boundary criteria |
| when it cannot be done | What does the user see when it is refused, missing, too late or half done? In what words? | a criterion, or an `If ..., then` requirement; the failing state of its screen |
| who may not | Who may do this, and what does someone who may not see? | a requirement; the security row |
| the terms | Does a word here mean exactly one thing? Measured how, from what? | a definition in the requirement; a Glossary line; a decision |
| the goal | Which goal is this for? | `Serves:`; if none, it is not a requirement |
| the priority | Would you release without this? | must, should, could or wont |
| where they are | Which screen, page or message is the user at, and what would they call it? | a screen in the UX pages, or a row of the Interface |
| another way through | Does anyone do the same work differently: another role, another site, a newcomer? | a second user or journey; a non-goal |

## 3. Product areas

Each is something most products need decided and first-time product
owners leave unsaid. The usual first answer is where most products start;
it is a recommendation to offer, not a default to write. Each area's own
entry holds its full list of questions, the options with what each costs,
and what is often forgotten: open it when the area applies and one
question is not enough.

| Area | Applies when | The question | Usual options, smallest first | Usual first answer |
|---|---|---|---|---|
| [sign-in](areas/accounts-and-sign-in.md) | data is kept per person, or must be hidden from others | How does a person prove who they are? | private access only; an account they already have; a magic link; a password; company single sign-on | one method, chosen by who the first users are |
| [roles](areas/roles-and-permissions.md) | more than one kind of person uses it | Who may do what, and who may not? | one role; a few fixed roles; roles the customer defines | one role, or two if one action is truly restricted |
| [teams](areas/organisations-and-teams.md) | the customer is a group, not a person | Does the data belong to a person or to the organisation? | personal accounts; one organisation per person; several | decide who owns the data now, even with one member |
| [onboarding](areas/onboarding.md) | a new user must do something before it is useful | What is the first useful moment, and what must happen before it? | done by hand for them; good empty screens; guided setup; sample data | by hand for the first users, and one sentence on each empty screen |
| [billing](areas/billing-and-pricing.md) | someone pays | Who pays, for what, and how is it collected? | free for now; invoice by hand; a payment provider's checkout; billing of its own | whichever is least work for the first customers; decide the price anyway |
| [notifications](areas/notifications.md) | something happens while the user is away | What must they be told when not looking, and how soon? | shown on the next visit; email; text message; push | the next visit, or email for the few things that cannot wait |
| [lists and search](areas/search-and-lists.md) | a user has more of something than fits a screen | How do they find one among many, and what comes first? | one sensible order; sort and a few filters; text search; saved views | the order they want most, and search on the field they know it by |
| [data in and out](areas/import-and-export.md) | users arrive with data, or need it elsewhere | Where is the data today, and where must it go? | loaded by hand for them; a file upload; a connection; a plain export | by hand in, a plain export out |
| [other systems](areas/integrations-and-api.md) | the work begins or ends in another product | Which system must it work with, in which direction, how fresh? | files; a connector service; one built connection; its own interface | at most one connection, the one the first users need |
| [back office](areas/admin-and-back-office.md) | anyone outside the team uses it | What will your own people need to see or fix for a user? | an engineer and the database; a general admin tool; staff screens | name the three things support will be asked, and who does each |
| [settings](areas/settings-and-profile.md) | a person's details can change, or users differ in what they want | What can a user change about themselves and about how it behaves? | nothing; a profile; preferences for real differences; settings for behaviour | a profile, and a decision in place of each proposed setting |
| [history and undo](areas/history-and-undo.md) | users change or delete things that matter | What can be destroyed with one click, and can it be put back? | confirm first; a bin with a time limit; an activity log; versions | a bin for what would be mourned |
| [files](areas/files-and-media.md) | users upload or download files | What is uploaded, how large, who may open it? | a link instead; attachments as they are; previews; reading inside | attachments unchanged, with a size limit and allowed types |
| [devices](areas/devices-and-offline.md) | always | Where is the user, and what is in their hands? | web for a large screen; web that adapts; an installed app; working offline | the web, laid out for the device the main journey happens on |
| [measuring](areas/measurement.md) | the document has goals | Where will each goal's number come from once it is live? | counted by hand; the few events behind the goals recorded; an analytics tool | by hand, or record those few events from day one |
| [privacy and law](areas/privacy-and-legal.md) | anything about a person is held, money is taken, or the field is regulated | What is held about people, why, and who qualified has looked at it? | hold less; standard terms; rights handled by hand; formal compliance | hold only what is needed; a qualified person for anything regulated |
| [help](areas/support-and-help.md) | anyone outside the team uses it | What does a stuck user do? | an email address; a sentence where they get stuck; a help centre; chat | one way to reach a person |
| [leaving](areas/leaving.md) | people have accounts or pay | How does use end, and what happens to the data? | by request; a cancel control; a grace period; immediate deletion | a way to cancel without a conversation, and a stated deletion date |
| [finding users](areas/acquisition.md) | the product must find its own users | How will the first ten hear of it? | approached one at a time; a page that collects interest; open sign-up | name the first ten and approach them |
| [release](areas/rollout.md) | it changes something in use, or opens to many at once | Who gets it first, and what if it goes wrong? | everyone at once; a named first group; gradual widening | a named first group |

The catalogue covers what most products with users need. It does not know
the user's field: ask what a product in this field has that the list does
not, and treat the answer as an area of its own.

## 4. What an engineer will ask

Read each requirement of the first release as the engineer who builds it
tomorrow and has never met the product side. A question the document
answers is not a gap. One it does not is resolved in one of three ways,
and never by inventing the answer:

- **written**: the answer follows from something already in the document,
  so write it where it belongs;
- **asked**: only the user or someone they name knows, so it becomes an
  open question;
- **engineering's**: it is a choice of how, so it becomes an open question
  for engineering, or is left to them.

| About | The question | It becomes |
|---|---|---|
| data | What is created, changed or removed, and by whom? What makes two of them the same one? What are the limits? What happens to it when its owner leaves? How long is it kept? | a requirement or criterion; the capacity and privacy rows; a constraint |
| rules | For every number: its unit, its rounding, its smallest and largest value? For every "each" or list: none, one, very many? For every date: whose time zone, and what happens at midnight and month end? | a criterion with real values |
| unwanted cases | What does the user see when it cannot be done: the input refused, another system down, too slow, half finished? Can they try again, and is trying twice safe? | an `If ..., then` requirement or a criterion; the failing state of its screen |
| people | Who may do this and who may not? What does someone who may not see instead? Does anyone else see the result, and are they told? | a requirement; the security row |
| two at once | What if two people do it to the same thing at the same moment? What if one person does it twice: a double click, a retry, two devices? | a criterion |
| states | What states can the thing be in, and which moves between them are allowed? Which is it in at the start? Can a move be undone, and until when? | a requirement per move that matters; the Glossary for the state names |
| volume and time | How many, how often, at the peak? How long may it take? Must it work while the product is being updated? | the speed, capacity and availability rows |
| neighbours | Which other systems does it read from or write to? Who owns each, and has anyone asked them? What does this product do when the neighbour answers late, wrongly or not at all? | a constraint; an open question for the owner or for engineering |
| what exists | What does the product do in this place today, and what happens to that? What happens to data and users that exist on release day? Is it released to everyone at once? | a requirement; a non-goal; a decision; the Release plan |
| words | Is every term used the same way everywhere? Would an outsider read a word differently? Is every text the user reads written out? | the Glossary; the screens' notes and states, or the Interface |
| afterwards | How will anyone know it works in use: what is counted for each goal, and where does the count come from? Who is told when it fails? What must support be able to see or do? | the proof row; a requirement; an open question for engineering |
| done | Could each requirement of the first release be shown to a user on its own? Is every criterion something a tester could check without asking? | the Release plan; the criterion's wording |

## 5. Qualities

Every quality has a row in the document. Ask each, and write the
requirement, `none:` with the user's reason in their words, or leave it
`open`.

| Quality | The question |
|---|---|
| speed | How long may the user wait at the slowest step, under what load? |
| capacity | How many users, records and requests, now and in a year? |
| availability | When must it work, and what happens if it is down for an hour? A day? |
| security | What here would be damaging in the wrong hands? |
| privacy | What does it hold about a person, on what ground, for how long? |
| accessibility | Who must be able to use it, and is a standard promised or required? |
| devices | On what must it run, and alongside what? |
| languages | Which languages, time zones, currencies and formats? |
| proof | What must you be able to show afterwards, to whom, for how long? |

## 6. How it is used and how it looks

Asked only when the screens, flows and design are being written, after the requirements
they draw on. [ux.md](ux.md) says how each answer is written down.

| About | The question | It becomes |
|---|---|---|
| the pieces of work | What does the user come to do, from what starts it to what counts as done? | one flow each |
| the order | What comes first, what can be skipped, where can they turn back? | the diagram's branches; the steps |
| who else | Does anyone or anything else take part: another person, another system, a message that arrives later? | a sequence diagram; a step outside the product |
| the screens | Which screens are there, and what would the users call each? Which is the one they live on? | one screen each |
| what is on it | On this screen, what must be seen at once, what can be one action away, and what stays in view while the rest moves? | the wireframe's regions and their order |
| the layout | Of these two or three layouts, which fits how you work? | a text sketch per option to choose between; the wireframe; a decision |
| the element | What does this show, in what words, and what happens when it is used? | a numbered element and its row |
| nothing yet | What does a user see here on the first day, or when a search finds nothing? | the empty state |
| waiting | What is shown while it loads, and is what was there before kept in view? | the loading state |
| failing | What does it say when it fails or refuses, and what can the user do next? | the failing state |
| the look | Is there a designer, a design system, a component library, or a product whose look this must follow? | the foundations, or three lines and a pointer |
| the components | Which building blocks come back on several screens? For each: which states can it be in, and how does each look? | one component each; the elements that use it name it |
| the patterns | How is a failure worded, and where does it show? What does a screen with nothing yet look like? How are money, numbers and dates written? | the patterns among the foundations |
| what colour means | Which colours carry meaning, and what does each mean? Is anything shown by colour alone? | the colours table; the accessibility row |
| density | How much must fit on the screen at once, on what size of display? | the density rules; the devices row |
