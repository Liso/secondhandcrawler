# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

tag_keywords = ('求', )

class SecondhandPipeline(object):
    def process_item(self, item, spider):
        return item

class TagPipeline(object):
    def process_item(self, item, spider):
      try:
        if not item['tag']:
            self.parseTitle(item)
      except KeyError:
            self.parseTitle(item)
      return item

    def parseTitle(self, item):
      if (item['title'].find(s) >= 0 for s in tag_keywords):
          item['tag'] = '求购'
      else:
          item['tag'] = '出售'

