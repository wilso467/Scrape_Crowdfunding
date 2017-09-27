# A python code to scrape data from crowdfund websites.
# @Evan M. Wilson 2017

# Use with 'scrapy crawl kicker' in top directory

import scrapy

# KickstartSpider is a subclass of spider and must implement these
# functions: start_requests() and parse()

class KickstartSpider(scrapy.Spider):
    name = "kicker"

    # Must return iterable Requests object
    def start_requests(self):

        urls = ['https://www.kickstarter.com/projects/1192053011/forbidden-lands-retro-open-world-survival-fantasy']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self,response):

        #Find all the links from the website
        le = scrapy.linkextractors.LinkExtractor()
        print('Parsing links...')
        for link in le.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse)
            #print(link.url)


        # Finding these via specific xpath is a bit of a 'hack.'  Clever regex would be better.
        name = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "medium", " " )) and contains(concat( " ", @class, " " ), concat( " ", "mb3", " " ))]').extract_first()
        pledge_numbers = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "js-usd_pledged", " " ))]/text()').extract_first()
        goal = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "money", " " ))]').extract_first()
        backer_numbers = response.xpath('//*[(@id = "backers_count")]').extract_first()

        print(name)
        print(pledge_numbers)
        print(backer_numbers)
        print(goal)



    # def link_parse(self, response):
    #    le = scrapy.LinkExtractor()
    #    print('Parsing links...')
    #    for link in le.extract_links(response):
    #        yield scrapy.Request(link.url, callback=self.parse)

        



