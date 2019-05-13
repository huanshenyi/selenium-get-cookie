# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
import os
import time
import pickle
from ArticleSpider.items import LagouJobItemLoader, LagouJobItem
from utils.common import get_md5
from datetime import datetime
from scrapy.loader import ItemLoader


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

    # selenium使用,startの書き直し
    def start_requests(self):
        # selenium使用してログイン,cookieを取得,scrapyのrequestに使用させる
        # 1.seleniumでログイン
        # x.cookieをファイルから取得
        cookies = []
        if os.path.exists(os.path.abspath(os.path.join(os.getcwd(), "..")) + '\cookies\lagou.cookic'):
            cookies = pickle.load(
                open(os.path.abspath(os.path.join(os.getcwd(), "..")) + '\cookies\lagou.cookic', "rb"))
        if not cookies:
            driverPath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '\driver\chromedriver.exe'
            browser = webdriver.Chrome(executable_path=driverPath)
            browser.get('https://passport.lagou.com/login/login.html')
            userInput = browser.find_element_by_xpath("//div[@class='form_body']//input[@class='input input_white']")
            userInput.send_keys('')
            pswdInput = browser.find_element_by_xpath("//div[@class='form_body']//input[@type='password']").send_keys(
                '')
            browser.find_element_by_xpath("//div[@class='form_body']//input[@type='submit']").click()
            time.sleep(10)
            # 2.cookie取得
            cookies = browser.get_cookies()

            # 3.cookieをファイルに書き込む
            filePath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '\cookies\lagou.cookic'
            pickle.dump(cookies, open(filePath, "wb"))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

    def parse_job(self, response):
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_xpath("salary", "//dd[@class='job_request']/p/span[@class='salary']/text()")
        item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")
        item_loader.add_css("tags", ".position-label li::text")
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_xpath("job_desc", "//*[@class='job_bt']/div[@class='job-detail']")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time", datetime.now())
        job_item = item_loader.load_item()

        return job_item
