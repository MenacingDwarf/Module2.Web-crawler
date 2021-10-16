import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import sys

class UrlInfo:
    def __init__(self, url, is_internal):
        self.url = url
        self.is_internal = is_internal

class WebCrawler:
    def __init__(self, url):
        self.main_url = url
        self.visited_urls = []
        self.urls_to_visit = [url]
        self.full_urls = []

    def download_url(self, url):
        return requests.get(url).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def add_url_to_visited(self, url):
        if url not in self.visited_urls:
            self.visited_urls.append(url)
            self.full_urls.append(UrlInfo(url, False))
    
    def crawl(self, url):
        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            if (self.is_internal(url)):
                self.add_url_to_visit(url)
            else:
                self.add_url_to_visited(url)
            
    def is_internal(self, url):
        return url is not None and url.startswith(self.main_url)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            print(f'Crawling: {url}')
            logging.info(f'Crawling: {url}')
            try:
                self.crawl(url)
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)
                self.full_urls.append(UrlInfo(url, True))
        
    def get_internal_urls(self):
        return list(filter(lambda item : item.is_internal, self.full_urls))
        
    def get_external_urls(self):
        return list(filter(lambda item : not item.is_internal, self.full_urls))
        
if __name__ == '__main__':
    crawler = WebCrawler(str(sys.argv[1]))
    crawler.run()
    
    print(f'Total visited urls: {len(crawler.full_urls)}')
    print(f'Total internal urls: {len(crawler.get_internal_urls())}')
    print(f'Total external urls: {len(crawler.get_external_urls())}')
    