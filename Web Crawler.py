import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import argparse
from fake_useragent import UserAgent
from robotexclusionrulesparser import RobotExclusionRulesParser
from collections import deque
import validators

logging.basicConfig(level=logging.INFO)

class LinkParser:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({
            'User-Agent': self.ua.random
        })
        self.robots_parser = RobotExclusionRulesParser()

    def extract_links(self, url, limit=10):
        links = set()
        try:
            response = self.session.get(url)
            if response.status_code == 200 and 'text/html' in response.headers['Content-Type']:
                soup = BeautifulSoup(response.content, 'html.parser')
                for a_tag in soup.find_all('a', href=True)[:limit]:
                    link = urljoin(url, a_tag['href'])
                    links.add(link)
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
        return links

    def can_fetch(self, url):
        try:
            robots_url = urljoin(url, '/robots.txt')
            self.robots_parser.fetch(robots_url)
            return self.robots_parser.can_fetch(self.ua.random, url)
        except:
            return True

def crawl(start_url, depth=2, link_limit=10, excluded_domains=[]):
    visited = set()
    parser = LinkParser()
    queue = deque([(start_url, 1)])

    while queue:
        url, current_depth = queue.popleft()
        if current_depth > depth or url in visited or any(domain in urlparse(url).netloc for domain in excluded_domains):
            continue
        if not parser.can_fetch(url):
            logging.info(f"Respecting robots.txt for {url}")
            continue
        visited.add(url)
        links = parser.extract_links(url, link_limit)
        logging.info(f"Depth: {current_depth}, URL: {url}, Links: {len(links)}")
        for link in links:
            logging.info(link)
            if current_depth < depth:
                queue.append((link, current_depth + 1))

def display_ascii_art():
    art = """
    W   W  EEEEE  B B B
    W   W  E      B   B
    W W W  EEEE   BBBBB
    W W W  E      B   B
    W   W  EEEEE  B B B
    """
    print(art)

def main():
    display_ascii_art()

    parser = argparse.ArgumentParser(description='Web Crawler CLI')
    parser.add_argument('url', type=str, help='Starting URL to crawl')
    parser.add_argument('--depth', type=int, default=2, help='Depth of crawling (default: 2)')
    parser.add_argument('--limit', type=int, default=10, help='Limit of links per page (default: 10)')
    parser.add_argument('--exclude', type=str, nargs='*', default=[], help='Domains to exclude from crawling')
    args = parser.parse_args()

    if not validators.url(args.url):
        logging.error("Invalid URL provided.")
        return

    crawl(args.url, args.depth, args.limit, args.exclude)

if __name__ == "__main__":
    main()