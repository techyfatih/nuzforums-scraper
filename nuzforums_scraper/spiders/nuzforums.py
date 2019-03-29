# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from nuzforums_scraper.items import NuzforumsPost

class NuzforumsSpider(scrapy.Spider):
    name = 'nuzforums'
    allowed_domains = ['tapatalk.com']
    start_urls = ['https://www.tapatalk.com/groups/nuzlocke_forum/ucp.php?mode=login']
    username = ''
    password = ''

    def parse(self, response):
        formRequest = scrapy.FormRequest.from_response(
            response,
            formid='login',
            formdata={'username': self.username, 'password': self.password, 'login': 'Login'},
            callback=self.after_login,
        )
        return formRequest

    def after_login(self, response):
        if 'index' in response.url:
            self.log("login success")
            links = response.xpath('//a[@class="forumtitle"]/@href').extract()
            yield scrapy.Request(response.urljoin(links[0]),callback=self.parse_topics)
            #for link in links:
            #    yield scrapy.Request(response.urljoin(link),callback=self.parse_topics)
        else:
            self.log("login fail")
    
    def parse_topics(self, response):
        #REQUEST TOPIC TITLE LINKS
        links = response.xpath('//a[@class="topictitle"]/@href').extract()
        yield scrapy.Request(response.urljoin(links[0]),callback=self.parse_posts)
        #for link in links:
        #    yield scrapy.Request(response.urljoin(link),callback=self.parse_posts)
        
        #IF NEXT PAGE EXISTS, FOLLOW
        #Next = response.xpath("//li[@class='next']//a[@rel='next']/@href").extract_first()
        #if Next:
        #    yield scrapy.Request(response.urljoin(Next),callback=self.parse_topics)

    def parse_posts(self, response):
        #COLLECT FORUM POST DATA
        usernames = response.xpath('//span[@itemprop="name"]/a/text() | //span[@itemprop="creator"]/a/text()').extract()
        postTimes = response.xpath('//span[@class="timespan"]/@title').extract()
        postTexts = response.xpath('//div[@class="pb2"]/div').extract()
        postTexts = [self.clean_text(s) for s in postTexts]

        #YIELD POST DATA
        for i in range(len(usernames)):
            post = NuzforumsPost()
            post['username'] = usernames[i]
            post['time'] = postTimes[i]
            post['text'] = postTexts[i]
            
            yield post
        
        #CLICK THROUGH NEXT PAGE
        Next = response.xpath("//li[@class='arrow next']/a[@rel='next']/@href").extract_first()
        self.log(Next)
        if Next:
            yield scrapy.Request(response.urljoin(Next),callback=self.parse_posts)

    def clean_text(self, string):
        soup = BeautifulSoup(string, 'html.parser')
        soup = soup.div.wrap(soup.new_tag('div'))
        soup.div.unwrap()
        text = str(soup).replace('\n','')
        return text
