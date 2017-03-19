# -*- coding: utf-8 -*-
# ------------------------------------------
#   作用：清空Redis数据，重新跑数据时用。
# ------------------------------------------
import logging
import sys

import settings
import redis

logger = logging.getLogger(__name__)

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
        prefix = "qq:Cookies"
        search_key = "{}:*".format(prefix)
        keys = rconn.keys(search_key)
        print "numbers of {} is {}".format(prefix, len(keys))
        for key in keys:
            print "{}===={}".format(prefix,key)
            if len(sys.argv) > 1 and sys.argv[1] == "yes":
                rconn.delete(key)

            if 'qq' in key:
                logger.info("qq:key===={}".format(key))

    if rconn:
        if 'qq:requests' in rconn.keys():
            rconn.delete('qq:requests')

    if rconn_filter:
        if 'qq:dupefilter0' in rconn.keys():
            rconn.delete('qq:dupefilter0')
        if 'qq:dupefilter1' in rconn.keys():
            rconn.delete('qq:dupefilter1')

    print 'Finish!'
