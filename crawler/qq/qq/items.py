# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field


class QqStatusItem(Item):
    text = Field()
    published_at = Field()
    pictures = Field()


class QqPhotoItem(Item):
    published_at = Field()
    images = Field()


class PictureItem(Item):
    url = Field()
    width = Field()
    height = Field()


class ImageItem(Item):
    text = Field()
    pictures = Field()
