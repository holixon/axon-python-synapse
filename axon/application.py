import asyncio
from aiohttp import web
import nest_asyncio
from .message_handler import MessageHandler, CommandMessage, EventMessage, QueryMessage
from .client import AxonSynapseClient

nest_asyncio.apply()


class AxonSynapseApplication:
    def __init__(self, endpoint: str = None) -> None:
        self.endpoint = endpoint
        self.event_handler = MessageHandler(EventMessage)
        self.query_handler = MessageHandler(QueryMessage)
        self.command_handler = MessageHandler(CommandMessage)

    def run(self, mainfunc):
        asyncio.run(self._run(mainfunc))

    async def _run(self, mainfunc):
        async with AxonSynapseClient() as client:
            await mainfunc(client)

    def listen(self, port: int, register_handlers: bool = True):
        app = web.Application()
        app.add_routes(
            [
                web.post("/events", self.event_handler.handle),
                web.post("/queries", self.query_handler.handle),
                web.post("/commands", self.command_handler.handle),
            ]
        )
        if register_handlers:
            self.run(self._register_handlers)
        web.run_app(app, port=port)

    async def _register_handlers(self, client: AxonSynapseClient):
        endpoint = "http://localhost:8888"
        component = "Giftcard"
        await client.register_handler(
            endpoint, "events", self.event_handler.names(), component
        )
        await client.register_handler(
            endpoint, "queries", self.query_handler.names(), component
        )
        await client.register_handler(
            endpoint, "commands", self.command_handler.names(), component
        )
