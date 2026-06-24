import pytest
from unittest.mock import patch, MagicMock

from dashboard.models import AutomationTask, Server
from dashboard.tasks import ping_server, check_disk_usage, check_memory, TASK_TYPE_MAP


class TestTaskTypeMap:
    def test_all_types_mapped(self):
        assert "ping" in TASK_TYPE_MAP
        assert "disk_usage" in TASK_TYPE_MAP
        assert "memory_check" in TASK_TYPE_MAP


class TestPingServer:
    @patch("dashboard.tasks.subprocess.run")
    def test_ping_success(self, mock_run, automation_task):
        mock_run.return_value = MagicMock(returncode=0, stdout="3 packets transmitted")
        result = ping_server(automation_task.id)

        assert result["reachable"] is True
        automation_task.refresh_from_db()
        assert automation_task.status == AutomationTask.Status.SUCCESS
        assert automation_task.server.status == "online"

    @patch("dashboard.tasks.subprocess.run")
    def test_ping_failure(self, mock_run, automation_task):
        mock_run.return_value = MagicMock(returncode=1, stdout="100% packet loss")
        result = ping_server(automation_task.id)

        assert result["reachable"] is False
        automation_task.refresh_from_db()
        assert automation_task.status == AutomationTask.Status.FAILURE

    @patch("dashboard.tasks.subprocess.run", side_effect=__import__("subprocess").TimeoutExpired("ping", 15))
    def test_ping_timeout(self, mock_run, automation_task):
        result = ping_server(automation_task.id)

        assert result["reachable"] is False
        assert "Timeout" in result["error"]


class TestDiskUsage:
    @patch("dashboard.tasks.psutil.disk_usage")
    def test_disk_usage_success(self, mock_disk, automation_task):
        automation_task.task_type = "disk_usage"
        automation_task.save()

        mock_disk.return_value = MagicMock(
            total=100 * 1024**3,
            used=60 * 1024**3,
            free=40 * 1024**3,
            percent=60.0,
        )
        result = check_disk_usage(automation_task.id)

        assert result["total_gb"] == 100.0
        assert result["percent"] == 60.0
        automation_task.refresh_from_db()
        assert automation_task.status == AutomationTask.Status.SUCCESS


class TestCheckMemory:
    @patch("dashboard.tasks.psutil.virtual_memory")
    def test_memory_check_success(self, mock_mem, automation_task):
        automation_task.task_type = "memory_check"
        automation_task.save()

        mock_mem.return_value = MagicMock(
            total=16 * 1024**3,
            available=8 * 1024**3,
            used=8 * 1024**3,
            percent=50.0,
        )
        result = check_memory(automation_task.id)

        assert result["total_gb"] == 16.0
        assert result["percent"] == 50.0
        automation_task.refresh_from_db()
        assert automation_task.status == AutomationTask.Status.SUCCESS
