# Подготовка к собеседованию: Junior Python-разработчик

Позиция: ФГАНУ НИИ Спецвузавтоматика, Ростов-на-Дону
Дата: 26 июня 2026

---

## 1. Python — основы, которые спрашивают всегда

### Mutable vs Immutable

Mutable (изменяемые): `list`, `dict`, `set`, `bytearray`
Immutable (неизменяемые): `int`, `float`, `str`, `tuple`, `frozenset`, `bytes`

Почему это важно:
- Immutable объекты можно использовать как ключи `dict` и элементы `set` (они hashable)
- При передаче mutable объекта в функцию — он может измениться снаружи

```python
def bad(items=[]):      # Ловушка! Один и тот же list на все вызовы
    items.append(1)
    return items

bad()  # [1]
bad()  # [1, 1] — сюрприз

def good(items=None):   # Правильно
    if items is None:
        items = []
    items.append(1)
    return items
```

### GIL (Global Interpreter Lock)

GIL — это мьютекс в CPython, который позволяет только одному потоку выполнять Python-байткод в один момент времени.

- `threading` — потоки работают параллельно для I/O (сеть, диск), но НЕ для CPU
- `multiprocessing` — отдельные процессы, каждый со своим GIL, реальный параллелизм для CPU
- `asyncio` — один поток, но кооперативная многозадачность для I/O

Когда что использовать:
- Скачать 100 страниц -> `asyncio` или `threading`
- Обработать 100 изображений -> `multiprocessing`
- Подождать ответ от БД -> `asyncio`

### Генераторы и итераторы

Итератор — объект с методами `__iter__()` и `__next__()`.
Генератор — функция с `yield`, которая возвращает итератор.

```python
# Генератор — ленивый, не хранит всё в памяти
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

# Генераторное выражение
squares = (x**2 for x in range(1_000_000))  # 0 памяти
squares_list = [x**2 for x in range(1_000_000)]  # ~8MB памяти
```

Зачем: обработка больших файлов, стримы данных, пайплайны.

### Декораторы

Декоратор — функция, которая принимает функцию и возвращает функцию.

```python
import functools
import time

def timer(func):
    @functools.wraps(func)  # сохраняет __name__, __doc__ оригинала
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```

`@functools.wraps` — всегда используй, иначе теряется имя и docstring декорированной функции.

### Контекстные менеджеры

```python
# Через класс
class DBConnection:
    def __enter__(self):
        self.conn = connect()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        return False  # не подавляем исключения

# Через contextlib
from contextlib import contextmanager

@contextmanager
def db_connection():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
```

Гарантируют освобождение ресурсов (файлы, соединения, локи) даже при исключениях.

### *args, **kwargs

```python
def func(*args, **kwargs):
    # args — tuple позиционных аргументов
    # kwargs — dict именованных аргументов
    pass

func(1, 2, name="test")
# args = (1, 2), kwargs = {"name": "test"}
```

Читать:
- https://docs.python.org/3/tutorial/
- https://realpython.com/python-interview-problems/
- https://realpython.com/python-gil/
- https://realpython.com/introduction-to-python-generators/

---

## 2. Django

### ORM и QuerySet

QuerySet — ленивый. Запрос к БД выполняется только когда данные реально нужны (итерация, `list()`, `len()`, слайс, `bool()`).

```python
# Плохо — N+1 запросов
tasks = AutomationTask.objects.all()
for task in tasks:
    print(task.server.name)  # Каждый раз отдельный SELECT к Server

# Хорошо — 1 JOIN запрос
tasks = AutomationTask.objects.select_related("server").all()
for task in tasks:
    print(task.server.name)  # Данные уже загружены
```

`select_related` — для ForeignKey/OneToOne (SQL JOIN)
`prefetch_related` — для ManyToMany/reverse FK (отдельный запрос + склейка в Python)

### Middleware

Middleware — цепочка обработчиков, через которую проходит каждый запрос и ответ.

```
Request -> SecurityMiddleware -> SessionMiddleware -> ... -> View
Response <- SecurityMiddleware <- SessionMiddleware <- ... <- View
```

Порядок в `MIDDLEWARE` имеет значение. `SecurityMiddleware` первым обрабатывает запрос и последним — ответ.

```python
class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Код ДО view
        response = self.get_response(request)
        # Код ПОСЛЕ view
        return response
```

### Миграции

`makemigrations` — создаёт файлы миграций на основе изменений в models.py
`migrate` — применяет миграции к БД

Миграция — это Python-файл с операциями (`CreateModel`, `AddField`, `AlterField` и т.д.).
Каждая миграция знает свои зависимости через `dependencies`.

Конфликт миграций — когда два разработчика создали миграцию с одним номером.
Решение: `python manage.py makemigrations --merge`

### CSRF (Cross-Site Request Forgery)

Атака: злоумышленник заставляет браузер пользователя отправить POST-запрос на твой сайт.
Защита: скрытый токен в каждой форме, который проверяется на сервере.

```html
<form method="post">
    {% csrf_token %}  <!-- генерирует <input type="hidden" name="csrfmiddlewaretoken" ...> -->
    ...
</form>
```

Без токена — Django вернёт 403 Forbidden.

Читать:
- https://docs.djangoproject.com/en/5.1/topics/
- https://docs.djangoproject.com/en/5.1/topics/db/queries/
- https://docs.djangoproject.com/en/5.1/topics/http/middleware/

---

## 3. Celery + Redis

### Архитектура Celery

```
Producer (Django view) --> Broker (Redis) --> Worker (Celery process)
                                                  |
                                                  v
                                          Result Backend (Django DB)
```

**Broker** — очередь сообщений. Worker забирает задачи из очереди.
**Result Backend** — хранилище результатов выполненных задач.

Redis выбирают как broker потому что он быстрый (in-memory), простой, поддерживает pub/sub.

### shared_task vs app.task

```python
# app.task — привязан к конкретному экземпляру Celery app
@app.task
def my_task():
    pass

# shared_task — не привязан, работает с любым app
# Используется в reusable Django apps
@shared_task
def my_task():
    pass
```

В Django-проектах используй `@shared_task` — он подхватывает app автоматически.

### Retry

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def unreliable_task(self, url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise self.retry(exc=exc)  # повторит через 60 сек, до 3 раз
```

`bind=True` — даёт доступ к `self` (инстанс Task), нужен для `self.retry()`.

### Celery Beat

Планировщик периодических задач. Работает как отдельный процесс.

```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    "check-servers-every-60s": {
        "task": "dashboard.tasks.check_all_servers",
        "schedule": 60.0,  # каждые 60 секунд
    },
}
```

Запуск: `celery -A config beat -l info`

### Redis — структуры данных

| Тип | Описание | Пример |
|-----|----------|--------|
| String | Простое значение | `SET key "value"` |
| List | Упорядоченный список | Очередь задач |
| Hash | Словарь | Объект пользователя |
| Set | Множество уникальных значений | Теги, онлайн-пользователи |
| Sorted Set | Множество с весами | Рейтинги, лидерборды |

TTL (Time To Live) — автоудаление ключа через N секунд. `EXPIRE key 300` — удалить через 5 минут.

Читать:
- https://docs.celeryq.dev/en/stable/getting-started/introduction.html
- https://docs.celeryq.dev/en/stable/userguide/tasks.html
- https://redis.io/docs/latest/develop/data-types/

---

## 4. Pytest

### Fixtures

Фикстуры — подготовка данных для тестов. Определяются в `conftest.py` (видны всем тестам в директории).

```python
@pytest.fixture
def server(db):  # db — встроенная фикстура pytest-django, даёт доступ к БД
    return Server.objects.create(name="Test", host="127.0.0.1")

def test_server_name(server):
    assert server.name == "Test"
```

Scopes: `function` (по умолчанию), `class`, `module`, `session` — определяют время жизни фикстуры.

### Parametrize

```python
@pytest.mark.parametrize("input,expected", [
    (1, True),
    (2, True),
    (4, False),
    (0, False),
])
def test_is_prime(input, expected):
    assert is_prime(input) == expected
# Запустит 4 отдельных теста
```

### Mocking

```python
from unittest.mock import patch, MagicMock

@patch("dashboard.tasks.subprocess.run")
def test_ping_success(mock_run, automation_task):
    mock_run.return_value = MagicMock(returncode=0, stdout="OK")
    result = ping_server(automation_task.id)
    assert result["reachable"] is True
```

`patch` подменяет объект на mock на время теста.
`MagicMock` — автоматически создаёт атрибуты и методы на лету.

Читать:
- https://docs.pytest.org/en/stable/
- https://pytest-django.readthedocs.io/en/latest/
- https://realpython.com/pytest-python-testing/

---

## 5. Docker

### Dockerfile

```dockerfile
FROM python:3.12-slim          # Базовый образ
WORKDIR /app                   # Рабочая директория
COPY requirements.txt .        # Копируем зависимости отдельно (кэш слоёв!)
RUN pip install -r requirements.txt
COPY . .                       # Копируем весь проект
EXPOSE 8000                    # Документация порта
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
```

Каждая инструкция = слой. Docker кэширует слои. Поэтому `COPY requirements.txt` отдельно — если код изменился, но зависимости нет, pip install берётся из кэша.

### Docker Compose

Оркестрация нескольких контейнеров. Контейнеры в одной сети общаются по имени сервиса.

```yaml
services:
  web:
    depends_on:
      redis:
        condition: service_healthy  # Ждать пока Redis запустится
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0  # "redis" — имя сервиса
```

`volumes: - .:/app` — bind mount, файлы на хосте синхронизируются с контейнером (для разработки).
Named volumes (`postgres_data:`) — для персистентных данных.

### Multi-stage build (бонус, для продвинутости)

```dockerfile
FROM python:3.12 AS builder
RUN pip wheel --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /wheels /wheels
RUN pip install /wheels/*
```

Уменьшает размер финального образа — билд-зависимости не попадают в прод.

Читать:
- https://docs.docker.com/get-started/
- https://docs.docker.com/compose/
- https://docs.docker.com/build/building/multi-stage/

---

## 6. Linux

### Права доступа

```
-rwxr-xr-- 1 user group file.txt
 |||  |  |
 |||  |  +-- others: read only
 |||  +----- group: read + execute
 |||-------- owner: read + write + execute
```

`chmod 755 file` — owner=rwx, group=r-x, others=r-x
`chmod +x script.sh` — добавить execute всем
`chown user:group file` — сменить владельца

### Процессы

```bash
ps aux                  # Все процессы
ps aux | grep python    # Фильтр по имени
top / htop              # Мониторинг в реальном времени
kill PID                # Отправить SIGTERM (мягкое завершение)
kill -9 PID             # SIGKILL (принудительное)
systemctl status nginx  # Статус systemd-сервиса
systemctl restart nginx # Перезапуск
```

### Сеть

```bash
ss -tlnp                # Какие порты слушают (замена netstat)
curl -v https://api.com # HTTP запрос с деталями
ping 8.8.8.8            # Проверка доступности
ip addr                 # IP адреса интерфейсов
```

### SSH

```bash
ssh-keygen -t ed25519                    # Генерация ключа
ssh-copy-id user@server                  # Копирование на сервер
ssh user@server                          # Подключение
scp file.txt user@server:/path/          # Копирование файла
```

Ключи хранятся в `~/.ssh/` — `id_ed25519` (приватный) и `id_ed25519.pub` (публичный).

Читать:
- https://linuxjourney.com/
- https://www.digitalocean.com/community/tutorials/an-introduction-to-linux-basics

---

## 7. Django Channels / WebSocket (бонус)

### Как работает WebSocket

HTTP: клиент отправляет запрос -> сервер отвечает -> соединение закрывается.
WebSocket: клиент и сервер держат постоянное соединение, оба могут слать данные в любой момент.

```
Browser <---WebSocket---> Daphne (ASGI server)
                              |
                        Channel Layer (Redis)
                              |
                        Celery Worker (отправляет обновления)
```

### WSGI vs ASGI

WSGI — синхронный протокол, один запрос = один поток. Не поддерживает WebSocket.
ASGI — асинхронный, поддерживает HTTP + WebSocket + фоновые задачи.

Daphne — ASGI-сервер (замена Gunicorn для WebSocket).

### Consumer

```python
class TaskStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("task_updates", self.channel_name)
        await self.accept()

    async def task_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
```

`channel_layer.group_add` — подписывает клиента на группу.
`group_send` — отправляет сообщение всем в группе.

Читать:
- https://channels.readthedocs.io/en/stable/
- https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

---

## 8. Вопросы про твой проект

Когда спросят "расскажите о проекте", структурируй ответ так:

**Что:** Task Automation Dashboard — веб-панель мониторинга серверов и запуска задач автоматизации.

**Зачем:** Автоматизация рутинных задач сисадмина — пинг серверов, проверка диска/памяти, с real-time обновлениями через WebSocket.

**Стек:** Django 5.1 + Celery + Redis + Django Channels + Docker Compose + Pytest.

**Архитектура:**
- Django — бэкенд, ORM, шаблоны
- Celery Workers — выполняют тяжёлые задачи (пинг, проверки) асинхронно, не блокируя веб-сервер
- Celery Beat — планировщик, каждые 60 секунд автоматически пингует все серверы
- Redis — и broker для Celery, и channel layer для WebSocket
- Daphne (ASGI) — обслуживает и HTTP, и WebSocket
- Docker Compose — поднимает всё одной командой: web, worker, beat, redis

**Тесты:** 23 теста на Pytest — модели, views, Celery-задачи (с моками subprocess и psutil), WebSocket consumer.

**Что бы улучшил:**
- Авторизация и разграничение доступа
- CI/CD пайплайн в GitLab
- PostgreSQL вместо SQLite для прода
- Grafana/Prometheus для метрик
- SSH-выполнение команд на удалённых серверах (paramiko)

---

## 9. Общие советы

- Если не знаешь ответ — скажи честно, но покажи ход мысли
- Если спрашивают "что использовали" — ссылайся на конкретные места в проекте
- `docker compose up --build` и покажи работающий дашборд — это сильнее любых слов
- Задавай вопросы в конце: "Какой стек используете?", "Как устроен CI/CD?", "Какие задачи на испытательном сроке?"
