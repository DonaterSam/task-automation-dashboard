import json

from channels.generic.websocket import AsyncWebsocketConsumer


class TaskStatusConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = "task_updates"

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            if data.get("type") == "request_status":
                from dashboard.models import AutomationTask
                from channels.db import database_sync_to_async

                task_id = data.get("task_id")
                if task_id:
                    task = await database_sync_to_async(
                        lambda: AutomationTask.objects.filter(pk=task_id).values(
                            "id", "name", "status", "result"
                        ).first()
                    )()
                    if task:
                        await self.send(text_data=json.dumps({
                            "type": "task_status",
                            "task": task,
                        }))

    async def task_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
