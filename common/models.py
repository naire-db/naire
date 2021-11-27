from django.core.exceptions import BadRequest


def save_or_400(model):
    try:
        model.save()
    except Exception as e:
        raise BadRequest
