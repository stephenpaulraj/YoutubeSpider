import scrapy


class AboutChannelInfo(scrapy.Item):
    about_channel_url = scrapy.Field()
    about_channel_name = scrapy.Field()
    about_subscribers = scrapy.Field()
    about_description = scrapy.Field()
    about_joined = scrapy.Field()
    about_views = scrapy.Field()
    about_location = scrapy.Field()
    about_email_present = scrapy.Field()


class ListOfChannelItems(scrapy.Item):
    channel_url = scrapy.Field()
    channel_name = scrapy.Field()
    videos = scrapy.Field()
    subscribers = scrapy.Field()
