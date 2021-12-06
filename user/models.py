from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    dname = models.CharField(max_length=120)
    root_folder = models.OneToOneField('form.Folder', on_delete=models.PROTECT)

    def info(self) -> dict[str]:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'dname': self.dname
        }

    def description(self) -> dict[str]:
        return {
            'username': self.username,
            'dname': self.dname
        }

    def id_description(self) -> dict[str]:
        return {
            'id': self.id,
            'username': self.username,
            'dname': self.dname
        }
