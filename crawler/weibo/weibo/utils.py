# -*- coding: utf-8 -*-

import random
import sys

from scrapy.http.headers import Headers

from crawler.misc.spider import CommonSpider
from crawler.misc import agents

reload(sys)
sys.setdefaultencoding('utf8')


class BaseHelper(object):
    WEIBO_LIST_PAGE_URL_PREFIX = "http://weibo.cn/u/{uid}?page={page}"
    WEIBO_SEARCH_URL = "http://weibo.cn/search/user/?keyword={nick_name}"
    M_WEIBO_HOME_URL = "http://m.weibo.cn/u/{uid}"
    M_WEIBO_STATUS_URL = "http://m.weibo.cn/container/getIndex?type=uid&value={uid}&containerid={cid}&page={page}"
    M_WEIBO_USER_URL = "http://m.weibo.cn/n/{nick_name}"
    M_WEIBO_USER_INFO_URL = "http://m.weibo.cn/container/getIndex?type=uid&value={uid}"

    @classmethod
    def get_headers(cls):
        return Headers({
            # 'User-Agent': self._get_user_agent(),
            # 'Content-Type': 'application/json',
            # "Connection": "keep-alive",
            'Accept': 'application/json; charset=utf-8',
            'Host': 'm.weibo.cn',
        })

    @classmethod
    def get_common_page_url(cls, nick_name):
        # encode = nick_name.encode('utf-8') if not isinstance(nick_name, unicode) else nick_name

        # valid_utf8 = True
        # try:
        #     nick_name.decode('utf-8')
        # except UnicodeDecodeError:
        #     valid_utf8 = False
        # encode = nick_name if valid_utf8 else nick_name.encode('utf-8')
        return cls.WEIBO_SEARCH_URL.format(nick_name=nick_name)

    @classmethod
    def get_weibo_status_url(cls, uid, page=1):
        return cls.WEIBO_LIST_PAGE_URL_PREFIX.format(uid=uid, page=page)

    @classmethod
    def get_m_weibo_status_url(cls, uid, cid, page=1):
        return cls.M_WEIBO_STATUS_URL.format(uid=uid, cid=cid, page=page)

    @classmethod
    def get_m_weibo_home_url(cls, uid):
        return cls.M_WEIBO_HOME_URL.format(uid=uid)
    @classmethod
    def get_m_weibo_user_url(cls, nick_name):
        return cls.M_WEIBO_USER_URL.format(nick_name=nick_name)

    @classmethod
    def get_m_weibo_user_info_url(cls, uid):
        return cls.M_WEIBO_USER_INFO_URL.format(uid=uid)

    @staticmethod
    def get_cookie_key_prefix(spider):
        sep = "_"
        assert spider.name.index(sep) > 0
        return "{}:Cookies".format(spider.name.split(sep)[0])
