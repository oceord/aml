#!/usr/bin/env python3

import json
import sys


def mapper():
    for line in sys.stdin:
        data_item = json.loads(line)
        print(f"{data_item.get("To_Bank")}+{data_item.get("To_Account")};{data_item.get("Amount_Received")}")


if __name__ == "__main__":
    mapper()
