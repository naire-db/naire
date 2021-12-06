from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from common.types import ensure_int

from org.models import Membership
from user.models import User
from .models import Form, Folder


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


def get_owned_form(request, data) -> Form:
    form_id = ensure_int(data['fid'])
    form = get_object_or_404(Form, id=form_id)
    ensure_owned_form(request.user, form)
    return form
