# A helper to crowd_scrape that sets up a selenium Chrome webdriver to interact with dynamically generated web
# elements

import selenium as se
from selenium import webdriver
import os

class web_driver_setup():

    path = os.path.dirname(__file__)
    driver_path = os.path.join(path, 'chromedriver.exe')

    print("This is the chrome driver path", driver_path)

    driver = se.webdriver.Chrome(driver_path)



