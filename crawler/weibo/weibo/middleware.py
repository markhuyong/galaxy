# -*- coding: utf-8 -*-

import json
import random

import redis
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message

from cookies import initCookie, updateCookie, removeCookie
from crawler.weibo.weibo.utils import BaseHelper


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
        prefix = BaseHelper.get_cookie_key_prefix(spider)
        redisKeys = self.rconn.keys("{}:*".format(prefix))

        if not redisKeys:
            return
        used_keys = self.rconn.smembers("cycle:{}".format(prefix))
        rand_keys = list(set(redisKeys) - used_keys)

        if not rand_keys:
            rand_keys = redisKeys
            self.rconn.delete("cycle:{}".format(prefix))

        elem = random.choice(rand_keys)
        cookie = json.loads(self.rconn.get(elem))
        if request.cookies:
            extra = request.cookies
            cookie.update(extra)
        request.cookies = cookie
        request.meta["accountText"] = elem.split(prefix)[-1]
        self.rconn.sadd("cycle:{}".format(prefix), elem)

    def process_response(self, request, response, spider):
        if response.status in [300, 301, 302, 303]:
            try:
                redirect_url = response.headers["location"]
                if "login.weibo" in redirect_url or "login.sina" in redirect_url:  # Cookie失效
                    spider.logger.warning("One Cookie need to be updating...")
                    updateCookie(request.meta['accountText'], self.rconn,
                                 spider.name)
                elif "weibo.cn/security" in redirect_url:  # 账号被限
                    spider.logger.warning("One Account is locked! Remove it!")
                    removeCookie(request.meta["accountText"], self.rconn,
                                 spider.name)
                elif "weibo.cn/pub" in redirect_url:
                    spider.logger.warning(
                        "Redirect to 'http://weibo.cn/pub'!( Account:%s )" %
                        request.meta["accountText"].split("--")[0])
                reason = response_status_message(response.status)
                return self._retry(request, reason, spider) or response  # 重试
            except Exception, e:
                raise IgnoreRequest
        elif response.status in [403, 414]:
            spider.logger.error("%s! Stopping..." % response.status)
        else:
            return response
