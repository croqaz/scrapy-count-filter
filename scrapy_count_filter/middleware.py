import logging
from collections import defaultdict

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.httpobj import urlparse_cached

logger = logging.getLogger(__name__)


class GlobalCountFilterMiddleware:
    """
    Downloader Middleware that allows a Scrapy Spider to stop the spider,
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

    def item_scraped(self, item, spider, response):
        self.counter['item_count'] += 1

    def process_request(self, request, spider):
        if not isinstance(getattr(spider, 'count_limits', False), dict):
            return
        count_limits = spider.count_limits
        if not count_limits:
            return

        conditions = []

        max_page_count: int = count_limits.get('page_count', 0)
        max_item_count: int = count_limits.get('item_count', 0)

        if max_page_count > 0:
            conditions.append(self.counter['page_count'] > max_page_count)
        if max_item_count > 0:
            conditions.append(self.counter['item_count'] > max_item_count)

        # If any of the conditions are met, start ignoring requests
        if any(conditions):
            logger.info('Spider shutdown (count overflow)', extra={'spider': spider})
            self.crawler.engine.close_spider(spider, 'closespider_global_counters_overflow')


class HostsCountFilterMiddleware:
    """
    Downloader Middleware that allows a Scrapy Spider to stop requests,
    or optionally stop the spider after a number of pages, or items scraped.
    """

    def __init__(self, crawler):
        self.crawler = crawler
        self.page_host_counter = defaultdict(int)
        self.item_host_counter = defaultdict(int)
        self._ignore_hosts = crawler.settings.get('COUNT_FILTER_IGNORE_HOSTS', [])

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)
        crawler.signals.connect(o.page_count, signal=signals.response_received)
        crawler.signals.connect(o.item_scraped, signal=signals.item_scraped)
        return o

    def page_count(self, response, request, spider):
        host = urlparse_cached(request).netloc.lower()
        if host not in self._ignore_hosts:
            self.page_host_counter[host] += 1

    def item_scraped(self, item, spider, response):
        host = urlparse_cached(response).netloc.lower()
        if host not in self._ignore_hosts:
            self.item_host_counter[host] += 1

    def process_request(self, request, spider):
        if not isinstance(getattr(spider, 'count_limits', False), dict):
            return
        count_limits = spider.count_limits
        if not count_limits:
            return

        max_page_host_count: int = count_limits.get('page_host_count', 0)
        max_item_host_count: int = count_limits.get('item_host_count', 0)

        host: str = urlparse_cached(request).netloc.lower()

        conditions = []

        if max_page_host_count > 0 and self.page_host_counter[host] > 0:
            conditions.append(self.page_host_counter[host] > max_page_host_count)
        if max_item_host_count > 0 and self.item_host_counter[host] > 0:
            conditions.append(self.item_host_counter[host] > max_item_host_count)

        # If any of the conditions are met, start ignoring requests
        if any(conditions):
            logger.debug('Dropping request (count overflow): %s', request, extra={'spider': spider})
            self.crawler.stats.inc_value('hosts_count_filter/dropped_requests')
            raise IgnoreRequest('counters_overflow')


DOWNLOADER_MIDDLEWARES = {
    # other middlewares ...
    'scrapy_count_filter.middleware.GlobalCountFilterMiddleware': 995,
    'scrapy_count_filter.middleware.HostsCountFilterMiddleware': 996,
}
