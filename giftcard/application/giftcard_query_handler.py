from application.repositories import ViewStateRepository
from giftcard.payloads import FetchCardSummariesQuery


def giftcard_query_handler(state_repository: ViewStateRepository):
    async def handle(query):
        match query:
            case FetchCardSummariesQuery():
                return list(state_repository.table.values())
            case _:
                print(f"Nothing found for {query}")

    return handle
