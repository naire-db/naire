from django.core.exceptions import BadRequest
from django.views.decorators.http import require_safe, require_POST

from common.deco import check_logged_in
from common.log import logger
from common.rest import rest_data, acquire_json, rest_ok
from common.types import ensure_str, ensure_dict
from .models import Form


@require_safe
@check_logged_in
def get_all(request):
    forms = Form.objects.filter(owner_user=request.user)
    return rest_data([dict(f.info(), resp_count=f.response_set.count()) for f in forms])


@require_POST
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
