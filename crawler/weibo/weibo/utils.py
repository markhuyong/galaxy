# -*- coding: utf-8 -*-

import random

from scrapy.http.headers import Headers

from crawler.misc.spider import CommonSpider
from crawler.misc import agents


class BaseHelper(object):
    BASE_URL = "http://www.jianshu.com"
    LECTURES_URL = "{base}/users/{{uid}}/collections_and_notebooks?slug={{uid}}".format(base=BASE_URL)

    @classmethod
    def get_headers(cls):
        return Headers({
            # 'User-Agent': self._get_user_agent(),
            # 'Content-Type': 'application/json',
            # "Connection": "keep-alive",
            'Accept': 'application/json',
            # 'Host': cls.BASE_URL,
        })

    @staticmethod
    def _get_user_agent():
        return str(random.choice(agents.AGENTS))
