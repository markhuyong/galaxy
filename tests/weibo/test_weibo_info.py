# -*- coding: utf-8 -*-

'''
Offline tests
'''

from unittest import TestCase
from mock import MagicMock

from crawler.weibo.weibo.spiders.info import WeiboInfoSpider
from ..response import fake_response_from_file
from crawler.weibo.weibo.items import WeiboUserItem


class TestWeiboInfoOffline(TestCase):
    def setUp(self):
        self.spider = WeiboInfoSpider()
        self.spider._logger = MagicMock()
        self.spider.stats_dict = {}
        self.spider.nick_name = u"哈囉李敖"

    def test_parse(self):
        user_info = self.spider.parse(
            fake_response_from_file('../weibo/user_info.html'))
        for item in user_info:
            if isinstance(item, WeiboUserItem):
                self.assertEqual(item['nick_name'], u"哈囉李敖",
                                 "not the same nick_name")
                self.assertEqual(item['uid'], '2134671703', "not the same uid")
            else:
                self.fail("the result is not a instance of WeiboUserItem")
