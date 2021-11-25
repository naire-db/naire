def ensure_int(o) -> int:
    if not isinstance(o, int):
        raise TypeError
    return o


def ensure_str(o) -> str:
    if not isinstance(o, str):
        raise TypeError
    return o


def ensure_dict(o) -> dict:
    if not isinstance(o, dict):
        raise TypeError
    return o
