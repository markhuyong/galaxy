# -*- coding: utf-8 -*-

BOT_NAME = 'jianshu'

SPIDER_MODULES = ['jianshu.spiders']
NEWSPIDER_MODULE = 'jianshu.spiders'

DOWNLOADER_MIDDLEWARES = {
    # Engine side
    'crawler.misc.middleware.agent.CustomUserAgentMiddleware': 401,
    #'scrapy_splash.SplashCookiesMiddleware': 723,
    #'scrapy_splash.SplashMiddleware': 725,
    #'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    # Downloader side
}

SPIDER_MIDDLEWARES = {
    #'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}
# SPLASH_URL = 'http://127.0.0.1:8050/'
#SPLASH_URL = 'http://139.196.182.47:8050/'
#DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
#HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
COOKIES_ENABLED = True
COOKIES_DEBUG = True

LOG_ENABLED = True
LOG_STDOUT = True
LOG_LEVEL = 'DEBUG'

ROBOTSTXT_OBEY = False

# DOWNLOAD_DELAY = 0.25