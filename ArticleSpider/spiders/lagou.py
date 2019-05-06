# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
import os
import time
import pickle


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("gongsi/j\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    # def parse_start_url(self, response):
    #     return []
    #
    # def process_results(self, response, results):
    #     return results

    #selenium使用,startの書き直し
    def start_requests(self):
        #selenium使用してログイン,cookieを取得,scrapyのrequestに使用させる
        #1.seleniumでログイン
        # x.cookieをファイルから取得
        cookies = []
        if os.path.exists(os.path.abspath(os.path.join(os.getcwd(), ".."))+'\cookies\lagou.cookic'):
            cookies = pickle.load(open(os.path.abspath(os.path.join(os.getcwd(), ".."))+'\cookies\lagou.cookic',"rb"))
        if not cookies:
            driverPath = os.path.abspath(os.path.join(os.getcwd(), ".."))+'\driver\chromedriver.exe'
            browser = webdriver.Chrome(executable_path=driverPath)
            browser.get('https://passport.lagou.com/login/login.html')
            userInput = browser.find_element_by_xpath("//div[@class='form_body']//input[@class='input input_white']")
            userInput.send_keys('')
            pswdInput = browser.find_element_by_xpath("//div[@class='form_body']//input[@type='password']").send_keys('')
            browser.find_element_by_xpath("//div[@class='form_body']//input[@type='submit']").click()
            time.sleep(10)
            #2.cookie取得
            cookies = browser.get_cookies()

            #3.cookieをファイルに書き込む
            filePath = os.path.abspath(os.path.join(os.getcwd(), ".."))+'\cookies\lagou.cookic'
            pickle.dump(cookies, open(filePath, "wb"))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)



    def parse_job(self, response):
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item
