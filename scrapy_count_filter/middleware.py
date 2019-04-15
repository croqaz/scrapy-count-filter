import logging
from collections import defaultdict

from scrapy import signals
from scrapy.exceptions import IgnoreRequest, CloseSpider

logger = logging.getLogger(__name__)


class CountFilterMiddleware:
    """
    Spider Middleware that allows a Scrapy Spider to stop requests,
    after a number of pages, or items scraped.
    """

    def __init__(self, crawler):
        self.crawler = crawler
        self.counter = defaultdict(int)

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)
        crawler.signals.connect(o.page_count, signal=signals.response_received)
        crawler.signals.connect(o.item_scraped, signal=signals.item_scraped)
        return o

    def page_count(self, response, request, spider):
        self.counter['page_count'] += 1

    def item_scraped(self, item, spider):
        self.counter['item_count'] += 1

    def process_request(self, request, spider):
        if not isinstance(getattr(spider, 'count_limits', False), dict):
            return

        page_count = spider.count_limits.get('page_count', 0)
        item_count = spider.count_limits.get('item_count', 0)
        extra = {'spider': spider}

        # If all conditions are met, force close the spider
        if page_count and self.counter['page_count'] >= page_count and \
                item_count and self.counter['item_count'] >= item_count:
            logger.info('Page count and item count overflow, spider stopping!', extra=extra)
            raise CloseSpider('closespider_countlimit')

        if page_count and self.counter['page_count'] >= page_count:
            logger.debug('Dropping link: %s', request.url, extra=extra)
            self.crawler.stats.inc_value('page_count_filtering/dropped_requests')
            raise IgnoreRequest

        if item_count and self.counter['item_count'] >= item_count:
            logger.debug('Dropping link: %s', request.url, extra=extra)
            self.crawler.stats.inc_value('item_count_filtering/dropped_requests')
            raise IgnoreRequest


DOWNLOADER_MIDDLEWARES = {
    'scrapy_count_filter.middleware.CountFilterMiddleware': 995,
}
