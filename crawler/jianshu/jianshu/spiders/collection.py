# -*- coding: utf-8 -*-

import json
from dateutil import parser

from scrapy import Selector
from scrapy.http.cookies import CookieJar

from scrapy.http.request import Request

from ..items import CollectionItem
from ..utils import CommonSpider
from ..utils import BaseHelper


class CollectionSpider(CommonSpider):
    name = "jianshu_collection"

    page = 1
    count = 10
    done = False
    max_page = 3000

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')
        if uid:
            self.logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_collection_url(uid)]

    def parse(self, response):
        sel = Selector(response)
        follow_button = '//div[@class="follow-button"]/@props-data-collection-id'
        notebook_button = '//div[@class="follow-button"]/@props-data-notebook-id'
        script_collection = '//script[@data-name="collection"]/text()'
        cid = sel.xpath(follow_button).extract_first() or sel.xpath(
            notebook_button).extract_first() or sel.xpath(
            script_collection).re_first('"id":(\d+)')
        if not cid:
            raise ValueError('no collection articles, collection id is None.')
        while not self.done:
            cookie_jar = response.meta.setdefault('cookiejar', CookieJar())
            cookie_jar.extract_cookies(response, response.request)
            if "/c/" in response.url:
                collection_url = BaseHelper.get_collection_articles_url(cid,
                                                                        self.page,
                                                                        self.count)
            elif "/nb/" in response.url:
                collection_url = BaseHelper.get_notebooks_articles_url(cid,
                                                                       self.page,
                                                                       self.count)
            request = Request(collection_url,
                              headers=BaseHelper.get_headers_json(),
                              callback=self.parse_collection)
            cookie_jar.add_cookie_header(request)  # apply Set-Cookie ourselves
            request.meta['cookiejar'] = cookie_jar
            yield request
            self.page += 1

    def parse_collection(self, response):
        rows = json.loads(response.body)
        self.logger.debug("row==========={}".format(rows))
        for row in rows:
            item = CollectionItem()
            item['title'] = row['title']
            item['url'] = "/p/{}".format(row['slug'])
            item['publishTime'] = row['first_shared_at']
            item['articleRead'] = row['views_count']
            item['articleComment'] = row['public_comments_count']
            item['articleLike'] = row['likes_count']
            item['reward'] = row['total_rewards_count']

            article_url = BaseHelper.BASE + item['url']
            self.logger.debug("article_url==========={}".format(article_url))
            request = Request(article_url, callback=self.parse_article)
            request.meta['cookiejar'] = response.meta['cookiejar']
            request.meta['item'] = item
            yield request
        if len(rows) == 0:
            self.done = True

    def parse_article(self, response):
        item = response.request.meta['item']
        res = Selector(response)
        self.logger.debug("res.css('.show-content')=========={}".format(
            res.css('.show-content')))
        item['content'] = res.css('.show-content').extract_first()
        item['wordCount'] = res.css('.wordage').re_first(ur'(\d+)') or 0
        yield item
