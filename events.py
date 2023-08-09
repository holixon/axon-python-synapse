from axon import event


@event("io.axoniq.demo.giftcard.api.CardIssuedEvent")
class CardIssuedEvent:
    id: str
    amount: int


@event("io.axoniq.demo.giftcard.api.CardRedeemedEvent")
class CardRedeemedEvent:
    id: str
    amount: int


@event("io.axoniq.demo.giftcard.api.CardCanceledEvent")
class CardCanceledEvent:
    id: str
