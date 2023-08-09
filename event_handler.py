import axon
from events import CardIssuedEvent

app = axon.AxonSynapseApplication()


@app.event_handler(CardIssuedEvent)
async def card_issued_event(event: CardIssuedEvent, message: axon.EventMessage):
    print(event)


app.listen(port=8888)
