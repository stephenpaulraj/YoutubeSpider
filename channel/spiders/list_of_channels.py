import scrapy
import os, sys
import re
import xlrd
import json
import requests
from urllib.parse import urljoin
from lxml import html
from channel.items import ListOfChannelItems


class ListOfChannels(scrapy.Spider):
    name = 'list_of_channels'
    allowed_domains = ['youtube.com']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }

    def start_requests(self):
        search_query_list = []

        file = xlrd.open_workbook("/Users/rvmdigital/Desktop/Stephen/den/channel/channel/spiders/input/searchList.xlsx")
        sheet = file.sheet_by_index(0)
        for k in range(1, sheet.nrows):
            search_query_list.append(str(sheet.row_values(k)[0]))

        for i in range(len(search_query_list)):
            item = ListOfChannelItems()
            yield scrapy.Request(
                url=search_query_list[i],
                headers=self.headers,
                meta={'item': item},
                callback=self.parse)

    def parse(self, response):
        item = response.meta.get('item')
        data = re.search('ytInitialData"] = (.*?);', response.body_as_unicode(), re.DOTALL)
        if data:
            data = json.loads(data.group(1))

        json_data = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}) \
            .get('sectionListRenderer', {}).get('contents')[0].get('itemSectionRenderer', {})

        ch_list_array = json_data.get('contents')
        for ch_info in ch_list_array:
            canonical_url = ch_info.get('channelRenderer', {}).get('navigationEndpoint', {}) \
                .get('browseEndpoint', {}).get('canonicalBaseUrl')
            youtube_link = "https://www.youtube.com" + canonical_url
            channel_name = ch_info.get('channelRenderer', {}).get('title', {}).get('simpleText')
            video_count = ch_info.get('channelRenderer', {}).get('videoCountText', {}).get('runs')[0].get('text')
            subscribers_count = ch_info.get('channelRenderer', {}).get('subscriberCountText', {}).get('simpleText')

            item['channel_url'] = youtube_link
            item['channel_name'] = channel_name
            item['subscribers'] = subscribers_count
            item['videos'] = video_count

            yield item

        continue_data = json_data.get('continuations')[0].get('nextContinuationData', {})
        ctoken = continue_data.get('continuation')

        ajax_url = 'https://www.youtube.com/browse_ajax?ctoken={ctoken}&continuation={ctoken}'.format(ctoken=ctoken)
        new_data = requests.get(ajax_url).json()