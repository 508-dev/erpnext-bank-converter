# Bank transaction CSV converter tool

This repo contains a python script, or set of scripts, to take CSV exports of bank transactions from banks such as Wise, Novo, and Chase, and converts them to the CSV format expected by the eprnext bank transaction import tool.

## Formats

### ERPNext bank transaction import tool

All formats are to be converted to this one. The headers of this csv are:

- Bank Account
- Date
- Description
- Withdrawal
- Deposit

Bank Account will always be the name of the bank for the given input, repeated twice. E.g. Wise will be "Wise - Wise" .

Date will be the date of the transaction in the format `YYYY-MM-DD`.

Description will be a combination of any description, payee, or related columns from a bank, concatenated into the Description column, with a 120 character limit applied (priority for concatenation in the order previously given.)

Withdrawal is the absolute value of a given transaction, if the transaction is a withdrawal from the account (usually, a negative value), else 0.

Deposit is the absolute value of a given transaction, if the transaction is a deposit into the account (usually, a positive value), else 0.

### Wise

The headers for a Wise CSV is:

```
ID Status Direction Created on Finished on Source fee amount Source fee currency Target fee amount Target fee currency Source name Source amount (after fees) Source currency Target name Target amount (after fees) Target currency Exchange rate Reference Batch Created by Category Note
```

Wise is interesting since the multi-currency nature of it means to get the true value in or out of the account itself must be calculated through a combination of columns, chosen carefully to ensure USD. In this case, the total withdrawal / deposit amount must be determined by adding the "Source fee amount" and "Source Amount (after fees)" columns.

There are also many columns that should be combined to make a description, such as Target name, reference, and note.

The Created On column should be used for date.

There's a Direction column that must be used to determine whether something is a withdrawal or deposit, wise doesn't list transactions as positive or negative to indicate whether something is a deposit or withdrawal.
