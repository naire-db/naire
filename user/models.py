from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    dname = models.CharField(max_length=120)
    root_folder = models.ForeignKey('form.Folder', on_delete=models.PROTECT)

    def info(self) -> dict[str]:
        return {
            'username': self.username,
            'uid': self.id,
            'email': self.email,
            'dname': self.dname
        }

    def description(self) -> dict[str]:
        return {
            'username': self.username,
            'dname': self.dname
        }
