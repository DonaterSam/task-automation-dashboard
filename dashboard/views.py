from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RunTaskForm, ServerForm
from .models import AutomationTask, Server
from .tasks import TASK_TYPE_MAP


def index(request):
    servers = Server.objects.all()
    recent_tasks = AutomationTask.objects.select_related("server")[:20]
    stats = {
        "servers_total": servers.count(),
        "servers_online": servers.filter(status="online").count(),
        "tasks_total": AutomationTask.objects.count(),
        "tasks_running": AutomationTask.objects.filter(status="running").count(),
    }
    return render(request, "dashboard/index.html", {
        "servers": servers,
        "recent_tasks": recent_tasks,
        "stats": stats,
        "run_form": RunTaskForm(),
    })


def server_list(request):
    servers = Server.objects.all()
    form = ServerForm()
    return render(request, "dashboard/servers.html", {
        "servers": servers,
        "form": form,
    })


@require_POST
def server_create(request):
    form = ServerForm(request.POST)
    if form.is_valid():
        form.save()
    return redirect("server_list")


def server_delete(request, pk):
    server = get_object_or_404(Server, pk=pk)
    if request.method == "POST":
        server.delete()
    return redirect("server_list")


@require_POST
def run_task(request):
    form = RunTaskForm(request.POST)
    if not form.is_valid():
        return redirect("index")

    server = form.cleaned_data["server"]
    task_type = form.cleaned_data["task_type"]

    task = AutomationTask.objects.create(
        name=f"{dict(AutomationTask.TaskType.choices)[task_type]} — {server.name}",
        task_type=task_type,
        server=server,
    )

    celery_func = TASK_TYPE_MAP.get(task_type)
    if celery_func:
        result = celery_func.delay(task.id)
        task.celery_task_id = result.id
        task.save(update_fields=["celery_task_id"])

    return redirect("index")


def task_detail(request, pk):
    task = get_object_or_404(AutomationTask, pk=pk)
    return JsonResponse({
        "id": task.id,
        "name": task.name,
        "status": task.status,
        "result": task.result,
        "created_at": task.created_at.isoformat(),
        "finished_at": task.finished_at.isoformat() if task.finished_at else None,
    })


def task_list(request):
    tasks = AutomationTask.objects.select_related("server").all()[:100]
    return render(request, "dashboard/tasks.html", {"tasks": tasks})
