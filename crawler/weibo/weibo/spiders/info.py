# -*- coding: utf-8 -*-
import json
import logging
import re
import sys

from scrapy import Request

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
            self.start_urls = [BaseHelper.get_m_weibo_user_url(uid)]

    def make_requests_from_url(self, url):
        meta = {
            'dont_redirect': True,
            'handle_httpstatus_list': [302]
        }
        return Request(url, meta=meta, dont_filter=True)

    def parse(self, response):
        location = response.headers.get('Location')
        if not (location and '/u/' in location):
            ValueError("user isn't exist.")
        uid_matcher = re.findall(r'/u/(\d+)', location)
        if not uid_matcher:
            ValueError("uid parser error.")
        info_url = BaseHelper.get_m_weibo_user_info_url(uid_matcher[0])
        headers = BaseHelper.get_headers()
        request = Request(info_url,
                          headers=headers,
                          callback=self.parse_info)
        yield request

    def parse_info(self, response):
        body = json.loads(response.body)
        user_info = body.get('userInfo')
        if not user_info:
            ValueError("user isn't exist.")

        item = WeiboUserItem()
        item['uid'] = user_info['id']
        item['nick_name'] = user_info['screen_name']
        item['profile_image'] = user_info['profile_image_url']
        yield item
