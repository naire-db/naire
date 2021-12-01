from django.db import models
from django.utils.translation import gettext_lazy as _

from naire import settings


class Org(models.Model):
    name = models.CharField(max_length=120)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', related_name='members_of_org')
    root_folder = models.ForeignKey('form.Folder', on_delete=models.PROTECT)
    ctime = models.DateTimeField(auto_now_add=True)


class Membership(models.Model):
    class Role(models.IntegerChoices):
        MEMBER = 0, _('member')
        ADMIN = 1, _('admin')
        OWNER = 2, _('owner')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    org = models.ForeignKey(Org, on_delete=models.CASCADE)
    ctime = models.DateTimeField(auto_now_add=True)
    role = models.IntegerField(
        choices=Role.choices,
        default=Role.MEMBER,
    )
