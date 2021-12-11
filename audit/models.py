from django.db import models

from common.utils import get_client_ip
from user.models import User


class Ip(models.Model):
    addr = models.GenericIPAddressField(unique=True)
    users = models.ManyToManyField(User, through='IpSession')

    @staticmethod
    def of(request) -> 'Ip':
        return Ip.objects.get_or_create(addr=get_client_ip(request))[0]


class IpSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.ForeignKey(Ip, on_delete=models.CASCADE)


action_texts = {
    'login': '登录',
    'login_failed': '登录失败',
    'register': '注册',
    'change_password': '修改密码',
    'change_password_failed': '修改密码失败',
    'save_profile': '保存资料',
    'create_form': '创建问卷',
    'remake_form': '编辑问卷',
    'remove_form': '删除问卷',
    'save_resp': '填写问卷',
    'create_org': '创建组织',
    'join_org': '加入组织',
    'leave_org': '退出组织',
    'dissolve_org': '解散组织',
}


class Log(models.Model):
    session = models.ForeignKey(IpSession, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    description = models.CharField(max_length=250, default='')
    ua = models.CharField(max_length=100, default='')
    object_id = models.BigIntegerField(blank=True, null=True)

    def detail(self) -> dict[str]:
        res = {
            'ip': self.session.ip.addr,
            'time': self.time.timestamp(),
            'ua': self.ua,
            'action': action_texts.get(self.action, self.action),
        }
        if self.description:
            res['object'] = self.description
        return res
