import secrets

from user_agents import parse


def generate_token_16():
    return secrets.token_urlsafe(16)


def get_client_ip(request):
    if xff := request.META.get('HTTP_X_FORWARDED_FOR'):
        return xff.split(',')[0]
    return request.META['REMOTE_ADDR']


def get_client_intro(request):
    return f"{get_client_ip(request)}, {str(parse(request.META.get('HTTP_USER_AGENT')))}"
