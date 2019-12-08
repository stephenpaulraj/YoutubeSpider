import scrapy
import os, sys
import re
import xlrd
import json
import requests
from urllib.parse import urljoin
from lxml import html
from channel.items import AboutChannelInfo
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class AboutCrawler(scrapy.Spider):
    name = 'channel_about_info_1'
    allowed_domains = ['youtube.com']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }

    custom_settings = {
        'ROBOTSTXT_OBEY': 'False',
    }

    def start_requests(self):
        channel_video_url_list = []
        file = xlrd.open_workbook(
            "/Users/rvmdigital/PycharmProjects/Scrapy_YoutubeChannel/Scrapy_Youtube_Channels/spiders/channels.xlsx")
        sheet = file.sheet_by_index(0)
        for k in range(1, sheet.nrows):
            channel_video_url_list.append(str(sheet.row_values(k)[0]))

        for i in range(len(channel_video_url_list)):
            item = AboutChannelInfo()
            yield scrapy.Request(
                url=channel_video_url_list[i],
                headers=self.headers,
                meta={'item': item},
                callback=self.parse_httpbin,
                errback=self.errback_httpbin,)

    def parse_httpbin(self, response):
        item = response.meta.get('item')

        data = re.search('ytInitialData"] = (.*?);', response.body_as_unicode(), re.DOTALL)
        if data:
            data = json.loads(data.group(1))

        json_data = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs')[5] \
            .get('tabRenderer', {}).get('content', {}).get('sectionListRenderer', {}).get('contents')[0] \
            .get('itemSectionRenderer', {}).get('contents')[0]

        json_sub_data = data.get('header', {}).get('c4TabbedHeaderRenderer', {}).get('subscriberCountText', {})

        channel_info_array = json_data.get('channelAboutFullMetadataRenderer')
        empty = ""
        test = channel_info_array.get('canonicalChannelUrl')
        if not test:
            item['about_channel_url'] = empty
        else:
            item['about_channel_url'] = test
        item['about_description'] = channel_info_array.get('description', {}).get('simpleText')
        item['about_channel_name'] = channel_info_array.get('title', {}).get('simpleText')
        item['about_subscribers'] = json_sub_data.get('runs')[0].get('text')
        item['about_joined'] = channel_info_array.get('joinedDateText', {}).get('runs')[1].get('text')
        item['about_views'] = channel_info_array.get('viewCountText', {}).get('runs')[0].get('text')
        item['about_location'] = channel_info_array.get('country', {}).get('simpleText')
        item['about_email_present'] = channel_info_array.get('businessEmailButton', {}).get('buttonRenderer', {}).get(
            'isDisabled')
        yield item

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
