from django import forms

from .models import AutomationTask, Server


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ["name", "host", "port"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Мой сервер"}),
            "host": forms.TextInput(attrs={"class": "form-control", "placeholder": "192.168.1.1"}),
            "port": forms.NumberInput(attrs={"class": "form-control"}),
        }


class RunTaskForm(forms.Form):
    server = forms.ModelChoiceField(
        queryset=Server.objects.all(),
        label="Сервер",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    task_type = forms.ChoiceField(
        choices=AutomationTask.TaskType.choices,
        label="Тип задачи",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
