import inspect
from typing import Optional

from django.http import HttpRequest

from common.models import get_user

from user.models import User
from .models import Log, Ip, IpSession


def get_ip(request: HttpRequest) -> Ip:
    ip = Ip.of(request)
    if user := get_user(request):
        IpSession.objects.get_or_create(user=user, ip=ip)
    return ip


def save_log(request: HttpRequest, action: Optional[str] = None, /, user: User = None) -> Log:
    if action is None:
        action = inspect.stack()[1].function
    if user is None:
        user = request.user

    ip = Ip.of(request)
    session = IpSession.objects.get_or_create(user=user, ip=ip)[0]
    return Log.objects.create(session=session, action=action)
