import functools

from django.http import HttpRequest

from .rest import rest_msg
from .errors import ERR_AUTH_REQUIRED


def check_logged_in(view):
    @functools.wraps(view)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        return rest_msg('login required', code=ERR_AUTH_REQUIRED)

    return wrapper
