from datetime import time

from django.db import models
from django.conf import settings
from django.utils.timezone import now

from org.models import Org


class Folder(models.Model):
    name = models.CharField(max_length=200)
    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    owner_org = models.ForeignKey(Org, on_delete=models.CASCADE, blank=True, null=True)

    def info(self) -> dict[str]:
        return {
            'id': self.id,
            'name': self.name,
            'form_count': self.form_set.count()
        }


class Form(models.Model):
    title = models.CharField(max_length=200)
    ctime = models.DateTimeField(auto_now_add=True)
    body = models.JSONField()
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)

    published = models.BooleanField(default=True)
    publish_time = models.DateTimeField(null=True, blank=True)
    unpublish_time = models.DateTimeField(null=True, blank=True)
    passphrase = models.CharField(max_length=100, null=True, blank=True)
    login_required = models.BooleanField(default=False)  # read as True when member_required presents
    member_required = models.BooleanField(default=False)

    class Limit(models.IntegerChoices):
        UNLIMITED = 0
        DAILY = 1
        ONCE = 2

    user_limit = models.IntegerField(choices=Limit.choices, default=Limit.UNLIMITED)  # does nothing without login_required
    user_limit_reset_time = models.TimeField(default=time(0, 0, 0))
    ip_limit = models.IntegerField(choices=Limit.choices, default=Limit.UNLIMITED)
    ip_limit_reset_time = models.TimeField(default=time(0, 0, 0))

    def info(self) -> dict[str]:
        return {
            'id': self.id,
            'title': self.title,
            'ctime': self.ctime.timestamp(),
            'resp_count': self.response_set.count()
        }

    def detail(self) -> dict[str]:
        return {
            'title': self.title,
            'body': self.body
        }

    def make_cloned(self, folder: Folder, title: str):
        self.folder = folder
        self.title = title
        self.ctime = now()


class Response(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    body = models.JSONField()
    ctime = models.DateTimeField(auto_now_add=True)

    def info(self) -> dict[str]:
        return {
            'id': self.id,
            'user': None if self.user is None else self.user.description(),
            'ctime': self.ctime.timestamp()
        }

    def detail(self) -> dict[str]:
        return {
            'id': self.id,
            'body': self.body
        }

    def full_detail(self) -> dict[str]:
        return {
            'id': self.id,
            'ctime': self.ctime.timestamp(),
            'user': None if self.user is None else self.user.description(),
            'body': self.body
        }
