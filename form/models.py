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
