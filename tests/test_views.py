import pytest
from django.test import Client
from django.urls import reverse

from dashboard.models import AutomationTask, Server


@pytest.fixture
def client():
    return Client()


class TestIndexView:
    def test_index_returns_200(self, client, db):
        response = client.get(reverse("index"))
        assert response.status_code == 200

    def test_index_shows_stats(self, client, server):
        response = client.get(reverse("index"))
        assert b"\xd0\xa1\xd0\xb5\xd1\x80\xd0\xb2\xd0\xb5\xd1\x80\xd0\xbe\xd0\xb2" in response.content  # "Серверов"


class TestServerViews:
    def test_server_list(self, client, server):
        response = client.get(reverse("server_list"))
        assert response.status_code == 200
        assert server.name.encode() in response.content

    def test_server_create(self, client, db):
        response = client.post(reverse("server_create"), {
            "name": "New Server",
            "host": "192.168.1.100",
            "port": 8080,
        })
        assert response.status_code == 302
        assert Server.objects.filter(name="New Server").exists()

    def test_server_delete(self, client, server):
        response = client.post(reverse("server_delete", args=[server.pk]))
        assert response.status_code == 302
        assert not Server.objects.filter(pk=server.pk).exists()


class TestTaskViews:
    def test_task_list(self, client, automation_task):
        response = client.get(reverse("task_list"))
        assert response.status_code == 200

    def test_task_detail_json(self, client, automation_task):
        response = client.get(reverse("task_detail", args=[automation_task.pk]))
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Ping"
        assert data["status"] == "pending"

    def test_task_detail_404(self, client, db):
        response = client.get(reverse("task_detail", args=[9999]))
        assert response.status_code == 404
