import json
import simplejson
import os


with open("kickstarter.log", 'r') as f:
    if os.stat("kickstarter.log").st_size > 0:
        log = simplejson.load(f)

        print(len(log))

    else:
            raise ValueError("No log file found.")

