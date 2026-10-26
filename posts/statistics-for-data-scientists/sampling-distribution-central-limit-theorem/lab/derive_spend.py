#!/usr/bin/env python3
"""Rebuild data/online_retail_customer_spend.csv from the UCI Online Retail archive.

You do not need this to run the lab: the CSV ships with it. It is here so the population the article
samples can be traced to the public file, line by line.

    python derive_spend.py online_retail.zip              # writes data/online_retail_customer_spend.csv
    python derive_spend.py online_retail.zip --out x.csv  # anywhere else

Download the archive (23.7 MB) from https://archive.ics.uci.edu/dataset/352/online+retail; the script
refuses any file whose SHA-256 differs from the one this lab was built from. Standard library only: the
workbook is a zip of XML parts, read as a stream (about 30 seconds).
"""

import argparse
import collections
import datetime
import hashlib
import pathlib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal

ARCHIVE_SHA256 = "f5385cbb54bbebf7196389109c6b0621faab0c304e3702548165e71c84aede8b"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
HERE = pathlib.Path(__file__).resolve().parent


def column(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def rows(book):
    """Yield each worksheet row as a list of strings, shared strings resolved."""
    shared = []
    with book.open("xl/sharedStrings.xml") as fh:
        for _, el in ET.iterparse(fh):
            if el.tag == NS + "si":
                shared.append("".join(t.text or "" for t in el.iter(NS + "t")))
                el.clear()
    with book.open("xl/worksheets/sheet1.xml") as fh:
        for _, el in ET.iterparse(fh):
            if el.tag != NS + "row":
                continue
            cells = {}
            for c in el.iter(NS + "c"):
                v = c.find(NS + "v")
                text = "" if v is None else v.text or ""
                cells[column(c.get("r"))] = shared[int(text)] if c.get("t") == "s" and text else text
            yield [cells.get(i, "") for i in range(max(cells) + 1)] if cells else []
            el.clear()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("archive", help="online+retail.zip from the UCI repository")
    ap.add_argument("--out", default=str(HERE / "data" / "online_retail_customer_spend.csv"))
    args = ap.parse_args()
    raw = pathlib.Path(args.archive).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != ARCHIVE_SHA256:
        sys.exit(f"SHA-256 {digest} is not the archive this lab was built from ({ARCHIVE_SHA256})")
    with zipfile.ZipFile(args.archive) as outer:
        inner = outer.read("Online Retail.xlsx")
    tmp = pathlib.Path(args.out).with_suffix(".xlsx.tmp")
    tmp.write_bytes(inner)
    net = collections.defaultdict(Decimal)
    lines = with_id = cancelled = 0
    first = last = None
    with zipfile.ZipFile(tmp) as book:
        it = rows(book)
        head = next(it)
        col = {name: i for i, name in enumerate(head)}
        for r in it:
            lines += 1
            serial = float(r[col["InvoiceDate"]])
            first = serial if first is None else min(first, serial)
            last = serial if last is None else max(last, serial)
            cid = r[col["CustomerID"]]
            if not cid:
                continue
            with_id += 1
            cancelled += r[col["InvoiceNo"]].upper().startswith("C")
            price = Decimal(repr(round(float(r[col["UnitPrice"]]), 6)))   # 2.5499999999999998 -> 2.55
            net[str(int(float(cid)))] += Decimal(r[col["Quantity"]]) * price
    tmp.unlink()
    pennies = {c: v.quantize(Decimal("0.01")) for c, v in net.items()}
    keep = sorted((c, v) for c, v in pennies.items() if v > 0)
    day = lambda s: (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(s))).isoformat()
    header = [
        "# Net spend per customer, UCI Online Retail, rebuilt by derive_spend.py from the public archive.",
        "# Source: D. Chen, 'Online Retail' [dataset], UCI Machine Learning Repository, 2015. https://doi.org/10.24432/C5BW33",
        "# Introduced in: D. Chen, S. L. Sain and K. Guo, Journal of Database Marketing and Customer Strategy Management 19(3), 2012. https://doi.org/10.1057/dbm.2012.17",
        "# Licence: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . Changed: invoice lines aggregated to one row per customer, as below.",
        f"# Archive online+retail.zip, SHA-256 {ARCHIVE_SHA256}; workbook 'Online Retail.xlsx', SHA-256 {hashlib.sha256(inner).hexdigest()}.",
        f"# Invoice dates {day(first)} to {day(last)}. {lines:,} invoice lines, {with_id:,} with a CustomerID ({cancelled:,} of them cancellations).",
        "# Rule: net_spend_gbp = sum of Quantity x UnitPrice over every line with that CustomerID, cancellations (negative",
        "# quantities) and adjustment lines (postage, discounts, manual entries) included, rounded to the penny.",
        f"# Kept: the {len(keep):,} of {len(pennies):,} customers whose net spend is positive; the population the article samples.",
    ]
    out = pathlib.Path(args.out)
    out.write_text("\n".join(header + ["customer_id,net_spend_gbp"] + [f"{c},{v}" for c, v in keep]) + "\n",
                   encoding="utf-8")
    total = sum(v for _, v in keep)
    print(f"{lines:,} lines, {with_id:,} with a customer ID; {len(pennies):,} customers, {len(keep):,} kept; "
          f"total net spend GBP {total:,.2f}; wrote {out.name}")


if __name__ == "__main__":
    main()
