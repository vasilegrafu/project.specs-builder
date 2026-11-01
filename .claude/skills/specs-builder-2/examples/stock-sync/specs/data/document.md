---
name: Stock sync
kind: process, library
status: agreed
---

The stock sync is Voltline's nightly job that takes the supplier's stock feed, refuses a feed that cannot be right, brings the shop's stock in line with it, and tells the operator on call in the morning what changed and what is running low.
No user drives it: a timer starts it at 02:30, and the operator runs it by hand from the runbook when a night went wrong.
This specification says what it does today, so that the team moving it to the new platform with the shop in the spring of 2027 builds the same job, less the holes the operations lead names (E1).

## Problem

The job's author has left, and the job moves to a new platform; without a specification the new team would read the old code and guess (E1).
In September 2026, 31 orders were cancelled because the product was not there to ship, about seven a week; most were products the supplier had stopped listing, which the shop went on showing in stock (E2, E24).
Three nights in September the run failed and nobody knew until a customer phoned, and each such morning cost the operator on call about three hours (E3, E31).

## Users

The timer: the scheduler that starts one run every night at 02:30, Berlin time (U1).
The operator on call: one of the three people in operations, a week each in turn, who reads the morning mail and, when a night went wrong, follows the runbook and runs the job by hand (U2).
The supplier, Nordkabel, who rebuilds the stock feed at 01:00 every night and publishes it at one address (U3).
The catalogue: the shop's own store of products and their stock, which the shop's pages read and the job writes to (U4). The catalogue team sets by hand the stock of what the supplier does not list (E4).

## Journey

1. At 01:00 the supplier rebuilds the feed; at 02:30 the timer starts the job.
2. The job fetches the feed, trying again ten minutes later while the supplier answers that it is still rebuilding.
3. It checks the feed, compares it with the shop's stock SKU by SKU, and refuses the whole run where the change is too large to be real.
4. It writes each new quantity to the catalogue, writes the night's report, and mails the operator where anything is low.
5. At 08:00 the operator reads the mail, or its absence; today a run that stopped on the catalogue's side sends nothing, and the night goes unnoticed until a customer phones.
6. Where the night went wrong, the operator follows the runbook: waits, reruns by hand, removes a lock left behind, or calls the supplier.

## Non-goals

- A second supplier: the job reads one feed, Nordkabel's, and the brief puts any other on the list for later (E5).
- Ordering from the supplier when stock runs low, and taking prices from the feed: the job sets quantities and nothing else (E5).
- Setting the stock of a product the feed no longer lists: the job names it, and the catalogue team sets it (E10, R11).
- Pages or an interface of its own: the job is read through its mail, its report, its log and its exit code (E73).

## Assumptions

- The supplier rebuilds the feed by 01:00 Berlin time, and a run at 02:30 finds it made within the last few hours. To check: the time each night's feed was made, in a month of logs.
- The operations team counts the orders cancelled for missing stock the same way after the move. To check: ask for the count of the first month after launch.
