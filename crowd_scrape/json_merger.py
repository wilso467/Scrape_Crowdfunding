# @Evan Wilson 2018
# A script to merge crowd_scrape logs with json Kickstarter data from other sources.

import os
import json
import simplejson
import sys


files_to_join = sys.argv[1:]

data = {}

for f in files_to_join:
    with open(f) as fin:
        d = json.load(fin)

        #data.update(d)

        print(d['projects'])

        #print(json.dump('project'))



# with open('kickstarter.log', 'wt') as fout:
#     fout.write(
#         json.dumps(data)
#     )