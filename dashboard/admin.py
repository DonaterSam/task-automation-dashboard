from django.contrib import admin

from .models import AutomationTask, Server


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "host", "port", "status", "last_checked")
    list_filter = ("status",)
    search_fields = ("name", "host")


@admin.register(AutomationTask)
class AutomationTaskAdmin(admin.ModelAdmin):
    list_display = ("name", "task_type", "server", "status", "created_at", "finished_at")
    list_filter = ("status", "task_type")
    search_fields = ("name",)
    readonly_fields = ("celery_task_id", "result")
