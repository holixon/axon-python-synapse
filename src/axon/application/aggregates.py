from functools import reduce
from typing import Tuple, TypeVar, Callable, Generic
from abc import abstractmethod
from axon.domain.decider import IDecider
from axon.application.repositories import EventRepository, EventLockingRepository

C = TypeVar("C")
S = TypeVar("S")
E = TypeVar("E")
V = TypeVar("V")


class IEventSourcingAggregate(Generic[C, E]):
    @abstractmethod
    async def handle(self, command: C) -> list[E]: ...


class IEventSourcingLockingAggregate(Generic[C, E, V]):
    @abstractmethod
    async def handle(self, command: C) -> list[Tuple[E, V]]: ...


# -----------------------------------------------------------------------------

EventComputation = Callable[[list[E], C, IDecider[C, S, E]], list[E]]


def compute_new_events_left_fold(
    events: list[E], command: C, decider: IDecider[C, S, E]
) -> list[E]:
    state = reduce(decider.evolve, events, decider.initial_state)
    return decider.decide(command, state)


# -----------------------------------------------------------------------------


class EventSourcingAggregate(
    Generic[C, S, E],
    IEventSourcingAggregate[C, E],
):
    def __init__(
        self,
        decider: IDecider[C, S, E],
        repository: EventRepository[C, E],
        compute: EventComputation[E, C, S] | None = None,
    ) -> None:
        self.repository = repository
        self.compute = compute or compute_new_events_left_fold
        self.decider = decider


class EventSourcingLockingAggregate(
    Generic[C, S, E, V],
    IEventSourcingLockingAggregate[C, E, V],
):
    def __init__(
        self,
        decider: IDecider[C, S, E],
        repository: EventLockingRepository[C, E, V],
        compute: EventComputation[E, C, S] | None = None,
    ) -> None:
        self.repository = repository
        self.decider = decider
        self.compute = compute or compute_new_events_left_fold

    async def __call__(self, command: C, _) -> list[Tuple[E, V]]:
        return await self.handle(command)

    async def handle(self, command: C) -> list[Tuple[E, V]]:
        # 1. Fetch events for this aggregateID
        current_events_v = await self.repository.fetch_events(command)
        print(f"GOT current_events_v {current_events_v}")
        current_events = [e[0] for e in current_events_v]
        # 2. Evolve and store the event (result)
        # 3. Use that state and the command to make decisions (new events, new facts)
        new_events = self.compute(current_events, command, self.decider)
        # 4. Store that event using apply
        latest_version = current_events_v[-1][1] if len(current_events_v) > 0 else None
        return await self.repository.save_all(new_events, latest_version)
