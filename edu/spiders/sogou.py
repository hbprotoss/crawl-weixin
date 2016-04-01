#!/usr/bin/env python
# coding=utf-8
import urllib

import requests
import scrapy

from edu.items import EduItem

__author__ = 'hbprotoss'


def to_text(raw_list):
    return ''.join(raw_list).strip()


class SogouSpider(scrapy.Spider):
    name = "sogou"
    allowed_domains = ["www.sogou.com"]
    # start_urls = [
    #     "https://www.sogou.com/web?query=%E6%95%99%E8%82%B2+site%3Amp.weixin.qq.com&q=%E6%95%99%E8%82%B2&page=1&ie=utf8"
    # ]

    def start_requests(self):
        for i in range(1, int(self.settings["PAGES"]) + 1):
            yield self.make_requests_from_url(
                "http://weixin.sogou.com/weixin?query=%s&type=2&page=%d&ie=utf8" % (
                    urllib.quote(self.settings["KEYWORD"]), i
                )
            )

    def parse(self, response):
        search_results = response.xpath('//div[@class="wx-rb wx-rb3"]')
        self.snuid = self.get_snuid(response.headers.getlist('Set-Cookie'))

        for result in search_results:
            item = EduItem()
            item['title'] = to_text(result.xpath('div/h4/a//text()').extract())
            item['link'] = self.get_location("http://weixin.sogou.com" + to_text(result.xpath('div/h4/a/@href').extract()))
            item['desc'] = to_text(result.xpath('div/p//text()').extract())
            yield item

    def get_snuid(self, cookies):
        for cookie in cookies:
            if cookie.startswith('SNUID'):
                return cookie.split(';', 1)[0].split('=')[-1]
        return ''

    def get_location(self, url):
        try:
            r = requests.head(url, cookies={"SNUID": self.snuid})
            if r.status_code == 302:
                return r.headers['Location']
            else:
                return url
        except requests.RequestException, e:
            self.logger.error("failed to follow sogou result link{%s}, message{%s}", url, e)
            return url

