# -*- coding: utf-8 -*-

import base64
import os
import requests
import json
import logging
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
from yumdama import identify

from crawler.weibo.weibo.utils import BaseHelper

logger = logging.getLogger(__name__)

IDENTIFY = 1  # 验证码输入方式:        1:看截图aa.png，手动输入     2:云打码
dcap = dict(DesiredCapabilities.PHANTOMJS)  # PhantomJS需要使用老版手机的user-agent，不然验证码会无法通过
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
)
logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)  # 将selenium的日志级别设成WARNING，太烦人

"""
    输入你的微博账号和密码，可去淘宝买，一元5个。
    建议买几十个，实际生产建议100+，微博反爬得厉害，太频繁了会出现302转移。
"""
myWeiBo = [
    # ('13764512048', 'lebooks2016'),
    ('14523526312', '6xso0iu'),
    ('14523520983', '8ptsdvi'),
    # ('14523526653', '2jk8swi'),
    # ('14523526103', '1l9dgqf'),
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


def getCookie_driver(account, password):
    """ 获取一个账号的Cookie """
    try:
        browser = webdriver.PhantomJS(desired_capabilities=dcap)
        browser.get("https://weibo.cn/login/")
        time.sleep(1)
        browser.save_screenshot("aa.png")

        failure = 0
        while "微博" in browser.title and failure < 5:
            failure += 1
            username = browser.find_element_by_name("mobile")
            username.clear()
            username.send_keys(account)

            psd = browser.find_element_by_xpath('//input[@type="password"]')
            psd.clear()
            psd.send_keys(password)
            try:
                code = browser.find_element_by_name("code")
                code.clear()
                if IDENTIFY == 1:
                    code_txt = raw_input("请查看路径下新生成的aa.png，然后输入验证码:")  # 手动输入验证码
                else:
                    from PIL import Image
                    img = browser.find_element_by_xpath(
                        '//form[@method="post"]/div/img[@alt="请打开图片显示"]')
                    x = img.location["x"]
                    y = img.location["y"]
                    im = Image.open("aa.png")
                    im.crop((x, y, 100 + x, y + 22)).save("ab.png")  # 剪切出验证码
                    code_txt = identify()  # 验证码打码平台识别
                code.send_keys(code_txt)
            except Exception, e:
                pass

            commit = browser.find_element_by_name("submit")
            commit.click()
            time.sleep(3)
            if "我的首页" not in browser.title:
                time.sleep(4)

        cookie = {}
        if "我的首页" in browser.title:
            for elem in browser.get_cookies():
                cookie[elem["name"]] = elem["value"]
            logger.warning("Get Cookie Success!( Account:%s )" % account)
        return json.dumps(cookie)
    except Exception, e:
        logger.warning("Failed %s!" % account)
        return ""
    finally:
        try:
            browser.quit()
        except Exception, e:
            pass

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
