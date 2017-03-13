# -*- coding: utf-8 -*-

import logging

from scrapy import Selector
from scrapy.exceptions import CloseSpider
from scrapy.http.cookies import CookieJar

from scrapy.http.request import Request

from ..items import CollectionItem
from ..utils import CommonSpider
from ..utils import BaseHelper

logger = logging.getLogger(__name__)


class CollectionSpider(CommonSpider):
    name = "jianshu_collection"

    page = 1
    max_page = 3

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')
        if uid:
            self.logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_collection_url(uid)]

    def parse(self, response):
        res = Selector(response)
        note_list = res.css('ul.note-list')
        if len(note_list) <= 0 and self.page == 1:
            raise CloseSpider('no collection articles.')

        next_page_suffix = note_list.css(
            '::attr(infinite-scroll-url)').extract_first()

        logger.debug("next_page_suffix==========={}".format(next_page_suffix))
        cookie_jar = response.meta.setdefault('cookiejar', CookieJar())
        cookie_jar.extract_cookies(response, response.request)

        rows = note_list.css('li')

        for row in rows:
            item = CollectionItem()
            t = row.css('a.title')
            item['title'] = t.css('::text').extract_first()
            item['url'] = t.css('::attr(href)').extract_first()
            item['publishTime'] = row.css(
                '.name .time::attr(data-shared-at)').extract_first()
            meta = row.css('.content .meta')
            item['articleRead'] = meta.css(
                ':nth-child(1)::text').re_first(ur'(\d+)') or 0
            item['articleComment'] = meta.css(
                ':nth-child(2)::text').re_first(ur'(\d+)') or 0
            item['articleLike'] = meta.css(
                ':nth-child(3)::text').re_first(ur'(\d+)') or 0
            item['reward'] = meta.css(
                ':nth-child(4)::text').re_first(ur'(\d+)') or 0
            article_url = BaseHelper.BASE_URL + item['url']
            logger.debug("article_url==========={}".format(article_url))
            request = Request(article_url, callback=self.parse_article)
            cookie_jar.add_cookie_header(request)  # apply Set-Cookie ourselves
            request.meta['item'] = item
            yield request

            yield item

        self.page += 1
        if self.page > self.max_page:
            raise CloseSpider('collection articles reach max limit.')

        if len(rows) > 0 and next_page_suffix:
            next_page = BaseHelper.BASE_URL + next_page_suffix \
                        + "&page={}".format(self.page)
            logger.debug("next_page==========={}".format(next_page))
            request = Request(next_page)
            cookie_jar.add_cookie_header(request)  # apply Set-Cookie ourselves
            yield request

    def parse_article(self, response):

        # print response.body
        item = response.request.meta['item']
        res = Selector(response)
        logger.debug("res.css('.show-content')=========={}".format(
            res.css('.show-content')))
        item['content'] = res.css('.show-content').extract_first()
        item['wordCount'] = res.css('.wordage').re_first(ur'(\d+)') or 0
