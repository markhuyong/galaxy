# -*- coding: utf-8 -*-

import random
import urllib

from scrapy.http.headers import Headers

from crawler.misc.spider import CommonSpider
from crawler.misc import agents


class BaseHelper(object):
    PROFILE_URL = "https://mobile.qzone.qq.com/profile?hostuin=USER_QQ_NUMBER"
    SHUOSHU_URL = "https://mobile.qzone.qq.com/list?g_tk=GTK&format=json&list_type=shuoshuo&action=0&res_uin=USER_QQ_NUMBER&count=PAGECOUNT"
    CODE_URL = "https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=101347930&client_secret=68270da4c08fddb26486283c1fab1b0a&code=CODE&redirect_uri=http%3a%2f%2f29060abb.nat123.net%2fPBMSWEBOOK%2fqqlogin&state=203"

    OPENID_URL = "https://graph.qq.com/oauth2.0/me?access_token=ACCESS_TOKEN"
    ALBUMLIST_URL = "https://graph.qq.com/photo/list_album?access_token=ACCESS_TOKEN&oauth_consumer_key=101347930&openid=OPENID&format=json"
    NICKNAME_URL = "https://graph.qq.com/user/get_user_info?access_token=ACCESS_TOKEN&oauth_consumer_key=101347930&openid=OPENID"
    POTOLIST_URL = "https://graph.qq.com/photo/list_photo?access_token=ACCESS_TOKEN&oauth_consumer_key=101347930&openid=OPENID&format=json&albumid=ALBUMID"
    ALBUM_URL = "https://mobile.qzone.qq.com/list?g_tk=GTK&format=json&list_type=album&action=0&res_uin=USER_QQ_NUMBER"
    PHOTO_URL = "http://h5.qzone.qq.com/webapp/json/mqzone_photo/getPhotoList2?g_tk=GTK&uin=USER_QQ_NUMBER&albumid=ALBUMID&ps=PS&pn=PN"

    PAGE_COUNT = '40'

    @classmethod
    def get_headers(cls):
        return Headers({
            # 'User-Agent': self._get_user_agent(),
            # 'Content-Type': 'application/json',
            # "Connection": "keep-alive",
            'Accept': 'application/json',
            # 'Host': cls.BASE_URL,
        })

    @classmethod
    def get_profile_url(cls, uid):
        return cls.PROFILE_URL.replace("USER_QQ_NUMBER", uid)

    @classmethod
    def get_shuoshuo_url(cls, uid, last_attach=None):
        url = cls.SHUOSHU_URL.replace("USER_QQ_NUMBER", uid) \
            .replace("PAGECOUNT", cls.PAGE_COUNT)
        return url if last_attach is None \
            else url + "&res_attach=" + cls._quote_url(last_attach)

    def get_code_url(self, uid):
        return self.SHUOSHU_URL.replace("USER_QQ_NUMBER", uid)

    def get_openid_url(self, uid):
        return self.SHUOSHU_URL.replace("USER_QQ_NUMBER", uid)

    def get_album_list_url(self, uid):
        return self.SHUOSHU_URL.replace("USER_QQ_NUMBER", uid)

    def get_photo_list_url(self, uid):
        return self.SHUOSHU_URL.replace("USER_QQ_NUMBER", uid)

    @classmethod
    def get_album_url(cls, uid, last_attach=None):
        url = cls.ALBUM_URL.replace("USER_QQ_NUMBER", uid)

        return url if last_attach is None \
            else url + "&res_attach=" + cls._quote_url(last_attach)

    @classmethod
    def get_photo_url(cls, uid, album_id, ps, pn, last_attach=None):
        url = cls.PHOTO_URL.replace("USER_QQ_NUMBER", uid) \
            .replace("ALBUMID", album_id) \
            .replace("PS", ps) \
            .replace("PN", pn)
        return url if last_attach is None \
            else url + "&res_attach=" + cls._quote_url(last_attach)

    @staticmethod
    def get_cookie_key_prefix(spider):
        sep = "_"
        assert spider.name.index(sep) > 0
        return "{}:Cookies".format(spider.name.split(sep)[0])

    @staticmethod
    def _quote_url(url):
        return urllib.quote(unicode(str(url), "UTF-8"))
