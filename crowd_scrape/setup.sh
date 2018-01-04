#!/bin/bash

sudo apt update
sudo apt install python python-virtualenv git
virtualenv -p `which python2` ~/venv
# now activate it
. ~/venv/bin/activate


# Now get the source:
#git clone https://github.com/wilso467/Scrape_Crowdfunding

# Now install the necessary packages
pip install -r ~/Scrape_Crowdfunding/crowd_scrape/requirements.txt