'''
Offline tests
'''

import json
from builtins import range
from unittest import TestCase
from mock import MagicMock
from crawler.qq.qq.spiders.status import QqStatusSpider
from scrapy.http import TextResponse
from scrapy.http import Request
from crawler.qq.qq.items import QqStatusItem


class TestQqStatusOffline(TestCase):

    def setUp(self):
        self.spider = QqStatusSpider()
        self.spider._logger = MagicMock()
        self.spider.stats_dict = {}

    def test_parse(self):

        with open('qq_status.json', 'r') as file:
            json_file = json.load(file)
            text = json.dumps(json_file)
            request = Request(url='http://www.qq.com')
            response = TextResponse('qq_status.url', body=text, request=request,
                                    encoding='utf8')

            for item in self.spider.parse(response):
                if not isinstance(item, QqStatusItem):
                    self.assertEqual(item['text'], "lebooks")
                else:
                    self.fail("returned item in not a instance of QqStatusItem.")
