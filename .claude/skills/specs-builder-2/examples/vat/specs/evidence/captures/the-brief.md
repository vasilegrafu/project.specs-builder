# The finance lead's brief, 2026-10-11

- **Given:** 2026-10-11, by Ines, who leads the finance team at Voltline, pasted into the conversation
- **Redacted:** nothing: the brief names no customer

vatkit puts the VAT on every invoice we issue, the shop's and the back office's. Its maintainer moves to another team at the end of the year, and whoever keeps it next must keep what it promises. Please write down what it does and what it promises, function by function and command by command.

What went wrong before: in the tax office's audit of 2024, 37 of the 4,100 invoices sampled had a VAT a few cents off the office's own figure, and each was corrected with a credit note. Version 2.0 put that right, and the audit of 2025 found none of the 3,900 sampled. It must stay none.

What still goes wrong: a change of a rate reaches our invoices late. Finland's rate changed on 1 January 2026; vatkit carried it from 12 January, so eleven days of invoices to Finland went out at the old rate, 214 of them, each corrected by hand. We heard of the change from a customer. We want every change of a rate on our invoices from the day it is in force.

Who uses it: the shop's invoicing and the back office's programs call it; the three of us in the back office use its command line to check a figure or a customer's VAT number by hand, a few times a day; and the maintainer follows each change of a rate and releases it.

What worries me: that the next maintainer misses a change of a rate, as we nearly did. From November the maintainer and I both take the Commission's notices of rate changes, so that two people hear of each.

Not now: checking with VIES that a VAT number is registered; countries outside the EU; and the rate that held on a date in the past, which we asked for to correct old invoices. Those credit notes stay written by hand for now.
