import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from dashboard.consumers import TaskStatusConsumer


@pytest.fixture
def channel_layer_settings(settings):
    settings.CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_consumer_connect(channel_layer_settings):
    communicator = WebsocketCommunicator(TaskStatusConsumer.as_asgi(), "/ws/tasks/")
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_consumer_receives_task_update(channel_layer_settings):
    communicator = WebsocketCommunicator(TaskStatusConsumer.as_asgi(), "/ws/tasks/")
    connected, _ = await communicator.connect()
    assert connected

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "task_updates",
        {
            "type": "task_update",
            "data": {
                "type": "task_status",
                "task": {
                    "id": 1,
                    "name": "Test",
                    "status": "success",
                },
            },
        },
    )

    response = await communicator.receive_json_from(timeout=3)
    assert response["type"] == "task_status"
    assert response["task"]["status"] == "success"

    await communicator.disconnect()
