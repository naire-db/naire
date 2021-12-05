from django.http import HttpRequest

from common.models import get_user

from .models import Log, Ip, IpSession


def get_ip(request: HttpRequest) -> Ip:
    ip = Ip.of(request)
    if user := get_user(request):
        IpSession.objects.get_or_create(user=user, ip=ip)
    return ip


# login required
def save_log(request: HttpRequest, action: str) -> Log:
    ip = Ip.of(request)
    session = IpSession.objects.get_or_create(user=request.user, ip=ip)
    return Log.objects.create(session=session, action=action)
