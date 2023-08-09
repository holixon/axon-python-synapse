import axon
from commands import IssueCardCommand


app = axon.AxonSynapseApplication()


@app.command_handler(IssueCardCommand)
async def card_issued_event(command: IssueCardCommand, message: axon.CommandMessage):
    print(command)


app.listen(port=8888)
