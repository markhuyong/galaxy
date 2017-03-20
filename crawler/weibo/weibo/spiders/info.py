# -*- coding: utf-8 -*-

import logging
import sys
from scrapy import Selector

from ..items import WeiboUserItem

from ..utils import CommonSpider
from ..utils import BaseHelper

logger = logging.getLogger(__name__)

reload(sys)
sys.setdefaultencoding('utf8')


class WeiboInfoSpider(CommonSpider):
    name = "weibo_info"
    nick_name = ""

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')  # nick_name
        if uid:
            self.nick_name = uid
            # self.logger.debug("uid item = {}".format(unicode(uid)))
            self.start_urls = [BaseHelper.get_common_page_url(uid)]

    def parse(self, response):
        res = Selector(response)
        user_info_table = res.css('table:first-of-type')
        find_nick_name = user_info_table.css(
            'td:nth-child(2) a::text').extract_first()
        if self.nick_name and self.nick_name == find_nick_name:
            user_info = WeiboUserItem()
            user_info['uid'] = user_info_table.css(
                'td:first-of-type a::attr(href)').re_first('(\d+)')
            if len(user_info['uid']) == 1:
                user_info['uid'] = user_info_table.xpath(
                    '//td/a[contains(@href, "attention")]/@href').re_first(
                    'uid=(\d+)')
        user_info['nick_name'] = find_nick_name
        user_info['profile_image'] = user_info_table.css(
            'td:nth-of-type(2) img::attr(src)').extract_first()
        yield user_info
