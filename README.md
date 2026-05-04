# Bank Transaction CSV Converter

Converts bank transaction CSV exports to the format expected by the ERPNext bank transaction import tool.

## Supported Banks

| Bank  | Status      |
|-------|-------------|
| Wise  | Supported   |
| Chase | Supported |
| Novo  | Supported |

## Installation

Requires Python 3.9+. No external dependencies.

```bash
git clone <repo-url>
cd eprnext-bank-converter
```

## Usage

```bash
python convert.py <bank> <input_csv> [-o <output_csv>]
```

### Arguments

- `bank` - Bank format: `wise`, `chase`, or `novo`
- `input_csv` - Path to the bank's exported CSV file
- `-o, --output` - Output file path (optional, defaults to `<input>_erpnext.csv`)

### Examples

Convert a Wise export:
```bash
python convert.py wise transaction-history.csv
```

Specify a custom output file:
```bash
python convert.py wise transaction-history.csv -o converted.csv
```

## Output Format

The converter produces a CSV with these columns:

| Column       | Description                                      |
|--------------|--------------------------------------------------|
| Bank Account | Bank name repeated (e.g., "Wise - Wise")         |
| Date         | Transaction date in YYYY-MM-DD format            |
| Description  | Combined description fields (max 120 characters) |
| Withdrawal   | Amount withdrawn (0 if deposit)                  |
| Deposit      | Amount deposited (0 if withdrawal)               |

## Bank-Specific Notes

### Wise

- Uses the "Created on" column for the transaction date
- Combines "Target name", "Reference", and "Note" for the description
- Calculates total amount as: Source fee amount + Source amount (after fees)
- Uses the "Direction" column (IN/OUT) to determine deposit vs withdrawal
