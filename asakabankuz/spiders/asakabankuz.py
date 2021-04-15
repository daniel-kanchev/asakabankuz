import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from asakabankuz.items import Article


class asakabankuzSpider(scrapy.Spider):
    name = 'asakabankuz'
    start_urls = ['https://asakabank.uz/ru/about-press']

    def parse(self, response):
        links = response.xpath('//a[@class="news_item"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="pull-right"]/text()').get()
        if date:
            date = " ".join(date.split()[1:])
        if not date:
            return

        content = response.xpath('//section[@class="section section--main"]//text()').getall() or \
                  response.xpath('//div[@class="section section--ptn textWrapper"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[3:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
