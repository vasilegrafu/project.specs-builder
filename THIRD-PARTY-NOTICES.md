# Third-party notices

specs-builder-2 is under the licence in [LICENSE](LICENSE). It needs only Python's
standard library. Nothing else is included in this folder.

Two libraries are downloaded by your browser when a page needs them, from
cdn.jsdelivr.net, at the exact version below:

| Library | Version | Licence | Used for |
|---|---|---|---|
| [D3](https://d3js.org) | 7.9.0 | ISC | The Graph page |
| [Mermaid](https://mermaid.js.org) | 11.9.0 | MIT | Flow diagrams |

Without an internet connection, the Graph page says so, and a flow shows its text
instead of its diagram.

The tutorial and the user manual load the Geist, Geist Mono and Crimson Pro fonts
from Google Fonts, and the bakery example's prototype loads Figtree and Fraunces,
all under the SIL Open Font License 1.1. Offline, they fall back to your system's
fonts.

Two extras are optional, and only help the skill read existing material. You
install them yourself, under their own licences: tree-sitter (MIT) and Playwright
for Python (Apache-2.0). See the skill's
[SETUP.md](.claude/skills/specs-builder-2/SETUP.md).

The icons are the project's own. Every product, person, number and address in the
examples is made up.
