# -*- coding: utf-8 -*-

import os
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
logger = logging.getLogger(__name__)
# handler = logging.StreamHandler()
handler = logging.FileHandler('hello.log')
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class CookiesMiddleware(RetryMiddleware):
    """ 维护Cookie """

    def __init__(self, settings, crawler):
        RetryMiddleware.__init__(self, settings)
        self.rconn = settings.get("RCONN", redis.Redis(
            crawler.settings.get('REDIS_HOST', 'localhsot'),
            crawler.settings.get('REDIS_PORT', 6379)))
        initCookie(self.rconn, "qq")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_request(self, request, spider):
        logger.debug("cookies request.url ======{}".format(request.url))
        redisKeys = self.rconn.keys()
        while len(redisKeys) > 0:
            elem = random.choice(redisKeys)
            if "{}:Cookies".format("qq") in elem:
                cookie = json.loads(self.rconn.get(elem))
                logger.info("cookies request.url ======{}".format(request.url))

                new_url = self._replace_token(request.url, cookie)
                if not request.url == new_url:
                    #FIXME: hack protected method
                    request._set_url(new_url)


                logger.debug("request.replace(url=new_url) request url ======{}".format(request.url))
                request.cookies = cookie
                request.meta["accountText"] = elem.split("Cookies:")[-1]
                break
            else:
                redisKeys.remove(elem)

    def process_response(self, request, response, spider):
        if response.status in [300, 301, 302, 303]:
            try:
                redirect_url = response.headers["location"]
                if "login.weibo" in redirect_url or "login.sina" in redirect_url:  # Cookie失效
                    logger.warning("One Cookie need to be updating...")
                    updateCookie(request.meta['accountText'], self.rconn,
                                 "qq")
                elif "weibo.cn/security" in redirect_url:  # 账号被限
                    logger.warning("One Account is locked! Remove it!")
                    removeCookie(request.meta["accountText"], self.rconn,
                                 "qq")
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
                         "qq")
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        else:
            return response

    @classmethod
    def _replace_token(cls, url, cookies):
        if "GTK" in url:
            for cookie in cookies:
                # if "p_skey" in cookie['name']:
                if "skey" == cookie['name']:
                    skey = cookie['value']
                    g_tk = cls._gen_p_skey(skey)
                    url = url.replace("GTK", g_tk)
        return url

    @staticmethod
    def _gen_p_skey(str_key):
        """
        Generate g_tk token required by fetcher
        :param str_key:
        :return:
        """
        hash_code = 5381
        for c in str_key:
            hash_code += (hash_code << 5) + ord(c)
        return str(hash_code & 0x7fffffff)
