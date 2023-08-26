import dataclasses
from adapter.payload_service import register_payloads


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


register_payloads(
    {
        "io.axoniq.demo.giftcard.api.IssueCardCommand": IssueCardCommand,
        "io.axoniq.demo.giftcard.api.RedeemCardCommand": RedeemCardCommand,
        "io.axoniq.demo.giftcard.api.CancelCardCommand": CancelCardCommand,
        "io.axoniq.demo.giftcard.api.CardIssuedEvent": CardIssuedEvent,
        "io.axoniq.demo.giftcard.api.CardRedeemedEvent": CardRedeemedEvent,
        "io.axoniq.demo.giftcard.api.CardCanceledEvent": CardCanceledEvent,
        "io.axoniq.demo.giftcard.api.CountCardSummariesQuery": CountCardSummariesQuery,
        "io.axoniq.demo.giftcard.api.FetchCardSummariesQuery": FetchCardSummariesQuery,
    }
)
