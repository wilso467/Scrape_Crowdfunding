# A logger class for crowd_scrape code.  Keeps a running tally of collected URLs for every

import os
import json
import io

class logger():
    url_dict = {}

    def init(self, crawl_type):

        #url_dict = self.url_dict
        if type(crawl_type) is not str:
            raise ValueError("A non-string was passed to logger.init()")
        if crawl_type == "traq" or "test":

            # TODO fix the init for JSON files
            # Check to see if the logger file is empty or exists, throw a warning if not
            if os.stat("kickstarter.log").st_size > 0:
                #raise Warning(" !- Kickstarter log file is empty at start.  This could be a problem... -!")
            #open("kickstarter.log", "w")
            #self.url_dict = json.load(open("kickstarter.log"))

            with open("kickstarter.log", 'r') as f:
                self.url_dict = json.load(f)
        else:
            raise ValueError("An unknown crawl_type was passed to the logger.")



    def add_url(self, url, status):
        url_dict = self.url_dict

        if type(url) is not str or status is not bool:
            raise ValueError("logger.add_url was called with the wrong type (string and bool) ")
        # If we find the url, check and see if it is open (false) or close (true)
        # If we don't find the url, make and entry with status
        if url in url_dict:
            if url_dict[url] == False and status == True:
                url_dict[url] == status
        else:
            url_dict[url] = status


    def write_out_log(self):
        url_dict = self.url_dict
        print("This is the url dict", url_dict)
        json.dump(url_dict, open("kickstarter.log", 'w'))














