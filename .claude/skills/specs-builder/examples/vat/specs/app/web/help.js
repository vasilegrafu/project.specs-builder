// The application's own help: what each part of the menu holds -- its kinds as the grammar says them, so it is
// never behind -- how to find things, what is open, changing it, the prototype, the appearance, handing it on, and
// the keys. Loaded before engine.js, with menu.js, whose parts and icons it shows.
"use strict";

function helpView() {
  const count = kindCount();
  const is = Object.fromEntries(state.summary.kinds.map((k) => [k.kind, k.is]));
  const section = (id, title, ...body) => h("section", { class: "help-section", id: `help-${id}` }, h("h2", {}, title), body);
  const kinds = (list) => h("dl", { class: "help-kinds" }, list.map((kind) => [
    h("dt", {}, h("span", { class: `kind-label kind-${kind}` }, PLURAL[kind] || kind),
      count[kind] ? h("span", { class: "help-count" }, count[kind]) : null),
    h("dd", {}, is[kind] || "")]));
  const parts = [
    ["Document", ["document"], "The whole document opens from here, and so do what is open and the overview."],
    ...GROUPS.map(([group, list]) => [group, list,
      group === "UX" ? "The design system, and every screen drawn small, open from its menu too." : group === "Evidence"
        ? "The files read -- captures, the agents' reports, the analyses -- open from its menu." : ""]),
    ["Prototype", ["screen"], "No menu: the prototype itself, each screen running full size."],
  ];
  const keys = [["Ctrl K, or /", "Search"], ["↓ on a part or its arrow", "Open its menu, and go into it"],
                ["← →", "From part to part"], ["↑ ↓", "Through a menu, or what a search found"],
                ["Enter", "Open what is chosen"], ["Esc", "Close the menu, the search, the drawer, the tree, a card, the preview or the inspector"],
                ["↑ ↓ in the prototype", "Out to the element around the one inspected, and in to the first inside it"]];
  return [
    h("h1", {}, "Help"),
    h("p", { class: "lead" }, "This specification is kept as data, and this application reads it: every link is " +
      "written once and read from both ends, every change is checked before it is made, and nothing here is a " +
      "page written by hand."),
    h("nav", { class: "help-toc", "aria-label": "Help" }, [["menu", "The menu"], ["find", "Finding things"],
      ["open", "What is open"], ["change", "Changing it"], ["prototype", "The prototype"], ["look", "The appearance"],
      ["hand", "Handing it on"], ["keys", "Keys"]].map(([id, text]) =>
      h("a", { href: `#/help`, onclick: (e) => { e.preventDefault(); document.getElementById(`help-${id}`).scrollIntoView({ behavior: "smooth" }); } }, text))),
    section("menu", "The menu",
      h("p", {}, "Each part in the row under the name opens a menu of the kinds it holds, each with how many there " +
        "are; one opens the whole list. The Prototype opens the prototype straight away, the Matrix every node and " +
        "link to walk through, and the Graph the whole specification as one picture."),
      h("div", { class: "help-parts" }, parts.map(([key, list, note]) => h("div", { class: "panel help-part" },
        h("div", { class: "help-part-head" }, h("span", { class: "help-mark" }, icon(PARTS[key].icon)),
          h("div", {}, h("strong", {}, key), h("div", { class: "help-lead" }, PARTS[key].lead))),
        kinds(list), note ? h("p", { class: "meta-note" }, note) : null)))),
    section("find", "Finding things", h("ul", {},
      h("li", {}, "Search finds an ID, the words of a name, and words anywhere in what a node says -- its rows too. " +
        "Every word must be found; an ID typed whole comes first."),
      h("li", {}, "Every ID is a link. A pause on it says what kind of thing it is. A right click on it, or a finger held on it, opens a card of what it is -- its kind, its name, a sentence or " +
        "two and the facts that place it, and whether anything about it is unsettled or stale. A right click on an ID inside a card opens another " +
        "beside it, so you can walk from node to node from any page; the card also lists the node's links by kind. The pin keeps " +
        "a card open from page to page, and any card moves by its top. × closes a card, Escape the newest, and a click on the page all but the pinned. The icons " +
        "at its foot open the node here, preview it over the page, or take it to Around, Layers, Impact or the Matrix; those with a small " +
        "arrow, in the row below, do the same in another tab."),
      h("li", {}, "A part's pages have its tree down the left: the part's name, which opens a page of everything " +
        "in it, then each kind with its letters and count, unfolding to its nodes, and the part's own pages. What is " +
        "open is marked. The part's name in the bar opens that page too. An " +
        "entry too long is cut after eight words, and a pause over it shows it whole. Drag the tree's " +
        "edge to widen it -- each part's tree keeps its width, a double click puts it back -- and « folds it to a " +
        "rail. On a narrow screen the tree is a button above the page."),
      h("li", {}, "A node's page shows its links both ways: what it stands on, and what stands on it."),
      h("li", {}, "A foundation's page draws what each row of its tables looks like, where its values say: a colour's " +
        "swatch and contrast, a text style's sample, the spacing scale, corners, borders, shadows and the focus ring. A row " +
        "names a token, --color-brand, and the value is shown beside it: every value lives in tokens.json alone, and the " +
        "Design system page says which foundations name each token and which prototypes it reaches. A screen or a component " +
        "follows the foundations it is drawn by, so a foundation changed makes them stale, and a value changed lists the " +
        "prototypes to look at, with what moved."),
      h("li", {}, "The prototype's last button folds the bars away -- the application's and its own -- so the " +
        "screen takes nearly the whole height; the button at the right of the strip left at the top shows them again. It stays folded until " +
        "you unfold it."),
      h("li", {}, "A flow's page begins with its story -- as its user, I want to do what it is named, so that the " +
        "goals it serves -- and a table of every requirement its steps name, with its priority, how well it is backed " +
        "and its criteria: what a team plans from."),
      h("li", {}, "A flow's page draws its diagram above its steps: the one written in its Diagram section, in Mermaid, " +
        "or, where it has none, one made from its steps. A box named by an ID opens it. Mermaid is fetched from the " +
        "internet; without a connection the diagram's text is shown."),
      h("li", {}, "A node's graph draws it with everything one link away, or two."),
      h("li", {}, "The Matrix opens on a grid: a row and a column for each kind, each number the links from the one to the " +
        "other, and a dot where there are none. Choose a number to list those links. Beside it the tree holds every node. " +
        "Its arrows fold, and its names show: a part its kinds, a kind what it is, how it is linked and its nodes, and a node " +
        "its links both ways, by sort. Choose a link to see both ends, how it reads from each, what goes " +
        "stale if one changes, whether it is stale now, and where it is written. The arrow on a link, or Go to, takes you " +
        "to the far end, and the trail under the page keeps the way you came. The list under Find narrows the tree to what is " +
        "stale, unlinked or has an open question. Above a node's links, Filter narrows them and By kind groups them. An amber " +
        "number in the grid holds stale links, and the path icon gives the shortest chain between two nodes. It fetches only what you look at, so it stays " +
        "quick however large the specification is, and it needs no connection."),
      h("li", {}, "The Graph has two scopes, all of the specification and one selected node, and fetches only what each shows. A node " +
        "stays selected from one picture to the next, until its x. Around puts it in the middle with what it is " +
        "linked to around it, and nothing else: a click spreads a node's links, a double click puts it in the middle, and a node " +
        "dragged stays. Impact shows what stands on a node, a step at a time. Layers lays the specification out left to right in " +
        "the order of the top menu, in bands sized by the links between kinds, which are all there at any " +
        "size. Click a kind or a band for its nodes, and scroll over them for more; Hide folds a column; and a click on a node " +
        "selects it, to show only what connects to it, one step out, two, or all the way. There the links the trace followed are " +
        "drawn, that node's own the strongest, and a pause on a node shows the rest of its links."),
      h("li", {}, "The Graph's map shows the whole specification. Each kind starts folded, a bubble with its count, and a line " +
        "between two kinds says how many links join them. Click a bubble to open it to a box of its nodes, and the box's " +
        "title to fold it. A right click on a node shows its card, a click puts it in focus, and what you point at lights what it is " +
        "linked to. A big kind opens to its most linked nodes, and its last tile shows more. A criterion or an element counts " +
        "as the node that holds it. Drag a kind to move it, scroll to zoom, Fit to see it all, and Find a node to focus on " +
        "one. D3 is fetched from the internet; without a connection the page says so."),
      h("li", {}, "The overview, under the name, shows every part at a glance."))),
    section("open", "What is open", h("ul", {},
      h("li", {}, "Open questions, additions not yet confirmed, qualities and risks left open, contradictions not " +
        "settled: the Document's menu says how many, and What is open lists them, the most deciding first."),
      h("li", {}, "A node is stale when something it stands on changed after it was last read: it is read again " +
        "against the change, and confirmed."),
      h("li", {}, "Where the content falls short, it says so: a claim with nothing under it, a state nobody accounted for, a prototype " +
        "that draws what the data does not hold. Any of it can stand while the work goes on. The gaps a review reads are listed there too, " +
        "and hold nothing up."),
      h("li", {}, "A specification is agreed only when nothing stands in the way, and only by the person it is for. Agreeing keeps it " +
        "as it stands, and spec.py changes says what moved since."),
      h("li", {}, "A page with several headings has an outline, On this page: beside it on a wide window, above it on " +
        "a narrow one. A node's page has small links to the node before and after it, in the order of the tree, at its " +
        "top and at its foot; a pause over one says which node it leads to."),
      h("li", {}, "The printer in the bar opens the page alone on a sheet of A4, in a new tab, as it will come out; " +
        "Print there sends it to paper or a PDF. A screen fills the width of the sheet and runs on to the next where it " +
        "is long; on the prototype it is the screen alone, in the state you are looking at. " +
        "The export gives the whole specification."),
      h("li", {}, "What is built is read from the code the specification is built from: a test counts by naming the " +
        "criterion it proves, R4.2 or R4_2, and spec.py snapshot --target <code> says where the code is. It tells what " +
        "the code names, not that a test passes."),
      h("li", {}, "How well a requirement or a rule stands is worked out from the findings behind it, never typed. The " +
        "first that holds: disputed, those findings disagree and it is not settled; corroborated, quoted from two " +
        "sources or more, one of them the product itself; seen, in the product itself, at rest or running; documented, " +
        "only documents say so, and it is listed under What is open to be checked against the product; inferred, " +
        "concluded from the material, never seen as such; added, the skill's own judgement, not confirmed; stated, " +
        "the user said so."))),
    section("change", "Changing it", h("ul", {},
      h("li", {}, "This application reads. A specification is changed in Claude Code, which makes the change, goes through " +
        "all that stands on it, the nodes and the screens, and shows you what it would adjust before it does."),
      h("li", {}, "Request a change, on a node's page or on its card, asks for one from here. It waits under What is open, " +
        "in the inbox, beside the data and never in it, until Claude Code takes it up. Your name is asked once."),
      h("li", {}, "Whoever builds from the specification asks back with spec.py ask, and the question waits in the same " +
        "place. While anything waits, the specification is not ready to be agreed."),
      h("li", {}, "An agreed specification takes no change until it is set back to draft."))),
    section("prototype", "The prototype", h("ul", {},
      h("li", {}, "The Prototype runs each screen full size, on its sample data. Its toolbar picks the screen, what it " +
        "shows -- a state, or a variant -- its width, and the view: the look, or the wireframe with every element " +
        "marked. In the look, the element under the pointer is marked, unless Marks is off."),
      h("li", {}, "A link in the prototype leads to the screen it names, and the toolbar follows."),
      h("li", {}, "A mark, clicked, opens the inspector: the element's row and what it stands on, each a link, and its " +
        "box and its text as drawn, beside the token that says each value. Resting on an ID there lights what it " +
        "names on the screen."),
      h("li", {}, "Every screen drawn small, flow by flow, is in the UX menu."))),
    section("look", "The appearance", h("p", {}, "The switch beside Help sets the appearance: as the system " +
      "prefers, light or dark. It is kept in this browser; the prototypes keep the product's own look.")),
    section("hand", "Handing it on", h("p", {}, "For someone without Python, the Export button in the bar, or ", h("code", {}, "python app/spec.py export"),
      " writes the whole specification as one HTML file, ", h("code", {}, "export/<name>.html"),
      ", that needs nothing beside it: every node, every ID a link within it with its card on a right click, and each " +
      "prototype drawn. Each flow's diagram is drawn when it is opened with a connection; without one, its text shows.")),
    section("keys", "Keys", h("div", { class: "table-frame" }, h("table", { class: "help-keys" },
      h("tbody", {}, keys.map(([key, does]) => h("tr", {}, h("td", {}, h("kbd", {}, key)), h("td", {}, does))))))),
  ];
}
