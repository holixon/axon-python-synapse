import dataclasses
from typing import Protocol, Any, runtime_checkable
from functools import partial


JSONType = str | int | float | bool | None | dict[str, Any], list[Any]
AXON_JAVA_CLASS_MAPPING = {}


@runtime_checkable
class AxonObject(Protocol):
    _name: str
    _group: str


def axon_object(group, name):
    def decorator(_class):
        _class._name = name
        _class._group = group
        _dataclass = dataclasses.dataclass(_class)
        AXON_JAVA_CLASS_MAPPING[name] = _dataclass
        return _dataclass

    return decorator


command = partial(axon_object, "commands")
query = partial(axon_object, "queries")
event = partial(axon_object, "events")
