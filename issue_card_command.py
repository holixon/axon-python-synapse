import axon
from commands import IssueCardCommand

app = axon.AxonSynapseApplication()


async def main(client: axon.AxonSynapseClient):
    command = IssueCardCommand("DemoCard-001", 75)
    await client.dispatch(command)


app.run(main)
