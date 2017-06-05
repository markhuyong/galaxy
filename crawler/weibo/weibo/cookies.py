# -*- coding: utf-8 -*-

import base64
import binascii
import json
import logging
import random
import time

import requests
import rsa
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from yumdama import identify

try:
    from PIL import Image
except:
    pass
try:
    from urllib.parse import quote_plus
except:
    from urllib import quote_plus

from crawler.weibo.weibo.utils import BaseHelper
from crawler.misc.proxy import FREE_PROXIES

IDENTIFY = 2  # 验证码输入方式:        1:看截图aa.png，手动输入     2:云打码

logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)  # 将selenium的日志级别设成WARNING，太烦人

"""
    输入你的微博账号和密码，可去淘宝买，一元5个。
    建议买几十个，实际生产建议100+，微博反爬得厉害，太频繁了会出现302转移。
"""

weiBo_str = """
15210347246----q123123
15853404528----q123123
13071443293----q123123
13403386148----q123123
13264021637----q123123
17071343719----q123123
13129003893----q123123
17704957527----q123123
15554986846----q123123
18363114994----q123123
17074225175----q123123
15360605109----q123123
13202887896----q123123
15725444017----q123123
13185864496----q123123
18160841549----q123123
17726741039----q123123
13643734360----q123123
18684945047----q123123
13190151040----q123123
13780289747----q123123
17076605834----q123123
15524809425----q123123
14723394480----q123123
15992045800----q123123
13172388028----q123123
17726744941----q123123
13266426443----q123123
17704964091----q123123
18221464745----q123123
"""

# weiBo_str = """
# 13754672984----q123123
# 15253312554----q123123
# 13229912842----q123123
# 17074139958----q123123
# 17184957472----q123123
# 15659030463----q123123
# 15694414587----q123123
# """

def get_su(account):
    """
    对 email 地址和手机号码 先 javascript 中 encodeURIComponent
    对应 Python 3 中的是 urllib.parse.quote_plus
    然后在 base64 加密后decode
    """
    username_quote = quote_plus(account)
    username_base64 = base64.b64encode(username_quote.encode("utf-8"))
    return username_base64.decode("utf-8")


# 预登陆获得 servertime, nonce, pubkey, rsakv
def get_server_data(su, session, headers):
    pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
    pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_="
    pre_url = pre_url + str(int(time.time() * 1000))
    pre_data_res = session.get(pre_url, headers=headers)

    sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))

    return sever_data


def get_password(password, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 拼接明文js加密文件中得到
    message = message.encode("utf-8")
    passwd = rsa.encrypt(message, key)  # 加密
    passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
    return passwd


def get_cha(pcid, session, headers):
    cha_url = "http://login.sina.com.cn/cgi/pin.php?r="
    cha_url = cha_url + str(int(random.random() * 100000000)) + "&s=0&p="
    cha_url = cha_url + pcid
    cha_page = session.get(cha_url, headers=headers)
    with open("cha.jpg", 'wb') as f:
        f.write(cha_page.content)
        f.close()
    try:
        im = Image.open("cha.jpg")
        im.show()
        im.close()
    except:
        print(u"请到当前目录下，找到验证码后输入")


def getCookie_mapi(account, password, spider):
    session = requests.Session()
    proxies = FREE_PROXIES
    p = random.choice(proxies)
    proxies = {'http': "http://%s" % p['ip_port']}
    headers = requests.utils.default_headers()
    headers.update(BaseHelper.get_login_headers())

    # 访问 初始页面带上 cookie
    login_url = "https://passport.weibo.cn/sso/login"
    postdata = {
        'entry': 'mweibo',
        'savestate': '1',
        'username': account,
        'password': password,
        'r': 'http://m.weibo.cn/',
        'ec': '0',
        'pagerefer': "https://passport.weibo.cn/signin/welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F",
        'wentry': '',
        'loginfrom': '',
        'client_id': '',
        'code': '',
        'qq': '',
        'mainpageflag': '1',
        'hff': '',
        'hfp': '',
    }
    # if showpin == 0:
    login_page = session.post(login_url, data=postdata, headers=headers)
    # else:
    #     pcid = sever_data["pcid"]
    #     get_cha(pcid, session, headers)
    #     postdata['door'] = raw_input(u"请输入验证码")
    #     login_page = session.post(login_url, data=postdata, headers=headers)
    jsonStr = login_page.content.decode("GBK")
    info = json.loads(jsonStr)
    if info["retcode"] == 20000000:
        spider.logger.warning("Get Cookie Success!( Account:%s )" % account)
        cookie = session.cookies.get_dict()
        return json.dumps(cookie)
    elif info["retcode"] == "4049":
        # pcid = sever_data["pcid"]
        # get_cha(pcid, session, headers)
        # postdata['door'] = raw_input(u"请输入验证码")
        # login_page = session.post(login_url, data=postdata, headers=headers)
        # jsonStr = login_page.content.decode("GBK")
        return ""
    else:
        spider.logger.warning("Failed!( Reason:%s )" % info["reason"])
        return ""


def getCookie_api(account, password, spider):
    session = requests.Session()
    proxies = FREE_PROXIES
    p = random.choice(proxies)
    proxies = {'http': "http://%s" % p['ip_port']}
    headers = requests.utils.default_headers()
    headers.update(BaseHelper.get_login_headers())

    # 访问 初始页面带上 cookie
    index_url = "http://weibo.com/login.php"
    try:
        session.get(index_url, headers=headers, timeout=2)
    except:
        session.get(index_url, headers=headers)
    # try:
    #     input = raw_input
    # except:
    #     pass
    # su 是加密后的用户名
    su = get_su(account)
    sever_data = get_server_data(su, session, headers)
    servertime = sever_data["servertime"]
    nonce = sever_data['nonce']
    rsakv = sever_data["rsakv"]
    pubkey = sever_data["pubkey"]
    showpin = sever_data["showpin"]
    password_secret = get_password(password, servertime, nonce, pubkey)

    postdata = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'useticket': '1',
        'pagerefer': "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl",
        'vsnf': '1',
        'su': su,
        'service': 'miniblog',
        'servertime': servertime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'rsakv': rsakv,
        'sp': password_secret,
        'sr': '1366*768',
        'encoding': 'UTF-8',
        'prelt': '115',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'TEXT'
    }
    login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
    if showpin == 0:
        login_page = session.post(login_url, data=postdata, headers=headers)
    else:
        pcid = sever_data["pcid"]
        get_cha(pcid, session, headers)
        postdata['door'] = raw_input(u"请输入验证码")
        login_page = session.post(login_url, data=postdata, headers=headers)
    jsonStr = login_page.content.decode("GBK")
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        spider.logger.warning("Get Cookie Success!( Account:%s )" % account)
        cookie = session.cookies.get_dict()
        return json.dumps(cookie)
    elif info["retcode"] == "4049":
        pcid = sever_data["pcid"]
        get_cha(pcid, session, headers)
        postdata['door'] = raw_input(u"请输入验证码")
        login_page = session.post(login_url, data=postdata, headers=headers)
        jsonStr = login_page.content.decode("GBK")
        return ""
    else:
        spider.logger.warning("Failed!( Reason:%s )" % info["reason"])
        return ""


def getCookie_old(account, password, spider):
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
    proxies = FREE_PROXIES
    p = random.choice(proxies)
    # proxies = {'http': "http://%s" % p['ip_port']}
    headers = requests.utils.default_headers()
    headers.update(BaseHelper.get_headers())
    # headers = BaseHelper.get_login_headers()

    # r = session.post(loginURL, data=postData, proxies=proxies, headers=headers)
    r = session.post(loginURL, data=postData, headers=headers)
    jsonStr = r.content.decode("gbk")
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        spider.logger.warning("Get Cookie Success!( Account:%s )" % account)
        cookie = session.cookies.get_dict()
        return json.dumps(cookie)
    else:
        spider.logger.warning("Failed!( Reason:%s )" % info["reason"])
        return ""


def getCookie(account, password, spider):
    """ 获取一个账号的Cookie """
    dcap = dict(DesiredCapabilities.PHANTOMJS)  # PhantomJS需要使用老版手机的user-agent，不然验证码会无法通过
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
    )
    # dcap["phantomjs.page.settings.userAgent"] = BaseHelper.random_user_agent()
    browser = webdriver.PhantomJS(desired_capabilities=dcap)
    try:
        # browser.set_window_size(480, 320)
        browser.get("https://weibo.cn/login/")
        time.sleep(3)
        import os
        try:
            os.remove("aa.png")
        except OSError:
            pass
        browser.save_screenshot("aa.png")

        failure = 0
        while "微博" in browser.title and failure < 5:
            failure += 1
            username = browser.find_element_by_id("loginName")
            username.clear()
            username.send_keys(account)

            psd = browser.find_element_by_id("loginPassword")
            psd.clear()
            psd.send_keys(password)
            try:
                code = browser.find_element_by_id("loginVCode")
                code.clear()
                if IDENTIFY == 1:
                    try:
                        from PIL import Image
                        im = Image.open("aa.png")
                        im.show()
                        im.close()
                    except:
                        print(u"请到当前目录下，找到验证码后输入")
                    code_txt = raw_input("请查看路径下新生成的aa.png，然后输入验证码:")  # 手动输入验证码
                else:
                    from PIL import Image
                    img = browser.find_element_by_xpath(
                        '//form[@method="post"]/div/img[@alt="请打开图片显示"]')
                    x = img.location["x"]
                    y = img.location["y"]
                    im = Image.open("aa.png")
                    im.crop((x, y, x + img.size.get("width"), y + img.size.get("height"))).save("ab.png")  # 剪切出验证码
                    code_txt = identify()  # 验证码打码平台识别
                code.send_keys(code_txt)
            except Exception, e:
                pass

            commit = browser.find_element_by_id("loginAction")
            commit.click()
            time.sleep(3)
            time.sleep(4)
            # if "我的首页" not in browser.title:
            #     time.sleep(4)
            # if '未激活微博' in browser.page_source:
            #     print '账号未开通微博'
            #     return {}

        cookie = {}
        # if "我的首页" in browser.title or True:
        if browser.title is not None:
            for elem in browser.get_cookies():
                cookie[elem["name"]] = elem["value"]
                spider.logger.warning("Get Cookie Success!( Account:%s )" % account)
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
    myWeiBo = [(line.split('----')[0], line.split('----')[1]) for line in filter(lambda l: l, weiBo_str.split('\n'))]
    throttle = 5
    for weibo in myWeiBo:
        if rconn.get("%s:%s--%s" % (prefix, weibo[0], weibo[1])) is None:  # 'weibo:Cookies:账号--密码'，为None即不存在。
            cookie = getCookie(weibo[0], weibo[1], spider)
            if len(cookie) > 0:
                rconn.set("%s:%s--%s" % (prefix, weibo[0], weibo[1]), cookie)
                throttle -= 1
        if throttle < 0:
            break
    cookieNum = len(rconn.keys("{}:*".format(prefix)))
    spider.logger.warning("The num of the cookies is %s" % cookieNum)
    if cookieNum == 0:
        spider.logger.error('initCookie: Stopping...')


def updateCookie(accountText, rconn, spider):
    """ 更新一个账号的Cookie """
    prefix = BaseHelper.get_cookie_key_prefix(spider)
    account = accountText.split("--")[0]
    password = accountText.split("--")[1]
    cookie = getCookie(account, password)
    if len(cookie) > 0:
        spider.logger.warning(
            "The cookie of %s has been updated successfully!" % account)
        rconn.set("%s:%s" % (prefix, accountText), cookie)
    else:
        spider.logger.error(
            "The cookie of %s updated failed! Remove it!" % accountText)
        removeCookie(accountText, rconn, spider)


def removeCookie(accountText, rconn, spider):
    """ 删除某个账号的Cookie """
    prefix = BaseHelper.get_cookie_key_prefix(spider)
    rconn.delete("%s:%s" % (prefix, accountText))
    cookieNum = len(rconn.keys("{}:*".format(prefix)))
    spider.logger.warning("The num of the cookies left is %s" % cookieNum)
    if cookieNum == 0:
        spider.logger.error('removeCookie, cookie is used up. Stopping...')
