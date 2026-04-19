# TestTask-AtlasIT

## Описание
Django-приложение для генерации XLSX-отчетов по заказам. В проекте реализовано два подхода к обработке данных:

1.  **Синхронный** - обычная блокирующая обработка в рамках HTTP-запроса.
2.  **Асинхронный** - неблокирующая обработка в фоновом режиме с использованием **Celery** и **Redis**.

## Схема работы (Workflow)
Асинхронный процесс генерации отчета включает следующие шаги:

1.  **Инициация**: Клиент отправляет `POST` запрос на эндпоинт генерации отчета. Сервер ставит задачу в очередь и возвращает `task_id`.
2.  **Опрос (Polling)**: Клиент периодически опрашивает эндпоинт `status`, передавая полученный `task_id`, до тех пор, пока не получит статус `SUCCESS`.
3.  **Загрузка**: Как только отчет готов, клиент выполняет переход по предоставленной ссылке `download` для скачивания готового файла.


## Модели данных

**Customer** — клиент:
| Поле  | Тип          | Описание          |
|-------|--------------|-------------------|
| id    | int (PK)     | Первичный ключ    |
| name  | varchar(255) | Имя клиента       |
| email | varchar      | Email (уникальный)|

**Order** — заказ:
| Поле       | Тип           | Описание                              |
|------------|---------------|---------------------------------------|
| id         | int (PK)      | Первичный ключ                        |
| customer   | FK → Customer | Клиент                                |
| amount     | decimal(10,2) | Сумма заказа                          |
| status     | varchar       | `paid` / `pending` / `canceled`       |
| created_at | datetime      | Дата и время создания                 |

> Составной индекс на `(status, created_at)` для ускорения фильтрации в отчётах.


## Sync API Endpoints

### 1. GET `/reports/revenue/`
Отчет по выручке - группировка по дате. Учитываются только заказы со статусом `paid`.

**Ответ:** файл `revenue_report.xlsx`

### 2. GET `/reports/customers/`
Отчет по клиентам - агрегация по каждому клиенту. Включает всех клиентов, в том числе без заказов.

**Ответ:** файл `customers_report.xlsx`

## Async API Endpoints

### 1. POST `/reports/revenue/async/`
Запуск генерации отчета по выручке.

**Ответ:** JSON с идентификатором задачи { "task_id": "c1a2b3c4-..." }

### 2. POST `/reports/customers/async/`
Запуск генерации отчета по клиентам.

**Ответ:** JSON с идентификатором задачи { "task_id": "c1a2b3c4-..." }

### 3. GET `/reports/status/<task_id>/`
Проверка статуса готовности (по task_id)

Параметры: task_id (string)
Статусы в ответе: PENDING, STARTED, SUCCESS, FAILURE

**Ответ:** 
{
  "task_id": "c1a2b3c4-...",
  "status": "SUCCESS",
  "result": "/tmp/reports/revenue_2024.xlsx"
}

### 4. GET `/reports/download/<task_id>/`
Скачивание готового XLSX файла.

**Ответ:** Файл `customers_8acf37c0-d961-4ebc-944e-c531fac85557.xlsx`


## Переменные окружения

Все переменные задаются в файле `.env` (пример в `.env.example`):

| Переменная    | Описание                              | Пример                     |
|---------------|---------------------------------------|----------------------------|
| `SECRET_KEY`  | Секретный ключ Django                 | `django-insecure-abc123`   |
| `DEBUG`       | Режим отладки (`True` / `False`)      | `False`                    |
| `ALLOWED_HOSTS` | Разрешённые хосты через запятую     | `localhost,127.0.0.1`      |
| `DB_ENGINE`   | Бэкенд БД                             | `django.db.backends.postgresql` |
| `DB_NAME`     | Имя базы данных                       | `atlas_db`                 |
| `DB_USER`     | Пользователь БД                       | `postgres`                 |
| `DB_PASSWORD` | Пароль БД                             | `secret`                   |
| `DB_HOST`     | Хост БД (имя сервиса в Docker)        | `postgres-db`              |
| `DB_PORT`     | Порт БД                               | `5432`                     |


## Требования

- Docker >= 24.x и Docker Compose >= 2.x (для запуска через Docker)
- Python 3.12+ и PostgreSQL 16 (для локального запуска)


## Запуск проекта

### Через Docker

**1. Создайте файл `.env` в корне проекта и заполните его данными:**

```bash
cp .env.example .env
```

**2. Соберите и запустите контейнеры:**

```bash
docker-compose up --build -d
```

**3. Примените миграции:**

```bash
docker-compose exec django-backend python manage.py migrate
```

**4. Сгенерируйте тестовые данные (~3000 клиентов, ~30000 заказов):**

```bash
docker-compose exec django-backend python manage.py generate_data
```
При повторной генерации, таблицы очищаются и данные генерируются снова

Приложение будет доступно по адресу: `http://localhost:8000`

## Бонусные требования
- [+] Docker (docker-compose)
- [+] Оптимизация для больших данных (iterator, batch processing)
- [+] Celery + Redis для фоновых задач

## Технологии
- Python 3.12 / Django 6
- openpyxl для XLSX
- Faker для тестовых данных
- PostgreSQL 16
- Docker / Docker Compose

## Структура проекта
```
project/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── config/
│   ├── settings.py
│   ├── urls.py
    ├── celery.py
│   └── ...
└── reports/
    ├── models.py     
    ├── views.py       
    ├── urls.py
    ├── tasks.py
    ├── reports.py    # логика генерации отчетов
    └── management/
        └── commands/
            └── generate_data.py  # команда для генерации данных
```
