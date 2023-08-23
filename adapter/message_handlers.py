import dataclasses
from abc import ABC, abstractmethod
from pprint import pprint
from aiohttp import web
from adapter.payload_service import object_from_payload, payload_from_object


@dataclasses.dataclass
class EventMessage:
    eventName: str
    messageId: str
    dateTime: str
    index: int
    aggregateId: str
    aggregateType: str
    sequenceNumber: int


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


class MessageHandler(ABC):
    def __init__(self, handle) -> None:
        self.handle = handle

    async def __call__(self, request):
        message = self.message_from_header(request.headers)
        payload = await request.json()
        obj = self.object_from_message(message, payload)
        result = await self.handle(obj)
        result = payload_from_object(result)

        if isinstance(result, dict | list):
            return web.json_response(result)
        else:
            return web.Response(text=str(result or ""))

    @abstractmethod
    def message_from_header(self, headers):
        pass

    @abstractmethod
    def object_from_message(self, message, payload):
        pass


class EventMessageHandler(MessageHandler):
    def message_from_header(self, headers):
        return EventMessage(
            eventName=headers.get("AxonIQ-EventName"),
            messageId=headers.get("AxonIQ-MessageId"),
            dateTime=headers.get("AxonIQ-DateTime"),
            index=headers.get("AxonIQ-Index"),
            aggregateId=headers.get("AxonIQ-AggregateId"),
            aggregateType=headers.get("AxonIQ-AggregateType"),
            sequenceNumber=headers.get("AxonIQ-SequenceNumber"),
        )

    def object_from_message(self, message, payload):
        return object_from_payload(message.eventName, payload)


class CommandMessageHandler(MessageHandler):
    def message_from_header(self, headers):
        return CommandMessage(
            commandName=headers.get("AxonIQ-CommandName"),
            messageId=headers.get("AxonIQ-MessageId"),
            payloadType=headers.get("AxonIQ-PayloadType"),
            priority=headers.get("AxonIQ-Priority"),
            routingKey=headers.get("AxonIQ-RoutingKey"),
        )

    def object_from_message(self, message, payload):
        return object_from_payload(message.payloadType, payload)


class QueryMessageHandler(MessageHandler):
    def message_from_header(self, headers):
        return QueryMessage(
            queryName=headers.get("AxonIQ-QueryName"),
            messageId=headers.get("AxonIQ-MessageId"),
            payloadType=headers.get("AxonIQ-PayloadType"),
        )

    def object_from_message(self, message, payload):
        return object_from_payload(message.payloadType, payload)
