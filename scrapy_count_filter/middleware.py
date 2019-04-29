import logging
from collections import defaultdict

from scrapy import signals
from scrapy.exceptions import IgnoreRequest, CloseSpider
from scrapy.utils.httpobj import urlparse_cached

logger = logging.getLogger(__name__)


def bool_match(max_value: int, current_value: int) -> bool:
    # Disabled match
    if max_value <= 0:
        return True
    # Failed match
    if current_value >= max_value:
        return False
    # Passed match
    return True


class CountFilterMiddleware:
    """
    Spider Middleware that allows a Scrapy Spider to stop requests,
    after a number of pages, or items scraped.
    """

    def __init__(self, crawler):
        self.crawler = crawler
        self.counter = defaultdict(int)
        self.page_host_counter = defaultdict(int)
        self.item_host_counter = defaultdict(int)

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)
        crawler.signals.connect(o.page_count, signal=signals.response_received)
        crawler.signals.connect(o.item_scraped, signal=signals.item_scraped)
        return o

    def page_count(self, response, request, spider):
        self.counter['page_count'] += 1
        host = urlparse_cached(request).netloc.lower()
        self.page_host_counter[host] += 1

    def item_scraped(self, item, spider, response):
        self.counter['item_count'] += 1
        host = urlparse_cached(response).netloc.lower()
        self.item_host_counter[host] += 1

    def process_request(self, request, spider):
        if not isinstance(getattr(spider, 'count_limits', False), dict):
            return
        count_limits = spider.count_limits
        if not count_limits:
            return

        page_count = count_limits.get('page_count', 0)
        item_count = count_limits.get('item_count', 0)
        page_host_count = count_limits.get('page_host_count', 0)
        item_host_count = count_limits.get('item_host_count', 0)

        extra = {'spider': spider}
        host = urlparse_cached(request).netloc.lower()

        # If all of the conditions are met, force close the spider
        if not bool_match(page_count, self.counter['page_count']) and \
           not bool_match(item_count, self.counter['item_count']) and \
           not bool_match(page_host_count, self.page_host_counter[host]) and \
           not bool_match(item_host_count, self.item_host_counter[host]):
            logger.info('All counters overflow, spider stopping!', extra=extra)
            raise CloseSpider('closespider_counters_overflow')

        url = request.url
        # If any of the conditions are met, start ignoring requests
        if not bool_match(page_count, self.counter['page_count']):
            logger.debug('Dropping link (pages %i>=%i): %s',
                         self.counter['page_count'],
                         page_count,
                         url,
                         extra=extra)
            self.crawler.stats.inc_value('dropped_requests/page_count_filtering')
            raise IgnoreRequest('page_count_filter')

        if not bool_match(item_count, self.counter['item_count']):
            logger.debug('Dropping link (items %i>=%i): %s',
                         self.counter['item_count'],
                         item_count,
                         url,
                         extra=extra)
            self.crawler.stats.inc_value('dropped_requests/item_count_filtering')
            raise IgnoreRequest('item_count_filter')

        if not bool_match(page_host_count, self.page_host_counter[host]):
            logger.debug('Dropping link (pages %i>=%i): %s',
                         self.page_host_counter[host],
                         page_host_count,
                         url,
                         extra=extra)
            self.crawler.stats.inc_value('dropped_requests/page_host_count_filtering')
            raise IgnoreRequest('page_host_count_filter')

        if not bool_match(item_host_count, self.item_host_counter[host]):
            logger.debug('Dropping link (items %i>=%i): %s',
                         self.item_host_counter[host],
                         item_host_count,
                         url,
                         extra=extra)
            self.crawler.stats.inc_value('dropped_requests/item_host_count_filtering')
            raise IgnoreRequest('item_host_count_filter')


DOWNLOADER_MIDDLEWARES = {
    'scrapy_count_filter.middleware.CountFilterMiddleware': 995,
}
