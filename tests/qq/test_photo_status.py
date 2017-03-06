'''
Offline tests
'''

import json
from builtins import range
from unittest import TestCase
from mock import MagicMock

from crawler.qq.qq.spiders.photo import QqPhotoSpider
from scrapy.http import TextResponse
from scrapy.http import Request
from crawler.qq.qq.items import QqStatusItem, QqPhotoItem


class TestQqPhotoOffline(TestCase):
    def setUp(self):
        self.spider = QqPhotoSpider()
        self.spider._logger = MagicMock()
        self.spider.stats_dict = {}

    # def test_parse_album(self):
    #
    #     with open('qq_album.json', 'r') as file:
    #         json_file = json.load(file)
    #         text = json.dumps(json_file)
    #         request = Request(url='http://www.qq.com')
    #         response = TextResponse('qq_status.url', body=text, request=request,
    #                                 encoding='utf8')
    #
    #         for item in self.spider.parse(response):
    #             if isinstance(item, QqStatusItem):
    #                 print item
    #                 # self.assertEqual(item['text'], "lebooks")
    #             else:
    #                 self.fail("returned item in not a instance of QqPhotoItem.")

    def test_parse_photo(self):

        with open('qq_photo.json', 'r') as file:
            json_file = json.load(file)
            text = json.dumps(json_file)
            request = Request(url='http://www.qq.com')
            response = TextResponse('qq_status.url', body=text, request=request,
                                    encoding='utf8')

            for item in self.spider.parse_photo(response):
                if isinstance(item, QqStatusItem):
                    self.assertEqual(item['text'], ' ')
                else:
                    self.fail("returned item in not a instance of QqPhotoItem.")
