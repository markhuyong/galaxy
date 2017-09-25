# -*- coding: utf-8 -*-

import json
import re
import sys
import urllib
from datetime import date, datetime, timedelta

from dateutil.parser import parse as date_parse
from scrapy.http.cookies import CookieJar
from scrapy.xlib.tx import ResponseFailed

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from w3lib.html import remove_tags

from scrapy import Request
from crawler.misc.spider import CommonSpider
from ..items import WeiboStatusItem

from ..utils import BaseHelper

reload(sys)
sys.setdefaultencoding('utf8')


class WeiboStatusSpider(CommonSpider):
    name = "weibo_status"
    uid = 0
    total_page = 20000
    max_download_page = 300000
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
        cookies_str = str(response.headers.get('Set-Cookie'))
        if 'M_WEIBOCN_PARAMS' not in cookies_str:
            ValueError("parse cookie encounter error.")
        matches = re.findall(u'[^l]fid=(\d+)', urllib.unquote(cookies_str))
        if not matches:
            ValueError("get fid failed.")
        fid = matches[0]
        first_url = BaseHelper.get_m_weibo_status_url(self.uid,
                                                      fid)
        temp = cookie_jar._cookies.get('.weibo.cn', {}).get('/')
        cookies = {c.name: c.value for c in temp.values()}
        headers = BaseHelper.get_status_headers(self.uid)
        request = Request(first_url,
                          headers=headers,
                          cookies=cookies,
                          callback=self.parse_weibo_containerid)
        cookie_jar.add_cookie_header(request)  # apply Set-Cookie ourselves
        request.meta['cookiejar'] = response.meta['cookiejar']
        yield request

    def parse_weibo_containerid(self, response):
        body = json.loads(response.body)
        tabs = body['tabsInfo'].get('tabs')

        if isinstance(tabs, dict):
            for tab in tabs.itervalues():
                if tab.get('tab_type') == u"weibo":
                    self.containerid = tab['containerid']
                    break
        elif isinstance(tabs, list):
            for tab in tabs:
                if tab.get('tab_type') == u"weibo":
                    self.containerid = tab['containerid']
                    break
        else:
            pass

        if self.containerid == 0:
            ValueError("get weibo containerid failed.")

        first_url = BaseHelper.get_m_weibo_status_url(self.uid,
                                                      self.containerid)
        headers = BaseHelper.get_status_headers(self.uid)
        request = Request(first_url,
                          headers=headers,
                          callback=self.parse_weibo)
        request.meta['cookiejar'] = response.meta['cookiejar']
        yield request

    def parse_weibo(self, response):
        try:
            body = json.loads(response.body)
        except ValueError:
            raise ResponseFailed("Response is not json format.")

        # self.logger.debug("body======{}".format(body))

        for card in filter(lambda c: c['card_type'] == 9, body['cards']):
            mid = card['mblog']['mid']
            status_url = BaseHelper.get_m_weibo_single_status(self.containerid,
                                                              mid)
            headers = BaseHelper.get_status_headers(self.uid)
            request = Request(status_url,
                              headers=headers,
                              callback=self.parse_weibo_status)
            yield request

            next_page = body['cardlistInfo']['page']

            def has_next():
                return next_page and int(next_page) <= self.total_page and \
                       int(next_page) <= self.max_download_page

            if has_next():
                next_page_url = BaseHelper.get_m_weibo_status_url(self.uid,
                                                                  self.containerid,
                                                                  next_page)
                headers = BaseHelper.get_status_headers(self.uid)
                request = Request(next_page_url,
                                  headers=headers,
                                  callback=self.parse_weibo)
                request.meta['cookiejar'] = response.meta['cookiejar']
                yield request

    def parse_weibo_status(self, response):
        STATUS_REGEXP = "var \$render_data = \[(\{.*\})\]\[0\]"

        body_str = str(response.body)
        matcher = re.findall(STATUS_REGEXP, body_str, re.S)

        if matcher:
            try:
                s = str(matcher.pop())
                # self.logger.debug("the STATUS_REGEXP matcher string is {}".format(s))
                card = json.loads(s)
                yield self._get_item(card)
            except ValueError:
                raise ResponseFailed("Response card matcher is not json format.")

    def _get_item(self, card):
        item = WeiboStatusItem()
        self.logger.debug("publishTime is {}".format(card['status']['created_at']))
        item['publishTime'] = date_parse(
            self._parse_publish_time(card['status']['created_at']), fuzzy_with_tokens=True)[0].isoformat()

        # parse text
        item['text'] = ''

        if not card['status'].get('isLongText'):
            if 'raw_text' in card['status']:
                item['text'] = card['status']['raw_text']
            else:
                item['text'] = remove_tags(card['status']['text'])
        else:
            item['text'] = self._get_long_text(card['status']['id'])

        if 'retweeted_status' in card['status']:
            isLongText = card['status']['retweeted_status'].get('isLongText')
            self.logger.debug('retweeted_status ====={}'.format(card['status']['retweeted_status']))
            user = card['status']['retweeted_status'].get('user')
            if user:
                screen_name = card['status']['retweeted_status']['user'][
                    'screen_name']
                item['text'] += "@{}".format(screen_name)

            if not isLongText:
                text = remove_tags(card['status']['retweeted_status']['text'])
                item['text'] += text
            else:
                item['text'] += self._get_long_text(card['status']['retweeted_status']['id'])

        # parse pics
        item['pictures'] = []
        pics = []
        if 'retweeted_status' in card['status']:
            pics = card['status']['retweeted_status'].get('pics') or []

        else:
            pics = card['status'].get('pics') or []
        for pic in pics:
            geo = pic['large']['geo']
            if geo:
                p = {"url": pic['large']['url'],
                     "width": pic['large']['geo']['width'],
                     "height": pic['large']['geo']['height']
                     }
            else:
                size = pic['large']['size']
                if size == "large":
                    p = {"url": pic['large']['url'],
                         "width": 360,
                         "height": 360
                         }
                else:
                    p = {"url": pic['large']['url'],
                         "width": 180,
                         "height": 180
                         }
            item['pictures'] += [p]
            return item

    def _get_long_text(self, text_id):
        import requests
        try:
            session = requests.Session()
            url = BaseHelper.get_m_weibo_long_text(text_id)
            body = session.get(url).content
            status = json.loads(body)
            return remove_tags(status.get('longTextContent'))
        except Exception, e:
            return ''

    def _parse_publish_time(self, time_str):
        pattern = re.compile(u'(\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return match

        pattern = re.compile(u'(\d{1,2}月\d{1,2}日 \d{1,2}:\d{1,2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(date.today().year) + '-' + match.replace(u'月', '-') \
                .replace(u'日', '')

        pattern = re.compile(u'今天.*(\d{1,2}:\d{1,2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(date.today()) + ' ' + match

        pattern = re.compile(u'(\d{1,2}).*分钟前')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return (datetime.now() - timedelta(minutes=int(match))).strftime("%Y-%m-%d %H:%M:%S")
        return time_str
