from django.db import models
from user.models import User


def get_client_ip(request):
    if xff := request.META.get('HTTP_X_FORWARDED_FOR'):
        return xff.split(',')[0]
    return request.META['REMOTE_ADDR']


class Ip(models.Model):
    addr = models.GenericIPAddressField(unique=True)
    users = models.ManyToManyField(User, through='IpSession')

    @staticmethod
    def of(request) -> 'Ip':
        return Ip.objects.get_or_create(addr=get_client_ip(request))


class IpSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.ForeignKey(Ip, on_delete=models.CASCADE)


class Log(models.Model):
    session = models.ForeignKey(IpSession, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
