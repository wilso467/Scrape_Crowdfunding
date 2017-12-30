# A helper to crowd_scrape that sets up a selenium Chrome webdriver to interact with dynamically generated web
# elements

import selenium as se
from selenium import webdriver
import os
import platform

# Needs to know what machine we're on
#Driver setup needs to know what crawler it's been called from


class web_driver_setup():



    def __init__(self,crawl_type):

        self.crawl_type = crawl_type

        if type(crawl_type) is not str:
            raise ValueError(" A non-string was passed into web_driver_setup.__init__ as 'crawl_type' ")

        if crawl_type== "test":
            self.setup_phantom_driver()
        elif crawl_type=="log":
            self.setup_chromedriver()
        elif crawl_type=="traq":
            self.setup_chromedriver()
        elif crawl_type == "dumb":
            self.setup_chromedriver()
        else:
            raise ValueError(" An unknown crawl type "+crawl_type+" was passed to web_driver_setup. ")

    def setup_chromedriver(self):

        path = os.path.dirname(__file__)
        system = platform.system()
        if system == 'Windows':
            driver_path = os.path.join(path, 'chromedriver.exe')
        elif system == 'Linux':
            driver_path = os.path.join(path, 'chromedriver')
        elif system == 'Darwin':
            driver_path = os.path.join(path, 'chromedrivermac')

        print("This is the chrome driver path", driver_path)

        self.driver = se.webdriver.Chrome(driver_path)


    def setup_phantom_driver(self):
        path = os.path.dirname(__file__)

        system = platform.system()
        if system == 'Windows':
            driver_path = os.path.join(path, 'phantomjs.exe')
        elif system == 'Linux':
            driver_path = os.path.join(path, 'phantomjs')



        self. driver = se.webdriver.PhantomJS(driver_path)


