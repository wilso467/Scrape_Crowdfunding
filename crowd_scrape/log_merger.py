import json
import sys

files_to_join = sys.argv[1:]

data = {}

for f in files_to_join:
    with open(f) as fin:
        d = json.load(fin)

        # Dictionaries are key -> value maps.
        # when you a.update(b) [with a and b both dictionaries]
        # you add all keys that aren't in a but are in b to a (along with
        # associated value).  Also, keys that are present in both a and b
        # cause the values for those keys to be updated to be those of b
        data.update(d)

with open('merged_output.json', 'wt') as fout:
    fout.write(
        json.dumps(data)
    )

########################
# Run like this:
# python merge.py 1.json 2.json 3.json ...
