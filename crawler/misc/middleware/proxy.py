# -*- coding: utf-8 -*-

from ..proxy import PROXIES, FREE_PROXIES
import requests
import redis
import random


class CustomHttpProxyFromRedisMiddleware(object):
    def __init__(self, settings, crawler):
        self.rconn = settings.get("RCONN", redis.Redis(
            crawler.settings.get('REDIS_HOST', 'localhsot'),
            crawler.settings.get('REDIS_PORT', 6379),
            crawler.settings.get('REDIS_DB', 0),
            crawler.settings.get('REDIS_PASS', None)))
        self.redis_key = "http:proxies"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_request(self, request, spider):
        # TODO implement complex proxy providing algorithm
        if self.use_proxy(request):
            try:
                if self.rconn.scard(self.redis_key) < 2:
                    self.update_proxy(spider)
                if request.meta.get('retry_times', 0):
                    ban_proxy = request.meta.get('proxy', '').replace("http://", '')
                    self.rconn.srem(self.redis_key, ban_proxy)
                request.meta['proxy'] = "http://%s" % self.rconn.srandmember(self.redis_key)
                spider.logger.debug("http proxy is {}".format(request.meta['proxy']))
            except Exception, e:
                spider.logger.critical("Exception %s" % e)

    def use_proxy(self, request):
        """
        using direct download for depth <= 2
        using proxy with probability 0.3
        """
        if "depth" in request.meta and int(request.meta['depth']) <= 2:
            return False
        i = random.randint(1, 10)
        return i <= 2
        # return True

    def update_proxy(self, spider):
        url = "http://3360623093271490.standard.hutoudaili.com/?num=10&area_type=1&ports=8123&anonymity=3&order=1"
        try:
            html_code = requests.get(url, timeout=20).text.decode('utf8')
            proxies = html_code.split()
            if not proxies:
                spider.logger.critical("http proxies is used up.")
                return
            self.rconn.sadd(self.redis_key, *proxies)

        except Exception, e:
            spider.logger.critical("Exception %s" % e)


class CustomHttpProxyMiddleware(object):
    def process_request(self, request, spider):
        # TODO implement complex proxy providing algorithm
        if self.use_proxy(request):
            p = random.choice(PROXIES)
            try:
                request.meta['proxy'] = "http://%s" % p['ip_port']
            except Exception, e:
                # log.msg("Exception %s" % e, _level=log.CRITICAL)
                spider.logger.critical("Exception %s" % e)

    def use_proxy(self, request):
        """
        using direct download for depth <= 2
        using proxy with probability 0.3
        """
        # if "depth" in request.meta and int(request.meta['depth']) <= 2:
        #    return False
        # i = random.randint(1, 10)
        # return i <= 2
        return True
