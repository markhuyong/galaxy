# -*- coding: utf-8 -*-

import sys
import re
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
        matcher = re.findall(self.COUNT_REGEXP, str(response.body))
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
            yield item
