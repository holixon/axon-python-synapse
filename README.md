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

To send commands, events, queries to the server, define an `async` function with one argument in its signature.

```
async def main(client: axon.AxonSynapseClient):
    command = IssueCardCommand("DemoCard-001", 75)
    await client.dispatch(command)
```

An `AxonSynapseClient` object implements the essential POST requests to commands, events and queries.

```
# Pseudo code 
class AxonSynapseClient:

    # Send commands with
    def dispatch(command): ...

    # Send queries with
    def query(query): ...

    # Send events with
    def apply(event): ...
```

To run the application use the `run()` method and pass your entry point. 

```
app.run(main)
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