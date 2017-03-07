# -*- coding: utf-8 -*-

import sys
import datetime
import requests
import re
from lxml import etree
from scrapy import Selector
from scrapy.http.cookies import CookieJar
from scrapy.linkextractors import LinkExtractor

from scrapy.conf import settings
from scrapy.http.request import Request
import json

from crawler.qq.qq.items import PictureItem, QqStatusItem
from ..profile_items import QQProfileItem

from ..utils import CommonSpider
from ..utils import BaseHelper

reload(sys)
sys.setdefaultencoding('utf8')


class QqPhotoSpider(CommonSpider):
    name = "qq_photo_status"
    fetch_size = 200
    uid = 0

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')
        if uid:
            self.logger.debug("uid item = {}".format(uid))
            self.uid = uid
            self.start_urls = [BaseHelper.get_photo_url(uid)]

    def parse(self, response):
        try:
            body = json.loads(response.body)
        except ValueError, e:
            pass

        if body['code'] != 0:
            raise "fetch error"

        last_attach = body['data']['attach_info']
        remain_count = body['data']['remain_count']

        for feed in body['data']['vFeeds']:
            if 'pic' in feed and not "说说和日志相册" == feed['pic']['albumname']:
                album_id = feed['pic']['albumid']
                photo_num = feed['pic']['albumnum']

                fetch_len = photo_num // self.fetch_size
                last_fetch_size = photo_num % self.fetch_size
                for n in xrange(0, photo_num // self.fetch_size):
                    already_fetch_num = n * self.fetch_size
                    fetch_batch_size = self.fetch_size if fetch_len - n > 0 \
                        else last_fetch_size
                    last_attach_temp = last_attach if n > 0 else None
                    photo_url = BaseHelper.get_photo_url(self.uid, album_id,
                                                         already_fetch_num,
                                                         fetch_batch_size,
                                                         last_attach_temp)
                    yield Request(photo_url, self.parse_photo)

                if remain_count > 0:
                    next_page = BaseHelper.get_album_url(self.uid, last_attach)
                    yield Request(next_page)

    def parse_photo(self, response):

        try:
            body = json.loads(response.body)
        except ValueError, e:
            pass

        if body['code'] != 0:
            raise "fetch error"

        photos_dict = body['data']['photos']
        for photos_key in body['data']['photos']:
            image_dict = {}
            ext_key = 'extra'
            pre_time = 0L
            time_dict = {}

            photo_dict = photos_dict[photos_key]
            for photo in photo_dict:
                print photo
                desc = photo['desc']
                pic = PictureItem()
                pic['url'] = photo['1']['url']
                pic['width'] = photo['1']['width']
                pic['height'] = photo['1']['height']

                if not '' == desc:
                    if desc not in image_dict:
                        image_dict[desc] = [pic]
                        time_dict[desc] = photo['uUploadTime']
                    else:
                        image_dict[desc] += [pic]
                else:
                    cur_time = photo['uUploadTime']
                    if abs(cur_time - pre_time) >= 2:
                        if ext_key not in image_dict:
                            image_dict[ext_key] = [pic]
                            time_dict[ext_key] = photo['uUploadTime']
                        else:
                            image_dict[ext_key] += [pic]
                    else:
                        # ext_key += " "
                        image_dict[ext_key] += [pic]
                        time_dict[ext_key] = photo['uUploadTime']
                pre_time = photo['uUploadTime']

            for key, value in image_dict.iteritems():
                status = QqStatusItem()
                status['published_at'] = time_dict.get(key, 0) * 1000
                status['text'] = ' ' if key == 'extra' else key.strip()
                status['pictures'] = value
                yield status
