import dataclasses
from giftcard.payloads import *
from domain.decider import IDecider


@dataclasses.dataclass
class GiftCard:
    id: str
    amount: int
    enabled: bool = True


class GiftCardDecider(IDecider[GiftCardCommand, GiftCard | None, GiftCardEvent]):
    def evolve(self, state: GiftCard | None, event: GiftCardEvent) -> GiftCard | None:
        match event:
            case CardIssuedEvent():
                return GiftCard(id=event.id, amount=event.amount)
            case CardRedeemedEvent():
                if state:
                    return GiftCard(id=state.id, amount=state.amount - event.amount)
            case CardCanceledEvent():
                if state:
                    return GiftCard(id=state.id, amount=state.amount, enabled=False)
            case _:
                print(f"Nothing found for {event}")
        return None

    def decide(
        self, command: GiftCardCommand, state: GiftCard | None
    ) -> list[GiftCardEvent]:
        print("DECIDE", type(command), state)
        match command:
            case IssueCardCommand():
                return [CardIssuedEvent(id=command.id, amount=command.amount)]
            case RedeemCardCommand():
                if state:
                    if state.amount < command.amount:
                        raise ValueError(f"{state}, {command}")
                    return [CardRedeemedEvent(id=state.id, amount=command.amount)]
            case CancelCardCommand():
                return [CardCanceledEvent(id=command.id)]
            case _:
                print(f"Nothing found for {command}")
        return []

    @property
    def initial_state(self) -> GiftCard | None:
        return None
