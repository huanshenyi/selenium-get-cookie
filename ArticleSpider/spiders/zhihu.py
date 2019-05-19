# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    # allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://ip.tool.chinaz.com/']
    #start_urls = ['http://www.zhihu.com/']

    #spider独自設定を定義
    # custom_settings = {
    #    "COOKIES_ENABLED": True
    # }
    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="D:\program\spider\ArticleSpider\driver\chromedriver.exe")
        super(ZhihuSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        #spider終わった時にブラウザを閉じる
        print("spider closed")
        self.browser.quit()

    def parse(self, response):
        print(response.xpath("//dd[@class='fz24']/text()"))
