import axon
from queries import FetchCardSummariesQuery, CardSummary


app = axon.AxonSynapseApplication()


async def main(client: axon.AxonSynapseClient):
    query = FetchCardSummariesQuery(0, 10)
    result = await client.query(query, CardSummary)
    return result


app.run(main)
