from typing import Any, Tuple
from synapse_client import AxonSynapseClient
from application.repositories import EventLockingRepository
from adapter.payload_service import (
    object_from_payload,
    payload_type_from_object,
    payload_from_object,
)
from giftcard.payloads import *


class GiftCardEventRepository(
    EventLockingRepository[GiftCardCommand, GiftCardEvent, int]
):
    def __init__(self, client: AxonSynapseClient) -> None:
        self.client = client

    async def fetch_events(self, c: GiftCardCommand) -> list[Tuple[GiftCardEvent, int]]:
        async with AxonSynapseClient() as client:
            response = await client.fetch_aggregate_events(c.id)
        events = [
            (object_from_payload(r.payloadType, r.payload), r.sequenceNumber)
            for r in response.items
        ]
        return events

    async def save(
        self, event: GiftCardEvent, latest_version: int | None
    ) -> Tuple[GiftCardEvent, int]:
        next_version = 0 if latest_version is None else latest_version + 1
        async with AxonSynapseClient() as client:
            await client.append_event(
                aggregate_id=event.id,  # TODO: externalize
                aggregate_type="GiftCard",
                payload_type=payload_type_from_object(event),
                payload=payload_from_object(event),
                sequence_number=next_version,
            )
        return (event, next_version)

    async def save_all(
        self, events: list[GiftCardEvent], latest_version: int | None
    ) -> list[Tuple[GiftCardEvent, int]]:
        results = []
        version = latest_version
        for event in events:
            results.append(await self.save(event, version))
            version = (version or 0) + 1
        return results
