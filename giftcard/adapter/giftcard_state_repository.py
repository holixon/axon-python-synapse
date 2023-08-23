from giftcard.domain.giftcard_view import GiftCardSummary
from giftcard.payloads import *
from application.repositories import ViewStateRepository


class GiftCardViewStateRepository(ViewStateRepository[GiftCardEvent, GiftCardSummary]):
    def __init__(self) -> None:
        self.table: dict[str, GiftCardSummary] = {}

    async def fetch_state(self, event: GiftCardEvent) -> GiftCardSummary | None:
        return self.table.get(event.id)

    async def save(self, state: GiftCardSummary) -> GiftCardSummary:
        if state:
            self.table[state.id] = state
        return state

    async def fetch_all(self) -> list[GiftCardSummary]:
        return list(self.table.values())
