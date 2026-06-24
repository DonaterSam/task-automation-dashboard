from django import template

register = template.Library()

STATUS_BADGES = {
    "online": "success",
    "offline": "danger",
    "unknown": "secondary",
    "pending": "warning",
    "running": "info",
    "success": "success",
    "failure": "danger",
}


@register.filter
def status_badge(value: str) -> str:
    return STATUS_BADGES.get(value, "secondary")
