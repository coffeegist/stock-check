import os
import logging
import requests
from bs4 import BeautifulSoup

from twilio_messenger import TwilioMessenger
from db import PostDB

LINK_COL = 0 # link
SMS_COL = 1 # phone number link was sms'ed to
LINKS_PER_MESSAGE = 10 # send up to 10 links at a time

# urls
item_urls = [
    'https://www.newegg.com/Product/ProductList.aspx?Submit=ENE&DEPA=0&Order=BESTMATCH&Description=rx+580&N=100007709%20600494828%20600007787&isNodeId=1', # 4G/8G RX 580
    'https://www.newegg.com/Product/ProductList.aspx?Submit=ENE&N=100007709%20600007787&IsNodeId=1&Description=rx%20570&name=Desktop%20Graphics%20Cards&Order=BESTMATCH&isdeptsrh=1' # 4G RX 570
]

my_numbers = os.environ['MY_NUMBER'].split(',')
twilio_number = os.environ['TWILIO_NUMBER']

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
        self._logger.info('Checking stock...\n')
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

def setup_logging(level, format_string):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    formatter = logging.Formatter(format_string)

    # STDOUT
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def remove_duplicate_links(db, stock_list, number):
    result = []
    links_in_db = db.get_all_links()
    for link in stock_list:
        if (link, number) not in links_in_db:
            result.append(link)

    return result

if __name__ == '__main__':
    logger = setup_logging(logging.INFO, '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info('Launching stock check...\n')

    db = PostDB(os.environ["DATABASE_URL"])
    db.delete_expired_links()

    stock = StockChecker()
    stock_list = stock.check_stock(item_urls)
    if len(stock_list) > 0:
        tm = TwilioMessenger()
        for number in my_numbers:
            links = '\n'.join(remove_duplicate_links(db, stock_list, number))

            # 1600 character limit with twilio
            while len(links) > 0:
                link_list = links.split('\n')[:LINKS_PER_MESSAGE]
                msg_body = '\n'.join(link_list)
                logger.info('Sending following text to {}:\n{}'.format(number, msg_body))
                message = tm.send_message(number, twilio_number, msg_body)
                links = '\n'.join(links.split('\n')[LINKS_PER_MESSAGE:])

                if message.status == 'queued':
                    logger.info('Text message queued to send!\n')
                    # Successfully queued to send. Add links to db
                    for link in link_list:
                        db.add_link(link, number)

    logger.info('{} new items detected.'.format(len(stock_list)))
    logger.info('Stock checker finished!')
