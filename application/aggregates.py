from functools import reduce
from typing import Tuple, TypeVar
from abc import abstractmethod
from domain.decider import IDecider
from .repositories import EventRepository, EventLockingRepository

C = TypeVar("C")
S = TypeVar("S")
E = TypeVar("E")
V = TypeVar("V")


class IEventSourcingAggregate(IDecider[C, S, E], EventRepository[C, E]):
    @abstractmethod
    async def handle(self, command: C) -> list[E]:
        ...


class IEventSourcingLockingAggregate(
    IDecider[C, S, E], EventLockingRepository[C, E, V]
):
    @abstractmethod
    async def handle(self, command: C) -> list[Tuple[E, V]]:
        ...


# -----------------------------------------------------------------------------


class EventComputation(IDecider[C, S, E]):
    def compute_new_events(self, events: list[E], command: C) -> list[E]:
        state = reduce(self.evolve, events, self.initial_state)
        return self.decide(command, state)


class DeciderProxy(IDecider[C, S, E]):
    def __init__(self, decider: IDecider[C, S, E]) -> None:
        self.decider = decider

    def decide(self, c: C, s: S | None) -> list[E]:
        return self.decider.decide(c, s)

    def evolve(self, s: S | None, e: E) -> S:
        return self.decider.evolve(s, e)

    @property
    def initial_state(self) -> S | None:
        return self.decider.initial_state


class EventSourcingAggregate(
    IEventSourcingAggregate[C, S, E], EventComputation, DeciderProxy
):
    def __init__(
        self, decider: IDecider[C, S, E], repository: EventRepository[C, E]
    ) -> None:
        super(DeciderProxy, self).__init__(decider)
        self.repository = repository


class EventSourcingLockingAggregate(
    IEventSourcingLockingAggregate[C, S, E, V],
    EventComputation[C, S, E],
    DeciderProxy[C, S, E],
):
    def __init__(
        self, decider: IDecider[C, S, E], repository: EventLockingRepository[C, E, V]
    ) -> None:
        super().__init__(decider)
        self.repository = repository

    async def handle(self, command: C) -> list[Tuple[E, V]]:
        # 1. Fetch events for this aggregateID
        current_events_v = await self.repository.fetch_events(command)
        current_events = [e[0] for e in current_events_v]
        # 2. Evolve and store the event (result)
        # 3. Use that state and the command to make decisions (new events, new facts)
        new_events = self.compute_new_events(current_events, command)
        # 4. Store that event using apply
        latest_version = current_events_v[-1][1] if len(current_events_v) > 0 else None
        return await self.repository.save_all(new_events, latest_version)

    async def fetch_events(self, c: C) -> list[Tuple[E, V]]:
        return await self.repository.fetch_events(c)

    async def save(self, e: E, latest_version: V | None) -> Tuple[E, V]:
        return await self.repository.save(e, latest_version)

    async def save_all(
        self, events: list[E], latest_version: V | None
    ) -> list[Tuple[E, V]]:
        return await self.repository.save_all(events, latest_version)
