import dataclasses
from datetime import datetime

from typing import Callable, Any, TypeVar, Awaitable
from pprint import pprint
from aiohttp import web
from aiohttp.typedefs import Handler
from termcolor import colored, cprint
from axon.adapter.payloads import payloadclass, dumps


@dataclasses.dataclass
class EventMessage:
    eventName: str
    messageId: str
    dateTime: str
    index: int
    aggregateId: str
    aggregateType: str
    sequenceNumber: int

    @property
    def payloadType(self):
        return self.eventName


@dataclasses.dataclass
class CommandMessage:
    commandName: str
    messageId: str
    payloadType: str
    priority: int
    routingKey: str


@dataclasses.dataclass
class QueryMessage:
    queryName: str
    messageId: str
    payloadType: str


AxonMessage = TypeVar("AxonMessage", CommandMessage, QueryMessage, EventMessage)

# AxonMessage = CommandMessage | QueryMessage | EventMessage
AxonMessageHandler = Callable[[Any, AxonMessage], Awaitable[Any | None]]
AxonHandlerFactory = Callable[[AxonMessageHandler], Handler]


def message_handler(
    mtype: type[AxonMessage],
) -> AxonHandlerFactory:
    def wrapper(handler: AxonMessageHandler) -> Handler:
        async def handle(request: web.Request) -> web.StreamResponse:
            if request.content_type != "application/json":
                return web.Response()
            kwargs = {
                f.name: f.type(request.headers.get(f"AxonIQ-{f.name}"))
                for f in dataclasses.fields(mtype)
            }
            message = mtype(**kwargs)
            # print(
            #     colored("MESSAGE", "green"),
            #     colored(str(message), "light_green"),
            # )
            payload = await request.json()
            # print(colored("PAYLOAD", "yellow"), payload)
            obj = payloadclass.to_instance(message.payloadType, payload)
            # print("OBJECT", obj)
            result = await handler(obj, message)
            # print(colored("RESULT", "light_blue"), result)
            return web.json_response(result, dumps=dumps)

        return handle

    return wrapper


event_message_handler: AxonHandlerFactory = message_handler(EventMessage)
command_message_handler: AxonHandlerFactory = message_handler(CommandMessage)
query_message_handler: AxonHandlerFactory = message_handler(QueryMessage)
