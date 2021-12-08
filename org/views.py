from django.core.exceptions import PermissionDenied, BadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe

from common.deco import check_logged_in
from common.models import save_or_400
from common.rest import acquire_json, rest_data, rest_ok, rest_fail
from common.types import ensure_str, ensure_int

from common.utils import generate_token_16
from audit.actions import save_log
from form.models import Folder
from .models import Org, Membership


@require_safe
@check_logged_in
def get_joined(request):
    return rest_data([m.org_info() for m in request.user.membership_set.all()])


@check_logged_in
@acquire_json
def create(request, data):
    name = ensure_str(data['name'])
    folder = Folder(name='未分类')
    folder.save()
    org = Org(name=name, root_folder=folder)
    save_or_400(org)
    folder.owner_org = org
    folder.save()
    m = Membership(user=request.user, org=org, role=Membership.Role.OWNER)
    m.save()
    save_log(request, 'create_org', name)
    return rest_data(org.id)


def get_owned_org_membership(request, data) -> tuple[Org, Membership]:
    oid = ensure_int(data['oid'])
    org = get_object_or_404(Org, id=oid)
    m = get_object_or_404(org.membership_set, user=request.user)
    if m.role < Membership.Role.OWNER:
        raise PermissionDenied
    return org, m


def get_joined_org_membership(request, data) -> tuple[Org, Membership]:
    oid = ensure_int(data['oid'])
    org = get_object_or_404(Org, id=oid)
    m = get_object_or_404(org.membership_set, user=request.user)
    return org, m


@check_logged_in
@acquire_json
def get_members(request, data):
    org, m = get_joined_org_membership(request, data)
    return rest_data({
        **org.common_info(),
        'role': m.role,
        'members': [m.member_info() for m in org.membership_set.all()],
    })


@check_logged_in
@acquire_json
def leave(request, data):
    org, m = get_joined_org_membership(request, data)
    m.delete()
    save_log(request, 'leave_org', org.name, object_id=org.id)
    return rest_ok()


@acquire_json
def check_invite_token(request, data):
    token = ensure_str(data['token'])
    try:
        org = Org.objects.get(invite_token=token)
    except Org.DoesNotExist:
        return rest_fail()
    return rest_data({
        'joined': request.user.is_authenticated and org.membership_set.filter(user=request.user).exists(),
        'org': org.common_info(),
    })


@check_logged_in
@acquire_json
def accept_invite(request, data):
    token = ensure_str(data['token'])
    oid = ensure_int(data['oid'])
    try:
        org = Org.objects.get(id=oid)
    except Org.DoesNotExist:
        return rest_fail()
    if org.invite_token != token:
        return rest_fail()
    org.members.add(request.user)
    save_log(request, 'join_org', org.name, object_id=org.id)
    return rest_ok()


@check_logged_in
@acquire_json
def get_profile(request, data):
    org, _ = get_owned_org_membership(request, data)
    return rest_data(org.privileged_info())


@check_logged_in
@acquire_json
def rename(request, data):
    org, _ = get_owned_org_membership(request, data)
    org.name = ensure_str(data['name'])
    save_or_400(org)
    return rest_ok()


@check_logged_in
@acquire_json
def refresh_invite_token(request, data):
    org, _ = get_owned_org_membership(request, data)
    res = org.invite_token = generate_token_16()
    org.save()
    return rest_data(res)


def get_owned_membership(request, data) -> Membership:
    org, _ = get_owned_org_membership(request, data)
    uid = ensure_int(data['uid'])
    if uid == request.user.id:
        raise BadRequest
    return get_object_or_404(org.membership_set, user_id=uid)


@check_logged_in
@acquire_json
def remove_member(request, data):
    m = get_owned_membership(request, data)
    m.delete()
    return rest_ok()


@check_logged_in
@acquire_json
def change_role(request, data):
    role = ensure_int(data['role'])
    m = get_owned_membership(request, data)
    m.role = role
    m.save()
    return rest_ok()


@check_logged_in
@acquire_json
def dissolve(request, data):
    org, _ = get_owned_org_membership(request, data)
    org.delete()
    save_log(request, 'dissolve_org', org.name)
    return rest_ok()
