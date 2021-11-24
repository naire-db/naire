import random

from form.models import Form
from user.models import User


def ri():
    return random.randint(10000, 99999)


def main():
    user = random.choice(User.objects.all())
    test_form = Form(owner_user=user, title=f'测试表单 {ri()}', body={'data': None, 'x': ri()})
    test_form.save()
    print('Created', test_form.info(), 'for', user.info())


main()
