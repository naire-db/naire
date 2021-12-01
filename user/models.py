from django.db import models
from django.contrib.auth.models import AbstractUser, Group

from naire import settings


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


class Org(Group):
    org_name = models.CharField(max_length=120)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='admin_of_org')
    admin = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admins_of_org')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='members_of_org')
    root_folder = models.ForeignKey('form.Folder', on_delete=models.PROTECT)
    ctime = models.DateTimeField(auto_now_add=True)

    def info(self) -> dict[str]:
        return {
            'oid': self.id,
            'org_name': self.org_name,
            'owner': self.owner,
            'member_count': self.user_set.count(),
        }

    def description(self) -> dict[str]:
        return {
            'org_name': self.org_name,
            'owner_name': self.owner.dname,
            'member_count': self.user_set.count(),
        }
