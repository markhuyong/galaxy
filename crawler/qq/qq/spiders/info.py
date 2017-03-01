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


class QqInfoSpider(CommonSpider):
    name = "qq_info"

    COUNT_REGEXP = "\"count\":\s*{[^}]*}{1}"
    PROFILE_REGEXP = "\"profile\":\s*{[^}]*}{1}"

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')
        if uid:
            self.logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_profile_url(uid)]

    def parse(self, response):
        # self.logger.debug("response.body======={}".format(response.body))
        # if "nav_bar_me" in response.body:
        #     self.logger.debug("Login successful")
        # else:
        #     self.logger.debug("Login failed")


        yield self.parse_profile(str(response.body))


        print(response.body)

    def parse_profile(self, body):
        matcher = re.findall(self.COUNT_REGEXP, body)
        if matcher:
            s = str(matcher.pop())
            self.logger.debug("the matcher string is {}".format(s))
            prefix = "\"count\":"
            s = s[len(prefix):len(s)]
            json_obj = json.loads(s)
            item = QQProfileItem()
            item['blog'] = json_obj['blog']
            item['message'] = json_obj['message']
            item['pic'] = json_obj['pic']
            item['shuoshuo'] = json_obj['shuoshuo']
            self.logger.debug("json item = {}".format(item))

        # matcher = re.findall(self.PROFILE_REGEXP, body)
        # if matcher:
        #     s = str(matcher.pop())
        #     self.logger.debug("the matcher string is {}".format(s))
        #     prefix = "\"profile\":"
        #     s = s[len(prefix):len(s)]
        #     json_obj = json.loads(s)
        #     item = QQProfileItem()
        #     item['nickname'] = json_obj['nickname']
        #     item['face'] = json_obj['face']
        #     self.logger.debug("json item = {}".format(item))

        return item
