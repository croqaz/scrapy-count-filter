import pytest
from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.utils.test import get_crawler
from scrapy.exceptions import IgnoreRequest

from scrapy_count_filter.middleware import GlobalCountFilterMiddleware, HostsCountFilterMiddleware


def _mock_mw(spider, mwcls):
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
    return mwcls.from_crawler(crawler)


def test_g_disabled():
    spider = Spider('spidr')
    mw = _mock_mw(spider, GlobalCountFilterMiddleware)

    req = Request('http://quotes.toscrape.com')

    mw.page_count(None, req, spider)
    mw.process_request(req, spider)
    mw.page_count(None, req, spider)
    mw.process_request(req, spider)

    assert mw.counter['page_count'] == 2
    assert mw.crawler.engine.fake_spider_closed_result is None


def test_g_enabled():
    spider = Spider('spidr')
    spider.count_limits = {'page_count': 1, 'item_count': 1}
    mw = _mock_mw(spider, GlobalCountFilterMiddleware)

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


def test_h_disabled():
    spider = Spider('spidr')
    mw = _mock_mw(spider, HostsCountFilterMiddleware)

    req = Request('http://quotes.toscrape.com')

    mw.page_count(None, req, spider)
    mw.process_request(req, spider)
    mw.page_count(None, req, spider)
    mw.process_request(req, spider)

    assert mw.page_host_counter['quotes.toscrape.com'] == 2


def test_h_enabled():
    spider = Spider('spidr')
    spider.count_limits = {'page_host_count': 1, 'item_host_count': 1}
    mw = _mock_mw(spider, HostsCountFilterMiddleware)

    req = Request('http://quotes.toscrape.com')

    mw.page_count(None, req, spider)
    mw.process_request(req, spider)

    with pytest.raises(IgnoreRequest):
        mw.page_count(None, req, spider)
        mw.process_request(req, spider)

    assert mw.page_host_counter['quotes.toscrape.com'] == 2
