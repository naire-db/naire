import functools
import json

from django.core.exceptions import BadRequest
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from common.errors import ERR_FAILURE


def acquire_json(view):
    @require_POST
    @functools.wraps(view)
    def wrapper(request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            raise BadRequest
        try:
            return view(request, data)
        except (TypeError, ValueError):
            raise BadRequest

    return wrapper


def rest_msg(msg: str, code: int = 0, **kw):
    return JsonResponse({
        'code': code,
        'message': msg,
        **kw
    })


def rest(code: int, **kw):
    return JsonResponse({
        'code': code,
        **kw
    })


def rest_data(data, code: int = 0, **kw):
    return JsonResponse({
        'code': code,
        'data': data,
        **kw
    })


def rest_ok():
    return JsonResponse({
        'code': 0
    })


def rest_fail():
    return JsonResponse({
        'code': ERR_FAILURE
    })
