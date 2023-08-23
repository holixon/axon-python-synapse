from typing import Tuple, Generic, TypeVar
from abc import ABC, abstractmethod
from domain.decider import C, S, E

# C = TypeVar("C")
# S = TypeVar("S")
# E = TypeVar("E")
V = TypeVar("V")


class EventRepository(ABC, Generic[C, E]):
    @abstractmethod
    async def fetch_events(self, command: C) -> list[E]:
        ...

    @abstractmethod
    async def save(self, event: E) -> E:
        ...

    @abstractmethod
    async def save_all(self, events: list[E]) -> list[E]:
        ...


class EventLockingRepository(ABC, Generic[C, E, V]):
    @abstractmethod
    async def fetch_events(self, c: C) -> list[Tuple[E, V]]:
        ...

    @abstractmethod
    async def save(self, e: E, latest_version: V | None) -> Tuple[E, V]:
        ...

    @abstractmethod
    async def save_all(
        self, events: list[E], latest_version: V | None
    ) -> list[Tuple[E, V]]:
        ...


class ViewStateRepository(ABC, Generic[E, S]):
    @abstractmethod
    async def fetch_state(self, e: E) -> S | None:
        ...

    @abstractmethod
    async def save(self, s: S) -> S:
        ...
