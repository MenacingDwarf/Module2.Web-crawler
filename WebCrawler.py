import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import sys
import time
import hyperlink

class UrlInfo:
    def __init__(self, url, is_internal, is_valid):
        self.url = url
        self.is_internal = is_internal
        self.is_valid = is_valid

class WebCrawler:
    def __init__(self, url):
        self.main_url = url
        self.visited_urls = []
        self.urls_to_visit = [url]
        self.full_urls = []
        self.url_index = 0
        self.total_externals = 0

    def download_url(self, url):
        r = requests.get(url)
        return r.text, r.status_code == 200

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def is_internal(self, url):
        return url is not None and url.startswith(self.main_url)

    def is_document(self, url):
        return url.endswith('.doc') or url.endswith('.docx') or url.endswith('.pdf')

    def is_image(self, url):
        return url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.gif') or url.endswith('.svg')

    def crawl(self, url, log=True):
        html, success = self.download_url(url)
        if log:
            logging.info(f'---- URL status: {"True" if success else "False"}')

        if not success:
            self.full_urls.append(UrlInfo(url, True, False))
            return

        self.visited_urls.append(url)
        if url != self.main_url:
            self.full_urls.append(UrlInfo(url, True, True))

        for clear_url in self.get_linked_urls(url, html):
            new_url = hyperlink.parse(clear_url).normalize().replace(fragment=u'').to_text()
            if new_url is None or not (new_url.startswith("https://") or new_url.startswith("http://")) or new_url == url:
                continue

            if self.is_internal(new_url):
                if not new_url in self.visited_urls and not new_url in self.urls_to_visit and len(list(filter(lambda item : item.url == new_url, self.full_urls))) == 0:
                    if log:
                        logging.info(f'---- New internal URL: {new_url}')

                    if self.is_document(new_url) or self.is_image(new_url):
                        self.full_urls.append(UrlInfo(new_url, True, True))
                    else:
                        self.urls_to_visit.append(new_url)

            else:
                self.total_externals = self.total_externals + 1
                if len(list(filter(lambda item : item.url == new_url, self.full_urls))) == 0:
                    self.full_urls.append(UrlInfo(new_url, False, True))
                    if log:
                        logging.info(f'---- New external URL: {new_url}')

    def run(self, debug=True, log=True):
        start_time = time.time()
        if log:
            logging.basicConfig(filename='crawler.log', encoding='utf-8', level=logging.INFO)
            logging.info(f'Start crawling {self.main_url}...')
            logging.info(f'-----------------------------------')
        while self.urls_to_visit:
            self.url_index = self.url_index + 1
            url = self.urls_to_visit.pop(0)

            if debug:
                print(f'Crawling: {self.url_index} of {len(self.urls_to_visit) + len(self.visited_urls) + 1}')
            if log:
                logging.info(f'Crawling {url}: {self.url_index} of {len(self.urls_to_visit) + len(self.visited_urls) + 1}')

            try:
                self.crawl(url, log)
            except Exception:
                if log:
                    logging.exception(f'Failed to crawl: {url}')

        if log:
            logging.info(f'-----------------------------------')
            logging.info(f'Crawling end with {time.time() - start_time} seconds!\n')

    def get_internal_urls(self):
        return list(filter(lambda item : item.is_internal, self.full_urls))

    def get_external_urls(self):
        return list(filter(lambda item : not item.is_internal, self.full_urls))

    def get_documents_urls(self):
        return list(filter(lambda item : self.is_document(item.url), self.full_urls))

    def report(self, short = False):
        print('\n--------- CRAWLER REPORT --------\n')
        print(f'Total visited urls: {len(self.full_urls)}')
        print(f'Total unique internal urls: {len(self.get_internal_urls())}')
        print(f'Total unique external urls: {len(self.get_external_urls())}')
        print(f'Total external urls: {self.total_externals}')
        print(f'Total unique document urls: {len(self.get_documents_urls())}')
        print(f'Valid internals: {len(list(filter(lambda item : item.is_valid,self.get_internal_urls())))}')
        print(f'Invalid internals: {len(list(filter(lambda item : not item.is_valid,self.get_internal_urls())))}')


        if short:
            return

        print('\n--------- INTERNAL URLS ---------\n')
        for link in self.get_internal_urls():
            print("    OK   " if link.is_valid else "NOT OK   ", link.url)

        print('\n--------- EXTERNAL URLS ---------\n')
        for link in self.get_external_urls():
            print("         " if link.is_valid else "NOT OK   ", link.url)

        print('\n--------- DOCUMENT URLS ---------\n')
        for link in self.get_documents_urls():
            print("         " if link.is_valid else "NOT OK   ", link.url)

if __name__ == '__main__':
    crawler = WebCrawler(str(sys.argv[1]))
    crawler.run()
    crawler.report()
