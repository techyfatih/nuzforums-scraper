# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

# https://stackoverflow.com/questions/43630434/how-to-handle-a-429-too-many-requests-response-in-scrapy
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import logging
import time

RETRY_DELAY = 60

class TooManyRequestsRetryMiddleware(RetryMiddleware):
    def __init__(self, crawler):
        super(TooManyRequestsRetryMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        elif response.status == 429:
            logging.warning('Too many requests, retrying in {} seconds...{}'.format(RETRY_DELAY, response))
            self.crawler.engine.pause()
            time.sleep(RETRY_DELAY)
            self.crawler.engine.unpause()
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        elif response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response 