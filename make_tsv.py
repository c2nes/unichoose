import json
import sys

for char in json.load(sys.stdin):
    row = ["U+" + char["cp"], char["_char"], char["_name"]]
    print("\t".join(row))
