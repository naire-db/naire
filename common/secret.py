from django.http import HttpRequest, Http404

from common.log import logger
from common.utils import get_client_intro

tokens = frozenset(('W4nqsVHAchgAGQ', 'nLvGE2xN7qVYuA', 'xowGfT4OrUKL7Q'))
authed_token = 'N6HgbdHqRg8A6f5oiiNhnjU7sGw'


def secret_middleware(get_response):

    def middleware(request: HttpRequest):
        if request.session.get('naire_auth_token') != authed_token:
            intro = f'[{request.method} {request.path}: {get_client_intro(request)}]'
            try:
                auth_token = request.headers['Authorization']
            except KeyError:
                logger.info('Dropping unauthed request %s', intro)
                raise Http404
            if auth_token in tokens:
                logger.info('Authing request %s', intro)
                request.session['naire_auth_token'] = authed_token
            else:
                logger.warning('Dropping request %s with bad token', intro)
                raise Http404

        return get_response(request)

    return middleware
