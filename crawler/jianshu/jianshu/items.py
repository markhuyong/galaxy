# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field


class CollectionItem(Item):
    articleRead = Field()          # 阅读数量
    articleComment = Field()       # 评论数量
    articleLike = Field()          # 喜欢数量
    title = Field()         # 文章标题
    url = Field()           # 文章链接
    reward = Field()        # 打赏数量
    createTime = Field()    # 创建时间
    publishTime = Field()  # 文章发布时间
    content = Field()       # 内容
    lastPublishTime = Field()   # 最后编辑时间
    wordCount = Field()    # 文字个数


class LecturesItem(Item):
    url = Field()
    authorName = Field()
    lectures = Field()
    specials = Field()
