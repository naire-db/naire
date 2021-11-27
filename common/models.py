from django.core.exceptions import BadRequest
from django.http import HttpRequest

from .log import logger


def save_or_400(model):
    try:
        model.save()
    except Exception as e:
        logger.warning(f'Bad request caused {type(e).__name__} {e}')
        raise BadRequest


def get_user(request: HttpRequest):
    return request.user if request.user.is_authenticated else None
