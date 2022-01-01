from django.contrib import auth
from django.core.exceptions import BadRequest
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.http import require_safe

from common.deco import check_logged_in
from common.errors import ERR_DUPL_USERNAME, ERR_DUPL_EMAIL
from common.log import logger
from common.rest import rest_ok, rest_fail, acquire_json, rest_data, rest
from common.types import ensure_str

from audit.actions import save_log
from audit.models import Log
from form.models import Folder, Response
from org.models import Org, Membership
from .models import User


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
            # Saving 'login_failed' logs means that not all IpSessions are logged
            save_log(request, 'login_failed', user=user)
            return rest_fail()
    else:
        username = username_or_email  # is username
        user = auth.authenticate(request, username=username, password=password)
        if user is None:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
            else:
                save_log(request, 'login_failed', user=user)
            return rest_fail()

    token = request.session.get('naire_auth_token')
    auth.login(request, user)
    if token:
        request.session['naire_auth_token'] = token
    logger.info(f'Logged: {user}')
    save_log(request, user=user)
    return rest_data(user.info())


@require_safe
def logout(request):
    token = request.session.get('naire_auth_token')
    auth.logout(request)
    if token:
        request.session['naire_auth_token'] = token
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
    save_log(request, user=user)
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
    save_log(request)
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
        save_log(request)
        return rest_ok()
    save_log(request, 'change_password_failed')
    return rest_fail()


MAX_FEED_COUNT = 10


@require_safe
@check_logged_in
def get_feeds(request):
    user: User = request.user
    orgs = Org.objects.filter(membership__user=user, membership__role__gte=Membership.Role.ADMIN)
    all_orgs = Org.objects.filter(membership__user=user)

    # TODO: 问卷发布？

    res = []
    for resp in Response.objects.filter(
        Q(form__folder__owner_user=user) |
        Q(form__folder__owner_org__in=orgs)
    ).order_by('-id')[:MAX_FEED_COUNT]:
        res.append((
            'resp',
            resp.ctime.timestamp(),
            resp.user.description() if resp.user else None,
            resp.form.description(),
        ))

    for log in Log.objects.filter(
        action__in=['join_org', 'leave_org'], object_id__in=all_orgs
    ).order_by('-id')[:MAX_FEED_COUNT]:
        org = Org.objects.get(id=log.object_id)
        res.append((
            log.action,
            log.time.timestamp(),
            log.session.user.description(),
            org.basic_info(),
        ))

    res.sort(key=lambda t: -t[1])
    return rest_data([{
        'type': t[0],
        'time': t[1],
        'user': t[2],
        'object': t[3],
    } for t in res[:MAX_FEED_COUNT]])
