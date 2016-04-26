#!/usr/bin/python
import csv
import sys
if len(sys.argv) < 3:
    sys.exit("Usage: csv2tsv.py file.csv file.tsv")
csv.field_size_limit(sys.maxsize)
csv.writer(file(sys.argv[2], 'w+'), delimiter="\t").writerows(csv.reader(open(sys.argv[1])))
