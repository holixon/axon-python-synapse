from abc import abstractmethod
from axon.domain.view import IView, S, E
from .repositories import ViewStateRepository


class IMaterializedView(IView[S, E]):
    @abstractmethod
    async def handle(self, event: E) -> S:
        ...


# -----------------------------------------------------------------------------


class MaterializedView(IMaterializedView[S, E]):
    def __init__(
        self, view: IView[S, E], repository: ViewStateRepository[E, S]
    ) -> None:
        self.view = view
        self.repository = repository

    @property
    def initial_state(self) -> S | None:
        return self.view.initial_state

    def evolve(self, s: S | None, e: E) -> S:
        return self.view.evolve(s, e)

    async def __call__(self, event: E, _) -> S:
        return await self.handle(event)

    async def handle(self, event: E) -> S:
        current_state = await self.repository.fetch_state(event)
        new_state = self.view.evolve(current_state or self.view.initial_state, event)
        return await self.repository.save(new_state)
