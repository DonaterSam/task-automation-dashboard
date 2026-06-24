import platform
import subprocess

import psutil
from celery import shared_task
from django.utils import timezone

from dashboard.ws_utils import notify_task_update


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def ping_server(self, task_id: int) -> dict:
    from dashboard.models import AutomationTask

    task = AutomationTask.objects.get(pk=task_id)
    task.status = AutomationTask.Status.RUNNING
    task.save(update_fields=["status"])

    host = task.server.host
    param = "-n" if platform.system().lower() == "windows" else "-c"

    try:
        result = subprocess.run(
            ["ping", param, "3", host],
            capture_output=True,
            text=True,
            timeout=15,
        )
        success = result.returncode == 0
        output = {
            "reachable": success,
            "stdout": result.stdout[:500],
        }
        task.status = AutomationTask.Status.SUCCESS if success else AutomationTask.Status.FAILURE
        task.server.status = "online" if success else "offline"
    except subprocess.TimeoutExpired:
        output = {"reachable": False, "error": "Timeout"}
        task.status = AutomationTask.Status.FAILURE
        task.server.status = "offline"

    task.result = output
    task.finished_at = timezone.now()
    task.save(update_fields=["status", "result", "finished_at"])
    task.server.last_checked = timezone.now()
    task.server.save(update_fields=["status", "last_checked"])
    notify_task_update(task)

    return output


@shared_task(bind=True)
def check_disk_usage(self, task_id: int) -> dict:
    from dashboard.models import AutomationTask

    task = AutomationTask.objects.get(pk=task_id)
    task.status = AutomationTask.Status.RUNNING
    task.save(update_fields=["status"])

    try:
        usage = psutil.disk_usage("/")
        output = {
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "percent": usage.percent,
        }
        task.status = AutomationTask.Status.SUCCESS
    except Exception as e:
        output = {"error": str(e)}
        task.status = AutomationTask.Status.FAILURE

    task.result = output
    task.finished_at = timezone.now()
    task.save(update_fields=["status", "result", "finished_at"])
    notify_task_update(task)
    return output


@shared_task(bind=True)
def check_memory(self, task_id: int) -> dict:
    from dashboard.models import AutomationTask

    task = AutomationTask.objects.get(pk=task_id)
    task.status = AutomationTask.Status.RUNNING
    task.save(update_fields=["status"])

    try:
        mem = psutil.virtual_memory()
        output = {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent,
        }
        task.status = AutomationTask.Status.SUCCESS
    except Exception as e:
        output = {"error": str(e)}
        task.status = AutomationTask.Status.FAILURE

    task.result = output
    task.finished_at = timezone.now()
    task.save(update_fields=["status", "result", "finished_at"])
    notify_task_update(task)
    return output


@shared_task
def check_all_servers() -> dict:
    from dashboard.models import Server, AutomationTask

    servers = Server.objects.all()
    launched = 0

    for server in servers:
        task = AutomationTask.objects.create(
            name=f"Auto-ping {server.name}",
            task_type=AutomationTask.TaskType.PING,
            server=server,
        )
        celery_result = ping_server.delay(task.id)
        task.celery_task_id = celery_result.id
        task.save(update_fields=["celery_task_id"])
        launched += 1

    return {"launched": launched}


TASK_TYPE_MAP = {
    "ping": ping_server,
    "disk_usage": check_disk_usage,
    "memory_check": check_memory,
}
