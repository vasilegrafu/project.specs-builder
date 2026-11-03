# Stock sync: the runbook

The job runs at 02:30 CET every night from the timer in `schedule/`. By
03:00 there is a line in `logs/<date>.log` and, where anything is low or
the run failed, a mail to ops@voltline.example. Nothing in the morning
mail means nothing changed and nothing is low.

## What each outcome means

| Exit | The log says | Means | Do |
|---|---|---|---|
| 0 | `done: N SKU(s) changed` | the shop's stock matches the feed | nothing |
| 1 | `nothing to do` | the feed and the shop agreed | nothing |
| 2 | `the feed was refused: ...` | the feed could not be fetched in three tries, was stale, empty, out of shape, or changed too much at once | see below; the shop's stock is as it was |
| 3 | `the run stopped: the catalogue refused ...` | some SKUs were written and one was refused | rerun by hand once the catalogue is up: `python stock_sync.py`; the rerun writes only what still differs |
| 4 | `another run holds the lock` | a run from before is still going, or died without cleaning up | if no `stock_sync.py` process runs, remove `stock_sync.lock` and rerun |

## The feed was refused

- **Could not be fetched.** The supplier rebuilds the feed at 01:00 CET;
  a 503 means the rebuild ran late. Rerun by hand after 08:00. If it is
  still 503, call Nordkabel's desk (in the ops wiki).
- **Stale.** The feed's `as_of` is older than 36 hours: last night's
  rebuild did not run. Nordkabel's desk; do not rerun with the old feed.
- **Out of shape.** A column is missing or a quantity is not a whole
  number: the supplier changed the format. Save the feed with `--feed`
  in hand for the developer; nothing is written until the parser is fixed.
- **Changed too much.** More than half of the SKUs would change: almost
  always a truncated feed. Open the feed; if it really is a stock take
  (the supplier will have said), run `python stock_sync.py --dry-run`,
  read the report, and then run with the guard lifted: set
  `MAX_CHANGE_RATIO` to 1.0 for that one run and put it back.

## A product is shown wrong on the shop

The shop's pages read the catalogue, not the feed. If a product says
"In stock" and Nordkabel has none, check `reports/<date>.txt` for the
SKU: if it is not there, the feed does not carry that SKU and the shop's
number is its own; the catalogue team sets it by hand.

## Secrets

`SUPPLIER_FEED_TOKEN` and `CATALOGUE_TOKEN` are in
`/etc/voltline/stock-sync.env`, readable by the `voltline` user alone.
Rotating either: change the file, no restart needed, the next run reads it.
