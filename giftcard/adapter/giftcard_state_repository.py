from giftcard.domain.giftcard_view import GiftCardSummary
from giftcard.payloads import *
from application.repositories import ViewStateRepository


class GiftCardViewStateRepository(
    ViewStateRepository[GiftCardEvent, GiftCardSummary | None]
):
    def __init__(self) -> None:
        self.table: dict[str, GiftCardSummary] = {}

    async def fetch_state(self, event: GiftCardEvent) -> GiftCardSummary | None:
        return self.table.get(event.id)

    async def save(self, state: GiftCardSummary | None) -> GiftCardSummary | None:
        if state:
            self.table[state.id] = state
        return state
