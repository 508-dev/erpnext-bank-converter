#!/usr/bin/env python3
"""Convert bank transaction CSVs to ERPNext import format."""

import argparse
import csv
import sys
from abc import ABC, abstractmethod
from pathlib import Path

SUPPORTED_BANKS = ["wise", "chase", "novo"]


class BankConverter(ABC):
    """Base class for bank-specific converters."""

    bank_name: str = ""

    @abstractmethod
    def convert_row(self, row: dict) -> dict:
        """Convert a single row to ERPNext format."""
        pass

    def convert(self, input_file: Path, output_file: Path) -> None:
        """Convert input CSV to ERPNext format."""
        with open(input_file, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)

        output_rows = [self.convert_row(row) for row in rows]

        with open(output_file, "w", newline="\n", encoding="utf-8") as outfile:
            fieldnames = ["Bank Account", "Date", "Description", "Withdrawal", "Deposit"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(output_rows)

        print(f"Converted {len(output_rows)} transactions to {output_file}")


class WiseConverter(BankConverter):
    """Converter for Wise bank exports."""

    bank_name = "Wise"

    def convert_row(self, row: dict) -> dict:
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

        return {
            "Bank Account": f"{self.bank_name} - {self.bank_name}",
            "Date": date,
            "Description": description,
            "Withdrawal": withdrawal,
            "Deposit": deposit,
        }


class ChaseConverter(BankConverter):
    """Converter for Chase bank exports."""

    bank_name = "Chase"

    def convert_row(self, row: dict) -> dict:
        raise NotImplementedError("Chase converter not yet implemented")


class NovoConverter(BankConverter):
    """Converter for Novo bank exports."""

    bank_name = "Novo"

    def convert_row(self, row: dict) -> dict:
        raise NotImplementedError("Novo converter not yet implemented")


CONVERTERS = {
    "wise": WiseConverter,
    "chase": ChaseConverter,
    "novo": NovoConverter,
}


def main():
    parser = argparse.ArgumentParser(description="Convert bank CSVs to ERPNext format")
    parser.add_argument("bank", choices=SUPPORTED_BANKS, help="Bank format (wise, chase, novo)")
    parser.add_argument("input", type=Path, help="Input CSV file")
    parser.add_argument("-o", "--output", type=Path, help="Output CSV file (default: input_erpnext.csv)")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output = args.output or args.input.with_stem(args.input.stem + "_erpnext")

    converter = CONVERTERS[args.bank]()
    converter.convert(args.input, output)


if __name__ == "__main__":
    main()
