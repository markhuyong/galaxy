#!/bin/bash
for i in {1..5}
do
 curl "http://localhost:9081/crawl.json?spider_name=lectures&url=http://www.lecturesshu.com/c/9c97d62b7f6a?order_by=commented_at&page=1"
done
