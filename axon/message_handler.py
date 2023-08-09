import json
import dataclasses
from aiohttp import web
from .objects import AxonObject, AXON_JAVA_CLASS_MAPPING


@dataclasses.dataclass
class QueryMessage:
    query_name: str
    message_id: str
    payload_type: str


@dataclasses.dataclass
class EventMessage:
    event_name: str
    message_id: str
    date_time: str
    index: int
    aggregate_id: str
    aggregate_type: str
    sequence_number: int


@dataclasses.dataclass
class CommandMessage:
    message_id: str
    command_name: str
    payload_type: str
    priority: int
    routing_key: str


class MessageHandler:
    def __init__(self, message_type: type[AxonObject]) -> None:
        self.message_type = message_type
        self.header_keys = self._get_header_keys()
        self.type_key = dataclasses.fields(message_type)[0].name
        self.handlers = {}

    def names(self):
        return list(self.handlers.keys())

    def __call__(self, objclass: type[AxonObject]):
        def decorator(func):
            self.handlers[objclass._name] = func
            return func

        return decorator

    async def handle(self, request):
        message = self._message_from_header(request.headers)
        body = await request.json()
        msg_name = getattr(message, self.type_key)
        ObjectClass = AXON_JAVA_CLASS_MAPPING.get(msg_name)
        obj = ObjectClass(**body)
        func = self.handlers.get(msg_name)
        result = await func(obj, message)
        result_txt = json.dumps(result or "")
        return web.Response(text=result_txt)

    def _message_from_header(self, header):
        return self.message_type(*[header.get(key) for key in self.header_keys])

    def _get_header_keys(self):
        def sc_to_cc(snake):
            return "".join(w.title() for w in snake.split("_"))

        return [
            f"AxonIQ-{sc_to_cc(f.name)}" for f in dataclasses.fields(self.message_type)
        ]
