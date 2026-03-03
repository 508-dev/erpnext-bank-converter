#!/usr/bin/env python3
"""Convert bank transaction CSVs to ERPNext import format."""

import argparse
import csv
import sys
from pathlib import Path


def convert_wise(input_file: Path, output_file: Path) -> None:
    """Convert Wise CSV to ERPNext format."""
    with open(input_file, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    output_rows = []
    for row in rows:
        # Date: extract YYYY-MM-DD from "Created on"
        date = row["Created on"].split(" ")[0]

        # Description: combine Target name, Reference, Note (max 120 chars)
        desc_parts = []
        for field in ["Target name", "Reference", "Note"]:
            val = row.get(field, "").strip()
            if val:
                desc_parts.append(val)
        description = " - ".join(desc_parts)[:120]

        # Amount: Source fee amount + Source amount (after fees)
        fee = float(row["Source fee amount"]) if row["Source fee amount"] else 0
        amount = float(row["Source amount (after fees)"]) if row["Source amount (after fees)"] else 0
        total = fee + amount

        # Direction determines withdrawal vs deposit
        direction = row["Direction"]
        if direction == "OUT":
            withdrawal = total
            deposit = 0
        else:  # IN
            withdrawal = 0
            deposit = total

        output_rows.append({
            "Bank Account": "Wise - Wise",
            "Date": date,
            "Description": description,
            "Withdrawal": withdrawal,
            "Deposit": deposit,
        })

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["Bank Account", "Date", "Description", "Withdrawal", "Deposit"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Converted {len(output_rows)} transactions to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Convert bank CSVs to ERPNext format")
    parser.add_argument("input", type=Path, help="Input CSV file")
    parser.add_argument("-o", "--output", type=Path, help="Output CSV file (default: input_erpnext.csv)")
    parser.add_argument("-b", "--bank", choices=["wise"], default="wise", help="Bank format (default: wise)")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output = args.output or args.input.with_stem(args.input.stem + "_erpnext")

    if args.bank == "wise":
        convert_wise(args.input, output)


if __name__ == "__main__":
    main()
