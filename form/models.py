from datetime import time, datetime
from typing import Optional

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


def present_datetime_or_none(t: Optional[datetime]):
    return None if t is None else t.timestamp()


def present_time(t: time):
    return str(t)[:5]


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
        ONCE = 1
        DAILY = 2

    user_limit = models.IntegerField(choices=Limit.choices, default=Limit.UNLIMITED)  # does nothing without login_required
    user_limit_reset_time = models.TimeField(default=time(0, 0, 0))
    ip_limit = models.IntegerField(choices=Limit.choices, default=Limit.UNLIMITED)
    ip_limit_reset_time = models.TimeField(default=time(0, 0, 0))

    def info(self) -> dict[str]:
        if self.update_published():
            self.save()
        return {
            'id': self.id,
            'title': self.title,
            'ctime': self.ctime.timestamp(),
            'resp_count': self.response_set.count(),
            'published': self.published
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

    def settings(self) -> dict[str]:
        org = self.folder.owner_org
        return {
            'form': self.info(),
            'settings': {
                k: getattr(self, k)
                for k in (
                    'published',
                    'passphrase',
                    'login_required', 'member_required',
                    'user_limit', 'ip_limit',
                )
            } | {
                'publish_time': present_datetime_or_none(self.publish_time),
                'unpublish_time': present_datetime_or_none(self.unpublish_time),
                'user_limit_reset_time': present_time(self.user_limit_reset_time),
                'ip_limit_reset_time': present_time(self.ip_limit_reset_time),
            },
            'org_name': None if org is None else org.name,
        }

    # Return if published field changes.
    def update_published(self) -> bool:
        n = now()
        if self.published:
            if self.unpublish_time and n >= self.unpublish_time:
                self.published = False
                return True
            return False

        if (not self.unpublish_time or n < self.unpublish_time) and self.publish_time and n >= self.publish_time:
            self.published = True
            return True
        return False


class Response(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    body = models.JSONField()
    ctime = models.DateTimeField(auto_now_add=True)

    ip = models.GenericIPAddressField()

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
