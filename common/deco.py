import functools

from .rest import rest_msg


def check_logged_in(view):
    @functools.wraps(view)
    def wrapper(request):
        if request.user.is_authenticated:
            return view(request)
        return rest_msg('login required', code=2)

    return wrapper
