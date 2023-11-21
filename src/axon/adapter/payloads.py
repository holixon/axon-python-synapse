import json
from typing import Callable, Protocol, ClassVar, TypeVar, Any, runtime_checkable
from dataclasses import dataclass, is_dataclass, asdict
from functools import partial

T = TypeVar("T")


class _PayloadClass:
    def __init__(self: Any):
        self._payloads: dict[str, type[object]] = {}
        self._payload_types: dict[type[object], str] = {}

    def __call__(self, payload_type: str) -> Callable[[type[T]], type[Any]]:
        def wrapper(cls: type[Any]) -> type[Any]:
            if not is_dataclass(cls):
                raise TypeError(f"{cls.__qualname__} is not a dataclass")
            self._payloads[payload_type] = cls
            self._payload_types[cls] = payload_type
            return cls

        return wrapper

    def type_name(self, cls):
        return self._payload_types[cls]

    def to_instance(self, payload_type: str, payload: dict[str, Any]) -> Any:
        cls = self._payloads[payload_type]
        return cls(**payload)

    def to_payload(self, obj):
        return asdict(obj)


payloadclass = _PayloadClass()


# ---------------------------------------------------------------------------
class _DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


dumps = partial(json.dumps, cls=_DataclassJSONEncoder)
