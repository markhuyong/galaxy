# -*- coding: utf-8 -*-

import random
import json
import logging
import re
import itertools
import threading

import scrapy
from scrapy import Selector
from scrapy.http.cookies import CookieJar
from scrapy.linkextractors import LinkExtractor

from scrapy.conf import settings
from scrapy.http.request import Request
from scrapy.http.headers import Headers

from ..items import LecturesItem
from ..utils import CommonSpider
from ..utils import BaseHelper

logger = logging.getLogger(__name__)



#class DmozSpider(scrapy.Spider):
class DmozSpider(CommonSpider):
    name = "jian"
    page_size = 10
    cur_page = 1
    flag_end = False

    # start_urls = [
    #     "http://www.jianshu.com/u/d232755b98c2",
    # ]


    # def parse(self, response):
    #     print ("parse == {}")

    # def parse_entry(self, response):
    #     print ("parse_entry == {}")

    def parse_start_url(self, response):
        print("next_link == {}")

    def parse(self, response):
        print("parse_start_url == {}".format(response.request.url))
        uid = str(response.request.url.split('/')[-1])
        cookie_jar = response.meta.setdefault('cookiejar', CookieJar())
        cookie_jar.extract_cookies(response, response.request)
        cookies_test = cookie_jar._cookies
        print "cookies -============ test:", cookies_test

        next_link = BaseHelper.LECTURES_URL.format(uid=uid)
        log.info("next_link == {}".format(next_link))

        headers = BaseHelper.get_headers()

        item = LecturesItem()
        res = Selector(response)
        titles = res.css('title::text').re(ur'(\w+)') or ['']
        item['author_name'] = titles[0]
        item['url'] = response.request.url
        lectures = []
        specials = []
        # request = Request(next_link, callback=self.parse_lecture_json, headers=headers,
        #                   meta={'dont_merge_cookies': True, 'cookiejar': cookie_jar}, cookies=cookies_test)
        request = Request(next_link, callback=self.parse_lecture_json, headers=headers)

        # request = Request(another_link, callback=self.parse_lecture_json)
        cookie_jar.add_cookie_header(request)  # apply Set-Cookie ourselves
        request.meta['item'] = item
        print "request.cookies========{}".format(request.cookies)
        print "request.headers========{}".format(request.headers)
        yield request

        yield item
        # print(lectures)
        # item['lectures'] = lectures
        # item['specials'] = specials
        # yield item
        # yield Request(another_link, callback=self.parse_lecture_test, headers=headers,
        #                 cookies=cookies_test)

    def parse_lecture_json(self, response):
        print "response=====json====".format(response)
        body = json.loads(response.body)
        lectures = []
        # specials = []
        item = response.request.meta['item']
        for notebook in body['notebooks']:
            print notebook
            lecture = dict()
            lecture['author_name'] = item['author_name']
            lecture['name'] = notebook['name']
            link = lecture['url'] = "{base}/nb/{id}".format(base=BaseHelper.BASE_URL, id=notebook['id'])
            # link = "{base}/nb/{id}".format(base=BaseHelper.BASE_URL, id=notebook['id'])
            # links += [link]
            # callback = functools.partial(self.parse_lecture_number, lecture)
            request = Request(link, callback=self.parse_lecture_number)
            request.meta['lecture'] = lecture
            yield request

            lectures += [lecture]

        print("lectures=========={}".format(lectures))

        item['lectures'] = lectures

        # return item

        # yield item


        # for spec in body['own_collections']:
        #     special = LectureItem()
        #     special['author_name'] = item['author_name']
        #     special['name'] = spec['name']
        #     link = special['url'] = "{base}/c/{slug}".format(base=BaseHelper.BASE_URL, slug=spec['slug'])
        #     callback = functools.partial(self.parse_lecture_number, special)
        #     request = Request(link, callback=callback)
        #     # request.meta['special'] = special
        #     yield request
        #
        #     specials += [special]



        # for link in links:
        #     request = Request(link, callback=self.parse_lecture_number)
        #     request.meta['item'] = item
        #     yield request

    def start_requests_(self):

        headers = Headers({
            'User-Agent': str(random.choice(self.user_agent_list)),
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "text/html",
            # 'Content-Type': 'application/json',
            # 'Accept': 'application/json'
        })
        print "===== {}".format(headers)
        BaseHelper.BASE_URL
        if self.cur_page <= self.page_size:
            yield Request(self.start_urls.format(self.cur_page), self.parse, headers=headers)
            self.cur_page += 1

    def parse_lecture_number(self, response):

        print "heheheheheheheh***********test*************"

        lecture = response.request.meta['lecture']
        res = Selector(response)
        numbers = res.css('div.info::text').re(ur'([0-9]+)') or [0]
        lecture['article_number'] = numbers[0]
        # return lecture


    def parse_lecture_list(self, response):

        cookie_jar = response.meta.setdefault('cookie_jar', CookieJar())
        cookie_jar.extract_cookies(response, response.request)
        # print response.body
        res = Selector(response)
        rows = res.css('ul.note-list li')

        for row in rows:
            item = LecturesItem()
            t = row.css('a.title')
            item['text'] = t.css('::text').extract_first()
            item['url'] = t.css('::attr(href)').extract_first()

            yield item

    def parse_(self, response):

        cookie_jar = response.meta.setdefault('cookie_jar', CookieJar())
        cookie_jar.extract_cookies(response, response.request)
        # print response.body
        res = Selector(response)
        rows = res.css('ul.note-list li')

        for row in rows:
            item = LecturesItem()
            t = row.css('a.title')
            item['text'] = t.css('::text').extract_first()
            item['url'] = t.css('::attr(href)').extract_first()

            yield item

        # for next_page in self.start_requests_():
        #     yield next_page
            # headers = Headers({
            #     'User-Agent': str(random.choice(self.user_agent_list)),
            #     "X-Requested-With": "XMLHttpRequest",
            #     "Accept": "text/html",
            #     # 'Content-Type': 'application/json',
            #     # 'Accept': 'application/json'
            # })
            #
            #
            # print "===== {}".format(headers)
            # if (not self.flag_end) and self.cur_page <= self.page_size:
            #     req = Request(self.start_urls.format(self.cur_page), self.parse, headers=headers)
            #     print "===== {}".format(req.url)
            #     yield req
            #     self.cur_page += 1

            # next_page = self.start_urls.format(self.count.next())
