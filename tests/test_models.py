import pytest
from dashboard.models import AutomationTask, Server


class TestServerModel:
    def test_create_server(self, server):
        assert server.pk is not None
        assert server.status == Server.Status.UNKNOWN
        assert str(server) == "Test Server (127.0.0.1)"

    def test_server_default_port(self, db):
        s = Server.objects.create(name="No port", host="10.0.0.1")
        assert s.port == 22

    def test_server_ordering(self, db):
        Server.objects.create(name="Bravo", host="10.0.0.2")
        Server.objects.create(name="Alpha", host="10.0.0.1")
        names = list(Server.objects.values_list("name", flat=True))
        assert names == ["Alpha", "Bravo"]


class TestAutomationTaskModel:
    def test_create_task(self, automation_task):
        assert automation_task.pk is not None
        assert automation_task.status == AutomationTask.Status.PENDING
        assert automation_task.result == {}

    def test_task_str(self, automation_task):
        assert "В очереди" in str(automation_task)

    def test_task_server_relation(self, automation_task, server):
        assert automation_task.server == server
        assert server.tasks.count() == 1

    def test_task_ordering(self, db, server):
        t1 = AutomationTask.objects.create(
            name="First", task_type="ping", server=server
        )
        t2 = AutomationTask.objects.create(
            name="Second", task_type="ping", server=server
        )
        tasks = list(AutomationTask.objects.values_list("name", flat=True))
        assert tasks == ["Second", "First"]
