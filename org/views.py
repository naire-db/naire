from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe

from common.deco import check_logged_in
from common.models import save_or_400
from common.rest import acquire_json, rest_data
from common.types import ensure_str, ensure_int

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
    m = Membership(user=request.user, org=org, role=Membership.Role.OWNER)
    m.save()
    return rest_data(org.id)


def get_owned_org_membership(request, data) -> tuple[Org, Membership]:
    oid = ensure_int(data['oid'])
    org = get_object_or_404(Org, id=oid)
    m = get_object_or_404(org.membership_set, user=request.user)
    if m.role < Membership.Role.OWNER:
        raise PermissionDenied
    return org, m


@check_logged_in
@acquire_json
def get_members(request, data):
    org, _ = get_owned_org_membership(request, data)
    # TODO: include a share token
    return rest_data({
        'name': org.name,
        'members': [m.member_info() for m in org.membership_set.all()]
    })
