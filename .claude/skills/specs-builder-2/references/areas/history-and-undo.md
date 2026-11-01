# History and undo

- **What it is:** What the product remembers about what happened, and whether a mistake can be taken back. It covers activity logs, earlier versions, deletion and recovery.
- **Applies when:** Users change or delete things that matter, more than one person changes the same things, or someone may later need to show what was done. A product whose data is disposable can skip it.
- **If left unsaid:** Deleting is immediate and final, and "who changed this?" has no answer. The first accidental deletion by a customer becomes a restore from backup by an engineer.
- **Ask:**
  1. What can a user destroy with one click, and how bad is it?
  2. When two people work on the same thing, will one need to know what the other did?
  3. Will anyone outside ask you to prove what happened -- an auditor, a customer in a dispute, a regulator?
  4. How far back does that need to go?
  5. Is being able to see what happened enough, or must it be possible to put it back?
- **Options:**
  - confirm before destroying -- a question before anything irreversible; cheapest, and users click through it without reading.
  - delete into a bin -- deleted things can be restored for a set time; solves most accidents and adds little.
  - an activity log -- who did what and when, shown to users; answers disputes, restores nothing.
  - full version history -- every earlier state can be seen and restored; expected for documents, heavy for everything else.
- **First release:** A bin with a time limit for anything a user would mourn, and a plain record of who created and last changed each thing. A log users can read, and version history, wait for a named need.
- **Often forgotten:** Restoring something whose parent is gone, or whose name is now taken. Whether a deleted thing still counts toward limits and totals. Deletion that the law requires to be real, which contradicts the bin. How long history is kept, which is a privacy question as much as a storage one. What undo means once a message has been sent to someone.
- **Becomes:** Requirements for deleting and restoring with their criteria; a proof quality requirement with how long records are kept; a privacy constraint on retention; non-goals for versioning.
