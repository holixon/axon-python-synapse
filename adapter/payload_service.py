import dataclasses

_PAYLOADS: dict = {}
_REVPAYLOADS: dict = {}


def register_payloads(payloads):
    _PAYLOADS.update(payloads)
    _REVPAYLOADS.update({cls: name for name, cls in payloads.items()})


def payload_type_from_object(obj):
    return _REVPAYLOADS[obj.__class__]


def payload_types_from_objects(*objects):
    return [payload_type_from_object(o) for o in objects]


def payload_from_object(obj):
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    elif isinstance(obj, list):
        return [payload_from_object(o) for o in obj]
    elif isinstance(obj, dict):
        return {k: payload_from_object(o) for k, o in obj.items()}
    elif isinstance(obj, tuple):
        return tuple(payload_from_object(o) for o in obj)
    return obj


def object_from_payload(payload_type, payload):
    try:
        cls = _PAYLOADS[payload_type]
        return cls(**payload)
    except Exception as e:
        print(e)
        raise e
