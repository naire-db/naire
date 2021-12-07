import secrets


def generate_token_16():
    return secrets.token_urlsafe(16)
