"""The command line: `vatkit gross 100 DE`, `vatkit net 119 DE --category books`, `vatkit check DE123456789`."""
from __future__ import annotations

import argparse
import sys

from . import check_vat_number, gross, money, net, rate_for, vat_of


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vatkit", description="The VAT of a sale in the EU.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("vat", "gross", "net"):
        one = sub.add_parser(name, help=f"the {name} of an amount")
        one.add_argument("amount")
        one.add_argument("country")
        one.add_argument("--category", default=None)
    rate = sub.add_parser("rate", help="the rate of a country")
    rate.add_argument("country")
    rate.add_argument("--category", default=None)
    check = sub.add_parser("check", help="whether a VAT number is in its country's form")
    check.add_argument("number")
    args = parser.parse_args(argv)
    try:
        if args.command == "rate":
            print(f"{(rate_for(args.country, args.category) * 100).normalize():f}%")
        elif args.command == "check":
            print(check_vat_number(args.number))
        else:
            done = {"vat": vat_of, "gross": gross, "net": net}[args.command](args.amount, args.country, args.category)
            print(money(done, args.country))
    except ValueError as problem:
        print(f"vatkit: {problem}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
