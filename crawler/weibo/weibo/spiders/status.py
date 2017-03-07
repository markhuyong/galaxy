# -*- coding: utf-8 -*-

import logging
import re
from datetime import date, datetime, timedelta

from scrapy import Request
from scrapy import Selector

from ..items import WeiboStatusItem

from ..utils import CommonSpider
from ..utils import BaseHelper

logger = logging.getLogger(__name__)


class WeiboStatusSpider(CommonSpider):
    name = "weibo_status"
    uid = 0
    total_page = 0

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')  # nick_name
        if uid:
            self.uid = uid
            self.logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_weibo_status_url(uid)]

    def parse(self, response):
        # if u"他还没发过微博" in response or u"她还没发过微博":
        #     return

        res = Selector(response)
        weibo_status = res.css('.c[id^=M_]')
        if self.total_page == 0:
            self.total_page = res.css('#pagelist').css(
                'input[name=mp]::attr(value)').extract_first()

        next_page_flag = u"下页" in res.css('#pagelist').css(
            'div a::text').extract_first()
        next_page_num = res.css('#pagelist').css(
            'div a::attr(href)').re_first(u'page=(\d+)')

        for weibo in weibo_status:
            item = WeiboStatusItem()
            item['published_at'] = self._parse_weibo_published_at(
                weibo.css('.ct').extract_first())
            item['text'] = weibo.css('.ctt').extract_first()
            yield item

        if next_page_flag:
            next_page = BaseHelper.get_weibo_status_url(self.uid, next_page_num)
            yield Request(url=next_page)

    def _parse_weibo_published_at(self, time_str):
        pattern = re.compile(u'(\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return match

        pattern = re.compile(u'(\d{1,2}月\d{1,2}日 \d{2}:\d{2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(date.today().year) + '-' + match.replace(u'月', '-') \
                .replace(u'日', '')

        pattern = re.compile(u'今天 (\d{2}:\d{2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(date.today()) + ' ' + match

        pattern = re.compile(u'(\d{2})分钟前')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(
                (datetime.now() - timedelta(minutes=int(match))).strftime(
                    "%Y-%m-%d %H:%M:%S"))
