# A helper to crowd_scrape that sets up a selenium Chrome webdriver to interact with dynamically generated web
# elements

import selenium as se
from selenium import webdriver
import os
import platform

class web_driver_setup():

    path = os.path.dirname(__file__)

    system = platform.system()
    if system == 'Windows':
        driver_path = os.path.join(path, 'chromedriver.exe')
    elif system == 'Linux':
        driver_path = os.path.join(path, 'chromedriver')
    elif system == 'Darwin':
        driver_path = os.path.join(path, 'chromedrivermac')

    print("This is the chrome driver path", driver_path)

    driver = se.webdriver.Chrome(driver_path)



