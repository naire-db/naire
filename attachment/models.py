import os.path

from django.db import models

from form.models import Response, Form


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/', max_length=1000)
    name = models.CharField(max_length=200)
    resp = models.ForeignKey(Response, on_delete=models.CASCADE, blank=True, null=True)

    def info(self) -> dict[str]:
        return {
            'id': self.id,
            'name': self.name,
            'resp_id': self.resp_id,
        }

    def detail(self) -> dict[str]:
        return {
            'name': self.name,
            'resp_id': self.resp_id,
        }


class Image(models.Model):
    file = models.FileField(upload_to='images/')
    filename = models.CharField(max_length=200)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, blank=True, null=True)

    def set_filename(self, s):
        if len(s) > 200:
            base, ext = os.path.splitext(s)
            s = base[:200 - len(ext)] + ext
        self.filename = s
