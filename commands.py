from axon import command


@command("io.axoniq.demo.giftcard.api.IssueCardCommand")
class IssueCardCommand:
    id: str
    amount: int


@command("io.axoniq.demo.giftcard.api.RedeemCardCommand")
class RedeemCardCommand:
    id: str
    amount: int


@command("io.axoniq.demo.giftcard.api.CancelCardCommand")
class CancelCardCommand:
    id: str
