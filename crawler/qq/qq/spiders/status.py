# -*- coding: utf-8 -*-

import sys
from scrapy.http.request import Request
import json
import datetime
from ..items import QqStatusItem

from ..utils import CommonSpider
from ..utils import BaseHelper

reload(sys)
sys.setdefaultencoding('utf8')


class QqStatusSpider(CommonSpider):
    name = "qq_user_status"

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')
        # uid = 646055372
        if uid:
            self.logger.debug("uid = {}".format(uid))
            self.start_urls = [BaseHelper.get_shuoshuo_url(uid)]

    def parse(self, response):
        body = json.loads(response.body)

        self.logger.debug("body======={}".format(body))
        if body['code'] != 0:
            raise ValueError("have no photos or your have no right to access.")

        last_attach = body['data']['attach_info']
        remain_count = body['data']['remain_count']
        if remain_count > 0:
            next_page = BaseHelper.get_shuoshuo_url(self.uid, last_attach)
            yield Request(next_page)

        # get user text and photos
        for feed in body['data']['vFeeds']:
            item = QqStatusItem()
            item['publishTime'] = datetime.datetime.fromtimestamp(feed['comm']['time']).strftime('%Y-%m-%d %H:%M:%S')
            item['text'] = feed['operation']['share_info']['summary']

            # get photo urls
            if 'pic' in feed:
                pictures = []
                for picdata in feed['pic']['picdata']['pic']:
                    photo_url = picdata['photourl']
                    cursor = None
                    if '0' in photo_url:
                        cursor = photo_url['0']
                    elif '1' in photo_url:
                        cursor = photo_url['1']
                    elif '11' in photo_url:
                        cursor = photo_url['11']
                    else:
                        pass
                    if cursor is not None:
                        url = cursor['url'].split('&', 1)[0]
                        width = cursor['width']
                        height = cursor['height']

                        pictures += [{
                            "url": url,
                            "width": width,
                            "height": height
                        }]

                        item['pictures'] = pictures

            self.logger.debug("item*======={}".format(item))
            # if len(item['pictures']) and item['text'] == '':
            #     ValueError("Parse item encounter errors.")
            # else:
            #     yield item
            if 'pictures' in item and len(item['pictures']) > 0 or len(item['text']) > 0:
                yield item
