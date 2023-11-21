import dataclasses
from . import JSONType

__all__ = [
    "EventResponse",
    "FetchAggregateEventsResponse",
    "RegisterCommandHandlerReponse",
    "RegisterEventHandlerReponse",
    "RegisterQueryHandlerReponse",
]


@dataclasses.dataclass
class EventResponse:
    aggregateId: str
    aggregateType: str
    dateTime: str
    id: str
    metaData: dict[str, str]
    name: str
    payload: JSONType
    payloadType: str
    sequenceNumber: int
    index: int | None = None
    payloadRevision: int | None = None


@dataclasses.dataclass
class FetchAggregateEventsResponse:
    items: list[EventResponse]


@dataclasses.dataclass
class RegisterCommandHandlerReponse:
    id: str
    names: list[str]
    endpoint: str
    endpointType: str
    endpointOptions: list[dict[str, str]]
    clientId: str
    componentName: str
    loadFactor: int
    concurrency: int
    enabled: bool
    context: str
    clientAuthenticationId: str | None = None
    serverAuthenticationId: str | None = None
    lastError: str | None = None


@dataclasses.dataclass
class RegisterEventHandlerReponse:
    id: str
    start: int
    context: str
    enabled: bool
    batchSize: int
    names: list[str]
    endpoint: str
    endpointType: str
    endpointOptions: list[dict[str, str]]
    clientId: str
    componentName: str
    synapseInstanceId: str | None = None
    clientAuthenticationId: str | None = None
    serverAuthenticationId: str | None = None
    lastError: str | None = None


@dataclasses.dataclass
class RegisterQueryHandlerReponse:
    id: str
    names: list[str]
    endpoint: str
    endpointType: str
    endpointOptions: list[dict[str, str]]
    clientId: str
    componentName: str
    context: str
    enabled: bool
    clientAuthenticationId: str | None = None
    serverAuthenticationId: str | None = None
    lastError: str | None = None
