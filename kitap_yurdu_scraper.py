"""
Tarık Burhan
"""


import sys
import scrapy
from scrapy.crawler import CrawlerProcess
from database_functions import Database


# Starting and ending page of the scraping has been given as arguments in scrapper runner.
# Casting type of arguments to int because given arguments taken as str.
try:
    scraping_starting_page = int (sys.argv[2])
except:
    scraping_starting_page = 1

try:
    scraping_ending_page = int (sys.argv[3])
except:
    scraping_ending_page = 5



# Crawler Process initialization
process = CrawlerProcess(
    settings={
        'LOG_LEVEL': "INFO",
        'FEED_EXPORT_ENCODING': 'utf-8',
        "DOWNLOAD_DELAY": 0.25
    }
)


class KitapYurduKitapScraper(scrapy.Spider):
    """
    Kitap Yurdu main book website scraper that scrapes more detailed info of the book.
    """
    name = "KitapYurduKitap"
    domain = "https://www.kitapyurdu.com"
    my_db = Database("mongodb://localhost:27017", "smartmaple", "kitapyurdu")

    def __init__(self, info: dict, url: str):
        """
        :param dict info: Scraped item that are passed from main website scraper to be added in database
        :param str url: Book website url that is going to be scraped.
        """
        self.info = info
        self.url = url
        # Mapping has been added because of in Kitap Yurdu, detailed book info is not in a formatted system such as 
        # ISBN value is not in the same place or not exists in some books.
        self.info_mapping = {'Yayın Tarihi': 'release_date', 'ISBN': 'isbn', 'Sayfa Sayısı': 'total_page', 
                             'Boyut': 'book_size'}

    def start_requests(self):
        yield scrapy.Request(self.url)
    
    def parse(self, response):
        """
        Parsing detailed book info in the book website.
        """
        book_info = response.css('div.attributes').xpath('table/tr')
        writer_publisher_info = response.css('a.pr_producers__link')
        self.info['title'] = response.css('h1.pr_header__heading::text').get()
        self.info['publisher'] = writer_publisher_info[1].xpath('text()').get()
        self.info['writers'] = writer_publisher_info[0].xpath('text()').get()[1:]
        self.info['book_type'] = response.css('li.rel-cats__item')[0].xpath('a/span')[1].xpath('text()').get()
        for info in book_info:
            info_name = info.xpath('td')[0].xpath('text()').get().replace(':', '')
            if info_name in self.info_mapping:
                self.info[self.info_mapping[info_name]] = info.xpath('td')[1].xpath('text()').get()
        self.info['summary'] = '\n'.join(response.css('span.info__text::text').extract())

        self.my_db.insert(self.info)


class KitapYurduScraper(scrapy.Spider):
    """
    Kitap Yurdu main website scraper that gets url's of books and starts more detailed book info scraper.
    """
    name = "KitapYurdu"
    domain = "https://www.kitapyurdu.com"
    my_db = Database("mongodb://localhost:27017", "smartmaple", "kitapyurdu")

    def __init__(self, starting_page: int, ending_page: int):
        """
        :param int starting_page: Starting page of scraping the items in website
        :param int ending_page: Ending page of scraping the items in website
        """
        self.starting_page = starting_page
        self.ending_page = ending_page
        self.run = True

    def start_requests(self):
        yield scrapy.Request(f"https://www.kitapyurdu.com/index.php?route=product/category&page={self.starting_page}&filter_category_all=true&path=1&filter_in_stock=1&sort=purchased_365&order=DESC&limit=50")

    def parse(self, response):
        """
        Parsing url and price of the book in the given page.
        """
        if self.run:
            page = response.css('div.product-cr')
            for div in page:
                book_page_url = div.css('div.image').css('a.pr-img-link').attrib['href']
                price = div.css('div.price-new').css('span.value::text').extract()[0].replace(' ', '')
                book_page_url = book_page_url
                item = {
                "url": book_page_url,
                "price": price
                }
                # If scraped book is already in the database, updates the price of the book
                if self.my_db.exists("url", book_page_url) == 0:
                   process.crawl(KitapYurduKitapScraper, info=item, url=book_page_url)
                else:
                   self.my_db.update_one('url', book_page_url, 'price', price)


            # Continue scraping to the ending page
            if self.starting_page != 0 and self.run:
                for next_page in range(self.starting_page, self.ending_page + 1):
                    yield (scrapy.Request(f'https://www.kitapyurdu.com/index.php?route=product/category&page={next_page}&filter_category_all=true&path=1&filter_in_stock=1&sort=purchased_365&order=DESC&limit=50',
                                          callback=self.parse))



# Scraping starts with adding scraper to the process with appropriate parameters.
process.crawl(KitapYurduScraper, starting_page=scraping_starting_page, ending_page=scraping_ending_page)
process.start()