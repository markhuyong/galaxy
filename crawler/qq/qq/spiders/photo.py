# -*- coding: utf-8 -*-

import sys
import json
import datetime
from dateutil.tz import tzlocal
from scrapy.http.request import Request

from crawler.qq.qq.items import PictureItem, QqStatusItem

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
            self.start_urls = [BaseHelper.get_album_url(uid)]

    def parse(self, response):
        self.logger.debug("{} {}".format("=" * 10, str(response.body)))
        try:
            body = json.loads(response.body)
        except ValueError, e:
            pass

        if body['code'] != 0:
            raise ValueError(body['message'])

        if 'vFeeds' not in body['data']:
            raise ValueError("user have no albums.")

        last_attach = body['data']['attach_info']
        remain_count = body['data']['remain_count']

        for feed in body['data']['vFeeds']:
            def is_valid():
                skip = "说说和日志相册" == feed['pic']['albumname'] or feed['pic'][
                                                                    'allow_access'] == 0
                return 'pic' in feed and not skip

            if is_valid():
                album_id = feed['pic']['albumid']
                photo_num = feed['pic']['albumnum']

                fetch_len = photo_num // self.fetch_size + 1
                last_fetch_size = photo_num % self.fetch_size
                for n in xrange(0, fetch_len):
                    already_fetch_num = n * self.fetch_size
                    fetch_batch_size = self.fetch_size if fetch_len - n > 0 \
                        else last_fetch_size
                    last_attach_temp = last_attach if n > 0 else None
                    photo_url = BaseHelper.get_photo_url(self.uid, album_id,
                                                         str(already_fetch_num),
                                                         str(fetch_batch_size),
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
            raise ValueError(body['message'])

        if 'photos' not in body['data']:
            raise ValueError("album have no photos.")

        photos_dict = body['data']['photos']
        for photos_key in body['data']['photos']:
            image_dict = {}
            ext_key = ''
            pre_time = 0L
            time_dict = {}

            photo_dict = photos_dict[photos_key]
            for photo in photo_dict:
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
                    if abs(cur_time - pre_time) <= 2:
                        if ext_key not in image_dict:
                            image_dict[ext_key] = [pic]
                            time_dict[ext_key] = photo['uUploadTime']
                        else:
                            image_dict[ext_key] += [pic]
                    else:
                        ext_key += ' '
                        image_dict[ext_key] = [pic]
                        time_dict[ext_key] = photo['uUploadTime']
                    pre_time = photo['uUploadTime']

            for key, value in image_dict.iteritems():
                status = QqStatusItem()
                status['publishTime'] = datetime.datetime.fromtimestamp(
                    time_dict.get(key, 0), tzlocal()).isoformat()
                status['text'] = key.strip()
                status['pictures'] = value
                self.logger.debug("status*======={}".format(status))
                if status['pictures'] or status['text']:
                    yield status
