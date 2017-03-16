# -*- coding: utf-8 -*-
# ------------------------------------------
#   clean Redis cookies
# ------------------------------------------

import settings
import redis

if __name__ == '__main__':
    try:
        rconn = redis.Redis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB, settings.REDIS_PASS)
    except Exception:
        rconn = redis.Redis(settings.REDIS_HOST, settings.REDIS_PORT)

    try:
        rconn_filter = redis.Redis(settings.FILTER_HOST, settings.FILTER_PORT, settings.FILTER_DB)
    except Exception:
        try:
            rconn_filter = redis.Redis(settings.FILTER_HOST, settings.FILTER_PORT)
        except Exception:
            rconn_filter = None

    if rconn:
        for key in rconn.keys():
            if "weibo" in key:
                print "weibo:key===={}".format(key)
                rconn.delete(key)

    if rconn_filter:
        if 'weibo:dupefilter0' in rconn.keys():
            rconn.delete('weibo:dupefilter0')
        if 'weibo:dupefilter1' in rconn.keys():
            rconn.delete('weibo:dupefilter1')

    print 'Finish!'
