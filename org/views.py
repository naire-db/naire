from common.deco import check_logged_in
from common.models import save_or_400
from common.rest import acquire_json, rest_data
from common.types import ensure_str

from form.models import Folder
from .models import Org, Membership


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
