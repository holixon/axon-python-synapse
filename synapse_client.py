import dataclasses
from typing import Any, Optional
from pprint import pprint
import asyncio
from aiohttp import ClientSession


JSONType = str | int | float | bool | None | dict[str, Any] | list[Any]


@dataclasses.dataclass
class AxonRequestError(Exception):
    path: str
    code: str
    error: str
    requestId: str
    timestamp: str
    status: int


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
    clientAuthenticationId: str
    serverAuthenticationId: str
    lastError: str
    id: str


@dataclasses.dataclass
class RegisterEventHandlerReponse:
    batchSize: int
    names: list[str]
    endpoint: str
    endpointType: str
    endpointOptions: list[dict[str, str]]
    clientId: str
    componentName: str
    synapseInstanceId: str | None
    start: int
    context: str
    enabled: bool
    clientAuthenticationId: str
    serverAuthenticationId: str
    lastError: str
    id: str


@dataclasses.dataclass
class RegisterQueryHandlerReponse:
    names: list[str]
    endpoint: str
    endpointType: str
    endpointOptions: list[dict[str, str]]
    clientId: str
    componentName: str
    context: str
    enabled: bool
    clientAuthenticationId: str
    serverAuthenticationId: str
    lastError: str
    id: str


class AxonSynapseClient:
    def __init__(self, api_url: str = "http://localhost:8080/v1") -> None:
        self.api_url = api_url
        self.session = ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        await self.session.close()

    async def fetch_aggregate_events(
        self, aggregate_id: str, context: str = "default"
    ) -> FetchAggregateEventsResponse:
        async with self.session.get(
            f"{self.api_url}/contexts/{context}/aggregate/{aggregate_id}/events"
        ) as response:
            response.raise_for_status()
            if response.content_type == "application/json":
                result = await response.json()
                items = [EventResponse(**e) for e in result.get("items")]
            else:
                items = []
            return FetchAggregateEventsResponse(items=items)

    async def dispatch_command(
        self,
        command_name: str,
        payload: JSONType,
        payload_type: str | None = None,
        payload_revision: str | None = None,
        priority: int | None = None,
        routing_key: str | None = None,
        context: str | None = "default",
    ) -> str:
        print(command_name, payload)
        async with self.session.post(
            url=f"{self.api_url}/contexts/{context}/commands/{command_name}",
            json=payload,
            headers={
                k: v
                for k, v in (
                    ("AxonIQ-PayloadType", payload_type),
                    ("AxonIQ-PayloadRevision", payload_revision),
                    ("AxonIQ-Priority", priority),
                    ("AxonIQ-RoutingKey", routing_key),
                )
                if v is not None
            },
        ) as response:
            response.raise_for_status()
            return await response.text()

    async def append_event(
        self,
        aggregate_id: str,
        aggregate_type: str,
        payload: JSONType,
        payload_type: str,
        payload_revision: str | None = None,
        sequence_number: int = 0,
        context: str = "default",
    ):
        async with self.session.post(
            url=f"{self.api_url}/contexts/{context}/events/{payload_type}",
            json=payload,
            headers={
                k: v
                for k, v in (
                    ("AxonIQ-PayloadRevision", payload_revision),
                    ("AxonIQ-AggregateType", aggregate_type),
                    ("AxonIQ-AggregateId", aggregate_id),
                    ("AxonIQ-SequenceNumber", str(sequence_number)),
                )
                if v is not None
            },
        ) as response:
            response.raise_for_status()

    async def publish_query(
        self,
        query_name: str,
        payload: JSONType,
        payload_type: str,
        response_type: str | None = None,
        response_cardinality: str | None = None,
        payload_revision: str | None = None,
        context: str = "default",
    ):
        async with self.session.post(
            url=f"{self.api_url}/contexts/{context}/queries/{query_name}",
            json=payload,
            headers={
                k: v
                for k, v in (
                    ("AxonIQ-PayloadType", payload_type),
                    ("AxonIQ-PayloadRevision", payload_revision),
                    ("AxonIQ-ResponseType", response_type),
                    ("AxonIQ-ResponseCardinality", response_cardinality),
                    ("AxonIQ-ResponseTypeEncoding", "application/json"),
                )
                if v is not None
            },
        ) as response:
            response.raise_for_status()
            result = await response.json()
            return result

    async def register_command_handler(
        self,
        handler_id: str,
        client_id: str,
        component_name: str,
        names: list[str],
        callback_endpoint: str,
        context: str = "default",
    ):
        result = await self.register_handler(
            handler_type="commands",
            handler_id=handler_id,
            client_id=client_id,
            component_name=component_name,
            names=names,
            callback_endpoint=callback_endpoint,
            context=context,
        )
        return RegisterCommandHandlerReponse(**result)

    async def register_event_handler(
        self,
        handler_id: str,
        client_id: str,
        component_name: str,
        names: list[str],
        callback_endpoint: str,
        context: str = "default",
    ):
        result = await self.register_handler(
            handler_type="events",
            handler_id=handler_id,
            client_id=client_id,
            component_name=component_name,
            names=names,
            callback_endpoint=callback_endpoint,
            context=context,
        )
        return RegisterEventHandlerReponse(**result)

    async def register_query_handler(
        self,
        handler_id: str,
        client_id: str,
        component_name: str,
        names: list[str],
        callback_endpoint: str,
        context: str = "default",
    ):
        result = await self.register_handler(
            handler_type="queries",
            handler_id=handler_id,
            client_id=client_id,
            component_name=component_name,
            names=names,
            callback_endpoint=callback_endpoint,
            context=context,
        )
        pprint(result)
        return RegisterQueryHandlerReponse(**result)

    async def register_handler(
        self,
        handler_type: str,  # enum: "commands", "events", "queries"
        handler_id: str,
        client_id: str,
        component_name: str,
        names: list[str],
        callback_endpoint: str,
        context: str = "default",
    ):
        async with self.session.put(
            url=f"{self.api_url}/contexts/{context}/handlers/{handler_type}/{handler_id}",
            json={
                "names": names,
                "endpoint": callback_endpoint,
                "endpoint_type": "http-raw",
                "clientId": client_id,
                "componentName": component_name,
            },
        ) as response:
            response.raise_for_status()
            result = await response.json()
            pprint(result)
            return result


async def test_query(client: AxonSynapseClient):
    summaries = await client.publish_query(
        "io.axoniq.demo.giftcard.api.FetchCardSummariesQuery",
        {
            "limit": 10,
            #  "offset": 0,
        },
        payload_type="io.axoniq.demo.giftcard.api.FetchCardSummariesQuery",
    )
    pprint(summaries)


async def test_card(client, card_id):
    await client.dispatch_command(
        "io.axoniq.demo.giftcard.api.IssueCardCommand",
        {"id": card_id, "amount": 100},
    )

    await client.dispatch_command(
        "io.axoniq.demo.giftcard.api.RedeemCardCommand",
        {"id": card_id, "amount": 11},
    )
    # await client.dispatch_command(
    #     "io.axoniq.demo.giftcard.api.RedeemCardCommand",
    #     {"id": card_id, "amount": 17},
    # )

    # await client.dispatch_command(
    #     "io.axoniq.demo.giftcard.api.RedeemCardCommand",
    #     {"id": card_id, "amount": 36},
    # )

    # await client.dispatch_command(
    #     "io.axoniq.demo.giftcard.api.RedeemCardCommand",
    #     {"id": card_id, "amount": 6},
    # )
    events = await client.fetch_aggregate_events(card_id)
    pprint(events)


import uuid


async def main():
    async with AxonSynapseClient() as client:
        for _ in range(10):
            await test_card(client, card_id=f"axon-demo-{uuid.uuid4()}")
        await test_query(client)

        # result = await client.append_event(
        #     aggregate_id="abc-via-event2",
        #     aggregate_type="GiftCard",
        #     payload={
        #         "id": "abc-via-event2",
        #     },
        #     payload_type="io.axoniq.demo.giftcard.api.CardIssuedEvent",
        #     sequence_number=5,
        # )
        # pprint(result)

        # result = await client.publish_query(
        #     query_name="io.axoniq.demo.giftcard.api.FetchCardSummariesQuery",
        #     payload={
        #         # "offset": 0,
        #         "limit": 10,
        #         # "id": "hello-py-1",
        #     },
        #     response_cardinality="multiple",
        #     payload_type="io.axoniq.demo.giftcard.api.FetchCardSummariesQuery",
        #     response_type="io.axoniq.demo.giftcard.api.CardSummary",
        # )
        # pprint(result)

        # result = await client.register_handler(
        #     handler_id="abc",
        #     handler_type="commands",
        #     names=["my.demo.command"],
        #     callback_endpoint="http://localhost:8088/commands",
        #     client_id="python-demo-7c78946494-p86ts",
        #     component_name="Demo",
        # )
        # pprint(result)

        # result = await client.register_command_handler(
        #     handler_id="abc",
        #     client_id="python-demo-7c78946494-p86ts",
        #     component_name="Demo",
        #     names=["my.demo.command"],
        #     callback_endpoint="http://localhost:8088/commands",
        # )
        # pprint(result)


if __name__ == "__main__":
    asyncio.run(main())
