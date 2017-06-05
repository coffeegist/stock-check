import os
import logging
import psycopg2
from urllib.parse import urlparse

class PostDB(object):

    def __init__(self, uri):
        self.__setup_logging(logging.INFO, '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        url = urlparse(uri)

        self._conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

    def __setup_logging(self, level, format_string):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(level)
        formatter = logging.Formatter(format_string)

        # STDOUT
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)


    def add_link(self, link):
        self._logger.info('Adding link {}...'.format(link))
        cur = self._conn.cursor()
        cur.execute("INSERT INTO links (link) VALUES (%s)", [link])
        self._conn.commit()
        cur.close()

        self._logger.info('Finished adding link!')

    def get_all_links(self):
        self._logger.info('Retrieving links...')
        cur = self._conn.cursor()
        cur.execute("SELECT link FROM links")
        links = cur.fetchall()
        self._conn.commit()
        cur.close()

        return [i[0] for i in links] # convert from list of tuples to list

    def delete_expired_links(self):
        self._logger.info('Deleting expired links...')
        cur = self._conn.cursor()
        cur.execute("DELETE FROM links WHERE expiration < NOW() RETURNING *")
        deleted_rows = cur.fetchall()
        self._conn.commit()
        cur.close()

        for row in deleted_rows:
            self._logger.info('{} expired at {} and has been removed.'.format(row[1], row[2]))

        self._logger.info('Finished deleting expired links!')

if __name__ == "__main__":
    db = PostDB(os.environ["DATABASE_URL"])
    db.delete_expired_links()
    #db.add_link('http://www.googl.com')
    print(db.get_all_links())
