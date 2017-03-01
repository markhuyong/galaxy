# -*- coding: utf-8 -*-

import logging
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

from ..items import InformationItem

from ..utils import CommonSpider
from ..utils import BaseHelper

logger = logging.getLogger(__name__)


class WeiboInfoSpider(CommonSpider):
    name = "weibo_info"

    def parse_(self, response):
        uid = response.request.url.split('/')[-1]

        logger.info("uid=============={}".format(uid))
        print("uid=============={}".format(uid))
        # cookie_jar = response.meta.setdefault('cookiejar', CookieJar())
        # cookie_jar.extract_cookies(response, response.request)
        #
        # headers = BaseHelper.get_headers()
        #
        # item = LecturesItem()
        # res = Selector(response)
        # titles = res.css('title::text').re(ur'(\w+)') or ['']
        # item['author_name'] = titles[0]
        # item['url'] = response.request.url
        #
        # next_link = BaseHelper.LECTURES_URL.format(uid=uid)
        # request = Request(next_link, callback=self.parse_lecture_json,
        #                   headers=headers)
        # cookie_jar.add_cookie_header(request)  # apply Set-Cookie ourselves
        # request.meta['item'] = item
        # yield request
        #
        # yield item


    # def parse_information(self, response):
    def parse(self, response):
        """ 抓取个人信息 """
        informationItem = InformationItem()
        selector = Selector(response)
        ID = re.findall('(\d+)/info', response.url)[0]
        try:
            text1 = ";".join(selector.xpath(
                'body/div[@class="c"]//text()').extract())  # 获取标签里的所有text()
            nickname = re.findall('昵称[：:]?(.*?);'.decode('utf8'), text1)
            gender = re.findall('性别[：:]?(.*?);'.decode('utf8'), text1)
            place = re.findall('地区[：:]?(.*?);'.decode('utf8'), text1)
            briefIntroduction = re.findall('简介[：:]?(.*?);'.decode('utf8'), text1)
            birthday = re.findall('生日[：:]?(.*?);'.decode('utf8'), text1)
            sexOrientation = re.findall('性取向[：:]?(.*?);'.decode('utf8'), text1)
            sentiment = re.findall('感情状况[：:]?(.*?);'.decode('utf8'), text1)
            vipLevel = re.findall('会员等级[：:]?(.*?);'.decode('utf8'), text1)
            authentication = re.findall('认证[：:]?(.*?);'.decode('utf8'), text1)
            url = re.findall('互联网[：:]?(.*?);'.decode('utf8'), text1)

            informationItem["_id"] = ID
            if nickname and nickname[0]:
                informationItem["NickName"] = nickname[0].replace(u"\xa0", "")
            if gender and gender[0]:
                informationItem["Gender"] = gender[0].replace(u"\xa0", "")
            if place and place[0]:
                place = place[0].replace(u"\xa0", "").split(" ")
                informationItem["Province"] = place[0]
                if len(place) > 1:
                    informationItem["City"] = place[1]
            if briefIntroduction and briefIntroduction[0]:
                informationItem["BriefIntroduction"] = briefIntroduction[0].replace(
                    u"\xa0", "")
            if birthday and birthday[0]:
                try:
                    birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                    informationItem["Birthday"] = birthday - datetime.timedelta(
                        hours=8)
                except Exception:
                    informationItem['Birthday'] = birthday[0]  # 有可能是星座，而非时间
            if sexOrientation and sexOrientation[0]:
                if sexOrientation[0].replace(u"\xa0", "") == gender[0]:
                    informationItem["SexOrientation"] = "同性恋"
                else:
                    informationItem["SexOrientation"] = "异性恋"
            if sentiment and sentiment[0]:
                informationItem["Sentiment"] = sentiment[0].replace(u"\xa0", "")
            if vipLevel and vipLevel[0]:
                informationItem["VIPlevel"] = vipLevel[0].replace(u"\xa0", "")
            if authentication and authentication[0]:
                informationItem["Authentication"] = authentication[0].replace(
                    u"\xa0", "")
            if url:
                informationItem["URL"] = url[0]

            try:
                urlothers = "http://weibo.cn/attgroup/opening?uid=%s" % ID
                r = requests.get(urlothers, cookies=response.request.cookies,
                                 timeout=5)
                if r.status_code == 200:
                    selector = etree.HTML(r.content)
                    texts = ";".join(
                        selector.xpath('//body//div[@class="tip2"]/a//text()'))
                    if texts:
                        num_tweets = re.findall('微博\[(\d+)\]'.decode('utf8'), texts)
                        num_follows = re.findall('关注\[(\d+)\]'.decode('utf8'),
                                                 texts)
                        num_fans = re.findall('粉丝\[(\d+)\]'.decode('utf8'), texts)
                        if num_tweets:
                            informationItem["Num_Tweets"] = int(num_tweets[0])
                        if num_follows:
                            informationItem["Num_Follows"] = int(num_follows[0])
                        if num_fans:
                            informationItem["Num_Fans"] = int(num_fans[0])
            except Exception, e:
                pass
        except Exception, e:
            pass
        else:
            print("informationItem====={}".format(informationItem))
            logger.debug("informationItem====={}".format(informationItem))
            yield informationItem
