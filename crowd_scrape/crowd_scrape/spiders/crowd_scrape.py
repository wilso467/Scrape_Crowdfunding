# A python code to scrape data from crowdfund websites.
# @Evan M. Wilson 2017

# Use with 'scrapy crawl kicker' in top directory

import scrapy
from scrapy.linkextractors import LinkExtractor

# KickstartSpider is a subclass of spider and must implement these
# functions: start_requests() and parse()

class Project_Item(scrapy.Item):
    name = scrapy.Field()
    total_raised = scrapy.Field()
    funding_target = scrapy.Field()
    num_backers = scrapy.Field()

class TestSpider(scrapy.spiders.CrawlSpider):
    name = 'test'
    allowed_domains = ['kickstarter.com']
    start_urls = ['http://www.kickstarter.com/discover']

    #allowed_domains = ['stackoverflow.com']
    #start_urls = ['http://www.stackoverflow.com/']

    rules = (
        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor()),
        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('projects')
        #                                                        ), callback='parse_xpaths')

        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor()),
        scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(#allow=('projects'),
                                                                deny=('blog', 'profile', 'comments', 'posts', 'community','faqs', 'updates', 'login')
                                                                ), callback='parse_xpaths', follow=True),

        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(deny=('profiles','comments'))),
        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('projects',)), callback='parse'),
        # scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(), callback='parse'),

        #scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('questions')), callback='parse')
    )

    # rules = (
    #     scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(deny=('questions'))),
    #     scrapy.spiders.Rule(scrapy.linkextractors.LinkExtractor(allow=('blog')),callback='parse'),
    # )

    def parse_xpaths(self, response):

        #print('The url is','DOOOOT DOOOT ', '', response.url)
        #self.logger.info('Hi, this is an web page! DOOT DOOOT %s', response.url)

        try:
            name = response.xpath(
                             '//*[contains(concat('
                             ' " ", @class, " " ), concat( " ", "medium", " " )) and contains('
                             'concat( " ", @class, " " ), concat( " ", "mb3", " " ))]').re(r'(\n.*\n)')[0].strip()

            pledge_numbers = response.xpath(
                '//*[contains(concat( " ", @class, " " ), concat( " ", "js-usd_pledged", " " ))]/text()').re(
                r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')[0].strip()

            goal = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "money", " " ))]').re(
                r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')[0].strip()

            backers = response.xpath('//*[(@id = "backers_count")]').re(r'"[-0-9.,]*"')[0].strip()

            print('\n', 'The name of the project is: ', name)
            print('\n', 'Total raised: ', pledge_numbers)
            print('\n', 'Funding target: ', goal)
            print('\n', 'Number of backers: ', backers)

            item = Project_Item()
            item['name']=name
            item['total_raised']=pledge_numbers
            item['funding_target']=goal
            item['num_backers']=backers
            return item


        except IndexError:
            # print('Caught IndexError parsing name')
            pass
















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













