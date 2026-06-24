import pytest
from dashboard.models import AutomationTask, Server


@pytest.fixture
def server(db):
    return Server.objects.create(
        name="Test Server",
        host="127.0.0.1",
        port=22,
    )


@pytest.fixture
def automation_task(db, server):
    return AutomationTask.objects.create(
        name="Test Ping",
        task_type=AutomationTask.TaskType.PING,
        server=server,
    )
