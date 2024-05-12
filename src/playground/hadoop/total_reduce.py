#!/usr/bin/env python3

import sys


def reducer():
    current_bank_account = None
    total_received = None
    for line in sys.stdin:
        bank_account, amount_received = line.strip().split("\t")
        if current_bank_account == bank_account:
            total_received += float(amount_received)
        else:
            if current_bank_account is not None:
                print(f"{current_bank_account}\t{total_received}")
            current_bank_account = bank_account
            total_received = float(amount_received)


if __name__ == "__main__":
    reducer()
