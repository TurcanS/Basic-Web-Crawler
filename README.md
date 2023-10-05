# Web Crawler CLI

A simple yet powerful command-line web crawler that fetches links from a given URL up to a specified depth.

## Features

__Dynamic User Agent:__ Adapts to different user agents for diverse requests.

__Robots.txt Respect:__ Ensures we're crawling politely.

__Configurable Domain Limitations:__ You decide which domains to exclude.

__URL Validation:__ Ensures only valid URLs are processed.

__Depth-based Crawling:__ Control how deep the rabbit hole goes.

__Loop-based Approach:__ Avoids recursion errors.

__ASCII Art:__ Because why not?

## Installation

```
pip install fake-useragent robotexclusionrulesparser validators
git clone https://github.com/TurcanS/Basic-Web-Crawler.git
cd Basic-Web-Crawler
```

## Usage
Run the script using:

```
python script_name.py [URL] --depth [DEPTH] --limit [LIMIT] --exclude [DOMAIN ...]
```

### Arguments

URL: The starting URL to crawl.

--depth: Depth of crawling (default: 2).

--limit: Limit of links per page (default: 10).

--exclude: Domains to exclude from crawling. Multiple domains can be specified.
