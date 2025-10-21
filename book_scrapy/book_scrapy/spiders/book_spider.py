from typing import Generator

import scrapy
from scrapy.http import Response
from word2number import w2n


class QuotesSpider(scrapy.Spider):
    name = "books"
    start_urls = [
        "https://books.toscrape.com/",
    ]


    def parse(self, response: Response, **kwargs):
        for book_link in response.css(".image_container a::attr(href)").getall():
            full_url = response.urljoin(book_link)
            yield scrapy.Request(full_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def parse_book(self, response: Response, **kwargs) -> Generator[dict, None, None]:
            quote = response.css(".content")
            yield {
                "title": quote.css(".product_main h1::text").get(),
                "price": quote.css(".product_main p.price_color::text").get().replace("£", ""),
                "amount_in_stock": quote.css(".product_main p.instock::text").re_first(r"\d+"),
                "rating": w2n.word_to_num(quote.css(".product_main p.star-rating::attr(class)").get().split()[-1]),
                "category": response.css(".breadcrumb li a::text")[2].get(),
                "description": quote.css("#product_description + p::text").get(),
                "upc": quote.css(".table-striped tr td::text")[0].get(),
            }
