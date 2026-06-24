from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def notify_task_update(task):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        "task_updates",
        {
            "type": "task_update",
            "data": {
                "type": "task_status",
                "task": {
                    "id": task.id,
                    "name": task.name,
                    "status": task.status,
                    "status_display": task.get_status_display(),
                    "result": task.result,
                    "server_name": task.server.name,
                    "server_status": task.server.status,
                    "finished_at": task.finished_at.isoformat() if task.finished_at else None,
                },
            },
        },
    )
