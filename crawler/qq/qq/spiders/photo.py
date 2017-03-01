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
from ..profile_items import QQProfileItem

from ..utils import CommonSpider
from ..utils import BaseHelper

reload(sys)
sys.setdefaultencoding('utf8')


class QqPhotoSpider(CommonSpider):
    name = "qq_photo"

    COUNT_REGEXP = "\"count\":\s*{[^}]*}{1}"
    PROFILE_REGEXP = "\"profile\":\s*{[^}]*}{1}"

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')
        if uid:
            self.logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_photo_url(uid)]

    def parse(self, response):
        # self.logger.debug("response.body======={}".format(response.body))
        # if "nav_bar_me" in response.body:
        #     self.logger.debug("Login successful")
        # else:
        #     self.logger.debug("Login failed")
        body = json.loads(response.body)

        if body['code'] != 0:
            raise "fetch error"

        last_attach = body['data']['attach_info']
        remain_count = body['data']['remain_count']

        # get user text and photos


        yield body