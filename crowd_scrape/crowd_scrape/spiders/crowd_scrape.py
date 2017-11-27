# A python code to scrape data from crowdfund websites.
# @Evan M. Wilson 2017

# Use with 'scrapy crawl test -o data.csv' in top directory to send data to csv

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import DropItem
import re
import web_driver_setup
import logger
import random
import time

# functions: start_requests() and parse()

# Scrapy Item subclass with fields for Kickstarter data
class Project_Item(scrapy.Item):
    name = scrapy.Field()
    total_raised = scrapy.Field()
    funding_target = scrapy.Field()
    num_backers = scrapy.Field()
    url = scrapy.Field()
    number_of_reward_levels = scrapy.Field()
    reward_levels = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    category = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    comments = scrapy.Field()
    number_of_comments = scrapy.Field()
    faqs = scrapy.Field()
    number_of_faqs = scrapy.Field()

# Spider subclasses implement start_requests() and parse()
class TestSpider(scrapy.spiders.CrawlSpider):
    name = 'test'

    def start_requests(self):
        # Get Chrome web driver from helper function
        driver = web_driver_setup.web_driver_setup.driver

        driver.get("https://www.kickstarter.com/")
        live_projects = driver.find_element_by_xpath('//*[(text()="Live projects")]')
        proj_count = live_projects.find_elements_by_xpath('//p[@class="bold"]')
        proj_count = proj_count[3].text
        proj_count = proj_count.encode('utf-8')
        proj_count = int(proj_count.replace(',', ""))
        print("Total number of live projects is ", proj_count)

        # Kickstarter API sort type
        #url_sort_types = ["newest", "end_date", "magic", "popularity"]
        url_sort_types = ["magic"]

        project_urls = []

        # Loop acquires list of urls to crawl
        for url_sort_type in url_sort_types:

            # Magic sort type randomizes based on some seed value
            # For magic, loop over a few random seeds to try to find all projects
            if url_sort_type == "magic":
                seeds = [str(random.randint(0, 999))]#, str(random.randint(0, 999)), str(random.randint(0, 9999)),
                         #str(random.randint(0, 99999)), str(random.randint(0, 9999999)),str(random.randint(0, 9999999)),
                         #str(random.randint(0, 999999))]
            else:
                seeds = [str(random.randint(0, 999))]

            for seed in seeds:

                base_url = ["https://www.kickstarter.com/discover/advanced?sort=", url_sort_type, "&seed=", seed]

                # Max page index is 200, loop over all of them
                for page in range(1, 2): #200):

                    page_number = ["&page=", str(page)]
                    full_url = ""
                    url = ""

                    full_url = base_url+page_number
                    page_url = url.join(full_url)

                    # Get the page after constructing url
                    driver.get(page_url)


                    # Gets the project urls
                    elements = driver.find_elements_by_xpath('//div[@class="js-track-project-card"]')

                    # TODO The logger should probably be called here to store the pulled URL with logic on the inside

                    log = logger.logger()
                    log.init("test")




                    for element in elements:

                        link = element.find_element_by_tag_name("a")
                        url = link.get_attribute("href")

                        #print url

                        if url not in project_urls:
                            project_urls.append(url)
                            log.add_url(url, False)

        percent_live_found = float(len(project_urls))/float(proj_count)*100.00
        print(len(project_urls), " project urls found.")
        print("Test spider found ", percent_live_found, "% of live Kickstarter projects")

        log.write_out_log()
        for url in project_urls:

            yield scrapy.Request(url, callback=self.parse_xpaths)

        #driver.close()


    # Main parsing function.
    def parse_xpaths(self, response):

        # Is this a 'projects' URL ?
        regexp = re.compile(r'projects')
        response.url

        driver = web_driver_setup.web_driver_setup.driver
        driver.get(response.url)

        if regexp.search(response.url):
            item = Project_Item()
            item['url'] = response.url
            try:
                # Use this one
                name = response.xpath('//html/head/title').re(r'(\n.*\n)')[0].strip()
                item['name'] = name

            except IndexError:
                print('Caught IndexError parsing name')
                # print('This url through an exception on parse: ', response.url)
                # pass

            try:
                # Use this one
                pledge_numbers = response.xpath('//*[@id="pledged"]').re(r'(?<=data-pledged=)"(.*[0-9])')[0]
                #
                item['total_raised'] = pledge_numbers

            except IndexError:
                print('Caught IndexError parsing pledged money')
                # print('This url through an exception on parse: ', response.url)
                # pass
                item['total_raised'] = 'NOT FOUND'

            try:
                # Use this one
                goal = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "money", " " ))]').re(
                    r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')[0].strip()
                # goal = response.xpath('//*[@id="content-wrap"]/section/div/div[3]/div/div/div[3]/div[1]/span[3]/span[1]').re(r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')[0]
                #
                item['funding_target'] = goal

            except IndexError:
                print('Caught IndexError parsing goal')
                # print('This url through an exception on parse: ', response.url)
                # pass
                item['funding_target'] = 'NOT FOUND'

            try:
                # Use this one
                backers = response.xpath('//*[(@id = "backers_count")]').re(r'"[-0-9.,]*"')[0].strip()
                item['num_backers'] = backers
            except IndexError:
                print('Caught IndexError on number of backers')
                # print('This url through an exception on parse: ', response.url)
                # pass
                item['num_backers'] = 'NOT FOUND'

            #This is ugly but ok...
            location = response.xpath('//*[(@class = "nowrap navy-700 flex items-center medium type-12")]').re(r'(\n.*\n)')[1].strip() #[2].strip()
            #print("The location is ", location)
            item['location'] = location

            # Gets the category of the project
            category = response.xpath('//*[(@class = "nowrap navy-700 flex items-center medium mr3 type-12")]').re(r'(\n.*\n)')[1].strip()
            print("The category is ", category)
            item['category'] = category

            # Gets the end date of the project
            end_date = driver.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "type-12", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "js-adjust-time", " " ))]')
            item['end_date'] = end_date.text

            # Start of code to find the all the different pledge/reward levels
            pledge_panels = driver.find_elements_by_xpath(
                '//li[@class="hover-group js-reward-available pledge--available pledge-selectable-sidebar"]')
            pledge_list = []

            for pledge_panel in pledge_panels:
                #pledge_amounts = pledge_panel.find_element_by_xpath('//span[@class="money"]')
                pledge_amounts = pledge_panel.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "pledge__amount", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "money", " " ))]')
                for pledge_amount in pledge_amounts:
                    #print("Pledge amounts are", pledge_amount.text, "for url", response.url)
                    pledge_list.append(pledge_amount.text)


            reward_levels = "{"
            for pledges in pledge_list:
                reward_levels = reward_levels+str(pledges)+";"
            reward_levels = reward_levels + "}"

            # Concatenated list of reward/pledge $ amounts
            item['reward_levels'] = reward_levels
            # Number of different pledge values
            item['number_of_reward_levels'] = len(pledge_list)

            # Gets all the description text
            # TODO could probably use some regex formatting
            description_text = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "formatted-lists", " " ))]//p')
            description = "{"
            for descriptions in description_text:
                description = description+descriptions.text
            description = description+"}"
            item['description'] = description

            # Find and concatenate all the comments for a project
            driver.get((response.url)+"/comments")
            comments = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ml3", " " ))]//p')
            comment_list = "{"
            for comment in comments:
                comment_list = comment_list+comment.text+";"
            comment_list = comment_list+"}"
            item['comments'] = comment_list
            item['number_of_comments'] = len(comment_list)

            # Find and concatenate all the faqs for a project
            driver.get((response.url)+"/faqs")
            faqs = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ml3", " " ))]//p')
            faq_list = "{"
            for faq in faqs:
                faq_list = faq_list+faq.text+";"
            faq_list = faq_list+"}"
            item['faqs'] = faq_list
            item['number_of_faqs'] = len(faq_list)

            #Item in this context is all the info about a single project
            return item


# Item Pipeline that
class DuplicatesPipeline(object):
    def __init__(self):
            self.ids_seen = set()

    def process_item(self, item, spider):
            #if item['id'] in self.ids_seen:
            if item['name'] in self.ids_seen:
                raise DropItem("Duplicate item found: %s" % item)
            else:
                #self.ids_seen.add(item['id'])
                self.ids_seen.add(item['name'])
                return item



class TraqSpider():
    name = 'traq'

    def start_requests(self):

        traq_urls = []
        start_page = "https://www.kicktraq.com/archive/"

        for i in range(1,8000):
            url = start_page+"?page="+str(i)
            traq_urls = traq_urls.append(url)

            for url in traq_urls:
                yield scrapy.Request(url, callback=self.parse_xpaths)



    #def parse_something(self):

        #print("parsed a thing")


# Land of discarded code.  Kept for reference.

# class KickstartSpider(scrapy.Spider):
#     name = "kicker"
#
#     # Must return iterable Requests object
#     def start_requests(self):
#
#         urls = ['https://www.kickstarter.com/projects/1192053011/forbidden-lands-retro-open-world-survival-fantasy']
#
#         for url in urls:
#             yield scrapy.Request(url=url, callback=self.parse)
#
#     def parse(self,response):
#
#         # Find all the links from the website
#         #le = scrapy.linkextractors.LinkExtractor()
#         #print('Parsing links...')
#         #for link in le.extract_links(response):
#         #    yield scrapy.Request(link.url, callback=self.parse)
#             #print(link.url)
#
#
#         # Finding these via specific xpath is a bit of a 'hack.'  Clever regex would be better.
#         name = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "medium", " " )) and contains(concat( " ", @class, " " ), concat( " ", "mb3", " " ))]').extract_first()
#         pledge_numbers = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "js-usd_pledged", " " ))]/text()').extract_first()
#         goal = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "money", " " ))]').extract_first()
#         backer_numbers = response.xpath('//*[(@id = "backers_count")]').extract_first()
#
#         print(name)
#         print(pledge_numbers)
#         print(backer_numbers)
#         print(goal)



    # def link_parse(self, response):
    #    le = scrapy.LinkExtractor()
    #    print('Parsing links...')
    #    for link in le.extract_links(response):
    #        yield scrapy.Request(link.url, callback=self.parse)

    # allowed_domains = ['kickstarter.com']
    # start_urls = ['https://www.kickstarter.com/']#['http://www.kickstarter.com/discover']
    #
    # rules = (
    #     # Rules for parsing links. Sends links to parse_xpaths. Works recursively.
    #     scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('discover', 'projects'),
    #                                                             deny=(
    #                                                             'blog', 'profile', 'comments', 'posts', 'community',
    #                                                             'faqs', 'updates', 'login')
    #                                                             ), callback='parse_xpaths', follow=True),
    #
    #     #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor()),
    #     #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('projects')
    #     #                                                        ), callback='parse_xpaths')
    #
    #     #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow='discover')),
    #
    #
    #     #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(deny=('profiles','comments'))),
    #     #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('projects',)), callback='parse'),
    #     # scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(), callback='parse'),
    #
    #     #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('questions')), callback='parse')

# class PeacockSpider(scrapy.Spider):
#     name = "peacock"
#     allowed_domains = ['kickstarter.com']
#
#     #start_urls = ['http://www..kickstarter.com']
#
#     def start_requests(self):
#         url = 'http://www.kickstarter.com'
#         yield scrapy.Request(url=url, callback=self.parse)
#
#
#     def parse(self, response):
#         print('do some other stuff')
#
#         le = LinkExtractor(deny=('profiles','comments'),)
#         for link in le.extract_links(response):
#             yield scrapy.Request(link.url, callback=self.parse_xpaths)
#
#
#     def parse_xpaths(self, response):
#
#         # This is almost correct but the formatting is no good.
#         # name = response.xpath(
#         #     '//*[contains(concat( " ", @class, " " ), concat( " ", "medium", " " )) and contains(concat( " ", @class, " " ), concat( " ", "mb3", " " ))]').extract_first()
#
#         # Xpaths picks out CSS elements on a web page, the quasi regex it uses is hacky, but workable for now
#         # These characters select out the name of a project on a project page.  The regex/strip() cleans the output.
#
#         print('The current URL is', response.url)
#         name = response.xpath(
#             '//*[contains(concat('
#             ' " ", @class, " " ), concat( " ", "medium", " " )) and contains('
#             'concat( " ", @class, " " ), concat( " ", "mb3", " " ))]').extract_first()
#
#
#
#         if (name != None) and (name!= 'None'):
#
#             name = response.xpath(
#                 '//*[contains(concat('
#                 ' " ", @class, " " ), concat( " ", "medium", " " )) and contains('
#                 'concat( " ", @class, " " ), concat( " ", "mb3", " " ))]').re(r'(\n.*\n)')[0].strip()
#
#             print('The project name is', ' ', name)
#
#
#             #pledge_numbers = response.xpath(
#             #    '//*[contains(concat( " ", @class, " " ), concat( " ", "js-usd_pledged", " " ))]/text()').extract_first().strip()
#
#             pledge_numbers = response.xpath(
#                 '//*[contains(concat( " ", @class, " " ), concat( " ", "js-usd_pledged", " " ))]/text()').re(
#                 r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')[0].strip()
#
#             goal = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "money", " " ))]').re(
#                 r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')[0].strip()
#
#             backers = response.xpath('//*[(@id = "backers_count")]').re(r'"[-0-9.,]*"')[0].strip()
#
#         else:
#             print('Nothing to find here')













