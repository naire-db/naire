import functools

from .rest import rest_msg
from .errors import ERR_AUTH_REQUIRED


def check_logged_in(view):
    @functools.wraps(view)
    def wrapper(request):
        if request.user.is_authenticated:
            return view(request)
        return rest_msg('login required', code=ERR_AUTH_REQUIRED)

    return wrapper
