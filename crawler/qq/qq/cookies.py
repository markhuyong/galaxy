# -*- coding: utf-8 -*-

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import qqlib

from crawler.qq.qq.utils import BaseHelper
from yundama import identify


"""
    输入你的微博账号和密码，可去淘宝买，一元5个。
    建议买几十个，实际生产建议100+，微博反爬得厉害，太频繁了会出现302转移。
"""
my_qq = [
    ('914095005', 'mike110_110'),
    # ('3246800755', 'huhongle79'),
]

IDENTIFY = 1  # 验证码输入方式:        1:看截图aa.png，手动输入     2:云打码

def getCookie(account, password, spider):
    """ 获取一个账号的Cookie """
    failure = 0
    while failure < 2:
        try:
            USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
            login_page = "http://ui.ptlogin2.qq.com/cgi-bin/login?style=9&pt_ttype=1&appid=549000929&pt_no_auth=1&pt_wxtest=1&daid=5&s_url=https%3A%2F%2Fh5.qzone.qq.com%2Fmqzone%2Findex"

            cap = webdriver.DesiredCapabilities.PHANTOMJS
            cap["phantomjs.page.settings.resourceTimeout"] = 5000
            cap["phantomjs.page.settings.loadImages"] = True
            cap["phantomjs.page.settings.userAgent"] = USER_AGENT

            driver = webdriver.PhantomJS(desired_capabilities=cap)
            driver.get(login_page)
            try:
                access = driver.find_element_by_id('guideSkip')  # 继续访问触屏版按钮
                access.click()
                time.sleep(1)
            except Exception, e:
                pass
            go = WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.ID, "go"))
            )
            driver.find_element_by_id("u").clear()
            driver.find_element_by_id("u").send_keys(account)
            driver.find_element_by_id("p").clear()
            driver.find_element_by_id("p").send_keys(password)

            driver.save_screenshot("logs/go_before.png")
            go.click()
            time.sleep(5)
            while '验证码' in driver.page_source:
                try:
                    spider.logger.debug('需要处理验证码！')
                    driver.save_screenshot('verification.png')
                    iframes = driver.find_elements_by_tag_name('iframe')
                    try:
                        driver.switch_to_frame(iframes[1])
                        input_verification_code = driver.find_element_by_id('cap_input')
                        submit = driver.find_element_by_id('verify_btn')
                        if IDENTIFY == 1:
                            try:
                                from PIL import Image
                                im = Image.open("verification.png")
                                im.show()
                                im.close()
                            except:
                                spider.logger.debug(u"请到当前目录下，找到验证码后输入")
                                verification_code = raw_input("请查看路径下新生成的 verification.png，然后输入验证码:")  # 手动输入验证码
                        else:
                            verification_code = identify()
                        spider.logger.debug('验证码识别结果: %s' % verification_code)
                        input_verification_code.clear()
                        input_verification_code.send_keys(verification_code)
                        submit.click()
                        time.sleep(1)
                    except Exception, e:
                        break
                except Exception, e:
                    driver.quit()
                    return ''
            if driver.title == 'QQ空间':
                cookies = {}
                for elem in driver.get_cookies():
                    cookies[elem["name"]] = elem["value"]
                    spider.logger.warning("Get Cookie Success!( Account:%s )" % account)
                driver.quit()
                return json.dumps(cookies)
            else:
                spider.logger.debug('Get the cookie of QQ:%s failed!' % account)
                return ''
        except Exception, e:
            failure += 1
            if 'driver' in dir():
                driver.quit()
        except KeyboardInterrupt, e:
            raise e
    return ''

def getCookie_api(account, password, spider):
    """ 获取一个账号的Cookie """
    qq = qqlib.QQ(account, password)
    qq.login()
    cookies = qq.session.cookies
    if "pt4_token" in cookies:
        spider.logger.warning("Get Cookie Success!( Account:%s )" % account)
        cookie = cookies.get_dict()
        return json.dumps(cookie)
    else:
        spider.logger.warning("Failed!( Reason:%s )" % "pt4_token does not exist.")
        return ""

def initCookie(rconn, spider):
    """ 获取所有账号的Cookies，存入Redis。如果Redis已有该账号的Cookie，则不再获取。 """
    prefix = BaseHelper.get_cookie_key_prefix(spider)
    for qq in my_qq:
        if rconn.get("%s:Cookies:%s--%s" % ("qq", qq[0], qq[1])) \
                is None:  # 'qq:Cookies:账号--密码'，为None即不存在。
            cookie = getCookie(qq[0], qq[1], spider)
            spider.log("qq cookies" + "=" * 10 + cookie)
            if len(cookie) > 0:
                rconn.set(
                    "%s:%s--%s" % (prefix, qq[0], qq[1]),
                    cookie)
    cookieNum = len(rconn.keys("{}:*".format(prefix)))
    spider.logger.warning("The num of the cookies is %s" % cookieNum)
    if cookieNum == 0:
        spider.logger.warning('Stopping...')


def updateCookie(accountText, rconn, spider):
    """ 更新一个账号的Cookie """
    prefix = BaseHelper.get_cookie_key_prefix(spider)
    account = accountText.split("--")[0]
    password = accountText.split("--")[1]
    cookie = getCookie(account, password, spider)
    if len(cookie) > 0:
        spider.logger.warning(
            "The cookie of %s has been updated successfully!" % account)
        rconn.set("%s:%s" % (prefix, accountText), cookie)
    else:
        spider.logger.warning(
            "The cookie of %s updated failed! Remove it!" % accountText)
        removeCookie(accountText, rconn, spider)


def removeCookie(accountText, rconn, spider):
    """ 删除某个账号的Cookie """
    prefix = BaseHelper.get_cookie_key_prefix(spider)
    rconn.delete("%s:%s" % (prefix, accountText))
    cookieNum = len(rconn.keys("{}:*".format(prefix)))
    spider.logger.warning("The num of the cookies left is %s" % cookieNum)
    if cookieNum == 0:
        spider.logger.warning('Stopping...')
