from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    dname = models.CharField(max_length=120)

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
