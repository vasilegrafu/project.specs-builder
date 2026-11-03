---
name: vatkit
kind: library
status: agreed
---

vatkit gives the VAT of a sale in the EU to the programs that make Voltline's invoices, and to the back office at the shell: the rate of each member state, the VAT, the gross and the net of a price, a sale split by rate as an invoice shows it, an amount written as its country writes it, and whether a VAT number is in its country's form.
This specification says what it does and what it promises, function by function and command by command, so that whoever keeps it after its maintainer moves on keeps the same promises (E78).
It is for invoices whose VAT is the tax office's figure to the cent, and that carry a change of a rate from the day it is in force.

## Problem

In the tax office's audit of 2024, 37 of the 4,100 invoices sampled had a VAT a few cents off the office's own figure, each corrected with a credit note; version 2.0 put that right, and the audit of 2025 found none of 3,900 (E79, E75, E76).
A change of a rate still reaches the invoices late: Finland's rate changed on 1 January 2026, vatkit carried it from 12 January, and 214 invoices to Finland went out at the old rate, each corrected by hand (E71, E80).
The finance team heard of that change from a customer, and vatkit's maintainer moves to another team at the end of the year, so what vatkit promises is written down nowhere but in its code (E78, E83).

## Users

The program that calls it: the shop's invoicing and the back office's programs, which ask vatkit for every rate, VAT and amount an invoice shows (U1).
The person at the shell: the three people of the back office, who check a figure or a customer's VAT number by hand from the command line a few times a day (U2).
The maintainer: who keeps vatkit, follows each change of a rate in the member states, and releases it (U3).

## Journey

1. The shop's invoicing has a sale: its lines, each with a net price and a category or none, the customer's country and, for a business, its VAT number.
2. It checks that the VAT number is in its country's form, and asks for the sale split by rate: for each rate, the net, the VAT and the gross.
3. It writes each amount on the invoice as the customer's country writes it, and issues the invoice.
4. In the back office someone checks a figure or a VAT number at the shell when a customer asks.
5. A member state changes a rate; the maintainer hears of it, changes vatkit and releases it; until the release, every invoice to that country carries the old rate, and today that is where it goes wrong (E80).

## Non-goals

- Whether a VAT number is registered: that is VIES's to say, and vatkit calls no other system (E34, E68, E84).
- Countries outside the EU: the finance team does not want them now (E84).
- The rate that held on a past day, to correct old invoices: asked for and left out, R11 (E85).
- Writing the invoice itself: vatkit gives the figures, and the invoicing writes and issues the invoice.

## Assumptions

- The tax office's audit samples the invoices of a year the same way each year, so that G1's counts compare. To check: read the size and the period of the sample in the tax office's letter of the 2026 audit.
