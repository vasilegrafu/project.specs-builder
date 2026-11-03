# Stock sync

A job no user drives: every night at 02:30 it takes the supplier's stock
feed and brings the Voltline shop's stock in line with it, then tells the
morning what changed and what is running low. No pages, no API of its
own: it calls the supplier's feed and the shop's catalogue.

- `stock_sync.py`: the job, from the fetch to the mail, with every limit it holds to.
- `config.toml`: where the feed and the catalogue are, the low-stock threshold, who is mailed.
- `schedule/`: the systemd timer and service that start it.
- `logs/2026-10-10.log`: one night's log, as it is written.
- `RUNBOOK.md`: what each outcome means and what to do.
- `tests/`: what the job promises.

Demo material for the specs-builder skill: the supplier and the addresses
are made up, and the job runs against nothing here.
