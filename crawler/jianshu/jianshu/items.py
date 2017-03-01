# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field


class CollectionItem(Item):
    read = Field()          # 阅读数量
    comment = Field()       # 评论数量
    like = Field()          # 喜欢数量
    title = Field()         # 文章标题
    url = Field()           # 文章链接
    reward = Field()        # 打赏数量
    created_at = Field()    # 创建时间
    published_at = Field()  # 文章发布时间
    content = Field()       # 内容
    modified_at = Field()   # 最后编辑时间
    word_count = Field()    # 文字个数


class LecturesItem(Item):
    url = Field()
    author_name = Field()
    lectures = Field()
    specials = Field()
