# -*- coding: utf-8 -*-

import logging
import sys
import re
from datetime import date, datetime, timedelta

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from PIL import Image
from w3lib.html import remove_tags

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
    total_page = 3
    max_download_page = 3000

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')  # nick_name
        if uid:
            self.uid = uid
            self.logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_weibo_status_url(uid)]

    def parse(self, response):
        if u"还没发过微博" in str(response):
            raise ValueError(u"TA还没发过微博")

        res = Selector(response)
        weibo_status = res.css('.c[id^=M_]')
        if self.total_page == 0:
            self.total_page = int(res.css('#pagelist').css(
                'input[name=mp]::attr(value)').extract_first("0"))

        next_page_flag = True if u"下页" in res.css('#pagelist').css(
            'div a::text').extract_first("") else False
        num_extractor = res.css('#pagelist').css(
            'div a::attr(href)').re_first(u'page=(\d+)')
        next_page_num = int(num_extractor) if num_extractor else 0

        for weibo in weibo_status:
            item = WeiboStatusItem()

            # parse published_at
            item['publishTime'] = self._parse_weibo_published_at(
                weibo.css('.ct').extract_first())

            item['pictures'] = []
            # parse text

            forward_from = remove_tags(weibo
                                       .xpath('//div/span[@class="cmt"]')
                                       .extract_first(""))
            forward_reason = weibo \
                .xpath('//div/span[@class="ct"]/../text()') \
                .extract_first("")
            item['text'] = forward_reason + forward_from

            has_pics = weibo.css(
                'div a[href^="http://weibo.cn/mblog/picAll/"]::attr(href)') \
                .extract_first()
            # 有原图
            has_orig_pic = weibo.css('img.ib::attr(src)').extract_first()

            # 有引文
            has_orig_text = weibo.css('div a[href^="/comment/"]::attr(href)') \
                .extract_first()
            if not has_orig_text:
                src_text = remove_tags(
                    weibo.css('span.ctt').extract_first(""))
                item['text'] += src_text
                if not has_pics:
                    # 没有多图
                    if not has_orig_pic:
                        # 没有图片
                        yield item
                    else:
                        # 有图片
                        singel_url = self._translate_thumb_to_large_url(
                            has_orig_pic)
                        request = Request(singel_url,
                                          callback=self.parse_weibo_image_src)
                        request.meta['item'] = item
                        request.meta['pics_count'] = 1
                        yield request
                else:
                    # 多图
                    request = Request(has_pics,
                                      callback=self.parse_weibo_image)
                    request.meta['item'] = item
                    yield request
            else:
                request = Request("http://weibo.cn{}".format(has_orig_text),
                                  callback=self.parse_orig_text)
                request.meta['item'] = item
                yield request

        def has_next():
            return next_page_flag and next_page_num <= self.total_page and \
                   next_page_num <= self.max_download_page

        if has_next():
            next_page = BaseHelper.get_weibo_status_url(self.uid,
                                                        next_page_num)
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
                .replace(u'日', '') + ":00"

        pattern = re.compile(u'今天 (\d{2}:\d{2})')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(date.today()) + ' ' + match + ":00"

        pattern = re.compile(u'(\d{2})分钟前')
        matches_list = pattern.findall(time_str)
        for match in matches_list:
            return str(
                (datetime.now() - timedelta(minutes=int(match))).strftime(
                    "%Y-%m-%d %H:%M:%S"))

    def _parse_weibo_text(self, weibo_css):
        forward_from = ""
        forward_reason = ""
        comment_list = weibo_css.css('.cmt')
        for cm in comment_list:
            cm_text = cm.css('::text').extract_first()
            if u"转发了" in cm_text:
                forward_from = remove_tags(weibo_css
                                           .xpath('//div/span[@class="cmt"]')
                                           .extract_first(""))
            elif u"转发理由:" in cm_text:
                forward_reason = weibo_css \
                    .xpath('//div/span[@class="ct"]/../text()') \
                    .extract_first("")

        return forward_reason + forward_from

    def parse_all_text(self, response):
        item = response.request.meta['item']
        comments = response.xpath(
            '//div/div/span[@class="ctt"]/..').extract_first("")
        item['text'] += remove_tags(comments)
        yield item

    def parse_orig_text(self, response):
        item = response.request.meta['item']
        weibos = response.css('.c[id^=M_]')
        weibo = weibos[0] if weibos else None
        if weibo:
            has_pics = weibo.css(
                'div a[href^="/mblog/picAll/"]::attr(href)') \
                .extract_first()
            has_orig_pic = weibo.css('.ib a::attr(href)').extract_first()
            item['text'] += remove_tags(
                weibo.css('span.ctt').extract_first())
            if not has_pics:
                # 没有多图
                if not has_orig_pic:
                    # 没有图片
                    yield item
                else:
                    # 有图片
                    singel_url = self._translate_thumb_to_large_url(
                        has_orig_pic)
                    request = Request(singel_url,
                                      callback=self.parse_weibo_image_src)
                    request.meta['item'] = item
                    request.meta['pics_count'] = 1
                    yield request
            else:
                # 多图
                request = Request("http://weibo.cn{}".format(has_pics),
                                  callback=self.parse_weibo_image)
                request.meta['item'] = item
                yield request

    def _get_weibo_image_request(self, url, key, text):
        request = Request(url, callback=self.parse_weibo_image)
        request.meta[key] = text
        return request

    def parse_weibo_image(self, response):
        item = response.request.meta['item']
        urls = response.css(
            '.c a img::attr(src)').extract()
        count = len(urls)
        for url in urls:
            request = Request(self._translate_thumb_to_large_url(url),
                              callback=self.parse_weibo_image_src)
            request.meta['item'] = item
            request.meta['pics_count'] = count
            yield request

    def parse_weibo_image_src(self, response):
        item = response.request.meta['item']
        count = response.request.meta['pics_count']
        orig_image = Image.open(BytesIO(response.body))

        width, height = orig_image.size
        pic = {
            "url": response.request.url,
            "width": width,
            "height": height

        }
        item['pictures'] += [pic]
        if count == len(item['pictures']):
            yield item

    def _translate_thumb_to_large_url(self, thumb_url):
        return thumb_url.replace("^http://ss", "http://ww") \
            .replace("&690$", ".jpg") \
            .replace("/thumb180/", "/large/") \
            .replace("/wap180/", "/large/")
