# -*- coding: utf-8 -*-
import scrapy
import pytz
from datetime import datetime, timedelta
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from secondhand.items import chineseinsfbayItem

class ChineseinsfbaySpider(CrawlSpider):
    name = 'chineseinsfbay'
    allowed_domains = ['chineseinsfbay.com']
    start_urls = ["http://www.chineseinsfbay.com/f/page_viewforum/f_3.html/"]
    next_page = u"下一页"
    _stop_following_links = False
    tz = pytz.timezone('America/Los_Angeles')
    today = datetime.now(tz)

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
        topics = response.xpath('//div[@class="topic_list_detail"]')
        for topic in topics:
            subject = topic.xpath('div[@class="topic_list_12"]/div[@class="havenopage"]/a[@class="title"]')
            if subject:
              item = chineseinsfbayItem()
              item['title'] = subject.xpath('text()').extract()[0]
              item['link'] = response.urljoin(subject.xpath('@href').extract()[0])
              item['timestamp'] = self._get_datetime(topic.xpath('div[@class="topic_list_2"]/div/span[@class="time"]/text()').extract()[0])
              items.append(item)
        return items

    def _timestamp_too_old(self, response):
        time_string = response.xpath('//span[@class="time"]/text()').extract()[0]
        three_days_ago = self.today - timedelta(days=3)
        if self._validate(time_string) and time_string < three_days_ago.date().strftime("%Y-%m-%d"):
            return True
        else:
            return False

    def _validate(self, date_text):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _get_datetime(self, time_string):
       try:
         if self._validate(time_string):
           return time_string
         else:
           return self.today.date().strftime("%Y-%m-%d") + " " + time_string 
       except ValueError:
           return self.today.date().strftime("%Y-%m-%d")
