# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3

class NuzforumsScraperPipeline(object):
    def __init__(self):
        self.con = sqlite3.connect('nuzforums-posts.db')
        self.cur = self.con.cursor()
        self.cur.execute('DROP TABLE IF EXISTS Posts')
        self.cur.execute(
            'CREATE TABLE Posts (' +
                'id INTEGER PRIMARY KEY AUTOINCREMENT,' +
                'username TEXT NOT NULL, ' +
                'time TEXT NOT NULL, ' +
                'text TEXT NOT NULL' +
            ')'
        )

    def process_item(self, item, spider):
        self.cur.execute(
            'INSERT INTO Posts(username,time,text) VALUES (?,?,?)',
            (
                item.get('username', ''),
                item.get('time', ''),
                item.get('text', '')
            )
        )
        self.con.commit()
        return item

    def __del__(self):
        self.con.close()
