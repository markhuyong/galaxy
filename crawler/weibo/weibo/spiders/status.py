# -*- coding: utf-8 -*-

import json
import sys
import re
import urllib

from dateutil.parser import parse as date_parse
from scrapy.http.cookies import CookieJar

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from w3lib.html import remove_tags

from scrapy import Request

from ..items import WeiboStatusItem

from ..utils import CommonSpider
from ..utils import BaseHelper

reload(sys)
sys.setdefaultencoding('utf8')


class WeiboStatusSpider(CommonSpider):
    name = "weibo_status"
    uid = 0
    total_page = 2000
    max_download_page = 3000
    containerid = 0
    done = False

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')  # nick_name
        if uid:
            self.uid = uid
            self.logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_m_weibo_home_url(uid)]

    def parse(self, response):
        if u"还没发过微博" in str(response):
            raise ValueError(u"TA还没发过微博")

        cookie_jar = response.meta.setdefault('cookiejar', CookieJar())
        cookie_jar.extract_cookies(response, response.request)
        cookies_str = str(response.headers['Set-Cookie'])
        if 'M_WEIBOCN_PARAMS' not in cookies_str:
            ValueError("parse cookie encounter error.")
        matches = re.findall(u'[^l]fid=(\d+)', urllib.unquote(cookies_str))
        if not matches:
            ValueError("get fid failed.")
        fid = matches[0]
        first_url = BaseHelper.get_m_weibo_status_url(self.uid,
                                                      fid)

        headers = BaseHelper.get_headers()
        request = Request(first_url,
                          headers=headers,
                          cookies=cookie_jar._cookies,
                          callback=self.parse_weibo_containerid)
        cookie_jar.add_cookie_header(request)  # apply Set-Cookie ourselves
        request.meta['cookiejar'] = response.meta['cookiejar']
        yield request

    def parse_weibo_containerid(self, response):
        body = json.loads(response.body)
        for tab in body['tabsInfo']['tabs']:
            if tab.get('tab_type') == "weibo":
                self.containerid = tab['containerid']
        if self.containerid == 0:
            ValueError("get weibo containerid failed.")

        first_url = BaseHelper.get_m_weibo_status_url(self.uid,
                                                      self.containerid)
        headers = BaseHelper.get_headers()
        request = Request(first_url,
                          headers=headers,
                          callback=self.parse_weibo)
        request.meta['cookiejar'] = response.meta['cookiejar']
        yield request

    def parse_weibo(self, response):

        body = json.loads(response.body)

        for card in filter(lambda c: c['card_type'] == 9, body['cards']):
            item = WeiboStatusItem()
            self.logger.debug("publishTime is {}".format(card['mblog']['created_at']))
            item['publishTime'] = date_parse(
                card['mblog']['created_at'], fuzzy_with_tokens=True)[0].isoformat()

            # parse text
            item['text'] = ''
            if 'raw_text' in card['mblog']:
                item['text'] = card['mblog']['raw_text']
            else:
                item['text'] = remove_tags(card['mblog']['text'])

            if 'retweeted_status' in card['mblog']:
                self.logger.debug('retweeted_status ====={}'.format(card['mblog']['retweeted_status']))
                screen_name = card['mblog']['retweeted_status']['user'][
                    'screen_name']
                text = remove_tags(card['mblog']['retweeted_status']['text'])
                retweeted = "@{}{}".format(screen_name, text)
                item['text'] += retweeted.replace(u"...全文", '')

            # parse pics
            item['pictures'] = []
            pics = []
            if 'retweeted_status' in card['mblog']:
                pics = card['mblog']['retweeted_status'].get('pics') or []

            else:
                pics = card['mblog'].get('pics') or []
            for pic in pics:
                p = {"url": pic['large']['url'],
                     "width": pic['large']['geo']['width'],
                     "height": pic['large']['geo']['height']
                     }
                item['pictures'] += [p]
            yield item

            next_page = body['cardlistInfo']['page']

            def has_next():
                return next_page and int(next_page) <= self.total_page and \
                       int(next_page) <= self.max_download_page

            if has_next():
                next_page_url = BaseHelper.get_m_weibo_status_url(self.uid,
                                                                  self.containerid,
                                                                  next_page)
                headers = BaseHelper.get_headers()
                request = Request(next_page_url,
                                  headers=headers,
                                  callback=self.parse_weibo)
                request.meta['cookiejar'] = response.meta['cookiejar']
                yield request
