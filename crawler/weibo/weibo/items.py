# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field


class WeiboUserItem(Item):
    uid = Field()
    nick_name = Field()
    profile_image = Field()


class WeiboStatusItem(Item):
    publishTime = Field()
    text = Field()
    pictures = Field()
