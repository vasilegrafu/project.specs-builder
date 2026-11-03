# Search and lists

- **What it is:** How people find one thing among many. It covers lists, their order, filtering, searching, and what happens when there are thousands.
- **Applies when:** A user will have more of something than fits on a screen: customers, orders, documents, messages. It does not apply while every user has a handful.
- **If left unsaid:** A list in the order things were created, with no way to find the one from last March. It works in the demonstration and fails in the third month of real use.
- **Ask:**
  1. How many of each thing will one user have after a year? The largest customer?
  2. When they look for one, what do they know about it: its name, a date, who it belongs to, a number?
  3. What do they most often want at the top of the list?
  4. Do they look for one thing, or for all the things that share something -- everything overdue, everything for one customer?
  5. Do they need the same view again tomorrow?
- **Options:**
  - a sorted list -- one sensible order and nothing else; enough for dozens.
  - sort and a few fixed filters -- the two or three questions users really ask, each one click; covers most needs up to thousands.
  - search by text -- type part of a name or number; expected by everyone, and needs deciding which fields it looks in.
  - saved views and combined filters -- users build and keep their own queries; for people who live in the list all day.
- **First release:** The order users want most, and search over the one or two fields they know things by. Add a filter only for a question named in a journey. Saved views wait.
- **Often forgotten:** The message when nothing matches. Whether search finds archived or deleted things. Typing mistakes and accents in names. How the list behaves at its largest size, which is a capacity question to answer with a number. Whether the list a user sees includes things they may not open.
- **Becomes:** Requirements for the order, each filter and search, with criteria using real values; a capacity quality requirement with the largest count; a row of the Interface with its empty state; a non-goal for saved views.
