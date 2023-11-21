import os
from pprint import pprint
from aiohttp import ClientSession
from . import JSONType
from .errors import AxonRequestError
from .responses import *


class AxonSynapseClient:
    def __init__(self, api_url: str | None = None) -> None:
        self.api_url = api_url or os.getenv(
            "AXON_SYNAPSE_API", "http://localhost:8080/v1"
        )
        print(f"API enpoint: {self.api_url}")
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
                # print(f'Got {len(result.get("items"))} events.')
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
        # print(
        #     f"APPEND EVENT {aggregate_id}, {aggregate_type}, {payload_type}, {sequence_number}"
        # )
        # print(f"{payload}")

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
    ) -> RegisterCommandHandlerReponse:
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

    async def unregister_event_handler(
        self,
        handler_id: str,
        context: str = "default",
    ):
        async with self.session.delete(
            url=f"{self.api_url}/contexts/{context}/handlers/events/{handler_id}"
        ) as response:
            response.raise_for_status()
            return response.status == 204

    async def register_event_handler(
        self,
        handler_id: str,
        client_id: str,
        component_name: str,
        names: list[str],
        callback_endpoint: str,
        batch_size: int = 1,
        start: int = 0,
        enabled: bool = True,
        context: str = "default",
    ) -> RegisterEventHandlerReponse:
        async with self.session.put(
            url=f"{self.api_url}/contexts/{context}/handlers/events/{handler_id}",
            json={
                "names": names,
                "endpoint": callback_endpoint,
                "endpointType": "http-raw",
                "clientId": client_id,
                "componentName": component_name,
                "batchSize": batch_size,
                "start": start,
                "enabled": enabled,
            },
        ) as response:
            response.raise_for_status()
            result = await response.json()
            pprint(result)
            return RegisterEventHandlerReponse(**result)

        # result = await self.register_handler(
        #     handler_type="events",
        #     handler_id=handler_id,
        #     client_id=client_id,
        #     component_name=component_name,
        #     names=names,
        #     callback_endpoint=callback_endpoint,
        #     context=context,
        # )

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
                "endpointType": "http-raw",
                "clientId": client_id,
                "componentName": component_name,
            },
        ) as response:
            response.raise_for_status()
            result = await response.json()
            pprint(result)
            return result

    async def get_event_handlers(self, context: str = "default"):
        async with self.session.get(
            url=f"{self.api_url}/contexts/{context}/handlers/events"
        ) as response:
            response.raise_for_status()
            data = await response.json()
            pprint(data)
            return [RegisterEventHandlerReponse(**e) for e in data["items"]]

    async def get_event_handler(self, handler_id: str, context: str = "default"):
        async with self.session.get(
            url=f"{self.api_url}/contexts/{context}/handlers/events/{handler_id}"
        ) as response:
            if response.status == 404:
                return None
            response.raise_for_status()
            data = await response.json()
            pprint(data)
            return RegisterEventHandlerReponse(**data)
