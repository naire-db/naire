from datetime import datetime

def ensure_int(o) -> int:
    if not isinstance(o, int):
        raise TypeError
    return o


def ensure_str(o) -> str:
    if not isinstance(o, str):
        raise TypeError
    return o


def ensure_bool(o) -> bool:
    if not isinstance(o, bool):
        raise TypeError
    return o


def ensure_dict(o) -> dict:
    if not isinstance(o, dict):
        raise TypeError
    return o


def ensure_number(o) -> float:
    if not isinstance(o, int) and not isinstance(o, float):
        raise TypeError
    return o


def ensure_datetime(o) -> datetime:
    try:
        return datetime.utcfromtimestamp(ensure_number(o))
    except (OverflowError, OSError):
        raise TypeError
