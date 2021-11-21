import functools
import json

from django.core.exceptions import BadRequest
from django.http import JsonResponse


def acquire_json(view):
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


def rest_msg(msg: str, code=0, **kw):
    return JsonResponse({
        'code': code,
        'message': msg,
        **kw
    })


def rest_code(code, **kw):
    return JsonResponse({
        'code': code,
        **kw
    })


def rest_ok():
    return JsonResponse({
        'code': 0
    })


def rest_fail():
    return JsonResponse({
        'code': 1
    })
