from django.db import models
from django.conf import settings


class Form(models.Model):
    body = models.JSONField()
    ctime = models.DateTimeField(auto_now_add=True)


class Response(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    body = models.JSONField()
