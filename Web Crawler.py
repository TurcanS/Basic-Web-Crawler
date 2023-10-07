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
    def __init__(self) -> None:
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({'User-Agent': self.ua.random})
        self.robots_parser = RobotExclusionRulesParser()

    def extract_links(self, url: str, limit: int = 10) -> set:
        """Extract links from a given URL up to a specified limit.

        Args:
            url (str): The target URL to extract links from.
            limit (int, optional): The maximum number of links to extract. Defaults to 10.

        Returns:
            set: A set containing the extracted links.
        """
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

    def can_fetch(self, url: str) -> bool:
        """Check if a given URL can be fetched according to its robots.txt.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL can be fetched, False otherwise.
        """
        try:
            robots_url = urljoin(url, '/robots.txt')
            self.robots_parser.fetch(robots_url)
            return self.robots_parser.can_fetch(self.ua.random, url)
        except:
            return True

def is_domain_excluded(url: str, excluded_domains: list) -> bool:
    """Check if the domain of a given URL is in the excluded domains list.

    Args:
        url (str): The URL to check.
        excluded_domains (list): The list of domains to exclude.

    Returns:
        bool: True if the URL's domain is in the excluded list, False otherwise.
    """
    return any(domain in urlparse(url).netloc for domain in excluded_domains)

def crawl(start_url: str, depth: int = 2, link_limit: int = 10, excluded_domains: list = []) -> None:
    """Crawl a website starting from a given URL up to a specified depth.

    Args:
        start_url (str): The starting URL.
        depth (int, optional): The maximum depth to crawl. Defaults to 2.
        link_limit (int, optional): The maximum number of links to extract per page. Defaults to 10.
        excluded_domains (list, optional): List of domains to exclude from crawling. Defaults to [].
    """
    visited = set()
    parser = LinkParser()
    queue = deque([(start_url, 1)])

    while queue:
        url, current_depth = queue.popleft()

        if current_depth > depth or url in visited or is_domain_excluded(url, excluded_domains):
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

def display_ascii_art() -> None:
    """Display ASCII art."""
    art = """
    W   W  EEEEE  B B B
    W   W  E      B   B
    W W W  EEEE   BBBBB
    W W W  E      B   B
    W   W  EEEEE  B B B
    """
    print(art)

def main() -> None:
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
