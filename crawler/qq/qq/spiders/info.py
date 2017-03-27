# -*- coding: utf-8 -*-

import sys
import re
import json

import logging

from ..profile_items import QQProfileItem
from ..utils import CommonSpider
from ..utils import BaseHelper

reload(sys)
sys.setdefaultencoding('utf8')

logger = logging.getLogger(__name__)


class QqInfoSpider(CommonSpider):
    name = "qq_info"

    COUNT_REGEXP = "\"count\":\s*{[^}]*}{1}"
    PROFILE_REGEXP = "\"profile\":\s*{[^}]*}{1}"

    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        uid = kwargs.get('uid')
        if uid:
            logger.debug("uid item = {}".format(uid))
            self.start_urls = [BaseHelper.get_profile_url(uid)]

    def parse(self, response):
        body_str = str(response.body)
        matcher = re.findall(self.PROFILE_REGEXP, body_str)
        item = QQProfileItem()
        if matcher:
            s = str(matcher.pop())
            logger.debug("the PROFILE_REGEXP matcher string is {}".format(s))
            prefix = "\"profile\":"
            s = s[len(prefix):len(s)]
            json_obj = json.loads(s)
            item['nickname'] = json_obj['nickname']

        matcher = re.findall(self.COUNT_REGEXP, body_str)
        if matcher:
            s = str(matcher.pop())
            logger.debug("the COUNT_REGEXP matcher string is {}".format(s))
            prefix = "\"count\":"
            s = s[len(prefix):len(s)]
            json_obj = json.loads(s)

            item['blog'] = json_obj['blog']
            item['message'] = json_obj['message']
            item['pic'] = json_obj['pic']
            item['shuoshuo'] = json_obj['shuoshuo']
        logger.debug("json item = {}".format(item))
        yield item
