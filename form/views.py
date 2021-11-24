from django.views.decorators.http import require_safe

from common.rest import rest_data
from common.deco import check_logged_in

from .models import Form


@require_safe
@check_logged_in
def get_all(request):
    forms = Form.objects.filter(owner_user=request.user)
    return rest_data([dict(f.info(), resp_count=f.response_set.count()) for f in forms])
