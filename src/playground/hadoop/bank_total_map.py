#!/usr/bin/env python3

import sys


def mapper():
    for line in sys.stdin:
        bank, _, amount = line.strip().replace("+", "\t").split("\t")
        print(f"{bank}\t{amount}")


if __name__ == "__main__":
    mapper()
