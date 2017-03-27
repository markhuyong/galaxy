# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ProfileItem(Item):
    nick_name = Field()
    profile_image = Field()
    uid = Field()


class QQProfileItem(ProfileItem):
    nickname = Field()
    blog = Field()
    message = Field()
    pic = Field()
    shuoshuo = Field()
