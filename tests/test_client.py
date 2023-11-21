import pytest
from axon.synapse.client import AxonSynapseClient
from axon.synapse.responses import *


@pytest.fixture
async def axon_client():
    async with AxonSynapseClient(api_url="http://localhost:8080/v1") as client:
        yield client


@pytest.mark.vcr
async def test_register_command_handler(axon_client):
    response = await axon_client.register_command_handler(
        handler_id="123456",
        client_id="pytest-command-handler",
        component_name="Test",
        names=["axon.test.command"],
        callback_endpoint="http://myhost:888/command",
    )

    assert response.id == "123456"
    assert response.names == ["axon.test.command"]
    assert response.endpoint == "http://myhost:888/command"
    assert response.endpointType == "http-raw"
    assert response.endpointOptions == []
    assert response.enabled == True
    assert response.context == "default"
    assert response.clientId == "pytest-command-handler"
    assert response.componentName == "Test"


@pytest.mark.vcr
async def test_register_event_handler(axon_client):
    response = await axon_client.register_event_handler(
        handler_id="123456",
        client_id="pytest-command-handler",
        component_name="Test",
        names=["axon.test.event"],
        callback_endpoint="http://myhost:888/command",
        # batch_size=1,
    )

    assert response.id == "123456"
    assert response.batchSize == 1
    assert response.names == ["axon.test.event"]
    assert response.endpoint == "http://myhost:888/command"
    assert response.endpointType == "http-raw"
    assert response.endpointOptions == []
    assert response.enabled == True
    assert response.context == "default"
    assert response.clientId == "pytest-command-handler"
    assert response.componentName == "Test"


@pytest.mark.vcr
async def test_register_query_handler(axon_client):
    response = await axon_client.register_query_handler(
        handler_id="123456",
        client_id="pytest-command-handler",
        component_name="Test",
        names=["axon.test.event"],
        callback_endpoint="http://myhost:888/command",
        # batch_size=1,
    )

    assert response.id == "123456"
    assert response.names == ["axon.test.event"]
    assert response.endpoint == "http://myhost:888/command"
    assert response.endpointType == "http-raw"
    assert response.endpointOptions == []
    assert response.enabled == True
    assert response.context == "default"
    assert response.clientId == "pytest-command-handler"
    assert response.componentName == "Test"
