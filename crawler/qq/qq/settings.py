# -*- coding: utf-8 -*-

BOT_NAME = 'qq'

SPIDER_MODULES = ['qq.spiders']
NEWSPIDER_MODULE = 'qq.spiders'

DOWNLOADER_MIDDLEWARES = {
    # Engine side
    # 'crawler.misc.middleware.agent.CustomUserAgentMiddleware': 401,
    'qq.middleware.CookiesMiddleware': 402,
}

SPIDER_MIDDLEWARES = {
    #'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# 种子队列的信息
REDIE_URL = None
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASS = 'AW6exN@pVw0mxcB4'

# 去重队列的信息
FILTER_URL = None
FILTER_HOST = 'localhost'
FILTER_PORT = 6379
FILTER_DB = 0

USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
# COOKIES_ENABLED = True
COOKIES_DEBUG = True

LOG_ENABLED = True
# LOG_STDOUT = True
LOG_LEVEL = 'DEBUG'
LOG_FILE = 'tttt.log'

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 1