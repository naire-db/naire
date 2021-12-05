from django.views.decorators.http import require_safe

from audit.models import Log
from common.deco import check_logged_in
from common.rest import rest_data


@require_safe
@check_logged_in
def get_logs(request):
    return rest_data([i.detail() for i in Log.objects.filter(session__user=request.user)])
