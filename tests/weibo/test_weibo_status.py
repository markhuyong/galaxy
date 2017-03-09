# -*- coding: utf-8 -*-

'''
Offline tests
'''

from unittest import TestCase
from mock import MagicMock
from datetime import date, datetime, timedelta

from crawler.weibo.weibo.spiders.status import WeiboStatusSpider
from ..response import fake_response_from_file
from crawler.weibo.weibo.items import WeiboStatusItem


class TestWeiboStatusOffline(TestCase):
    def setUp(self):
        self.spider = WeiboStatusSpider()
        self.spider._logger = MagicMock()
        self.spider.stats_dict = {}

    def test_parse(self):
        weibos = self.spider.parse(
            fake_response_from_file('../weibo/weibo_liao.html'))
        for item in weibos:
            if isinstance(item, WeiboStatusItem):
                self.assertTrue(u"台北市通化街有家小店" in item['text'],
                                "not include expected string")
            else:
                self.fail("the result is not a instance of WeiboUserItem")
            break

    def test__parse_weibo_status_published_at(self):
        stand_time = u'2013-05-28 10:48:13 [来自微博 weibo.com]'
        stand_parser = self.spider._parse_weibo_published_at(stand_time)
        self.assertEqual(stand_parser, u'2013-05-28 10:48:13')

        chinese_short_time = u'6月14日 12:11 [来自微博 weibo.com]'
        chinese_short_parser = self.spider._parse_weibo_published_at(
            chinese_short_time)
        self.assertEqual(chinese_short_parser,
                         str(date.today().year) + u'-6-14 12:11')

        today_time = u'今天 16:00 [来自微博 weibo.com]'
        today_parser = self.spider._parse_weibo_published_at(today_time)
        self.assertEqual(today_parser, str(date.today()) + u' 16:00')

        minus_before_time = u'27分钟前 [来自微博 weibo.com]'
        minus_before_parser = self.spider._parse_weibo_published_at(
            minus_before_time)
        self.assertEqual(minus_before_parser, str(
            (datetime.now() - timedelta(minutes=27)).strftime(
                "%Y-%m-%d %H:%M:%S")))

    def test__parse_weibo_text(self):
        response = fake_response_from_file('../weibo/yufeihong.html')
        text_css = response.css('.c[id^=M_EyP14odBh]')
        weibo_text = self.spider._parse_weibo_text(text_css)
        self.assertTrue(u'各位女神节日快乐' in weibo_text, "text is not in source")