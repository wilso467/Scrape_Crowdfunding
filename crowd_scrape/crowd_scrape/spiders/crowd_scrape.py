# A python code to scrape data from crowdfund websites.
# @Evan M. Wilson 2017

# Use with 'scrapy crawl test -o data.csv' in top directory to send data to csv

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import DropItem
import re

# functions: start_requests() and parse()

# Scrapy Item subclass with fields for Kickstarter data
class Project_Item(scrapy.Item):
    name = scrapy.Field()
    total_raised = scrapy.Field()
    funding_target = scrapy.Field()
    num_backers = scrapy.Field()

# Spider subclasses implement start_requests() and parse()
class TestSpider(scrapy.spiders.CrawlSpider):
    name = 'test'
    allowed_domains = ['kickstarter.com']
    start_urls = ['https://www.kickstarter.com/']#['http://www.kickstarter.com/discover']

    rules = (
        # Rules for parsing links. Sends links to parse_xpaths. Works recursively.
        scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('discover', 'projects'),
                                                                deny=(
                                                                'blog', 'profile', 'comments', 'posts', 'community',
                                                                'faqs', 'updates', 'login')
                                                                ), callback='parse_xpaths', follow=True),

        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor()),
        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('projects')
        #                                                        ), callback='parse_xpaths')

        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow='discover')),


        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(deny=('profiles','comments'))),
        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('projects',)), callback='parse'),
        # scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(), callback='parse'),

        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('questions')), callback='parse')
    )

    # Main parsing function.
    def parse_xpaths(self, response):

        # Is this a 'projects' URL ?
        regexp = re.compile(r'projects')
        response.url

        if regexp.search(response.url):
            item = Project_Item()
            try:
                # Use this one
                name = response.xpath('//html/head/title').re(r'(\n.*\n)')[0].strip()

                # name = response.xpath(
                #                  '//*[contains(concat('
                #                  ' " ", @class, " " ), concat( " ", "medium", " " )) and contains('
                #                  'concat( " ", @class, " " ), concat( " ", "mb3", " " ))]').re(r'(\n.*\n)')[0].strip()
                #
                # pledge_numbers = response.xpath(
                #     '//*[contains(concat( " ", @class, " " ), concat( " ", "js-usd_pledged", " " ))]/text()').re(
                #     r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')[0].strip()
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

            #
            # print('\n', 'The name of the project is: ', name)
            # print('\n', 'Total raised: ', pledge_numbers)
            # print('\n', 'Funding target: ', goal)
            # print('\n', 'Number of backers: ', backers)
            #

            return item

# Item Pipeline that
# TODO Refine this pipeline to filter out extraneous results
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













