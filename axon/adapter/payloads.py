import json
from typing import Callable, Protocol, ClassVar, TypeVar, Any, runtime_checkable
from dataclasses import dataclass, is_dataclass, asdict
from functools import partial

T = TypeVar("T")


@runtime_checkable
class Payload(Protocol):
    _payload_type: ClassVar[str]


_PAYLOADS: dict[str, type[Payload]] = {}


def payloadclass(payload_type: str) -> Callable[[type[T]], type[Any]]:
    def wrapper(cls: type[Any]) -> type[Any]:
        # dcls = dataclass(kw_only=True, frozen=True)(cls)
        cls._payload_type = payload_type
        _PAYLOADS[payload_type] = cls
        return cls

    return wrapper


def object_from_payload(payload_type: str, payload: dict[str, Any]) -> Any:
    cls = _PAYLOADS[payload_type]
    return cls(**payload)


def payload_from_object(obj):
    return asdict(obj)


class _DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


dumps = partial(json.dumps, cls=_DataclassJSONEncoder)
