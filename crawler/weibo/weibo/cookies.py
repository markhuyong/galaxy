# -*- coding: utf-8 -*-

import base64
import os
import requests
import json
import logging

from crawler.weibo.weibo.utils import BaseHelper

logger = logging.getLogger(__name__)

"""
    输入你的微博账号和密码，可去淘宝买，一元5个。
    建议买几十个，实际生产建议100+，微博反爬得厉害，太频繁了会出现302转移。
"""
myWeiBo = [
    #('14523526312', '6xso0iu'),
    ('13764512048', 'lebooks2016'),
    ('14523526653', '2jk8swi'),
    ('14523526103', '1l9dgqf'),
]


def getCookie(account, password):
    """ 获取一个账号的Cookie """
    loginURL = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)"
    username = base64.b64encode(account.encode("utf-8")).decode("utf-8")
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    session = requests.Session()
    r = session.post(loginURL, data=postData)
    jsonStr = r.content.decode("gbk")
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        logger.warning("Get Cookie Success!( Account:%s )" % account)
        cookie = session.cookies.get_dict()
        return json.dumps(cookie)
    else:
        logger.warning("Failed!( Reason:%s )" % info["reason"])
        return ""


def initCookie(rconn, spider):
    """ 获取所有账号的Cookies，存入Redis。如果Redis已有该账号的Cookie，则不再获取。 """
    prefix = BaseHelper.get_cookie_key_prefix(spider)
    for weibo in myWeiBo:
        if rconn.get("%s:%s--%s" % (prefix, weibo[0], weibo[1])) \
                is None:  # 'weibo:Cookies:账号--密码'，为None即不存在。
            cookie = getCookie(weibo[0], weibo[1])
            if len(cookie) > 0:
                rconn.set(
                    "%s:%s--%s" % (prefix, weibo[0], weibo[1]),
                    cookie)
    cookieNum = len(rconn.keys("{}:*".format(prefix)))
    logger.warning("The num of the cookies is %s" % cookieNum)
    if cookieNum == 0:
        logger.warning('Stopping...')
        os.system("pause")


def updateCookie(accountText, rconn, spider):
    """ 更新一个账号的Cookie """
    prefix = BaseHelper.get_cookie_key_prefix(spider)
    account = accountText.split("--")[0]
    password = accountText.split("--")[1]
    cookie = getCookie(account, password)
    if len(cookie) > 0:
        logger.warning(
            "The cookie of %s has been updated successfully!" % account)
        rconn.set("%s:%s" % (prefix, accountText), cookie)
    else:
        logger.warning(
            "The cookie of %s updated failed! Remove it!" % accountText)
        removeCookie(accountText, rconn, spider)


def removeCookie(accountText, rconn, spider):
    """ 删除某个账号的Cookie """
    prefix = BaseHelper.get_cookie_key_prefix(spider)
    rconn.delete("%s:%s" % (prefix, accountText))
    cookieNum = len(rconn.keys("{}:*".format(prefix)))
    logger.warning("The num of the cookies left is %s" % cookieNum)
    if cookieNum == 0:
        logger.warning('Stopping...')
        os.system("pause")
