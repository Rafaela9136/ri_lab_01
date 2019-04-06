# -*- coding: utf-8 -*-
import scrapy
import json

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem

class Brasil247Spider(scrapy.Spider):
    name = 'brasil_247'
    allowed_domains = ['brasil247.com']
    start_urls = []
    months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    def __init__(self, *a, **kw):
        super(Brasil247Spider, self).__init__(*a, **kw)
        with open('seeds/brasil_247.json') as json_file:
            data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        links = response.css('h3 a::attr(href)').getall()[2:]
        main_article = response.css('h2 a::attr(href)').get()

        links.append(main_article)

        # Follow found links to capture details about the articles
        for i in range(0, len(links)):
            yield response.follow(links[i], callback=self.parse_article_detail)

    def parse_article_detail(self, response):
        item = RiLab01Item()

        item['title'] = response.css('h1::text').get()

        item['sub_title'] = response.xpath('//p[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]/text()').get()

        author = response.css('section p strong::text, strong a::text').get()
        item['author'] = self.format_author(author)

        item['date'] = self.format_date(
            response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "meta", " " ))]/text()').get())

        item['section'] = response.url.split('/')[5]

        item['text'] = self.format_text(
            response.css('.entry p::text, p span::text, p a::text, entry span::text, strong::text').getall(), author)

        item['url'] = response.url

        yield item

    def format_author(self, author):
        for ch in ['-', ',', "–"]:
            author = author.replace(ch, '')

        if ":" in author:
            author = author.split(':')[1]
        return author

    def format_text(self, texts, author):
        formatted_text = ''

        for i in range(1, len(texts) - 1):
            formatted_text = formatted_text + texts[i] + ' '
        formatted_text = formatted_text + texts[len(texts) - 1]

        formatted_text = formatted_text.split(author)[1]
        return formatted_text

    def format_date(self, date):
        splitted_date = date.split(' ')

        day = int(splitted_date[0])
        month = self.months.index(splitted_date[2]) + 1
        year = splitted_date[4]
        hour = splitted_date[6].split('\n')[0]

        return "%02d/%02d/%s %s:00" % (day, month, year, hour)
