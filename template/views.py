from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe

from common.deco import check_logged_in
from common.rest import rest_data, acquire_json, rest_ok
from common.types import ensure_int

from form.actions import get_owned_form
from .models import Template


@check_logged_in
@acquire_json
def check_form(request, data):
    form = get_owned_form(request, data)
    return rest_data(form.tmpl_status())


@check_logged_in
@acquire_json
def create(request, data):
    form = get_owned_form(request, data)
    tmpl = Template(title=form.title, user=request.user, body=form.body, mtime=form.mtime)
    tmpl.save()
    form.tmpl = tmpl
    form.save()
    return rest_ok()


@check_logged_in
@acquire_json
def update(request, data):
    form = get_owned_form(request, data)
    tmpl = form.tmpl
    if tmpl is None:
        raise Http404
    tmpl.body = form.body
    tmpl.mtime = form.mtime
    tmpl.save()
    return rest_ok()


def get_owned_tmpl(request, data):
    tid = ensure_int(data['tid'])
    tmpl = get_object_or_404(Template, id=tid)
    if tmpl.user != request.user:
        raise PermissionDenied
    return tmpl


@check_logged_in
@acquire_json
def remove(request, data):
    tmpl = get_owned_tmpl(request, data)
    tmpl.delete()
    return rest_ok()


@require_safe
def get_all(request):
    return rest_data([t.info() for t in Template.objects.all()])
