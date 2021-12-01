from django.contrib import auth
from django.core.exceptions import BadRequest
from django.http import HttpResponse
from django.views.decorators.http import require_safe

from common.deco import check_logged_in
from common.errors import ERR_DUPL_USERNAME, ERR_DUPL_EMAIL
from common.log import logger
from common.models import save_or_400
from common.rest import rest_ok, rest_fail, acquire_json, rest_data, rest
from common.types import ensure_str

from form.models import Folder
from .models import User, Org, Membership


@require_safe
def hello(request):
    logger.info(f'hello to {request.user}')
    if request.user.is_authenticated:
        return HttpResponse(f'Hello, {request.user.username}?')
    return HttpResponse('Hello, world!')


@require_safe
def info(request):
    if request.user.is_authenticated:
        return rest_data(request.user.info())
    return rest_fail()


@acquire_json
def login(request, data):
    username_or_email = ensure_str(data['username_or_email'])
    password = ensure_str(data['password'])
    if '@' in username_or_email:
        try:
            user = User.objects.get(email=username_or_email)
        except User.DoesNotExist:
            return rest_fail()
        if not user.check_password(password):
            return rest_fail()
    else:
        username = username_or_email  # is username
        user = auth.authenticate(request, username=username, password=password)
        if user is None:
            return rest_fail()
    auth.login(request, user)
    logger.info(f'Logged: {user}')
    return rest_data(user.info())


@require_safe
def logout(request):
    auth.logout(request)
    return rest_ok()


@acquire_json
def register(request, data):
    username = ensure_str(data['username'])
    email = ensure_str(data['email']).lower()
    password = ensure_str(data['password'])
    dname = ensure_str(data['dname'])
    if User.objects.filter(username=username).exists():
        return rest(ERR_DUPL_USERNAME)
    if User.objects.filter(email=email).exists():
        return rest(ERR_DUPL_EMAIL)
    folder = Folder(name='未分类')
    folder.save()
    try:
        user = User.objects.create_user(
            username=username, password=password,
            email=email, dname=dname,
            root_folder=folder
        )
    except Exception as e:
        # Shouldn't be reached from our validating frontend
        folder.delete()
        logger.warning(f'Bad request caused {type(e).__name__} {e}')
        raise BadRequest
    folder.owner_user = user
    folder.save()
    logger.info(f'Registered: {user}')
    return rest_data(user.info())


@check_logged_in
@acquire_json
def save_profile(request, data):
    email = ensure_str(data['email'])
    dname = ensure_str(data['dname'])  # display name
    user = request.user
    if email != user.email:
        if User.objects.filter(email=email).exists():
            return rest(ERR_DUPL_EMAIL)
        user.email = email
    user.dname = dname
    user.save()
    return rest_data(user.info())


@check_logged_in
@acquire_json
def change_password(request, data):
    password = ensure_str(data['password'])
    new_password = ensure_str(data['new_password'])
    user = request.user
    if user.check_password(password):
        user.set_password(new_password)
        user.save()
        return rest_ok()
    return rest_fail()


@check_logged_in
@acquire_json
def create_org(request, data):
    name = ensure_str(data['name'])
    folder = Folder(name='未分类')
    folder.save()
    org = Org(name=name, root_folder=folder)
    save_or_400(org)
    m = Membership(user=request.user, org=org, role=Membership.Role.OWNER)
    m.save()
    return rest_data(org.id)
