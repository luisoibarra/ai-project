from datetime import date
from ..items import LetterToDirectionItem
import scrapy


class LettersToDirectionSpider(scrapy.Spider):
    name = 'letters_to_direction'
    allowed_domains = ['www.granma.cu']
    start_urls = ['http://www.granma.cu/']
    base_url = 'http://www.granma.cu'

    letters_to_direction_section = 14
    
    def __init__(self, initial_page = 1, max_page=144, **kwargs):
        super().__init__(**kwargs)
        self.initial_page = initial_page
        self.max_page = max_page

    def start_requests(self):
        page = self.initial_page
        while page <= self.max_page:
            yield scrapy.Request(url=f"{self.base_url}/archivo?page={page}&q=&s={self.letters_to_direction_section}", callback=self.parse)

    def parse(self, response):
        links_to_letters = response.xpath('//h2/a[contains(@href, "/cartas/")]/@href')
        for link in links_to_letters.getall():
            yield scrapy.Request(url=f"{self.base_url}{link}", callback=self.parse_letter)

    
    def parse_letter(self, response):

        title = response.xpath('//h1[contains(@itemprop, "headline")]/text()').get()
        texts = response.xpath('//div[contains(@itemprop, "articleBody")]/p/text()').getall()
        
        original_letter_link = None
        if response.xpath('//h3[contains(text(), "Responde a:")]'):
            response_to_letter = response.xpath('//h4/a[contains(@href, "/cartas/")]')
            original_letter_link = f"{self.base_url}{response_to_letter.xpath('@href').get()}"

        date_str = response.url.split("/")[-2]
        comments = response.xpath('//p[contains(@class, "comment-message")]/text()').getall()

        self.log(f"Letter: {response.url}")

        if not texts:
            self.log(f"EMPTY Letter: {response.url}")

        item = LetterToDirectionItem(
            title=title,
            body="\n".join(texts),
            link=response.url,
            original_letter_link=original_letter_link,
            is_response=original_letter_link is not None,
            date=date_str,
            comments=comments
        )
        
        yield item
