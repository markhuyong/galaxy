# -*- coding: utf-8 -*-

import random

from scrapy.http.headers import Headers

from crawler.misc.spider import CommonSpider
from crawler.misc import agents


class BaseHelper(object):
    HOST = "www.jianshu.com"
    BASE = "http://" + HOST
    USER_URL = "{base}/u/{uid}"
    COLLECTION_URL = "{base}/{uuid}"
    COLLECTION_ARTICLES_URL = "{base}/mobile/collections/{cid}/public_notes" \
                              "?order_by=commented_at&page={page}&count={count}"
    LECTURES_URL = "{base}/users/{uid}/collections_and_notebooks?slug={uid}"
    COLLECTION_SUFFIX = "?order_by=commented_at&page={}"

    @classmethod
    def get_headers_json(cls):
        return Headers({
            # 'User-Agent': self._get_user_agent(),
            # 'Content-Type': 'application/json',
            # "Connection": "keep-alive",
            'Accept': 'application/json',
            'Host': cls.HOST,
        })

    @classmethod
    def get_lectures_url(cls, uid):
        return cls.LECTURES_URL.format(base=cls.BASE, uid=uid)

    @classmethod
    def get_user_url(cls, uid):
        return cls.USER_URL.format(base=cls.BASE, uid=uid)

    @classmethod
    def get_collection_url(cls, uuid):
        return cls.COLLECTION_URL.format(base=cls.BASE, uuid=uuid)

    @classmethod
    def get_collection_articles_url(cls, cid, page, count):
        return cls.COLLECTION_ARTICLES_URL.format(base=cls.BASE, cid=cid,
                                                  page=page,
                                                  count=count)
