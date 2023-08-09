# Axon Synapse Demo in Python

Defined commands, events and queries using the decorators `@command`, `@event` and `@query` respectively.

```
@command("io.axoniq.demo.giftcard.api.IssueCardCommand")
class IssueCardCommand:
    id: str
    amount: int

@event("io.axoniq.demo.giftcard.api.CardIssuedEvent")
class CardIssuedEvent:
    id: str
    amount: int

@query("io.axoniq.demo.giftcard.api.FetchCardSummariesQuery")
class FetchCardSummariesQuery:
    limit: int
    offset: int

```

The root object in a client application is `AxonSynapseApplication`. 

```
app = axon.AxonSynapseApplication()
```

To register a handler use the decorators `@app.command_handler`, `@app.event_handler`, `@app.query_handler`. 

Example:

```
@app.event_handler(CardIssuedEvent)
async def card_issued_event(event: CardIssuedEvent, message: axon.EventMessage):
    print(event)
```

To start the application and listen to handlers use the `app.listen` method.

```
app.listen(port=8888)
```