# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class NuzforumsForum(Item):
    forumId = Field()
    parentId = Field()
    title = Field()
    desc = Field()

class NuzforumsTopic(Item):
    topicId = Field()
    forumId = Field()
    title = Field()
    creator = Field()

class NuzforumsPost(Item):
    topicId = Field()
    poster = Field()
    time = Field()
    text = Field()

    def __repr__(self):
        return repr({
            'topicId': self['topicId'],
            'poster': self['topicId'],
            'time': self['time']
        })
