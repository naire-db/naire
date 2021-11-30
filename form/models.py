from django.db import models
from django.conf import settings


class Folder(models.Model):
    name = models.CharField(max_length=200)
    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

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
    folder = models.ForeignKey(Folder, on_delete=models.PROTECT)

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
