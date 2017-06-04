import logging
from logging.handlers import RotatingFileHandler
import requests
from bs4 import BeautifulSoup

# urls
item_urls = [
    'https://www.newegg.com/Product/ProductList.aspx?Submit=ENE&N=100007709&IsNodeId=1&Description=rx%20580&name=Desktop%20Graphics%20Cards&Order=BESTMATCH&isdeptsrh=1',
    'https://www.newegg.com/Product/ProductList.aspx?Submit=ENE&N=100007709&IsNodeId=1&Description=rx%20570&name=Desktop%20Graphics%20Cards&Order=BESTMATCH&isdeptsrh=1'
]

class StockChecker:
    def __init__(self):
        self.__setup_logging(logging.INFO, '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def __setup_logging(self, level, format_string):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(level)
        formatter = logging.Formatter(format_string)

        # STDOUT
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def __get_items(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup.find_all('div', class_='item-container')

    def __is_in_stock(self, item):
        in_stock = False
        promo = item.get_text()
        if (promo and "OUT OF STOCK" not in promo):
            in_stock = True
        return in_stock

    def check_stock(self, urls): # get all items
        self._logger.info('Beginning stock check...')
        in_stock_urls = []

        for url in urls:
            # initialize
            self._logger.info('Checking stock for {}'.format(url))
            in_stock = 0
            out_of_stock = 0

            # find items for a given url
            items = self.__get_items(url)
            self._logger.info('Found {} items...'.format(len(items)))

            # process items on page
            for item in items:
                if (self.__is_in_stock(item)):
                    link = item.find('a', class_="item-title")['href']
                    self._logger.info("IN STOCK - {}".format(link))
                    in_stock_urls.append(link)
                    in_stock += 1
                else:
                    out_of_stock += 1

            self._logger.info('{}/{} of these items are in stock.\n'.format(in_stock, out_of_stock + in_stock))

        self._logger.info('Done checking stock.\n')

        return in_stock_urls

if __name__ == '__main__':
    stock = StockChecker()
    stock_list = stock.check_stock(item_urls)
    if len(stock_list) > 0:
        print('\n'.join(stock_list))
