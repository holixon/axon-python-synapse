from pprint import pprint
from aiohttp import web
import aiohttp_jinja2
import jinja2
from giftcard.payloads import *
from adapter.payload_service import *
from synapse_client import AxonSynapseClient
from contextvars import ContextVar

CLIENT = ContextVar[AxonSynapseClient | None]("Client", default=None)


class GiftCardCommandGateway:
    async def dispatch(self, command: GiftCardCommand):
        payload_type = payload_type_from_object(command)
        client = CLIENT.get()
        if client is None:
            return ""
        return await client.dispatch_command(
            command_name=payload_type,
            payload_type=payload_type,
            payload=payload_from_object(command),
        )


class GiftCardQueryGateway:
    async def query(self, query: GiftCardQuery):
        payload_type = payload_type_from_object(query)
        client = CLIENT.get()
        if client is None:
            return []
        return await client.publish_query(
            query_name=payload_type,
            payload_type=payload_type,
            payload=payload_from_object(query),
        )


@aiohttp_jinja2.template("index.jinja2")
async def get_giftcards(request):
    gateway = request.app["QueryGateway"]
    giftcards = await gateway.query(FetchCardSummariesQuery(limit=100))
    pprint(giftcards)
    return {"giftcards": reversed(giftcards)}


async def create_giftcard(request):
    dispatch = request.app["CommandGateway"].dispatch
    data = await request.post()
    card_id = data["id"]
    amount = int(data["amount"])
    await dispatch(IssueCardCommand(id=card_id, amount=amount))
    raise web.HTTPFound("/")


async def redeem_giftcard(request):
    dispatch = request.app["CommandGateway"].dispatch
    data = await request.post()
    card_id = data["id"]
    amount = int(data["amount"])
    await dispatch(RedeemCardCommand(id=card_id, amount=amount))
    raise web.HTTPFound("/")


async def cancel_giftcard(request):
    dispatch = request.app["CommandGateway"].dispatch
    data = await request.post()
    card_id = data["id"]
    await dispatch(CancelCardCommand(id=card_id))
    raise web.HTTPFound("/")


async def on_startup(app):
    print("on_startup", CLIENT.get())
    app["CommandGateway"] = GiftCardCommandGateway()
    app["QueryGateway"] = GiftCardQueryGateway()
    CLIENT.set(AxonSynapseClient())


async def on_cleanup(app):
    print("on_cleanup", CLIENT.get())
    CLIENT.get().close()
    CLIENT.reset()


async def main():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("templates"))
    app.router.add_get("/", get_giftcards)
    app.router.add_post("/issue", create_giftcard)
    app.router.add_post("/redeem", redeem_giftcard)
    app.router.add_post("/cancel", cancel_giftcard)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


web.run_app(main(), port=3333)
