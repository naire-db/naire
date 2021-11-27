from django.core.exceptions import BadRequest
from django.views.decorators.http import require_safe

from common.deco import check_logged_in
from common.log import logger
from common.rest import rest_data, acquire_json, rest_ok, rest_fail
from common.types import ensure_str, ensure_dict, ensure_int

from .models import Form, Response


@require_safe
@check_logged_in
def get_all(request):
    forms = Form.objects.filter(owner_user=request.user)
    return rest_data([dict(f.info(), resp_count=f.response_set.count()) for f in forms])


@check_logged_in
@acquire_json
def create(request, data):
    title = ensure_str(data['title'])
    body = ensure_dict(data['body'])
    form = Form(title=title, body=body, owner_user=request.user)
    try:
        form.save()
    except Exception as e:
        # Abuser may provide a too long title
        logger.warning(f'form.create: Bad request caused {type(e).__name__} {e}')
        raise BadRequest
    return rest_ok()


@acquire_json
def get_detail(request, data):
    fid = ensure_int(data['fid'])
    try:
        form = Form.objects.get(id=fid)
    except Form.DoesNotExist:
        return rest_fail()

    # TODO: Check (future) permissions.
    #  Maybe we shouldn't distinguish permission denying from nonexistence in the result code for security?

    return rest_data(form.detail())


@acquire_json
def save_resp(request, data):
    fid = ensure_int(data['fid'])
    resp_body = ensure_dict(data['resp_body'])
    try:
        form = Form.objects.get(id=fid)
    except Form.DoesNotExist:
        return rest_fail()
    if request.user.is_anonymous:
        resp = Response(form=form, body=resp_body)
    else:
        resp = Response(form=form, body=resp_body, user=request.user)
    resp.save()
    return rest_ok()


@acquire_json
def save_title(request, data):
    fid = ensure_int(data['fid'])
    title = ensure_str(data['title'])
    try:
        form = Form.objects.get(id=fid)
    except Form.DoesNotExist:
        return rest_fail()
    form.title = title
    form.save()
    return rest_ok()


@acquire_json
def change_body(request, data):
    fid = ensure_int(data['fid'])
    body = ensure_dict(data['body'])
    try:
        form = Form.objects.get(id=fid)
    except Form.DoesNotExist:
        return rest_fail()
    Response.objects.filter(form=form).delete()
    form.body = body
    form.save()
    return rest_ok()

