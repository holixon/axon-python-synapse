import asyncio
from pprint import pprint
from aiohttp import web
import nest_asyncio

from adapter.payload_service import register_payloads, payload_types_from_classes
from adapter.message_handlers import (
    EventMessageHandler,
    CommandMessageHandler,
    QueryMessageHandler,
)

from application.aggregates import EventSourcingLockingAggregate
from application.views import MaterializedView

from giftcard.adapter.giftcard_state_repository import GiftCardViewStateRepository
from giftcard.adapter.giftcard_event_repository import GiftCardEventRepository
from giftcard.application.giftcard_query_handler import giftcard_query_handler
from giftcard.domain.giftcard import GiftCard, GiftCardDecider
from giftcard.domain.giftcard_view import GiftCardSummaryView, GiftCardSummary
from giftcard.payloads import *

from synapse_client import AxonSynapseClient

nest_asyncio.apply()


async def run(client: AxonSynapseClient, port=8888):
    state_repository = GiftCardViewStateRepository()
    event_repository = GiftCardEventRepository(client)
    decider = GiftCardDecider()
    aggregate: EventSourcingLockingAggregate[
        GiftCardCommand, GiftCard | None, GiftCardEvent, int
    ] = EventSourcingLockingAggregate(decider, event_repository)

    app = web.Application()
    app.add_routes(
        [
            web.post(
                "/events",
                EventMessageHandler(
                    MaterializedView[GiftCardSummary, GiftCardEvent](
                        view=GiftCardSummaryView(),
                        repository=state_repository,
                    ).handle
                ),
            ),
            web.post(
                "/commands",
                CommandMessageHandler(aggregate.handle),
            ),
            web.post(
                "/queries",
                QueryMessageHandler(giftcard_query_handler(state_repository)),
            ),
        ]
    )
    web.run_app(app, port=port)


async def register_handlers(client: AxonSynapseClient):
    callback_url = "http://localhost:8888"

    kwargs = dict(
        handler_id="0274567e-1742-4446-b649-8f949ebf5527",
        client_id="python-demo-7c78946494-p86ts",
        component_name="GiftCard",
    )

    response = await client.register_event_handler(
        callback_endpoint=f"{callback_url}/events",
        names=payload_types_from_classes(
            CardIssuedEvent, CardRedeemedEvent, CardCanceledEvent
        ),
        **kwargs,
    )
    pprint(response)
    response = await client.register_command_handler(
        callback_endpoint=f"{callback_url}/commands",
        names=payload_types_from_classes(
            IssueCardCommand, RedeemCardCommand, CancelCardCommand
        ),
        **kwargs,
    )
    pprint(response)
    response = await client.register_query_handler(
        callback_endpoint=f"{callback_url}/queries",
        names=payload_types_from_classes(
            CountCardSummariesQuery, FetchCardSummariesQuery
        ),
        **kwargs,
    )
    pprint(response)


async def main():
    async with AxonSynapseClient() as client:
        await register_handlers(client=client)
        await run(client)


if __name__ == "__main__":
    asyncio.run(main())
