import scrapy


#KickstartSpider is a subclass of spider and must implement these
#functions

class KickstartSpider(scrapy.Spider):
    name = "kicker"

    #Must return iterable Requests object
    def start_requests(self):

        urls = []



    def parse(self,response):

        page = response.url.split("/")[-2]
