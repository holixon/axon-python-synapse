from application.repositories import ViewStateRepository
from giftcard.payloads import FetchCardSummariesQuery, GiftCardQuery


def giftcard_query_handler(state_repository: ViewStateRepository):
    async def handle(query: GiftCardQuery):
        match query:
            case FetchCardSummariesQuery():
                return await state_repository.fetch_all()
            case _:
                print(f"Nothing found for {query}")

    return handle
