from common.deco import check_logged_in
from common.log import logger
from common.rest import acquire_json, rest_fail, rest_data
from common.types import ensure_str

from .crawl import fetch


@check_logged_in
@acquire_json
def crawl(request, data):
    url = ensure_str(data['url'])
    try:
        res = fetch(url)
    except Exception as e:
        logger.info('Failed to crawl from %s: %s: %s', url, type(e).__name__, e)
        return rest_fail()
    else:
        return rest_data(res)
