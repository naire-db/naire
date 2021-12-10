# requirements: aiohttp bs4 html5lib

import asyncio
import functools
import json
import os
import sys
from pprint import pp

import aiohttp
from bs4 import BeautifulSoup, element

bs_parser = 'html5lib'
cache_file = 'naire-crawled.html'

with open(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'crawl-headers.json'), 'r', encoding='utf-8') as fp:
    common_headers = json.load(fp)


def try_deco(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AttributeError as e:
            # print(f'Suppressed {type(e).__name__} in {f.__name__})
            return None

    return wrapper


@try_deco
def get_options(q: element) -> list[str]:
    return [li.find('label').text for li in q.find('ul').find_all('li')]


@try_deco
def get_dropdown_options(q: element) -> list[str]:
    return [opt.text for opt in q.find('select').find_all('option')]


@try_deco
def get_labels_tmpl(q: element) -> list[str]:
    return [
        e.find('label').text
        for e in q.find_all(class_='topic__type-items')
    ]


async def get_html(url: str) -> str:
    comment = f'<!-- {url} !-->\n'
    if os.path.exists(cache_file):
        with open(cache_file, encoding='utf-8') as fp:
            html = fp.read()
        if html.startswith(comment):
            print('Using cached html')
            return html

    headers = common_headers
    if '/xz/' in url:
        headers = dict(headers) | {
            'Referer': 'https://www.wjx.cn/newwjx/mysojump/selecttemplatelogin.aspx'
        }

    async with aiohttp.ClientSession(headers=headers) as client:
        async with client.get(url) as resp:
            resp.raise_for_status()
            html = await resp.text()

    with open(cache_file, 'w', encoding='utf-8') as fp:
        fp.write(comment)
        fp.write(html)

    return html


async def main():
    try:
        url = sys.argv[1]
    except IndexError:
        url = 'https://www.wjx.cn/vj/eNU6wHX.aspx'
        print('Using preset url', url)

    html = await get_html(url)
    soup = BeautifulSoup(html, bs_parser)

    if '/vj/' in url:
        soup = soup.find('div', class_='survey')
        title = soup.find('h1').text.strip()
        if title.endswith('[复制]'):
            title = title[:-4]
        print('Title:', title)
        desc = soup.find('div', class_='surveydescription').text.strip()
        print('Description:', desc)
        for q in soup.find_all(class_='div_question'):
            title = q.find(class_='div_title_question').text.strip()
            if title.endswith('【多选题】'):
                print('Checkbox:', title)
                pp(get_options(q))
            elif q.find('textarea') is not None:
                print('Input:', title)
            elif opts := get_dropdown_options(q):
                print('Dropdown:', title)
                pp(opts)
            elif opts := get_options(q):
                print('Radio:', title)
                pp(opts)
            else:
                print('Unknown type', title)
    else:
        assert '/xz/' in url
        # Find them in https://www.wjx.cn/newwjx/mysojump/selecttemplatelogin.aspx
        title = soup.find('h1', class_='htitle').text.strip()
        print('Title:', title)
        for q in soup.find('div', class_='topic__type-body').find_all('fieldset'):
            title = q.find('legend').text.strip()
            if q.find(class_='select__type'):
                print('Dropdown:', title)
                print('(Dropdown options are not rendered in templates)')
            elif q.find(class_='text__type'):
                print('Input:', title)
            elif q.find(class_='textarea__type'):
                print('Text:', title)
            elif q.find(class_='radio__type'):
                print('Radio:', title)
            elif q.find(class_='checkbox__type'):
                print('Checkbox:', title)
            else:
                print('Comment or Unknown:', title)

            # It seems inputs can also have options, like in https://www.wjx.cn/xz/57055486.aspx
            if opts := get_labels_tmpl(q):
                pp(opts)


if __name__ == '__main__':
    asyncio.run(main())
