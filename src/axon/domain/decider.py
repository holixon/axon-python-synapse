from typing import Protocol, Generic, TypeVar, Any
from abc import ABC, abstractmethod, abstractproperty

C = TypeVar("C")
S = TypeVar("S")
E = TypeVar("E")


class IDecider(ABC, Generic[C, S, E]):
    @abstractmethod
    def decide(self, c: C, s: S | None) -> list[E]:
        ...

    @abstractmethod
    def evolve(self, s: S | None, e: E) -> S:
        ...

    @abstractproperty
    def initial_state(self) -> S | None:
        ...
