# -*- coding: utf-8 -*-

import random

from scrapy.http.headers import Headers

from crawler.misc.spider import CommonSpider
from crawler.misc import agents


class BaseHelper(object):
    BASE = "www.jianshu.com"
    BASE_URL = "http://{}".format(BASE)
    LECTURES_URL = "{base}/users/{{uid}}/collections_and_notebooks?slug={{uid}}".format(base=BASE_URL)
    COLLECTION_SUFFIX = "?order_by=commented_at&page={}"

    @classmethod
    def get_headers_json(cls):
        return Headers({
            # 'User-Agent': self._get_user_agent(),
            # 'Content-Type': 'application/json',
            # "Connection": "keep-alive",
            'Accept': 'application/json',
            'Host': cls.BASE,
        })

    @staticmethod
    def _get_user_agent():
        return str(random.choice(agents.AGENTS))
