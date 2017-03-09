# -*- coding: utf-8 -*-

import logging
import sys
import re
from datetime import date, datetime, timedelta

from scrapy import Request
from scrapy import Selector

from ..items import WeiboStatusItem

from ..utils import CommonSpider
from ..utils import BaseHelper

logger = logging.getLogger(__name__)

reload(sys)
sys.setdefaultencoding('utf8')


class WeiboStatusSpider(CommonSpider):
    name = "weibo_status"
    uid = 0
    total_page = 0
    max_download_page = 1

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')  # nick_name
        if uid:
            self.uid = uid
            self.logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_weibo_status_url(uid)]

    def parse(self, response):
        # if u"他还没发过微博" in response or u"她还没发过微博":
        #     return

        res = Selector(response)
        weibo_status = res.css('.c[id^=M_]')
        if self.total_page == 0:
            self.total_page = res.css('#pagelist').css(
                'input[name=mp]::attr(value)').extract_first()

        next_page_flag = u"下页" in res.css('#pagelist').css(
            'div a::text').extract_first()
        next_page_num = res.css('#pagelist').css(
            'div a::attr(href)').re_first(u'page=(\d+)')

        for weibo in weibo_status:
            item = WeiboStatusItem()
            item['published_at'] = self._parse_weibo_published_at(
                weibo.css('.ct').extract_first())
            item['text'] = self._parse_weibo_text(weibo)
            item['pictures'] = []  # self._parse_weibo_images(weibo)
            yield item

        if next_page_flag and next_page_num <= self.max_download_page:
            next_page = BaseHelper.get_weibo_status_url(self.uid, next_page_num)
            yield Request(url=next_page)

    def _parse_weibo_published_at(self, time_str):
        pattern = re.compile(u'(\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return match

        pattern = re.compile(u'(\d{1,2}月\d{1,2}日 \d{2}:\d{2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(date.today().year) + '-' + match.replace(u'月', '-') \
                .replace(u'日', '')

        pattern = re.compile(u'今天 (\d{2}:\d{2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(date.today()) + ' ' + match

        pattern = re.compile(u'(\d{2})分钟前')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(
                (datetime.now() - timedelta(minutes=int(match))).strftime(
                    "%Y-%m-%d %H:%M:%S"))

    def _parse_weibo_text(self, weibo_css):
        text_span = weibo_css.css('.ctt')
        tag = weibo_css.css('div a[href^="/comment/"]').extract_first()

        tag_text = ""
        tag_key = "tag_key"

        if tag:
            self._get_tag_text_request("http://weibo.cn" + tag, tag_key,
                                       tag_text)
        weibo_src_text = tag_text if tag \
            else weibo_css.css('span.ctt::text').extract_first()

        forward_from = ""
        forward_reason = ""
        comment_list = weibo_css.css('.cmt')
        for cm in comment_list:
            cm_text = cm.css('::text').extract_first()
            if u"转发了" in cm_text:
                forward_from = cm_text
            elif u"转发理由:" in cm_text:
                forward_reason = weibo_css.css('div::text').re_first(
                    u'转发理由:(.*) 赞[\d+]')

        return forward_reason + forward_from + weibo_src_text

    def _get_tag_text_request(self, url, key, text):
        request = Request(url, callback=self.parse_all_text)
        request.meta[key] = text
        return request

    def parse_all_text(self, response, key):
        response.request.meta[key] = response.css(
            '.c[id^=M_].ctt::text').extract_first()

        # def _parse_weibo_images(self, weibo_css):
        #     text_span = weibo_css.css('.ctt')
        #     pictures = []
        #     view_all_pics = weibo_css.css(
        #         'div a[href^="http://weibo.cn/mblog/picAll/"]::attr(href)')\
        #         .extract_first()
        #     if view_all_pics:
        #         self._get_weibo_image_request(view_all_pics)
        #     else:
        #         thumb = weibo_css.css('.ib a::attr(href)').extract_first()
        #         if thumb:
        #             singel_url = self._translate_thumb_to_large_url(thumb)
        #             pictures = [self._get_weibo_single_image_request(singel_url, 'picture')]
        #     return pictures
        #
        # def _get_weibo_image_request(self, url, key, text):
        #     request = Request(url, callback=self.parse_weibo_image)
        #     request.meta[key] = text
        #     return request
        #
        # def parse_weibo_image(self, response, key):
        #     response.request.meta[key] = response.css('.c[id^=M_].ctt::text').extract_first()
        #
        # def _get_weibo_single_image_request(self, url, key, text):
        #     request = Request(url, callback=self.parse_weibo_single_image())
        #     request.meta[key] = text
        #     return request
        #
        # def parse_weibo_single_image(self, response, key):
        #     response.request.meta[key] = response.css(
        #         '.c[id^=M_].ctt::text').extract_first()
        #
        # def _translate_thumb_to_large_url(self, thumb_url):
        #     return thumb_url.replace("^http://ss", "http://ww") \
        #         .replace("&690$", ".jpg") \
        #         .replace("/thumb180/", "/large/") \
        #         .replace("/wap180/", "/large/")
