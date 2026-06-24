from django.db import models


class Server(models.Model):
    class Status(models.TextChoices):
        ONLINE = "online", "Онлайн"
        OFFLINE = "offline", "Оффлайн"
        UNKNOWN = "unknown", "Неизвестно"

    name = models.CharField("Название", max_length=255)
    host = models.CharField("Хост / IP", max_length=255)
    port = models.PositiveIntegerField("Порт", default=22)
    status = models.CharField(
        "Статус",
        max_length=10,
        choices=Status.choices,
        default=Status.UNKNOWN,
    )
    last_checked = models.DateTimeField("Последняя проверка", null=True, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Сервер"
        verbose_name_plural = "Серверы"

    def __str__(self):
        return f"{self.name} ({self.host})"


class AutomationTask(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "В очереди"
        RUNNING = "running", "Выполняется"
        SUCCESS = "success", "Успешно"
        FAILURE = "failure", "Ошибка"

    class TaskType(models.TextChoices):
        PING = "ping", "Пинг сервера"
        DISK_USAGE = "disk_usage", "Проверка диска"
        MEMORY_CHECK = "memory_check", "Проверка памяти"
        CUSTOM_SCRIPT = "custom_script", "Пользовательский скрипт"

    name = models.CharField("Название", max_length=255)
    task_type = models.CharField(
        "Тип задачи",
        max_length=20,
        choices=TaskType.choices,
    )
    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Сервер",
    )
    status = models.CharField(
        "Статус",
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    result = models.JSONField("Результат", default=dict, blank=True)
    celery_task_id = models.CharField(
        "Celery Task ID", max_length=255, blank=True, default=""
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    finished_at = models.DateTimeField("Завершена", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return f"{self.name} [{self.get_status_display()}]"
