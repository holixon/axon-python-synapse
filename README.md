# Axon Synapse Demo in Python

### Interfaces

Domain Layer

- IView
- IDecider

Application Layer

- IMaterializedView
- ViewStateRepository
- EventRepository, EventLockingRepository
- IEventSourcingAggregate, IEventSourcingLockingAggregate

### Implementation

Adapter Layer

- GiftCardEventRepository
- GiftCardViewStateRepository


Application Layer

- MaterializedView: Handles events and updates states
- giftcard_query_handler: Handles queries on updated states
- EventSourcingAggregate, EventSourcingLockingAggregate: Handle commands and emit events

Domain Layer

- GiftCardSummaryView: Implementes the `evolve` function.
- GiftCardDecider: Implements the `evolve` and `decide` functions.
