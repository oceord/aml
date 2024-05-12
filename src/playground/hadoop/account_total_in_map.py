#!/usr/bin/env python3

import json
import sys


def mapper():
    for line in sys.stdin:
        data_item = json.loads(line)
        print(
            f"{data_item['To_Bank']}+{data_item['To_Account']}\t"
            + str(data_item["Amount_Received"]),
        )


if __name__ == "__main__":
    mapper()
