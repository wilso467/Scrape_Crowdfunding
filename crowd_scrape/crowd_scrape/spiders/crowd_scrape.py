# A python code to scrape data from crowdfunding websites.
# @Evan M. Wilson 2017

# Use with 'scrapy crawl test -o data.csv' in top directory to send data to csv
# Use 'scrapy crawl traq' to find urls from

import scrapy
# from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import DropItem
import re
import web_driver_setup
import logger
import random
import time

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
    number_of_updates = scrapy.Field()
    updates = scrapy.Field()
    num_pics = scrapy.Field()
    num_vids = scrapy.Field()

# Spider subclasses implement start_requests() and parse()


class TestSpider(scrapy.spiders.CrawlSpider):
    name = 'test'

    def start_requests(self):
        # Get Chrome web driver from helper function
        #driver = web_driver_setup.chrome_driver_setup.driver
        #driver = web_driver_setup.phantom_driver_setup.driver

        driver_set_up = web_driver_setup.web_driver_setup("test")
        driver = driver_set_up.driver

        #driver.get("https://www.kickstarter.com/")
        #driver.save_screenshot('screenshot.png')
        #time.sleep(2)

        #driver.get("https://www.kickstarter.com/discover/advanced")
        #driver.save_screenshot('advanced.png')
        #live_projects = driver.find_element_by_xpath('//*[(text()="Live projects")]')
        #proj_count = live_projects.find_elements_by_xpath('//p[@class="bold"]')s

        #proj_count = driver.find_elements_by_xpath('//p[@class="bold"]')


        #proj_count = driver.find_elements_by_xpath('')

        #print proj_count

        #print ("This is the proj count",len(proj_count),proj_count[0].text.encode('utf-8'), proj_count[1].text,proj_count[2].text,proj_count[3].text)

        #proj_count = proj_count[3].text

        #proj_count = proj_count.text

        #proj_count = proj_count.encode('utf-8')

        #print ("This is the proj count", proj_count)
        #time.sleep(2)
        #proj_count = int(proj_count.replace(',', ""))
        #print("Total number of live projects is ", proj_count)

        # Kickstarter API sort type

        # Uncomment this when not testing...
        #url_sort_types = ["newest", "end_date", "magic", "popularity", "most_backed", "most_funded"]
        #url_sort_types = ["newest", "end_date", "magic", "popularity"]
        url_sort_types = ["magic"]

        project_urls = []

        # Loop acquires list of urls to crawl
        for url_sort_type in url_sort_types:

            # Magic sort type randomizes based on some seed value
            # For magic, loop over a few random seeds to try to find all projects
            if url_sort_type == "magic" or url_sort_type == "most_backed" or url_sort_type == "most_funded":
                seeds = [str(random.randint(0, 999))]

                #Uncomment this when not testing...
                # seeds = [str(random.randint(0, 999)), str(random.randint(0, 999)), str(random.randint(0, 9999)),
                #          str(random.randint(0, 99999)), str(random.randint(0, 9999999)),str(random.randint(0, 9999999)),
                #          str(random.randint(0, 999999))]
            else:
                seeds = [str(random.randint(0, 999))]

            for seed in seeds:

                base_url = ["https://www.kickstarter.com/discover/advanced?sort=", url_sort_type, "&seed=", seed]

                # Max page index is 200, loop over all of them
                for page in range(1, 2):#200): #200):

                    page_number = ["&page=", str(page)]
                    full_url = ""
                    url = ""

                    full_url = base_url+page_number
                    page_url = url.join(full_url)

                    # Get the page after constructing url
                    driver.get(page_url)


                    # Gets the project urls
                    elements = driver.find_elements_by_xpath('//div[@class="js-track-project-card"]')

                    log = logger.logger()
                    log.init("test")

                    for element in elements:

                        link = element.find_element_by_tag_name("a")
                        url = link.get_attribute("href")

                        print(url)
                        #print(type(url))

                        if url not in project_urls:
                            project_urls.append(url)
                            print url
                            print str(url.encode('utf8'))
                            log.add_url(str(url.encode('utf8')), "open")

        #percent_live_found = float(len(project_urls))/float(proj_count)*100.00
        print(len(project_urls), " project urls found.")
        #print("Test spider found ", percent_live_found, "% of live Kickstarter projects")

        log.write_out_log()
        time.sleep(5)
        # for url in project_urls:
        #
        #     yield scrapy.Request(url, callback=self.parse_xpaths)

        for url in project_urls:
            yield scrapy.Request(url, callback=self.parse)

        #driver.close()

    #def parse_easy(self,response):

    # Main parsing function.
    def parse_xpaths(self, response):

        # Is this a 'projects' URL ?
        regexp = re.compile(r'projects')
        response.url

        #driver = web_driver_setup.web_driver_setup.driver
        driver = web_driver_setup.phantom_driver_setup.driver
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
                # goal = response.xpath('//*[@id="content-wrap"]/section/div/div[3]/div/div/div[3]/div[1]/
                # span[3]/span[1]').re(r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')[0]
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

            # This is all images -- even small ones.
            pics = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "fit", " " ))]')
            # pics = driver.find_elements_by_tag_name("img")
            # print("The number of images is ", len(pics))
            item['num_pics'] = len(pics)

            #Get the number of videos
            vids = driver.find_elements_by_tag_name("iframe")
            item['num_vids'] = len(vids)


            # Start of code to find the all the different pledge/reward levels
            pledge_panels = driver.find_elements_by_xpath(
                '//li[@class="hover-group js-reward-available pledge--available pledge-selectable-sidebar"]')
            pledge_list = []

            for pledge_panel in pledge_panels:

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
            #faqs = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ml3", " " ))]//p')
            #faqs = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "js-expanded", " " ))]//*[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]')
            faqs = driver.find_elements_by_xpath('//*[@id="project-faqs"]')
            #print("Just the faqs, mame", faqs)

            faq_list = "{"
            for faq in faqs:
                #print(faq.text)
                faq_list = faq_list+faq.text+";"
            faq_list = faq_list+"}"
            item['faqs'] = faq_list
            time.sleep(20)
            num_faqs = driver.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "project-nav__link--faqs", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "count", " " ))]')#len(faq_list)
            item['number_of_faqs'] = num_faqs.text


            # Find how many updates there are
            driver.get((response.url)+"/updates")
            updates = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "js-adjust-time", " " ))]')

            update_len = len(updates)
            start_date = updates[update_len-1].text
            item['start_date'] = start_date
            #print("Start date is ", start_date)
            item['number_of_updates'] = len(updates[1:update_len-2])
            # for update in updates:
            #     update_list = update_list+update.text+";"
            # update_list = update_list+"}"

            #print((response.url)+"/updates")
            #print("This is the list of updates.", update_list )
            #time.sleep(10)
            #item['faqs'] = faq_list
            #item['number_of_faqs'] = len(faq_list)

            #Gets the text for updates
            update_texts = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "grid-post__content", " " ))]//p')
            update_text_list = '{'
            for update_text in update_texts:
                update_text_list = update_text_list+update_text.text+";"
            update_text_list = update_text_list+"}"
            item['updates'] = update_text_list

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



class TraqSpider(scrapy.spiders.CrawlSpider):
    name = "traq"

    def start_requests(self):

        traq_urls = []
        start_page = ["https://www.kicktraq.com/archive/"]

        for page in range(6700, 8000):#(1, 8000):  # 8000): 46

            page_number = ["?page=", str(page)]
            full_url = ""
            url = ""
            full_url = start_page + page_number
            page_url = url.join(full_url)
            traq_urls.append(page_url)


        for url in traq_urls:
            #yield scrapy.Request(url, callback=self.parse_traq)
            yield scrapy.Request(url, callback=self.parse_arch_page)

    def parse_arch_page(self, response):

        archive_pages = []

        # arch_page_link = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "project-infobox", " " ))]//a')

        # This horrible regex monster finds the 'href' value of an <a>
        arch_page_links = response.xpath('//h2//a').re(r'<a\s+(?:[^>]*?\s+)?href=([\"\'])(.*?)\1')
        for arch_page_link in arch_page_links:
            # print(" This is the partial link", arch_page_link)

             # print(len(arch_page_link))

            # temp=arch_page_link.re(r'<a\s+(?:[^>]*?\s+)?href=([\"\'])(.*?)\1')
            # print temp
            if len(arch_page_link) > 1:
                arch_page = 'https://www.kicktraq.com' + arch_page_link
                # print("This should be the full link", arch_page)
                archive_pages.append(arch_page)


        for arch_page in archive_pages:
            yield scrapy.Request(arch_page, callback=self.parse_ks_link)
            #time.sleep(0.75)

    def parse_ks_link(self, response):

        kickstarter_pages = []

        log = logger.logger()
        log.init("traq")

        ks_link = response.xpath('//*[(@id = "button-backthis")]').re(r'<a\s+(?:[^>]*?\s+)?href=([\"\'])(.*?)\1')[1]
        ks_link = ks_link.encode('utf-8')
        # print("The kickstarter link is ", ks_link)

        kickstarter_pages.append(ks_link)

        for link in kickstarter_pages:
            log.add_url(link, "closed")

        log.write_out_log()

        # print(arch_page_link)

class LogSpider(scrapy.spiders.CrawlSpider):
    name = "log"


    def start_requests(self):
        log = logger.logger()
        log.init("log")

        url_dict = log.url_dict

        for url in url_dict:
            # yield scrapy.Request(url, callback=self.parse_traq)
            yield scrapy.Request(url, callback=self.parse_xpaths)

    # This is inelegant copy-pasta, but works
    # TODO use polymorphism or something to make this unnecessary
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
                # goal = response.xpath('//*[@id="content-wrap"]/section/div/div[3]/div/div/div[3]/div[1]/
                # span[3]/span[1]').re(r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')[0]
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

            # This is all images -- even small ones.
            pics = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "fit", " " ))]')
            # pics = driver.find_elements_by_tag_name("img")
            # print("The number of images is ", len(pics))
            item['num_pics'] = len(pics)

            #Get the number of videos
            vids = driver.find_elements_by_tag_name("iframe")
            item['num_vids'] = len(vids)


            # Start of code to find the all the different pledge/reward levels
            pledge_panels = driver.find_elements_by_xpath(
                '//li[@class="hover-group js-reward-available pledge--available pledge-selectable-sidebar"]')
            pledge_list = []

            for pledge_panel in pledge_panels:

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
            #faqs = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ml3", " " ))]//p')
            #faqs = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "js-expanded", " " ))]//*[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]')
            faqs = driver.find_elements_by_xpath('//*[@id="project-faqs"]')
            #print("Just the faqs, mame", faqs)

            faq_list = "{"
            for faq in faqs:
                #print(faq.text)
                faq_list = faq_list+faq.text+";"
            faq_list = faq_list+"}"
            item['faqs'] = faq_list
            time.sleep(20)
            num_faqs = driver.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "project-nav__link--faqs", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "count", " " ))]')#len(faq_list)
            item['number_of_faqs'] = num_faqs.text


            # Find how many updates there are
            driver.get((response.url)+"/updates")
            updates = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "js-adjust-time", " " ))]')

            update_len = len(updates)
            start_date = updates[update_len-1].text
            item['start_date'] = start_date
            #print("Start date is ", start_date)
            item['number_of_updates'] = len(updates[1:update_len-2])
            # for update in updates:
            #     update_list = update_list+update.text+";"
            # update_list = update_list+"}"

            #print((response.url)+"/updates")
            #print("This is the list of updates.", update_list )
            #time.sleep(10)
            #item['faqs'] = faq_list
            #item['number_of_faqs'] = len(faq_list)

            #Gets the text for updates
            update_texts = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "grid-post__content", " " ))]//p')
            update_text_list = '{'
            for update_text in update_texts:
                update_text_list = update_text_list+update_text.text+";"
            update_text_list = update_text_list+"}"
            item['updates'] = update_text_list

            #Item in this context is all the info about a single project
            return item














