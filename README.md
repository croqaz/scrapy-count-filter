# Scrapy-count-filter

Downloader Middleware that allows a Scrapy Spider to stop requests after a number of pages, or items scraped.
There is a similar functionality in the [CloseSpider extension](https://scrapy.readthedocs.io/en/latest/topics/extensions.html#module-scrapy.extensions.closespider) that stops spiders after a number of pages, items, or errors, but this middleware allows defining rules per job and per domain.


## Install

This project requires [Python 3.6+](https://www.python.org/) and [pip](https://pip.pypa.io/). Using a [virtual environment](https://virtualenv.pypa.io/) is strongly encouraged.

```sh
$ pip install git+https://github.com/croqaz/scrapy-count-filter
```


## Usage

For the middleware to be enabled, it must be added in the project `settings.py`:

```
DOWNLOADER_MIDDLEWARES = {
    # maybe other Downloader Middlewares ...
    'scrapy_count_filter.middleware.CountFilterMiddleware': 995,
}
```

Also, the limits must be defined either in the spider instance, in a `spider.count_limits` dict.

Example when both counters are active:

```py
spider = {"page_count": 99, "item_count": 10}
```

Note that the Spider stops when ALL counters overflow.

-----

## License

[BSD3](LICENSE) © Cristi Constantin.
