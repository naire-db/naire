from django.db import models
from user.models import User


class Template(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.JSONField()
    mtime = models.DateTimeField()
    use_count = models.IntegerField(default=0)

    def info(self) -> dict[str]:
        return {
            'id': self.id,
            'title': self.title,
            'user': self.user.id_description(),
            'use_count': self.use_count,
            'mtime': self.mtime.timestamp(),
        }

    def owner_info(self) -> dict[str]:
        return {
            'id': self.id,
            'title': self.title,
            'use_count': self.use_count,
        }

    def detail(self) -> dict[str]:
        return {
            'title': self.title,
            'body': self.body,
        }
