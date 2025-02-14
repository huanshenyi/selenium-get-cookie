# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.settings import SQL_DATETIME_FORMAT

# htmlのtagを排除用
from w3lib.html import remove_tags



class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def remove_splash(value):
    # job_cityの/を削除
    return value.replace("/", "")


class LagouJobItemLoader(ItemLoader):
    default_input_processor = TakeFirst()

def handle_jobaddr(value):
    add_list = value.split("\n")
    add_list = [item.strip() for item in add_list if item.strip() != "查看地图"]
    return "".join(add_list)

class LagouJobItem(scrapy.Item):
    # lagouwang
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()

    # sql
    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url,url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary),job_desc=VALUES (job_desc)
        
        """
        params = (
            self["title"], self['url'],self['url_object_id'], self['salary'], self["job_city"], self["work_years"], self["degree_need"],
            self["job_type"], self['publish_time'], self['job_advantage'], self["job_desc"], self["job_addr"],
            self['company_name'], self['company_url'], self['tags'], self['crawl_time'][0].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params