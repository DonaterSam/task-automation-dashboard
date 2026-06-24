from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("servers/", views.server_list, name="server_list"),
    path("servers/create/", views.server_create, name="server_create"),
    path("servers/<int:pk>/delete/", views.server_delete, name="server_delete"),
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/run/", views.run_task, name="run_task"),
    path("tasks/<int:pk>/detail/", views.task_detail, name="task_detail"),
]
