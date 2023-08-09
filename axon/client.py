import dataclasses
from typing import Any
from aiohttp import ClientSession
from .objects import AxonObject

JSONType = str | int | float | bool | None | dict[str, Any], list[Any]


@dataclasses.dataclass
class AxonRequestError(Exception):
    path: str = None
    code: str = None
    error: str = None
    requestId: str = None
    timestamp: str = None
    status: int = None


class AxonSynapseClient:
    def __init__(self, url: str = None, context: str = "default") -> None:
        self.url = url or "http://localhost:8080"
        self.context = context
        self.session = ClientSession()

    async def dispatch(self, command: AxonObject):
        endpoint = self._make_url_from_obj(command)
        jsondata = dataclasses.asdict(command)
        return await self._post(endpoint, jsondata)

    async def query(
        self,
        query: AxonObject,
        response_type: type[AxonObject],
        response_cardinality: str = "multiple",
    ):
        endpoint = self._make_url_from_obj(query)
        jsondata = dataclasses.asdict(query)
        headers = {
            "AxonIQ-PayloadType": query._name,
            "AxonIQ-ResponseType": response_type._name,
            "AxonIQ-ResponseCardinality": response_cardinality,
        }
        return await self._post(endpoint, jsondata, headers)

    async def apply(
        self,
        event: AxonObject,
        aggregate_id: str,
        aggregate_type: str,
        sequence_number: int,
    ):
        endpoint = self._make_url_from_obj(event)
        jsondata = dataclasses.asdict(event)
        headers = {
            "AxonIQ-AggregateId": aggregate_id,
            "AxonIQ-AggregateType": aggregate_type,
            "AxonIQ-SequenceNumber": f"{sequence_number}",
        }
        return await self._post(endpoint, jsondata, headers)

    async def register_handler(
        self, local_endpoint: str, group: str, names: list[str], component_name: str
    ):
        if len(names) == 0:
            return
        endpoint = self._make_url("handlers", group)
        await self._post(
            endpoint,
            json={
                "names": names,
                "endpoint": f"{local_endpoint}/{group}",
                "endpointType": "http-raw",
                "clientId": "axon-python",
                "componentName": component_name,
                # "batchSize": 2,
            },
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        await self.session.close()

    def _make_url(self, group: str, name: str):
        return f"{self.url}/v1/contexts/{self.context}/{group}/{name}"

    def _make_url_from_obj(self, obj: AxonObject):
        return self._make_url(obj._group, obj._name)

    async def _post(self, endpoint: str, json: JSONType, headers=None) -> JSONType:
        async with self.session.post(endpoint, headers=headers, json=json) as response:
            if response.content_type == "application/json":
                result = await response.json()
            else:
                result = await response.text()

            print("RESPONSE:", result)

            if not response.ok:
                if isinstance(result, dict):
                    raise AxonRequestError(**result)
                response.raise_for_status()

            return result
