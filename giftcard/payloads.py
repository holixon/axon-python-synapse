import dataclasses


@dataclasses.dataclass(kw_only=True)
class CardIssuedEvent:
    id: str
    amount: int = 50


@dataclasses.dataclass(kw_only=True)
class CardRedeemedEvent:
    id: str
    amount: int


@dataclasses.dataclass(kw_only=True)
class CardCanceledEvent:
    id: str


GiftCardEvent = CardIssuedEvent | CardRedeemedEvent | CardCanceledEvent


@dataclasses.dataclass(kw_only=True)
class IssueCardCommand:
    id: str
    amount: int


@dataclasses.dataclass(kw_only=True)
class RedeemCardCommand:
    id: str
    amount: int


@dataclasses.dataclass(kw_only=True)
class CancelCardCommand:
    id: str


GiftCardCommand = IssueCardCommand | RedeemCardCommand | CancelCardCommand


@dataclasses.dataclass(kw_only=True)
class CountCardSummariesQuery:
    ...


@dataclasses.dataclass(kw_only=True)
class FetchCardSummariesQuery:
    limit: int
    # offset: int


GiftCardQuery = CountCardSummariesQuery | FetchCardSummariesQuery
