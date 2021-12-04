import os.path

from django.db import models

from form.models import Response, Form


def trim_filename(s: str) -> str:
    if len(s) <= 200:
        return s
    base, ext = os.path.splitext(s)
    return base[:200 - len(ext)] + ext


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    name = models.CharField(max_length=200)
    resp = models.ForeignKey(Response, on_delete=models.CASCADE, blank=True, null=True)

    def set_filename(self, s):
        self.filename = trim_filename(s)


class Image(models.Model):
    file = models.FileField(upload_to='images/')
    filename = models.CharField(max_length=200)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, blank=True, null=True)

    def set_filename(self, s):
        self.filename = trim_filename(s)
