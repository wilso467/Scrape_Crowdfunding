

import scrapy
import crowd_scrape
import web_driver_setup
import re


class Dumb_Item(scrapy.Item):

    name = scrapy.Field()
    url = scrapy.Field()
    comments = scrapy.Field()
    number_of_comments = scrapy.Field()
    number_of_faqs = scrapy.Field()
    number_of_updates = scrapy.Field()


class StupidSpider(scrapy.spiders.CrawlSpider):

    name = "dumb"
    # print ("I am a dumb spider.")



    def start_requests(self):

        url = "https://www.kickstarter.com/projects/1291357699/ancelmo-james-first-full-length-album-completely-d/?ref=kicktraq"

        yield scrapy.Request(url, callback=self.dumb_parse)

    def dumb_parse(self,response):

        print("Duuuur, parse stuff")

        item = Dumb_Item()
        item['url'] = response.url
        item['name'] = "The name."

        print("This is the url I was told to parse", response.url)

        web_driver = web_driver_setup.web_driver_setup("dumb")
        driver = web_driver.driver

        driver.get(response.url)

        loc_and_cat = driver.find_element_by_xpath('//*[contains(@class, "NS_projects__category_location")]')

        kids = loc_and_cat.find_elements_by_xpath('.//*')

        print("This is the locations", loc_and_cat.text)

        lc_list = []
        for kid in kids:

            if len(kid.text) > 3:
                print("These are the kids",  kid.text)
                lc_list.append(kid.text)

        location = lc_list[0]
        category = lc_list[1]

        print("Location and and category are ", location, " ", category)






        # Find status
        stat_live = driver.find_elements_by_xpath('//div[@class="Campaign-state-successful"]')

        if len(stat_live) > 0:

            print("This is the campaign state", stat_live)
        else:
            print("No campaign state found.")

        element = driver.find_element_by_xpath('//*[((@class = "NS_projects__content"))]')

        # Updates
        sub_element = element.find_element_by_xpath('//a[(@data-content="updates")]')
        print("This is the sub_element", sub_element.text.encode('utf8'))
        text = sub_element.text.encode('utf8')
        result = [int(s) for s in text.split() if s.isdigit()]

        if len(result) == 0:
            result = 0

        print(" Result of regex search ", result)
        item['number_of_updates'] = result

        # FAQs
        sub_element = element.find_element_by_xpath('//a[(@data-content="faqs")]')
        print("This is the sub_element", sub_element.text.encode('utf8'))
        text = sub_element.text.encode('utf8')
        result = [int(s) for s in text.split() if s.isdigit()]
        if len(result) == 0:
            result = 0
        print(" Result of regex search ", result)
        item['number_of_faqs'] = result



        #Comments
        sub_element = element.find_element_by_xpath('//a[(@data-content="comments")]')
        print("This is the sub_element", sub_element.text.encode('utf8'))
        text = sub_element.text.encode('utf8')
        result = [int(s) for s in text.split() if s.isdigit()]

        if len(result) == 0:
            result = 0

        print(" Result of regex search ", result)

        item['number_of_comments'] = result

        driver.get("https://www.kickstarter.com/projects/1291357699/ancelmo-james-first-full-length-album-completely-d/comments")

        comments_section = driver.find_element_by_xpath('//ol[@class="comments"]')

        print("These are the comments from xpath", comments_section.text.encode('utf8'))

        # comments = []

        comments = driver.find_elements_by_xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "ml3", " " ))]//p')

        comment_list = "{"
        for comment in comments:
            comment_list = comment_list + comment.text + ";"
            print("This is a commnen", comment.text)
        comment_list = comment_list + "}"
        item['comments'] = comment_list


        driver.close()

        return item



