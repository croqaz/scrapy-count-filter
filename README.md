# Scrapy-count-filter

![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Two Downloader Middlewares that allows a [Scrapy Spider](https://scrapy.readthedocs.io/en/latest/topics/spiders.html) to stop requests after a number of pages, or items are scraped.
There is a similar functionality in the [CloseSpider extension](https://scrapy.readthedocs.io/en/latest/topics/extensions.html#module-scrapy.extensions.closespider) that stops spiders after a number of pages, items, or errors, but this middleware allows defining counters per domain, and define them as spider arguments instead of project settings.


## Install

This project requires [Python 3.6+](https://www.python.org/) and [pip](https://pip.pypa.io/). Using a [virtual environment](https://virtualenv.pypa.io/) is strongly encouraged.

```sh
$ pip install git+https://github.com/croqaz/scrapy-count-filter
```


## Usage

For the middlewares to be enabled, they must be added in the project `settings.py`:

```
DOWNLOADER_MIDDLEWARES = {
    # maybe other Downloader Middlewares ...
    'scrapy_count_filter.middleware.GlobalCountFilterMiddleware': 995,
    'scrapy_count_filter.middleware.HostsCountFilterMiddleware': 996,
}
```

You can use one, or the other, or both middlewares.

The counter limits must be defined in the spider instance, in a `spider.count_limits` dict.

The possible fields are:
* `page_count` and `item_count` - are used by the GlobalCountFilterMiddleware to stop the spider, if the number of requests, or items scraped is larger than the value provided
* `page_host_count` and `item_host_count` - are used by the HostsCountFilterMiddleware to start ignoring requests, if the number of requests, or items scraped *per host* is larger than the value provided

All field values must be integers.

Note that the Spider stops when **any of the counters** overflow.


Example when the count of requests, and items scraped are active:

```py
from scrapy.spiders import Spider

class MySpider(Spider):
    count_limits = {"page_count": 99, "item_count": 10}
```

-----

## License

[BSD3](LICENSE) © Cristi Constantin.
