# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime, timedelta
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from secondhand.items import moonbbsItem

class MoonbbsSpider(CrawlSpider):
    name = 'moonbbs'
    allowed_domains = ['moonbbs.com']
    start_urls = ["http://www.moonbbs.com/forum-46-1.html"]
    _stop_following_links = False

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        # Rule(LinkExtractor(allow=('category\.php', ), deny=('subsection\.php', ))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="pg"]/a[@class="nxt"]', )), callback='parse_start_url', follow=True),
    )

    def parse_start_url(self, response):
        if self._stop_following_links:
            self._follow_links = False
            return

        self.logger.info('Hi, this is an item page! %s', response.url)
        if self._timestamp_too_old(response):
            self._stop_following_links = True
        
        items = []
        topics = response.xpath('//tbody[starts-with(@id, "normalthread_")]')
        for topic in topics:
            subject = topic.xpath('tr/th[@class="new"]')
            if subject:
              item = moonbbsItem()
              item['tag'] = subject.xpath('em/a/text()').extract()
              item['title'] = subject.xpath('a[@class="xst"]/text()').extract()
              item['link'] = response.urljoin(subject.xpath('a[@class="xst"]/@href').extract()[0])
              item['timestamp'] = topic.xpath('tr/td[@class="by"]/em/span/span/@title').extract()[0]
              items.append(item)
        return items

    def _timestamp_too_old(self, response):
        time_string = response.xpath('//td[@class="by"]/em/span/span/@title').extract()[0]
        three_days_ago = datetime.today() - timedelta(days=3)
        if time_string < three_days_ago.date().strftime("%Y-%m-%d"):
            return True
        else:
            return False

    def _validate(self, date_text):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False
