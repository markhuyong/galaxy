# -*- coding: utf-8 -*-

import base64
import os
import requests
import json
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

"""
    输入你的微博账号和密码，可去淘宝买，一元5个。
    建议买几十个，实际生产建议100+，微博反爬得厉害，太频繁了会出现302转移。
"""
my_qq = [
    # ('1544269229', '1rwi4o8d'),
    ('914095005', 'mike110_110'),
]


def getCookie(account, password):
    """ 获取一个账号的Cookie """

    USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
    login_page = "http://ui.ptlogin2.qq.com/cgi-bin/login?style=9&pt_ttype=1&appid=549000929&pt_no_auth=1&pt_wxtest=1&daid=5&s_url=https%3A%2F%2Fh5.qzone.qq.com%2Fmqzone%2Findex"

    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap["phantomjs.page.settings.resourceTimeout"] = 5000
    cap["phantomjs.page.settings.loadImages"] = False
    cap["phantomjs.page.settings.userAgent"] = USER_AGENT

    driver = webdriver.PhantomJS(desired_capabilities=cap)
    # driver.delete_all_cookies()
    driver.get(login_page)

    # print driver.page_source
    go = WebDriverWait(driver, 500).until(
        EC.presence_of_element_located((By.ID, "go"))
    )
    driver.find_element_by_id("guideSkip").click()
    # driver.find_element_by_id("u").send_keys("324632148")
    driver.find_element_by_id("u").clear()
    driver.find_element_by_id("u").send_keys(account)
    driver.find_element_by_id("p").clear()
    driver.find_element_by_id("p").send_keys(password)
    # driver.find_element_by_id("p").send_keys("hongle79")
    # driver.find_element_by_id("go").click()
    # driver.save_screenshot("logs/test1.png")
    go.click()
    WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.ID, "nav_bar_me"))
    )

    # driver.save_screenshot("logs/test.png")
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Click here for results of recent tournaments")))
    #  print driver.page_source

    cookies = driver.get_cookies()
    driver.quit()

    logger.debug("cookies".format(cookies))
    logger.warning("Get Cookie Success!( Account:%s )" % account)
    return json.dumps(cookies)

    # if info["retcode"] == "0":
    #     logger.warning("Get Cookie Success!( Account:%s )" % account)
    #     cookie = session.cookies.get_dict()
    #     return json.dumps(cookie)
    # else:
    #     logger.warning("Failed!( Reason:%s )" % info["reason"])
    #     return ""


def initCookie(rconn, spiderName):
    """ 获取所有账号的Cookies，存入Redis。如果Redis已有该账号的Cookie，则不再获取。 """
    for qq in my_qq:
        if rconn.get("%s:Cookies:%s--%s" % (spiderName, qq[0], qq[1])) \
                is None:  # 'qq:Cookies:账号--密码'，为None即不存在。
            cookie = getCookie(qq[0], qq[1])
            if len(cookie) > 0:
                rconn.set(
                    "%s:Cookies:%s--%s" % (spiderName, qq[0], qq[1]),
                    cookie)
    cookieNum = "".join(rconn.keys()).count("qq:Cookies")
    logger.warning("The num of the cookies is %s" % cookieNum)
    if cookieNum == 0:
        logger.warning('Stopping...')
        # os.system("pause")


def updateCookie(accountText, rconn, spiderName):
    """ 更新一个账号的Cookie """
    account = accountText.split("--")[0]
    password = accountText.split("--")[1]
    cookie = getCookie(account, password)
    if len(cookie) > 0:
        logger.warning(
            "The cookie of %s has been updated successfully!" % account)
        rconn.set("%s:Cookies:%s" % (spiderName, accountText), cookie)
    else:
        logger.warning(
            "The cookie of %s updated failed! Remove it!" % accountText)
        removeCookie(accountText, rconn, spiderName)


def removeCookie(accountText, rconn, spiderName):
    """ 删除某个账号的Cookie """
    rconn.delete("%s:Cookies:%s" % (spiderName, accountText))
    cookieNum = "".join(rconn.keys()).count("qq:Cookies")
    logger.warning("The num of the cookies left is %s" % cookieNum)
    if cookieNum == 0:
        logger.warning('Stopping...')
        # os.system("pause")
