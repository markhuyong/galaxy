# -*- coding: utf-8 -*-

import random

from scrapy.http.headers import Headers

from crawler.misc.spider import CommonSpider
from crawler.misc import agents


class BaseHelper(object):
    WEIBO_LIST_PAGE_URL_PREFIX = "http://weibo.cn/u/{uid}?page={page}"
    WEIBO_SEARCH_URL = "http://weibo.cn/search/user/?keyword={nickname}"

    @classmethod
    def get_headers(cls):
        return Headers({
            # 'User-Agent': self._get_user_agent(),
            # 'Content-Type': 'application/json',
            # "Connection": "keep-alive",
            'Accept': 'application/json',
            # 'Host': cls.BASE_URL,
        })

    @classmethod
    def get_common_page_url(cls, nick_name):
        cls.WEIBO_SEARCH_URL.format(nickname=unicode(nick_name))

    @classmethod
    def get_weibo_status_url(cls, uid, page=1):
        cls.WEIBO_LIST_PAGE_URL_PREFIX.format(uid=uid, page=page)
