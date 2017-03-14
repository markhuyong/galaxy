# -*- coding: utf-8 -*-

import json
import logging

from scrapy import Selector
from scrapy.http.cookies import CookieJar

from scrapy.http.request import Request

from ..items import LecturesItem
from ..utils import CommonSpider
from ..utils import BaseHelper

logger = logging.getLogger(__name__)


class LectureSpider(CommonSpider):
    name = "jianshu_lectures"

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')
        if uid:
            self.logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_user_url(uid)]

    def parse(self, response):
        uid = response.request.url.split('/')[-1]

        cookie_jar = response.meta.setdefault('cookiejar', CookieJar())
        cookie_jar.extract_cookies(response, response.request)

        headers = BaseHelper.get_headers_json()

        item = LecturesItem()
        res = Selector(response)
        titles = res.css('title::text').re(ur'(\w+)') or ['']
        item['authorName'] = titles[0]
        item['url'] = response.request.url

        next_link = BaseHelper.LECTURES_URL.format(uid=uid)
        request = Request(next_link, callback=self.parse_lecture_json,
                          headers=headers)
        cookie_jar.add_cookie_header(request)  # apply Set-Cookie ourselves
        request.meta['item'] = item
        yield request

        yield item

    def parse_lecture_json(self, response):
        body = json.loads(response.body)
        logger.debug("json_body============{}".format(body))
        item = response.request.meta['item']
        collection = []

        for record in body['notebooks']:
            lecture = self._get_partial_lecture(record, item['authorName'])
            yield self._get_parse_article_number_request(lecture, 'lecture')
            collection += [lecture]

        item['lectures'] = collection

        collection = []
        for record in body['own_collections']:
            lecture = self._get_partial_lecture(record, item['authorName'],
                                                isSpecial=True)
            yield self._get_parse_article_number_request(lecture, 'lecture')
            collection += [lecture]

        item['specials'] = collection

    def parse_article_number(self, response):
        lecture = response.request.meta['lecture']
        res = Selector(response)
        numbers = res.css('div.info::text').re(ur'([0-9]+)') or [0]
        lecture['articleNumber'] = numbers[0]

    def _get_partial_lecture(self, record, author_name, isSpecial=False):
        if isSpecial:
            return self._init_partial_lecture(record, author_name,
                                              title_key='title', link_infix='c',
                                              link_suffix='slug')
        return self._init_partial_lecture(record, author_name, title_key='name',
                                          link_infix='nb', link_suffix='id')

    def _init_partial_lecture(self, record, author_name, title_key, link_infix,
                              link_suffix):
        lecture = dict()
        lecture['authorName'] = author_name
        lecture['name'] = record[title_key]
        lecture['url'] = "{base}/{infix}/{id}".format(base=BaseHelper.BASE_URL,
                                                      infix=link_infix,
                                                      id=record[link_suffix])
        return lecture

    def _get_parse_article_number_request(self, record, key):
        request = Request(record['url'], callback=self.parse_article_number)
        request.meta[key] = record
        return request
