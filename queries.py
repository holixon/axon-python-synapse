from axon import query, axon_object


@query(name="io.axoniq.demo.giftcard.api.CountCardSummariesQuery")
class CountCardSummariesQuery:
    ...


@query(name="io.axoniq.demo.giftcard.api.FetchCardSummariesQuery")
class FetchCardSummariesQuery:
    limit: int
    offset: int


@axon_object(name="io.axoniq.demo.giftcard.api.CardSummary", group="data")
class CardSummary:
    id: str
    initialValue: int
    remainingValue: int
    issued: str
    lastUpdated: str
