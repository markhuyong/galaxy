# -*- coding: utf-8 -*-

import sys
import random
import redis
import json
import logging
from cookies import initCookie, updateCookie, removeCookie
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware

# from logging.config import fileConfig

# fileConfig('logging_config.ini')
from crawler.qq.qq.utils import BaseHelper

logger = logging.getLogger(__name__)


# handler = logging.StreamHandler()
# handler = logging.FileHandler('hello.log')
# formatter = logging.Formatter(
#         '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)


class CookiesMiddleware(RetryMiddleware):
    """ 维护Cookie """

    def __init__(self, settings, crawler):
        RetryMiddleware.__init__(self, settings)
        self.rconn = settings.get("RCONN", redis.Redis(
            crawler.settings.get('REDIS_HOST', 'localhsot'),
            crawler.settings.get('REDIS_PORT', 6379),
            crawler.settings.get('REDIS_DB', 0),
            crawler.settings.get('REDIS_PASS', None)))
        initCookie(self.rconn, crawler.spider)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_request(self, request, spider):
        logger.debug("cookies request.url ======{}".format(request.url))
        prefix = BaseHelper.get_cookie_key_prefix(spider)
        redisKeys = self.rconn.keys("{}:*".format(prefix))
        while len(redisKeys) > 0:
            elem = random.choice(redisKeys)
            if prefix in elem:
                cookie = json.loads(self.rconn.get(elem))
                logger.info("cookies request.url ======{}".format(request.url))

                new_url = self._replace_token(request.url, cookie)
                if not request.url == new_url:
                    # FIXME: hack protected method
                    request._set_url(new_url)

                logger.debug(
                    "request.replace(url=new_url) request url ======{}".format(
                        request.url))
                request.cookies = cookie
                request.meta["accountText"] = elem.split("Cookies:")[-1]
                break
            else:
                redisKeys.remove(elem)

    def process_response(self, request, response, spider):
        prefix = BaseHelper.get_cookie_key_prefix(spider)
        if response.status in [300, 301, 302, 303]:
            try:
                redirect_url = response.headers["location"]
                if "login.weibo" in redirect_url or "login.sina" in redirect_url:  # Cookie失效
                    logger.warning("One Cookie need to be updating...")
                    updateCookie(request.meta['accountText'], self.rconn,
                                 spider)
                elif "weibo.cn/security" in redirect_url:  # 账号被限
                    logger.warning("One Account is locked! Remove it!")
                    removeCookie(request.meta["accountText"], self.rconn,
                                 spider)
                elif "weibo.cn/pub" in redirect_url:
                    logger.warning(
                        "Redirect to 'http://weibo.cn/pub'!( Account:%s )" %
                        request.meta["accountText"].split("--")[0])
                reason = response_status_message(response.status)
                return self._retry(request, reason, spider) or response  # 重试
            except Exception, e:
                raise IgnoreRequest
        elif response.status in [403, 414]:
            logger.error("%s! Stopping..." % response.status)
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
            # os.system("pause")
        elif u'登录态失效，请重新登录' in response.body:
            logger.warning("One Cookie need to be updating...")
            updateCookie(request.meta['accountText'], self.rconn,
                         spider)
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        else:
            return response

    @classmethod
    def _replace_token(cls, url, cookies):
        if "GTK" in url:
            p_skey = None
            skey = None
            rv2 = None
            for cookie in cookies:
                if "p_skey" in cookie['name']:
                    p_skey = cookie['value']
                if "skey" == cookie['name']:
                    skey = cookie['value']
                if "rv2" == cookie['name']:
                    rv2 = cookie['value']
            g_tk = cls.getNewGTK(p_skey, skey, rv2)
            url = url.replace("GTK", g_tk)
        return url

    # @classmethod
    # def _replace_token(cls, url, cookies):
    #     if "GTK" in url:
    #         for cookie in cookies:
    #             # if "p_skey" in cookie['name']:
    #             if "skey" == cookie['name']:
    #                 skey = cookie['value']
    #                 g_tk = cls._gen_p_skey(skey)
    #                 url = url.replace("GTK", g_tk)
    #     return url
    #
    # @staticmethod
    # def _gen_p_skey(str_key):
    #     """
    #     Generate g_tk token required by fetcher
    #     :param str_key:
    #     :return:
    #     """
    #     hash_code = 5381
    #     for c in str_key:
    #         hash_code += (hash_code << 5) + ord(c)
    #     return str(hash_code & 0x7fffffff)

    @staticmethod
    def LongToInt(value):  # 由于int+int超出范围后自动转为long型，通过这个转回来
        if isinstance(value, int):
            return int(value)
        else:
            return int(value & sys.maxint)

    @staticmethod
    def LeftShiftInt(number, step):  # 由于左移可能自动转为long型，通过这个转回来
        if isinstance((number << step), long):
            return int((number << step) - 0x200000000L)
        else:
            return int(number << step)

    @classmethod
    def getOldGTK(cls, skey):
        a = 5381
        for i in range(0, len(skey)):
            a = a + cls.LeftShiftInt(a, 5) + ord(skey[i])
            a = cls.LongToInt(a)
        return str(a & 0x7fffffff)

    @classmethod
    def getNewGTK(cls, p_skey, skey, rv2):
        b = p_skey or skey or rv2
        a = 5381
        for i in range(0, len(b)):
            a = a + cls.LeftShiftInt(a, 5) + ord(b[i])
            a = cls.LongToInt(a)
        return str(a & 0x7fffffff)
