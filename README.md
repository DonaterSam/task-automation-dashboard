# Task Automation Dashboard

Веб-панель для мониторинга серверов и запуска задач автоматизации.

## Стек

- **Python 3.12** + **Django 5.1** — бэкенд и шаблоны
- **Celery 5.4** + **Redis 7** — асинхронные фоновые задачи
- **Pytest** — тестирование
- **Docker Compose** — оркестрация сервисов
- **Bootstrap 5** — UI

## Возможности

- CRUD серверов (добавление, удаление, список)
- Запуск задач автоматизации через Celery:
  - **Ping** — проверка доступности сервера
  - **Disk Usage** — проверка дискового пространства
  - **Memory Check** — проверка оперативной памяти
- Периодическая проверка всех серверов (Celery Beat, каждые 60 сек)
- Дашборд со статистикой и историей задач
- JSON API для деталей задач (AJAX-совместимо)

## Быстрый старт

```bash
# Через Docker Compose (рекомендуется)
docker compose up --build

# Открыть http://localhost:8000
```

### Локально (без Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Нужен запущенный Redis на localhost:6379
python manage.py migrate
python manage.py runserver &
celery -A config worker -l info &
celery -A config beat -l info &
```

## Тесты

```bash
pip install -r requirements.txt
pytest -v
```

## Структура проекта

```
├── config/              # Django-проект (settings, celery, urls)
├── dashboard/           # Основное приложение
│   ├── models.py        # Server, AutomationTask
│   ├── tasks.py         # Celery-задачи (ping, disk, memory)
│   ├── views.py         # Views (dashboard, CRUD, JSON API)
│   ├── forms.py         # Django Forms
│   ├── templates/       # HTML-шаблоны (Bootstrap 5)
│   └── templatetags/    # Кастомные теги шаблонов
├── tests/               # Pytest тесты
├── docker-compose.yml   # Docker-оркестрация
├── Dockerfile
└── requirements.txt
```
