# Import and export

- **What it is:** Getting data in from where it lives today and out again for use elsewhere. It covers files, spreadsheets, copying from another product, and reports.
- **Applies when:** Users arrive with data they already have, or need the product's data somewhere else: a spreadsheet, an accountant, an auditor, a successor product. A product whose data starts and ends inside it may skip both.
- **If left unsaid:** New customers face typing in years of records by hand and do not start. Existing customers feel locked in, and the first request for "all our data" arrives as an emergency.
- **Ask:**
  1. Where is this information today -- a spreadsheet, another product, paper, people's heads?
  2. How much of it must be in the product before it is useful? All of it, or only what is current?
  3. Who would do the moving, and how many times: once per customer, or every week?
  4. What do users need to take out, in what form, and who receives it?
  5. If a customer leaves, what do you owe them?
- **Options:**
  - you do it for them -- they send a file and you load it; nothing to build, and you see how messy real data is before designing anything.
  - a spreadsheet upload -- the user maps columns and fixes errors themselves; the usual self-service answer, and the error handling is most of the work.
  - a connection to the other product -- data flows without files; best for the user and a continuing cost to keep working.
  - export to a file -- a CSV or PDF of what is on screen; cheap, and answers most "can I get my data" questions.
- **First release:** Load the first customers' data by hand. Offer a plain export of the main lists, because it is cheap and removes the fear of being locked in. A self-service import waits until manual loading costs more than building it.
- **Often forgotten:** Rows that fail: the whole file refused, or the good rows kept. Duplicates on a second import. Dates, decimals and names in the customer's local form. Undoing an import that went wrong. An export that includes data the person exporting may not see.
- **Becomes:** Requirements for each import and export with the refused-row cases; a decision on who does the first imports; a privacy quality requirement on exports; non-goals for the connections left out.
