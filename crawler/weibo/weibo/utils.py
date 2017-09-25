# -*- coding: utf-8 -*-

import random
import sys

from scrapy.http.headers import Headers

from crawler.misc import mobile_agents

reload(sys)
sys.setdefaultencoding('utf8')


class BaseHelper(object):
    WEIBO_LIST_PAGE_URL_PREFIX = "https://weibo.cn/u/{uid}?page={page}"
    WEIBO_SEARCH_URL = "https://weibo.cn/search/user/?keyword={nick_name}"
    M_WEIBO_HOME_URL = "https://m.weibo.cn/u/{uid}"
    M_WEIBO_STATUS_URL = "https://m.weibo.cn/container/getIndex?type=uid&value={uid}&containerid={cid}&page={page}"
    M_WEIBO_USER_URL = "https://m.weibo.cn/n/{nick_name}"
    M_WEIBO_USER_INFO_URL = "https://m.weibo.cn/container/getIndex?type=uid&value={uid}"
    M_WEIBO_LONG_TEXT = "https://m.weibo.cn/statuses/extend?id={text_id}"
    M_WEIBO_SINGLE_STATUS = "https://m.weibo.cn/{container_id}/{mid}"
    M_WEIBO_STATUS_MID = "https://m.weibo.cn/status/{mid}"

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
    def get_login_headers(cls):
        return {
            # 'User-Agent': cls._get_user_agent(),
            # 'User-Agent': "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
            "Pragma": "no-cache",
            "Origin": "https://passport.weibo.cn",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.8,zh;q=0.6",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Referer": "https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F",
            "Connection": "keep-alive",
        }

    @classmethod
    def get_status_headers(cls, uid):
        return Headers({
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh;q=0.6',
            'Accept': 'application/json, text/plain, */*',
            'Host': 'm.weibo.cn',
            'Referer': cls.get_m_weibo_home_url(uid),
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        })

    @classmethod
    def get_single_status_headers(cls, uid):
        """
        head for single status of weibo
        :param uid:
        :return:
        """
        return Headers({
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh;q=0.6',
            'Host': 'm.weibo.cn',
            'Referer': cls.get_m_weibo_home_url(uid),
        })
    @staticmethod
    def random_user_agent():
        return str(random.choice(mobile_agents.AGENTS))

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

    @classmethod
    def get_m_weibo_long_text(cls, text_id):
        return cls.M_WEIBO_LONG_TEXT.format(text_id=text_id)

    @classmethod
    def get_m_weibo_single_status(cls, container_id, mid):
        return cls.M_WEIBO_SINGLE_STATUS.format(container_id=container_id, mid=mid)

    @classmethod
    def get_m_weibo_status_mid(cls, mid):
        return cls.M_WEIBO_STATUS_MID.format(mid=mid)
    @staticmethod
    def get_cookie_key_prefix(spider):
        sep = "_"
        assert spider.name.index(sep) > 0
        return "{}:Cookies".format(spider.name.split(sep)[0])
