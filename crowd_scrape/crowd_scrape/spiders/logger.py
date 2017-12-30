# A logger class for crowd_scrape code.  Keeps a running tally of collected URLs for every

import os
import json
import simplejson
import re
import io

class logger():
    url_dict = {}

    def init(self, crawl_type):

        #url_dict = self.url_dict
        if type(crawl_type) is not str:
            raise ValueError("A non-string was passed to logger.init()")
        if crawl_type == "traq" or "test" or "log":

            with open("kickstarter.log", 'r') as f:
                if os.stat("kickstarter.log").st_size > 0:
                    self.url_dict = simplejson.load(f)
                    # print("The json file ", f.name, " was loaded.")
                else:
                    print("No existing json log file was found...")
        else:
            raise ValueError("An unknown crawl_type was passed to the logger.")

    def add_url(self, url, status):
        url_dict = self.url_dict

        if type(url) is not str or type(status) is not str:
            raise ValueError("logger.add_url was called with the wrong type ")

        # Get rid of the "ref=XXX" part of the url which makes things cumbersome

        url = self.strip_ref(url)

        # If we find the url, check and see if it is open  or closed

        if url in url_dict:
            if url_dict[url] == "open" and status == "closed":
                url_dict[url] = status

        # If we don't find the url, make an entry with status
        else:
            url_dict[url] = status

    # Writes out the log file in json format which is easy for machines and people to read/write
    def write_out_log(self):
        url_dict = self.url_dict
        # print("This is the url dict", url_dict)
        json.dump(url_dict, open("kickstarter.log", 'w'))
        print("The logfile write out is complete.")

    def strip_ref(self, url):
        if type(url) is not str:
            raise ValueError("A non-string was passed to strip.")

        regexp = re.compile('(?:(?!\?ref=).)*')

        return regexp.search(url).group(0)














