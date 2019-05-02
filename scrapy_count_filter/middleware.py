import logging
from collections import defaultdict

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.httpobj import urlparse_cached

logger = logging.getLogger(__name__)


class CountFilterMiddleware:
    """
    Downloader Middleware that allows a Scrapy Spider to stop requests,
    after a number of pages, or items scraped.
    """

    def __init__(self, crawler):
        self.crawler = crawler
        self.counter = defaultdict(int)
        self.page_host_counter = defaultdict(int)
        self.item_host_counter = defaultdict(int)
        self._close_spider = crawler.settings.getbool('COUNT_FILTER_CLOSE_SPIDER', False)
        self._ignore_hosts = crawler.settings.get('COUNT_FILTER_IGNORE_HOSTS', [])

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)
        crawler.signals.connect(o.page_count, signal=signals.response_received)
        crawler.signals.connect(o.item_scraped, signal=signals.item_scraped)
        return o

    def page_count(self, response, request, spider):
        self.counter['page_count'] += 1
        host = urlparse_cached(request).netloc.lower()
        if host not in self._ignore_hosts:
            self.page_host_counter[host] += 1

    def item_scraped(self, item, spider, response):
        self.counter['item_count'] += 1
        host = urlparse_cached(response).netloc.lower()
        if host not in self._ignore_hosts:
            self.item_host_counter[host] += 1

    def process_request(self, request, spider):
        if not isinstance(getattr(spider, 'count_limits', False), dict):
            return
        count_limits = spider.count_limits
        if not count_limits:
            return

        max_page_count: int = count_limits.get('page_count', 0)
        max_item_count: int = count_limits.get('item_count', 0)
        max_page_host_count: int = count_limits.get('page_host_count', 0)
        max_item_host_count: int = count_limits.get('item_host_count', 0)

        host: str = urlparse_cached(request).netloc.lower()

        conditions = []

        if max_page_count > 0:
            conditions.append(self.counter['page_count'] > max_page_count)
        if max_item_count > 0:
            conditions.append(self.counter['item_count'] > max_item_count)
        if max_page_host_count > 0:
            conditions.append(self.page_host_counter[host] > max_page_host_count)
        if max_item_host_count > 0:
            conditions.append(self.item_host_counter[host] > max_item_host_count)

        # If all conditions are met, start ignoring requests
        if all(conditions):
            extra = {'spider': spider}
            if self._close_spider:
                logger.info('Spider shutdown (count overflow)', extra=extra)
                self.crawler.engine.close_spider(spider, 'closespider_counters_overflow')
                return

            logger.debug('Dropping link (count overflow): %s', request.url, extra=extra)
            self.crawler.stats.inc_value('count_filter/dropped_requests')
            raise IgnoreRequest('counters_overflow')


DOWNLOADER_MIDDLEWARES = {
    # other middlewares ...
    'scrapy_count_filter.middleware.CountFilterMiddleware': 995
}
