import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import sys

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

    def add_url_to_visit(self, url):
        if not url in self.visited_urls and not url in self.urls_to_visit:
            self.urls_to_visit.append(url)
    
    def crawl(self, url):
        html, success = self.download_url(url)
        if not success:
            self.full_urls.append(UrlInfo(url, True, False))
            return
        
        self.visited_urls.append(url)
        if url != self.main_url:
            self.full_urls.append(UrlInfo(url, True, True))
        
        for new_url in self.get_linked_urls(url, html):
            if not (new_url.startswith("https://") or new_url.startswith("http://")) or new_url == url:
                continue
                
            if self.is_internal(new_url):
                self.add_url_to_visit(new_url)
            else:
                try:
                    _, valid = self.download_url(new_url)
                    if len(list(filter(lambda item : item.url == new_url, self.full_urls))) == 0:
                        self.full_urls.append(UrlInfo(new_url, False, valid))
                except Exception:
                    if len(list(filter(lambda item : item.url == new_url, self.full_urls))) == 0:
                        self.full_urls.append(UrlInfo(new_url, False, False))
                    pass
            
    def is_internal(self, url):
        return url is not None and url.startswith(self.main_url)

    def run(self):
        while self.urls_to_visit:
            self.url_index = self.url_index + 1
            print(f'Crawling: {self.url_index} of {len(self.urls_to_visit) + len(self.visited_urls)}')
            
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling {url}: {self.url_index} of {len(self.urls_to_visit) + len(self.visited_urls) + 1}')
            try:
                self.crawl(url)
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
        
    def get_internal_urls(self):
        return list(filter(lambda item : item.is_internal, self.full_urls))
        
    def get_external_urls(self):
        return list(filter(lambda item : not item.is_internal, self.full_urls))
        
    def report(self, short = False):
        print('\n--------- CRAWLER REPORT --------\n')
        print(f'Total visited urls: {len(self.full_urls)}')
        print(f'Total internal urls: {len(self.get_internal_urls())}')
        print(f'Total external urls: {len(self.get_external_urls())}')
        
        if short:
            return
        
        print('\n--------- INTERNAL URLS ---------\n')
        for link in self.get_internal_urls():
            print("    OK   " if link.is_valid else "NOT OK   ", link.url)
            
        print('\n--------- EXTERNAL URLS ---------\n')
        for link in self.get_external_urls():
            print("    OK   " if link.is_valid else "NOT OK   ", link.url)
        
if __name__ == '__main__':
    crawler = WebCrawler(str(sys.argv[1]))
    crawler.run()
    crawler.report()
    
    