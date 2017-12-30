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

        driver_set_up = web_driver_setup.web_driver_setup("test")
        driver = driver_set_up.driver


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


    def parse_xpaths(self, response):
        # Is this a 'projects' URL ?
        regexp = re.compile(r'projects')
        url = response.url

        driver_set_up = web_driver_setup.web_driver_setup("log")
        driver = driver_set_up.driver

        driver.get(url)

        log = logger.logger()
        log.init("log")

        # This check may now be unnecessary
        if regexp.search(response.url):
            item = Project_Item()
            item['url'] = response.url

            print("This is the logger URL", response.url)

            # Check the status of the project
            stat_live = driver.find_elements_by_xpath('//div[@class="Campaign-state-live"]')
            if len(stat_live) > 0:
                print("The status of project "+str(response.url)+" is live.")
                status = "open"
            else:
                print("Live state not found.")
                status = "closed"

            # add url has all the logic to adjust status in log file
            log.add_url(response.url, status)

            if status == "closed":
                print("Find the dates for a closed project")

                funding_period = driver.find_element_by_xpath('//*[@class="NS_campaigns__funding_period"]')
                beg_end = funding_period.find_elements_by_xpath('.//time')

                start_date = beg_end[0].get_attribute('datetime')
                end_date = beg_end[1].get_attribute('datetime')

                print("This is the start date for a closed project", start_date)
                print("This is the end date for a closed project", end_date)

                item['start_date'] = start_date
                item['end_date'] = end_date

            elif status == "open":
                print("Find the dates for an open project")

                # start_date_element = driver.find_element_by_xpath('//*[contains(@class, "js-state_changed_at")]')
                # start_date_element = driver.find_element_by_xpath('//*[@class="js-state_changed_at"]')
                # start_date_element = start_date_element.find_element_by_xpath('//time')

                # print("This is the start date for an open project", start_date_element.get_attribute('datetime'))

                end_date_element = driver.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "type-12", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "js-adjust-time", " " ))]')

                print("This is the end date for an open project", end_date_element.get_attribute('datetime'))

                # start_date = start_date_element.get_attribute('datetime')
                start_date = driver.find_element_by_xpath('//*[@class="js-adjust-time"]').text
                end_date = end_date_element.get_attribute('datetime')

                item['start_date'] = start_date
                item['end_date'] = end_date

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

            if item['total_raised'] == 'NOT FOUND':
                try:

                    pledge_numbers = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "mb0", " " ))]'
                                                    '//*[contains(concat( " ", @class, " " ),'
                                                    ' concat( " ", "money", " " ))]').re(
                        r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')

                    item['total_raised'] = pledge_numbers
                except:
                    print('Caught a super bad error parsing total funding raised')

                    item['total_raised'] = 'NOT FOUND'
                    pass



            if status == "open":
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

            elif status == "closed":
                try:
                    goal = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "navy-500", " " ))]'
                                      '//*[contains(concat( " ", @class, " " ), concat( " ", "money", " " ))]').re(
                        r'\$[-0-9.,]+[-0-9.,a-zA-Z]*\b')

                    item['funding_target'] = goal

                except:
                    print('Caught a super bad error parsing funding goal')
                    item['funding_target'] = 'NOT FOUND'
                    pass

            try:
                # Use this one
                backers = response.xpath('//*[(@id = "backers_count")]').re(r'"[-0-9.,]*"')[0].strip()
                item['num_backers'] = backers
            except:
                print('Caught IndexError on number of backers')
                # print('This url through an exception on parse: ', response.url)
                # pass
                item['num_backers'] = 'NOT FOUND'
                pass

            # Another try-except that should work for closed projects
            # This xpath just happens to get both amount raised and # backers
            if item['num_backers'] == 'NOT FOUND':
                try:

                    backers_amt = driver.find_element_by_xpath('//div[@class="mb0"]')

                    # Handy xpath magic for finding integers in a string
                    temp_back = [int(s) for s in backers_amt.text.split() if s.isdigit()]

                    backers = temp_back[0]

                    item['num_backers'] = backers

                except:
                    print('Caught a super bad error finding number of backers')
                    item['num_backers'] = 'NOT FOUND'


            if status == "closed":
                # Get the category and location
                loc_and_cat = driver.find_element_by_xpath('//*[contains(@class, "NS_projects__category_location")]')
                kids = loc_and_cat.find_elements_by_xpath('.//*')
                print("This is the locations", loc_and_cat.text)
                lc_list = []
                for kid in kids:

                    if len(kid.text) > 3:
                        print("These are the kids", kid.text)
                        lc_list.append(kid.text)

                location = lc_list[0]
                category = lc_list[1]

                item['location'] = location
                item['category'] = category
            elif status == "open":
                try:

                    #This is ugly but ok...
                    location = response.xpath('//*[(@class = "nowrap navy-700 flex items-center medium type-12")]').re(r'(\n.*\n)')[1].strip() #[2].strip()
                    #print("The location is ", location)
                    item['location'] = location

                    # Gets the category of the project
                    category = response.xpath('//*[(@class = "nowrap navy-700 flex items-center medium mr3 type-12")]').re(r'(\n.*\n)')[1].strip()
                    #print("The category is ", category)
                    item['category'] = category
                except:

                    print("Caught nasty exception parsing category and location")
                    item['location'] = 'NOT FOUND'
                    item['category'] = 'NOT FOUND'
                    pass

            # Gets the end date of the project
            #end_date = driver.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "type-12", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "js-adjust-time", " " ))]')
            #item['end_date'] = end_date.text

            # This is all images -- even small ones.
            pics = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "fit", " " ))]')
            # pics = driver.find_elements_by_tag_name("img")
            # print("The number of images is ", len(pics))
            item['num_pics'] = len(pics)

            #Get the number of videos
            vids = driver.find_elements_by_tag_name("iframe")
            item['num_vids'] = len(vids)

            # Get numbers like number of updates, FAQs, etc
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

            # Comments
            sub_element = element.find_element_by_xpath('//a[(@data-content="comments")]')
            print("This is the sub_element", sub_element.text.encode('utf8'))
            text = sub_element.text.encode('utf8')
            result = [int(s) for s in text.split() if s.isdigit()]

            if len(result) == 0:
                result = 0

            print(" Result of regex search ", result)

            item['number_of_comments'] = result

            # Start of code to find the all the different pledge/reward levels

            outer_level_pledge_panel = driver.find_element_by_xpath('//ol')
            pledge_amounts = outer_level_pledge_panel.find_elements_by_xpath('.//*[@class="pledge__amount"]')

            # if len(pledge_amounts) > 0:
            #
            #     print("I found pledge amounts")
            #
            # else:
            #
            #     print("I didn't find pledge amounts")

            pledge_list = []
            for pledge_amount in pledge_amounts:
                try:
                    money = pledge_amount.find_element_by_xpath('.//*[@class="money"]')
                    pledge_list.append(money.text)
                except:
                    print("Caught a 'NoSuchElementException' ")


            reward_levels = "{"
            for pledges in pledge_list:
                reward_levels = reward_levels+str(pledges)+";"
            reward_levels = reward_levels + "}"

            # Concatenated list of reward/pledge $ amounts
            item['reward_levels'] = reward_levels
            # Number of different pledge values
            #item['number_of_reward_levels'] = len(pledge_list)

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
            #item['number_of_comments'] = len(comment_list)

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
            # num_faqs = driver.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "project-nav__link--faqs", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "count", " " ))]')#len(faq_list)
            #item['number_of_faqs'] = num_faqs.text


            # Find how many updates there are

            driver.get((response.url)+"/updates")
            updates = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "js-adjust-time", " " ))]')

            #update_len = len(updates)
            #start_date = updates[update_len-1].text
            #item['start_date'] = start_date
            #print("Start date is ", start_date)


            #item['number_of_updates'] = len(updates[1:update_len-2])
            #for update in updates:
             #    update_list = update_list+update.text+";"
             #update_list = update_list+"}"

            #print((response.url)+"/updates")
            #print("This is the list of updates.", update_list )
            #time.sleep(10)
            #item['faqs'] = faq_list
            #item['number_of_faqs'] = len(faq_list)

            # Gets the text for updates
            update_texts = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "grid-post__content", " " ))]//p')
            update_text_list = '{'
            for update_text in update_texts:
                update_text_list = update_text_list+update_text.text+";"
            update_text_list = update_text_list+"}"
            item['updates'] = update_text_list

            #Item in this context is all the info about a single project

            driver.close()
            return item














