from scrapy.spiders import Spider
from scrapy.http import Request, Response
from scrapy.utils.test import get_crawler

from scrapy_count_filter.middleware import GlobalCountFilterMiddleware


def _mock_mw(spider):
    class MockedDownloader:
        slots = {}

        def _get_slot_key(self, a, b):
            return str(a) + str(b)

    class MockedEngine:
        downloader = MockedDownloader()
        fake_spider_closed_result = None

        def close_spider(self, spider, reason):
            self.fake_spider_closed_result = (spider, reason)

    # with `spider` instead of `type(spider)` raises an exception
    crawler = get_crawler(type(spider))
    crawler.engine = MockedEngine()
    return GlobalCountFilterMiddleware.from_crawler(crawler)


def test_disabled():
    spider = Spider('spidr')
    mw = _mock_mw(spider)

    req = Request('http://quotes.toscrape.com')

    mw.page_count(None, req, spider)
    mw.process_request(req, spider)
    mw.page_count(None, req, spider)
    mw.process_request(req, spider)

    assert mw.counter['page_count'] == 2
    assert mw.crawler.engine.fake_spider_closed_result is None


def test_enabled():
    spider = Spider('spidr')
    spider.count_limits = {'page_count': 1, 'item_count': 1}
    mw = _mock_mw(spider)

    req = Request('http://quotes.toscrape.com')
    mw.page_count(None, req, spider)
    mw.process_request(req, spider)

    assert mw.counter['page_count'] == 1

    mw.page_count(None, req, spider)
    mw.process_request(req, spider)

    assert mw.counter['page_count'] == 2
    closed_result = mw.crawler.engine.fake_spider_closed_result
    assert closed_result is not None
    assert closed_result[1] == 'closespider_global_counters_overflow'
