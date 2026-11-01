# Concepts, for an engineer

The terms a requirements document is written in, each with what it is,
what it is like in engineering, and the mistake a first-time product
owner makes with it. Explain one the first time it comes up in a question,
or when the user asks why, in three sentences at most. This file is the
source, not a script to read out.

| Concept | What it is | In engineering terms | The usual mistake |
|---|---|---|---|
| **problem** | what is wrong today for a particular person, before any product exists | the bug report, not the patch | describing the product instead: "there is no app for X" is not a problem |
| **assumption** | a claim the plan depends on that nobody has checked | an unverified precondition | leaving it unwritten, so nobody notices when it turns out false |
| **open question** | something nobody has answered yet, with who must answer | a blocking TODO with an owner | answering it with a plausible guess to make the document look finished |
| **decision** | a choice someone with the authority made, with what they chose against | an architecture decision record | recording what was chosen and not what lost, so it is argued again later |
| **goal** | a change in the world that can be measured | the acceptance test for the whole product, run in production | writing an output ("ship the export") instead of an outcome ("fewer support tickets") |
| **guard-rail goal** | something that must not get worse while the goal improves | a regression test | meeting the target while breaking what nobody was watching |
| **non-goal** | something a reader would expect to be included that is deliberately not | an explicit out-of-scope in an interface contract | saying nothing, which readers take as included |
| **user** | a role, defined by what the person is trying to get done | a client of an interface, defined by how it calls it | inventing a person with a name and hobbies instead of observing a real one |
| **journey** | one piece of work, step by step, from what starts it to what counts as done | a sequence diagram with the human as an actor | drawing only the happy path, or the product's screens instead of the user's work |
| **requirement** | one behaviour of the product that someone outside it can observe | a specification of behaviour at the interface, not of the implementation | describing how it works inside, or packing three behaviours into one sentence |
| **acceptance criterion** | a concrete case that shows a requirement is met | a test case with given, when and then | describing the kind of case ("a large file") instead of the case ("a 200-line invoice") |
| **quality requirement** | how well the product must do what it does: speed, capacity, security and the rest | a non-functional requirement, a service level | an adjective without a number: "fast", "secure", "scalable" |
| **constraint** | something fixed from outside that the product must fit within | a platform limit, a pinned dependency | passing off a preference as a constraint |
| **priority** | which requirements the release cannot ship without | a blocker versus a nice-to-have | marking everything `must`, which ranks nothing |
| **first release** | the thinnest version that crosses the whole main journey; often called an MVP | the smallest end-to-end path that runs; a walking skeleton | making it the smallest set of features one is not ashamed of, instead of the smallest that tests the least certain assumption |
| **the four risks** | value, usability, feasibility, viability: the four ways a product fails | failure modes to design against | checking feasibility thoroughly and the other three not at all |
