import datetime

from django.core.exceptions import PermissionDenied, BadRequest
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from django.views.decorators.http import require_safe

from audit.actions import get_ip, save_log
from audit.models import Ip
from common.deco import check_logged_in
from common.errors import ERR_EXPIRED, ERR_AUTH_REQUIRED, ERR_DENIED, ERR_LIMITED
from common.models import save_or_400, get_user
from common.rest import rest_data, acquire_json, rest_ok, rest_fail, rest
from common.types import ensure_str, ensure_dict, ensure_int, ensure_bool, ensure_datetime

from user.models import User
from org.models import Membership, Org
from .models import Form, Response, Folder


def get_admin_org(user: User, oid: int):
    org = get_object_or_404(Org, id=oid)
    m = get_object_or_404(org.membership_set, user=user)
    if m.role < Membership.Role.ADMIN:
        raise PermissionDenied
    return org


def add_overview_base(user: User, d: dict[str]):
    admin_mss = user.membership_set.filter(role__gte=Membership.Role.ADMIN)
    d['admin_orgs'] = [f.org.basic_info() for f in admin_mss]


def get_raw_overview(user: User):
    root_forms = Form.objects.filter(folder=user.root_folder)
    folders = Folder.objects.filter(owner_user=user)
    res = {
        'root_fid': user.root_folder_id,
        'root_forms': [f.info() for f in root_forms],
        'folders': [f.info() for f in folders],
    }
    add_overview_base(user, res)
    return res


@require_safe
@check_logged_in
def get_overview(request):
    return rest_data(get_raw_overview(request.user))


def get_raw_org_overview(user: User, org: Org):
    root_forms = Form.objects.filter(folder=org.root_folder)
    folders = Folder.objects.filter(owner_org=org)
    return {
        'root_fid': org.root_folder_id,
        'root_forms': [f.info() for f in root_forms],
        'folders': [f.info() for f in folders],
    }


@check_logged_in
@acquire_json
def get_org_overview(request, data):
    oid = ensure_int(data['oid'])
    org = get_admin_org(request.user, oid)
    return rest_data(get_raw_org_overview(request.user, org))


@check_logged_in
@acquire_json
def get_folder_overview(request, data):
    folder = get_owned_folder(request, data)
    user: User = request.user
    if folder.owner_org:
        res = get_raw_org_overview(request.user, folder.owner_org)
        add_overview_base(user, res)
        res['context'] = folder.owner_org_id
    else:
        res = get_raw_overview(user)
        res['context'] = None
    return rest_data(res)


def ensure_owned_folder(user: User, folder: Folder):
    if user != folder.owner_user:
        try:
            m = folder.owner_org.membership_set.get(user=user)
        except Membership.DoesNotExist:
            raise PermissionDenied
        if m.role < Membership.Role.ADMIN:
            raise PermissionDenied


def ensure_owned_form(user: User, form: Form):
    ensure_owned_folder(user, form.folder)


def get_owned_folder(request, data) -> Folder:
    folder_id = ensure_int(data['folder_id'])
    folder = get_object_or_404(Folder, id=folder_id)
    ensure_owned_folder(request.user, folder)
    return folder


def get_owned_form(request, data) -> Form:
    form_id = ensure_int(data['fid'])
    form = get_object_or_404(Form, id=form_id)
    ensure_owned_form(request.user, form)
    return form


def get_owned_resp_form(request, data):
    fid = ensure_int(data['fid'])
    rid = ensure_int(data['rid'])
    resp = get_object_or_404(Response, id=rid)
    form = resp.form
    if form.id != fid:
        raise Http404  # TODO: can be exploited
    ensure_owned_form(request.user, form)
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
    oid = data['oid']
    user = request.user
    if oid is None:
        folder = Folder(name=name, owner_user=user)
    else:
        org = get_admin_org(user, ensure_int(oid))
        folder = Folder(name=name, owner_org=org)
    folder.save()
    return rest_data(folder.info())


@check_logged_in
@acquire_json
def remove_folder(request, data):
    folder = get_owned_folder(request, data)
    # TODO: more optimized?
    if folder.owner_user is None:
        folder.form_set.update(folder_id=folder.owner_org.root_folder_id)
    else:
        folder.form_set.update(folder_id=folder.owner_user.root_folder_id)
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
    title = ensure_str(data['title'])
    body = ensure_dict(data['body'])
    folder_id = data['folder_id']
    if folder_id is None:
        folder = request.user.root_folder
    else:
        folder = get_owned_folder(request, data)
    form = Form(title=title, body=body, folder=folder)
    save_or_400(form)
    save_log(request, 'create_form', title)
    return rest_ok()


def check_limit(form: Form, limit: int, reset_time: datetime.time, q: Q):
    if limit == Form.Limit.ONCE:
        if form.response_set.filter(q).exists():
            return ERR_LIMITED
    elif limit == Form.Limit.DAILY:
        if resp := form.response_set.filter(q).order_by('id').last():
            last_time = localtime(resp.ctime)
            now = localtime()
            dt = now - last_time
            if dt.days < 1:
                lt = last_time.time()
                rt = now.time()
                mt = reset_time
                if not ((lt <= rt and lt <= mt < rt) or (lt > rt and (lt <= mt or mt < rt))):
                    return ERR_LIMITED


def ensure_form_fillable(request, form: Form, ip: Ip):
    user: User = request.user

    if form.update_published():
        form.save()

    if not form.published:
        return ERR_EXPIRED

    lr = form.login_required or form.member_required

    if not user.is_authenticated and lr:
        return ERR_AUTH_REQUIRED

    if form.member_required and not form.folder.owner_org.members.filter(id=user.id).exists():
        return ERR_DENIED

    if lr:
        if err := check_limit(form, form.user_limit, form.user_limit_reset_time, Q(user=user)):
            return err

    if err := check_limit(form, form.ip_limit, form.ip_limit_reset_time, Q(ip=ip)):
        return err


@acquire_json
def get_detail(request, data):
    fid = ensure_int(data['fid'])
    try:
        form = Form.objects.get(id=fid)
    except Form.DoesNotExist:
        return rest_fail()

    ip = get_ip(request)
    if code := ensure_form_fillable(request, form, ip):
        return rest(code=code)

    return rest_data(form.detail())


@acquire_json
def save_resp(request, data):
    fid = ensure_int(data['fid'])
    resp_body = ensure_dict(data['resp_body'])
    # TODO: After we implement Orgs, some member might delete a Form which another is editing.
    form = get_object_or_404(Form, id=fid)

    ip = get_ip(request)
    if code := ensure_form_fillable(request, form, ip):
        return rest(code=code)

    resp = Response(form=form, body=resp_body, user=get_user(request), ip=ip)
    resp.save()
    save_log(request, desc=form.title)
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
def get_status(request, data):
    form = get_owned_form(request, data)
    return rest_data(form.detail())


@check_logged_in
@acquire_json
def get_resp_count(request, data):
    form = get_owned_form(request, data)
    return rest_data(form.response_set.count())


@check_logged_in
@acquire_json
def remake(request, data):
    form = get_owned_form(request, data)
    title = ensure_str(data['title'])
    body = ensure_dict(data['body'])
    form.body = body
    form.title = title
    save_or_400(form)
    form.response_set.all().delete()
    save_log(request, 'remake_form', title)
    return rest_ok()


@check_logged_in
@acquire_json
def remove(request, data):
    form = get_owned_form(request, data)
    form.delete()
    save_log(request, 'remove_form', form.title)
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
def get_form_resp_full_details(request, data):
    form = get_owned_form(request, data)
    return rest_data([r.full_detail() for r in form.response_set.all()])


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


@check_logged_in
@acquire_json
def get_form_settings(request, data):
    form = get_owned_form(request, data)
    if form.update_published():
        form.save()
    return rest_data(form.settings())


@check_logged_in
@acquire_json
def save_form_settings(request, data):
    form = get_owned_form(request, data)
    data = ensure_dict(data['settings'])
    title = data['title']
    if not title:
        raise BadRequest
    form.title = title
    form.published = ensure_bool(data['published'])
    lt = data['publish_time']
    if form.published or lt is None:
        form.publish_time = None
    else:
        form.publish_time = ensure_datetime(lt)
    rt = data['unpublish_time']
    form.unpublish_time = None if rt is None else ensure_datetime(rt)
    pp = data['passphrase']
    form.passphrase = None if pp is None else pp
    form.member_required = mr = ensure_bool(data['member_required'])
    if mr and form.folder.owner_org is None:
        raise BadRequest
    lr = ensure_bool(data['login_required'])
    form.login_required = mr or lr
    form.user_limit = ensure_int(data['user_limit'])
    form.ip_limit = ensure_int(data['ip_limit'])
    form.user_limit_reset_time = ensure_str(data['user_limit_reset_time'])
    form.ip_limit_reset_time = ensure_str(data['ip_limit_reset_time'])
    form.update_published()
    save_or_400(form)
    return rest_ok()
