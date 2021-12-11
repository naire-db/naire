import json
import os
import re
import sys
import urllib.parse
from pprint import pp
from typing import Optional

import pathvalidate
import requests

from .parse import parse_vj, parse_xz

here = os.path.dirname(os.path.realpath(__file__))

cache_dir = os.path.join(here, 'cache')
if not os.path.isdir(cache_dir):
    try:
        os.mkdir(cache_dir)
    except FileExistsError:
        pass

with open(os.path.join(here, 'crawl-headers.json'), 'r', encoding='utf-8') as fp:
    common_headers = json.load(fp)


class HtmlCache:
    def __init__(self, url: str):
        self.cache_file = os.path.join(
            cache_dir,
            pathvalidate.sanitize_filename(
                urllib.parse.urlparse(url).path + '.html'
            )
        )
        self.comment = f'<!-- {url} !-->\n'

    def get(self) -> Optional[str]:
        file = self.cache_file
        if os.path.exists(file):
            with open(file, encoding='utf-8') as fp:
                html = fp.read()

            if html.startswith(self.comment):
                return html

    def save(self, html: str):
        with open(self.cache_file, 'w', encoding='utf-8') as fp:
            fp.write(self.comment)
            fp.write(html)


def get_headers(url: str) -> dict[str]:
    if '/xz/' in url:
        return common_headers | {
            'Referer': 'https://www.wjx.cn/newwjx/mysojump/selecttemplatelogin.aspx'
        }

    return common_headers


def get_html(url: str) -> str:
    cache = HtmlCache(url)
    if r := cache.get():
        return r

    resp = requests.get(url, headers=get_headers(url), timeout=20)
    resp.raise_for_status()
    html = resp.text

    cache.save(html)
    return html


def parse(html: str, url: str) -> dict[str]:
    if '/vj/' in url:
        return parse_vj(html)

    if '/xz/' in url:
        return parse_xz(html)

    raise ValueError


reg = re.compile(r'https?://(?:www\.)?wjx\.cn/(?:vj|xz)/[a-zA-Z0-9]+\.aspx')


def check_url(url: str):
    if not reg.fullmatch(url):
        raise ValueError


def fetch(url: str):
    check_url(url)
    html = get_html(url)
    return parse(html, url)


def main():
    try:
        url = sys.argv[1]
    except IndexError:
        url = 'https://www.wjx.cn/vj/eNU6wHX.aspx'
        print('Using preset url', url)

    pp(fetch(url))


if __name__ == '__main__':
    main()
