"""
Tarık Burhan
"""


from time import sleep
from threading import Thread
import subprocess


# Threading is used for avoiding not restartable twisted reactor

def ks_scraper_runner(python_file:str, type_of_book:str, starting_page:str, ending_page:str):
    """
    Kitap Sepeti Scraper runner function that runs the python file as a subprocess in a new thread.

    :param str python_file: Name of the python file to be run
    :param str type_of_book: Book type of the scraped items
    :param str starting_page: Starting page of scraping
    :param str ending_page: Ending page of scraping
    """
    thread = Thread(target=subprocess.run, args=(["python", python_file, type_of_book, starting_page, ending_page],))
    thread.start()
    thread.join()

def ky_scraper_runner(python_file:str, starting_page:str, ending_page:str):
    """
    Kitap Yurdu Scraper runner function that runs the python file as a subprocess in a new thread.

    :param str python_file: Name of the python file to be run
    :param str starting_page: Starting page of scraping
    :param str ending_page: Ending page of scraping
    """
    thread = Thread(target=subprocess.run, args=(["python", python_file, starting_page, ending_page],))
    thread.start()
    thread.join()

def kitap_sepeti_runner(start: int, end: int):
    """
    Kitap Sepeti different types of books runner function.

    :param int start: Starting page of scraping
    :param int end: Ending page of scraping
    """
    ks_scraper_runner("kitap_sepeti_scraper.py", "cocuk-kitaplari", str(start), str(end))
    sleep(2)
    ks_scraper_runner("kitap_sepeti_scraper.py", "edebiyat", str(start), str(end))
    sleep(2)
    ks_scraper_runner("kitap_sepeti_scraper.py", "saglik", str(start), str(end))
    sleep(2)
    ks_scraper_runner("kitap_sepeti_scraper.py", "gezi-ve-rehber-kitaplari", str(start), str(end))
    sleep(2)
    ks_scraper_runner("kitap_sepeti_scraper.py", "insan-ve-toplum", str(start), str(end))
    sleep(2)
    ks_scraper_runner("kitap_sepeti_scraper.py", "psikoloji", str(start), str(end))
    sleep(2)
    ks_scraper_runner("kitap_sepeti_scraper.py", "hukuk", str(start), str(end))
    sleep(2)
    ks_scraper_runner("kitap_sepeti_scraper.py", "islam", str(start), str(end))
    sleep(2)
    ks_scraper_runner("kitap_sepeti_scraper.py", "egitim", str(start), str(end))
    sleep(2)
    ks_scraper_runner("kitap_sepeti_scraper.py", "inanc-kitaplari-mitolojiler", str(start), str(end))
    sleep(2)


# Getting starting page and ending page of scraping for both Kitap Sepeti and Kitap Yurdu
while True:
    try:
        ks_st_page = int(input("Starting Page of Kitap Sepeti \n"))
        ky_st_page = int(input("Starting Page of Kitap Yurdu \n"))
        break
    except:
        pass

while True:
    try:
        ks_end_page = int(input("Ending Page of Kitap Sepeti \n"))
        ky_end_page = int(input("Ending Page of Kitap Yurdu \n"))
        break
    except:
        pass

# Step size to avoid exceed cache
step = 2


# Infinite loop to scraping and can be terminated after scraping has been done and can be restarted after giving any other input
while True:
    print('Kitap Sepeti Scraper Starting in 5 seconds...')
    sleep(5)
    for x in range(ks_st_page, ky_st_page+1, step):
        kitap_sepeti_runner(x, x+step-1)
        sleep(1)

    print('Kitap Yurdu Scraper Starting in 4 seconds...')
    sleep(5)
    for x in range(ks_end_page, ky_end_page+1, step):
        ky_scraper_runner("kitap_yurdu_scraper.py", x, x+step-1)
    print('Scraping Ended for both Kitap Sepeti and Kitap Yurdu')
    sleep(5)
    try:
        input_val = int(input("Give an input 0 to terminate scraping.\n"))
        if input_val == 0:
            break
    except:
        pass
    