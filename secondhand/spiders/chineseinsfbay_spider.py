# -*- coding: utf-8 -*-
import scrapy
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from secondhand.items import chineseinsfbayItem

class ChineseinsfbaySpider(CrawlSpider):
    name = 'chineseinsfbay'
    allowed_domains = ['chineseinsfbay.com']
    start_urls = ["http://www.chineseinsfbay.com/f/page_viewforum/f_3.html/"]
    next_page = u"下一页"
    _stop_following_links = False

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        # Rule(LinkExtractor(allow=('category\.php', ), deny=('subsection\.php', ))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="topic_option_right pagination_right"]/a[text()="' + next_page + '"]', )), callback='parse_start_url', follow=True),
    )

    def parse_start_url(self, response):
        if self._stop_following_links:
            self._follow_links = False
            return

        self.logger.info('Hi, this is an item page! %s', response.url)
        if self._timestamp_too_old(response):
            self._stop_following_links = True
        
        items = []
        topics = response.xpath('//div[@class="havenopage"]/a[@class="title"]')
        for topic in topics:
            item = chineseinsfbayItem()
            item['title'] = topic.xpath('text()').extract()
            item['link'] = response.urljoin(topic.xpath('@href').extract()[0])
            items.append(item)
        return items

    def _timestamp_too_old(self, response):
        time_string = response.xpath('//span[@class="time"]/text()').extract()[0]
        if self._validate(time_string) and time_string < '2016-05-00':
            return True
        else:
            return False

    def _validate(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False
