from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe

from common.deco import check_logged_in
from common.models import save_or_400, get_user
from common.rest import rest_data, acquire_json, rest_ok, rest_fail
from common.types import ensure_str, ensure_dict, ensure_int

from user.models import User
from .models import Form, Response, Folder


def ensure_modifiable(user: User, form: Form):
    # TODO: form owner 有可能是 Org
    if user != form.folder.owner_user:
        raise PermissionDenied


@require_safe
@check_logged_in
def get_overview(request):
    # TODO: folder id
    root_forms = Form.objects.filter(folder=request.user.root_folder)
    folders = Folder.objects.filter(owner_user=request.user)
    return rest_data({
        'root_fid': request.user.root_folder_id,
        'root_forms': [f.info() for f in root_forms],
        'folders': [f.info() for f in folders]
    })


def get_owned_folder(request, data) -> Folder:
    folder_id = ensure_int(data['folder_id'])
    folder = get_object_or_404(Folder, id=folder_id)
    if folder.owner_user != request.user:
        raise PermissionDenied
    return folder


def get_owned_form(request, data) -> Form:
    form_id = ensure_int(data['fid'])
    form = get_object_or_404(Form, id=form_id)
    if form.folder.owner_user != request.user:
        raise PermissionDenied
    return form


def get_owned_resp_form(request, data):
    fid = ensure_int(data['fid'])
    rid = ensure_int(data['rid'])
    resp = get_object_or_404(Response, id=rid)
    form = resp.form
    if form.id != fid:
        raise Http404  # TODO: can be exploited
    ensure_modifiable(request.user, form)
    return resp, form


@check_logged_in
@acquire_json
def get_folder_all(request, data):
    folder = get_owned_folder(request, data)
    return rest_data({
        'forms': [f.info() for f in folder.form_set.all()]
    })


@check_logged_in
@acquire_json
def create_folder(request, data):
    name = ensure_str(data['name'])
    folder = Folder(name=name, owner_user=request.user)
    folder.save()
    return rest_data(folder.info())


@check_logged_in
@acquire_json
def remove_folder(request, data):
    folder = get_owned_folder(request, data)
    folder.form_set.update(folder_id=request.user.root_folder_id)
    folder.delete()
    return rest_ok()


@check_logged_in
@acquire_json
def rename_folder(request, data):
    folder = get_owned_folder(request, data)
    name = ensure_str(data['name'])
    folder.name = name
    save_or_400(folder)
    return rest_ok()


@check_logged_in
@acquire_json
def move_to_folder(request, data):
    form = get_owned_form(request, data)
    folder = get_owned_folder(request, data)
    form.folder = folder
    form.save()
    return rest_ok()


@check_logged_in
@acquire_json
def copy(request, data):
    form = get_owned_form(request, data)
    folder = get_owned_folder(request, data)
    title = ensure_str(data['title'])
    form.pk = None
    form._state.adding = True
    form.make_cloned(folder, title)
    save_or_400(form)
    return rest_data(form.info())


@check_logged_in
@acquire_json
def create(request, data):
    # TODO: folder id
    title = ensure_str(data['title'])
    body = ensure_dict(data['body'])
    form = Form(title=title, body=body, folder=request.user.root_folder)
    save_or_400(form)
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
    resp = Response(form=form, body=resp_body, user=get_user(request))
    resp.save()
    return rest_ok()


@check_logged_in
@acquire_json
def save_title(request, data):
    form = get_owned_form(request, data)
    title = ensure_str(data['title'])
    form.title = title
    save_or_400(form)
    return rest_ok()


@check_logged_in
@acquire_json
def change_body(request, data):
    form = get_owned_form(request, data)
    body = ensure_dict(data['body'])
    form.response_set.all().delete()
    form.body = body
    form.save()
    return rest_ok()


@check_logged_in
@acquire_json
def remove(request, data):
    form = get_owned_form(request, data)
    form.delete()
    return rest_ok()


@check_logged_in
@acquire_json
def get_form_resps(request, data):
    form = get_owned_form(request, data)
    return rest_data({
        'form': form.detail(),
        'resps': [r.info() for r in form.response_set.all()]
    })


@check_logged_in
@acquire_json
def get_form_stats(request, data):
    form = get_owned_form(request, data)
    return rest_data({
        'form': form.detail(),
        'resps': [r.detail() for r in form.response_set.all()]
    })


@check_logged_in
@acquire_json
def get_resp_detail(request, data):
    resp, _ = get_owned_resp_form(request, data)
    return rest_data(resp.detail())


@check_logged_in
@acquire_json
def remove_resp(request, data):
    resp, _ = get_owned_resp_form(request, data)
    resp.delete()
    return rest_ok()
