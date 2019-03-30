# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3

from nuzforums_scraper.items import NuzforumsForum, NuzforumsTopic, NuzforumsPost
import logging

ITEMS_LOG = 'logs/items.txt'
ERRORS_LOG = 'logs/errors.txt'

class NuzforumsScraperPipeline(object):

    def open_spider(self, spider):
        open(ITEMS_LOG, 'w').close()
        open(ERRORS_LOG, 'w').close()
        self.con = sqlite3.connect('nuzforums-posts.db')
        self.cur = self.con.cursor()

        self.cur.execute('DROP TABLE IF EXISTS Forum')
        self.cur.execute('DROP TABLE IF EXISTS Topic')
        self.cur.execute('DROP TABLE IF EXISTS Post')

        self.cur.execute(
            'CREATE TABLE Forum (' +
                'forum_id INTEGER PRIMARY KEY,' +
                'parent_id INTEGER,' +
                'title TEXT NOT NULL,' +
                'desc TEXT,' +
                'FOREIGN KEY(parent_id) REFERENCES Forum(forum_id)'
            ')'
        )
        self.cur.execute(
            'CREATE TABLE Topic (' +
                'topic_id INTEGER PRIMARY KEY,' +
                'forum_id INTEGER,' +
                'title TEXT NOT NULL,' +
                'creator TEXT,' +
                'FOREIGN KEY(forum_id) REFERENCES Forum(forum_id)'
            ')'
        )
        self.cur.execute(
            'CREATE TABLE Post (' +
                'post_id INTEGER PRIMARY KEY AUTOINCREMENT,' +
                'topic_id INTEGER NOT NULL,' +
                'poster TEXT NOT NULL,' +
                'time TEXT NOT NULL,' +
                'text TEXT NOT NULL,' +
                'FOREIGN KEY(topic_id) REFERENCES Topic(topic_id)' +
            ')'
        )

    def process_item(self, item, spider):
        with open(ITEMS_LOG, 'a') as f:
            tab = '' if isinstance(item, NuzforumsForum) else '\t'
            tab = tab + ('\t' if isinstance(item, NuzforumsPost) else '')
            f.write(tab + str(type(item)) + '\n')
            i = item
            if 'text' in item:
                i = dict(item)
                del i['text']
            f.write(tab + str(i).replace('\n','\n'+tab) + '\n\n')
            f.flush()
    
        try:
            if isinstance(item, NuzforumsForum):
                self.cur.execute(
                    'INSERT INTO Forum VALUES (?,?,?,?)',
                    (
                        item.get('forumId'),
                        item.get('parentId'),
                        item.get('title'),
                        item.get('desc')
                    )
                )
            elif isinstance(item, NuzforumsTopic):
                self.cur.execute(
                    'INSERT INTO Topic VALUES (?,?,?,?)',
                    (
                        item.get('topicId'),
                        item.get('forumId'),
                        item.get('title'),
                        item.get('creator'),
                    )
                )
            elif isinstance(item, NuzforumsPost):
                self.cur.execute(
                    'INSERT INTO Post(topic_id,poster,time,text) VALUES (?,?,?,?)',
                    (
                        item.get('topicId'),
                        item.get('poster'),
                        item.get('time'),
                        item.get('text')
                    )
                )
            
            self.con.commit()
        except Exception as e:
            with open(ERRORS_LOG, 'a') as f:
                f.write(str(e) + '\n')
                f.write(str(item) + '\n')
                f.flush()
        return item

    def close_spider(self, spider):
        self.con.close()
