import dataclasses


@dataclasses.dataclass
class AxonRequestError(Exception):
    path: str
    code: str
    error: str
    requestId: str
    timestamp: str
    status: int
