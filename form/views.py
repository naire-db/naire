from django.core.exceptions import BadRequest
<<<<<<< HEAD
=======
from django.http import HttpResponseForbidden
>>>>>>> f891aea0cdac2ac29bb1e5005876e59b3e03192d
from django.shortcuts import get_object_or_404
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
    # TODO: After we implement Orgs, some member might delete a Form which another is editing.
    form = get_object_or_404(Form, id=fid)
    resp = Response(
        form=form, body=resp_body,
        user=request.user if request.user.is_authenticated else None
    )
    resp.save()
    return rest_ok()


@check_logged_in
@acquire_json
def save_title(request, data):
    fid = ensure_int(data['fid'])
    title = ensure_str(data['title'])
    form = get_object_or_404(Form, id=fid)
    form.title = title
    try:
        form.save()
    except Exception as e:
        # title too long
        logger.warning(f'form.save_title: Bad request caused {type(e).__name__} {e}')
        raise BadRequest
    return rest_ok()


@check_logged_in
@acquire_json
def change_body(request, data):
    fid = ensure_int(data['fid'])
    body = ensure_dict(data['body'])
    form = get_object_or_404(Form, id=fid)
    # use entryset
    Response.objects.filter(form=form).delete()
    form.body = body
    form.save()
    return rest_ok()


@check_logged_in
@acquire_json
def remove(request, data):
    fid = ensure_int(data['fid'])
    form = get_object_or_404(Form, id=fid)
    if request.user != form.owner_user:
        return HttpResponseForbidden()  # response 403 Forbidden
    form.delete()
    return rest_ok()
