# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from nuzforums_scraper.items import NuzforumsForum, NuzforumsTopic, NuzforumsPost

class NuzforumsSpider(scrapy.Spider):
    name = 'nuzforums'
    allowed_domains = ['tapatalk.com']
    start_urls = ['https://www.tapatalk.com/groups/nuzlocke_forum/ucp.php?mode=login']

    forumId = 0
    topicId = 0

    def parse(self, response):
        # submit form request to login url above
        formRequest = scrapy.FormRequest.from_response(
            response,
            formid='login', # needed because there are multiple forms on page
            formdata={
                'username': self.settings.get('USERNAME'),
                'password': self.settings.get('PASSWORD'),
                'login': 'Login'
            },
            callback=self.after_login,
        )
        return formRequest

    def after_login(self, response):
        if 'index' in response.url:
            self.log("login success")

            if self.settings.get('WHOLE_FORUM'):
                forumLinks = response.xpath('//h2[contains(@class, "forum-title")]/a/@href').getall()
                for link in forumLinks:
                    yield scrapy.Request(
                        response.urljoin(link),
                        callback=self.parse_forum,
                        priority=-self.forumId,
                        meta={'forumId': self.forumId}
                    )
                    self.forumId = self.forumId + 1
            else:
                for forum in self.settings.get('FORUM_URLS'):
                    yield scrapy.Request(
                        response.urljoin(forum),
                        callback=self.parse_forum,
                        priority=-self.forumId,
                        meta={'forumId': self.forumId}
                    )
                    self.forumId = self.forumId + 1
                for topic in self.settings.get('TOPIC_URLS'):
                    yield scrapy.Request(
                        response.urljoin(topic.replace('?view=unread#unread','')),
                        callback=self.parse_topic,
                        priority=-self.topicId,
                        meta={'topicId': self.topicId}
                    )
                    self.topicId = self.topicId + 1
                    
        else:
            self.log("login fail")

    def parse_forum(self, response):
        # parse and store forum data
        title = response.xpath('//h2[@class="forum-title"]/a/text()').get()
        desc = response.xpath('//p[@class="forum-description"]/text()').get()

        forum = NuzforumsForum()
        forum['forumId'] = response.meta['forumId']
        forum['parentId'] = response.meta.get('parentId')
        forum['title'] = title
        forum['desc'] = desc if desc is not None else ''
        yield forum

        # parse topics if any
        for req in self.parse_topics(response):
            yield req

        # parse subforums if any
        forumLinks = response.xpath('//a[@class="forumtitle"]/@href').getall()
        for link in forumLinks:
            yield scrapy.Request(
                response.urljoin(link),
                callback=self.parse_forum,
                priority=-self.forumId,
                meta={'forumId': self.forumId,'parentId': forum['forumId']}
            )
            self.forumId = self.forumId + 1

    def parse_topics(self, response):
        forumId = response.meta['forumId']

        # parse topics if any
        topicLinks = response.xpath('//a[@itemprop="headline"]/@href').getall()
        for link in topicLinks:
            yield scrapy.Request(
                response.urljoin(link.replace('?view=unread#unread','')),
                callback=self.parse_topic,
                priority=-forumId-self.topicId,
                meta={'forumId': forumId, 'topicId': self.topicId}
            )
            self.topicId = self.topicId + 1

        # parse next page if it exists
        nextPage = response.xpath('//a[@rel="next"]/@href').get()
        if nextPage:
            yield scrapy.Request(
                response.urljoin(nextPage),
                callback=self.parse_topics,
                priority=-forumId-self.topicId,
                meta={'forumId': forumId}
            )

    def parse_topic(self, response):
        # parse and store topic data
        title = response.xpath('//h2[@class="topic-title"]/a/text()').get()
        creator = response.xpath('//span[@itemprop="creator"]/a/text()').get()

        topic = NuzforumsTopic()
        topic['topicId'] = response.meta['topicId']
        topic['forumId'] = response.meta.get('forumId')
        topic['title'] = title
        topic['creator'] = creator
        yield topic

        # recursively parse posts
        for req in self.parse_posts(response):
            yield req

    def parse_posts(self, response):
        forumId = response.meta.get('forumId')
        if forumId is None:
            forumId = 0
        topicId = response.meta['topicId']

        # parse and store forum post data
        usernames = response.xpath('//span[@itemprop="name"]/a/text() | //span[@itemprop="creator"]/a/text()').getall()
        postTimes = response.xpath('//span[@class="timespan"]/@title').getall()
        postTexts = response.xpath('//div[@class="pb2"]/div').getall()
        postTexts = [self.clean_text(s) for s in postTexts]

        for i in range(len(usernames)):
            post = NuzforumsPost()
            post['topicId'] = topicId
            post['poster'] = usernames[i]
            post['time'] = postTimes[i]
            post['text'] = postTexts[i]
            yield post
        
        # parse next page if it exists
        nextPage = response.xpath("//a[@rel='next']/@href").get()
        if nextPage:
            yield scrapy.Request(
                response.urljoin(nextPage),
                callback=self.parse_posts,
                priority=-forumId-topicId,
                meta={'forumId': forumId, 'topicId': topicId}
            )

    def clean_text(self, string):
        soup = BeautifulSoup(string, 'html.parser')
        soup = soup.div.wrap(soup.new_tag('div'))
        soup.div.unwrap()
        text = str(soup).replace('\n','')
        return text
