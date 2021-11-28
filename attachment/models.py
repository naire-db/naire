from django.db import models

from form.models import Response


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/', max_length=1000)
    name = models.CharField(max_length=200)
    # TODO: add path on here
    resp = models.ForeignKey(Response, on_delete=models.CASCADE)

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

