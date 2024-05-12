#!/usr/bin/env python3

import json
import sys


def mapper():
    for line in sys.stdin:
        data_item = json.loads(line)
        print(
            f"{data_item['From_Bank']}+{data_item['From_Account']}\t"
            + str(data_item["Amount_Paid"]),
        )


if __name__ == "__main__":
    mapper()
