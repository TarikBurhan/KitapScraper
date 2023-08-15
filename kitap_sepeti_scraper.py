"""
Tarık Burhan
"""


import sys
import scrapy
from scrapy.crawler import CrawlerProcess
from database_functions import Database

# In the website, books have been divided to their types. Scraping website url changes with book type.
try:
    book_type = sys.argv[1]
except:
    sys.exit('Book type should be given as an argument')

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

class KitapSepetiKitapScraper(scrapy.Spider):
    """
    Kitap Sepeti main book website scraper that scrapes more detailed info of the book.
    """
    name = "KitapSepetiKitap"
    domain = "https://www.kitapsepeti.com"
    my_db = Database("mongodb://localhost:27017", "smartmaple", "kitapsepeti")

    def __init__(self, info: dict, url: str):
        """
        :param dict info: Scraped item that are passed from main website scraper to be added in database
        :param str url: Book website url that is going to be scraped.
        """
        self.info = info
        self.url = url

    def start_requests(self):
        yield scrapy.Request(self.url)
    
    def parse(self, response):
        """
        Parsing detailed book info in the book website.
        """        
        detail_book_info = response.css('div.col.cilt.col-12').css('div.fl.col-6')
        self.info['book_type'] = detail_book_info[0].xpath('span')[1].xpath('text()').get()
        self.info['total_page'] = detail_book_info[1].xpath('span')[1].xpath('text()').get()
        self.info['isbn'] = detail_book_info[2].xpath('span')[1].xpath('text()').get()
        self.info['book_size'] = detail_book_info[3].xpath('span')[1].xpath('text()').get()
        self.info['release_date'] = detail_book_info[6].xpath('span')[1].xpath('text()').get()
        self.info['summary'] = '\n'.join(response.xpath('/html/body/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div[2]/div/ul/li[1]/div/div/div/p/text()').extract())
        
        self.my_db.insert(self.info)



class KitapSepetiScraper(scrapy.Spider):
    """
    Kitap Sepeti main website scraper that gets url's of books and starts more detailed book info scraper.
    """

    name = "KitapSepeti"
    domain = "https://www.kitapsepeti.com"
    my_db = Database("mongodb://localhost:27017", "smartmaple", "kitapsepeti")

    def __init__(self, type_of_book: str, starting_page: int, ending_page: int):
        """
        :param str type_of_book: Type of the book to be scraped in website
        :param int starting_page: Starting page of scraping the items in website
        :param int ending_page: Ending page of scraping the items in website
        """
        self.type_of_book = type_of_book
        self.starting_page = starting_page
        self.ending_page = ending_page
        self.run = True

    def start_requests(self):
        yield scrapy.Request(f"https://www.kitapsepeti.com/{self.type_of_book}?stock=1&pg={self.starting_page}")

    def parse(self, response):
        """
        Parsing url, price, title, writers and publisher of the book in the given page.
        """
        if self.run:
            page = response.xpath('/html/body/div[2]/div/div/div/div/div/div/div[3]/div/div[2]/div/div').css('div.col.col-3.col-md-4.col-sm-6.col-xs-6.p-right.mb.productItem.zoom.ease')
            for div in page:
                book_info = div.css('div.box.col-12.text-center').xpath('div/a')
                title = book_info[0].xpath('text()').get().replace('\n', '')
                publisher = book_info[1].xpath('text()').get().replace('\n', '')
                writers = book_info[2].xpath('text()').get().replace('\n', '')
                price = div.css('div.col.col-12.currentPrice').xpath('text()').get().replace('\n', '')

                book_page_url = div.css('div.col.col-12.drop-down.hover.lightBg').css('div.row')[0].xpath('a').attrib['href']
                book_page_url = self.domain + book_page_url
                item = {
                "title": title,
                "publisher": publisher,
                "writers": writers,
                "price": price,
                "url": book_page_url
                }
                # If scraped book is already in the database, updates the price of the book
                if self.my_db.exists("url", book_page_url) == 0:
                    process.crawl(KitapSepetiKitapScraper, info=item, url=book_page_url)
                else:
                    self.my_db.update_one('url', book_page_url, 'price', price)

            # Continue scraping to the ending page
            if self.starting_page != 0 and self.run:
                for next_page in range(self.starting_page, self.ending_page + 1):
                    yield (scrapy.Request(f'https://www.kitapsepeti.com/{self.type_of_book}?stock=1&pg={next_page}',
                                          callback=self.parse))



# Scraping starts with adding scraper to the process with appropriate parameters.
process.crawl(KitapSepetiScraper, type_of_book = book_type, starting_page=scraping_starting_page, ending_page=scraping_ending_page)
process.start()