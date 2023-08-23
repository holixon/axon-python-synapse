from typing import Protocol, Generic, TypeVar, Any
from abc import ABC, abstractmethod, abstractproperty

S = TypeVar("S")
E = TypeVar("E")


class IView(ABC, Generic[S, E]):
    @abstractmethod
    def evolve(self, s: S | None, e: E) -> S:
        ...

    @abstractproperty
    def initial_state(self) -> S | None:
        ...
