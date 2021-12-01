from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _

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
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', related_name='members_of_org')
    root_folder = models.ForeignKey('form.Folder', on_delete=models.PROTECT)
    ctime = models.DateTimeField(auto_now_add=True)


class MemberShip(models.Model):
    class Role(models.IntegerChoices):
        OWNER = 0, _('owner')
        ADMIN = 1, _('admin')
        MEMBER = 2, _('member')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    org = models.ForeignKey(Org, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
    role = models.CharField(
        max_length=6,
        choices=Role.choices,
        default=Role.MEMBER,
    )
