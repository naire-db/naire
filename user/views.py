from django.http import HttpResponse
from django.views.decorators.http import require_safe, require_POST
from django.contrib import auth

from common.rest import rest_ok, rest_fail, acquire_json
from common.log import logger


@require_safe
def hello(request):
    logger.info(f'hello to {request.user}')
    if request.user.is_authenticated:
        return HttpResponse(f'Hello, {request.user.username}?')
    return HttpResponse('Hello, world!')


@require_POST
@acquire_json
def login(request, data):
    username = str(data['username'])
    password = str(data['password'])
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        logger.info(f'{request.session} logged in as {user}')
        return rest_ok()
    return rest_fail()


@require_safe
def logout(request):
    auth.logout(request)
    return rest_ok()
