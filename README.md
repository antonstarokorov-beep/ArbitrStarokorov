# Apex Intelligence MVP Backend

Backend-first skeleton для legal marketing intelligence platform с осью данных:

`lead -> click_id -> bot_chat_id -> crm_deal_id -> revenue`

## Что реализовано

- FastAPI API (`app/main.py`)
- Pydantic v2 схемы (`app/schemas/`)
- SQLAlchemy 2.0 модели (`app/models/`):
  - `leads`
  - `bot_events`
  - `crm_events`
  - `lead_touchpoints`
- Repository layer (`app/repositories/`)
- Service layer (`app/services/`)
- PostgreSQL-конфиг через env (`app/core/config.py`)
- Alembic + первая миграция (`alembic/versions/20260315_0001_initial_schema.py`)
- Render blueprint (`render.yaml`) для стабильного деплоя

## Структура

```text
.
├── app
│   ├── api/v1
│   ├── core/config.py
│   ├── db
│   ├── models
│   ├── repositories
│   ├── schemas
│   ├── services
│   └── main.py
├── alembic
│   └── versions
├── alembic.ini
├── .env.example
├── main.py
├── render.yaml
└── requirements.txt
```

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Проверка здоровья:

```bash
curl http://127.0.0.1:8000/health
```

Ожидается:

```json
{"status": "ok"}
```

## Деплой на Render (пошагово)

### 1) Почему у вас упал build

Вы деплоили коммит `756141a...`, где в `requirements.txt` были desktop-зависимости (`PyQt6`, `xhtml2pdf`, `pyinstaller`). Render пытался собрать их на Python 3.14, что привело к ошибке в `python-bidi`/Rust toolchain.

Нужно деплоить **текущий backend-коммит**, где зависимости backend-only.

### 2) Создание Web Service

1. Render -> **New +** -> **Web Service**
2. Подключите GitHub-репозиторий
3. В поле branch укажите нужную ветку с backend-кодом
4. Build command:
   - `pip install -r requirements.txt`
5. Start command:
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Либо используйте `render.yaml` (Blueprint deploy) — команда и env уже зашиты.

### 3) Обязательные env-переменные в Render

- `PYTHON_VERSION=3.11.9`
- `APP_NAME=Apex Intelligence API`
- `APP_VERSION=0.1.0`
- `DEBUG=false`
- `POSTGRES_USER=...`
- `POSTGRES_PASSWORD=...`
- `POSTGRES_HOST=...`
- `POSTGRES_PORT=5432`
- `POSTGRES_DB=...`

## Neon: где взять доступы (очень подробно)

### Вариант A (через веб-интерфейс Neon, проще всего)

1. Войдите на https://console.neon.tech
2. Создайте Project
3. Откройте проект -> слева **Dashboard**
4. Найдите блок **Connection string** или кнопку **Connect**
5. Выберите:
   - Role: обычно `neondb_owner`
   - Database: обычно `neondb`
   - Branch: `main`
6. Скопируйте connection string вида:
   - `postgresql://USER:PASSWORD@HOST/DB?sslmode=require`

Из строки берём переменные так:

- `POSTGRES_USER` = `USER`
- `POSTGRES_PASSWORD` = `PASSWORD`
- `POSTGRES_HOST` = `HOST`
- `POSTGRES_PORT` = `5432` (если явно не указан)
- `POSTGRES_DB` = `DB`

Пример разбора вашей строки:

`postgresql://neondb_owner:npg_***@ep-misty-scene-agv4om3v-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

- `POSTGRES_USER=neondb_owner`
- `POSTGRES_PASSWORD=npg_***`
- `POSTGRES_HOST=ep-misty-scene-agv4om3v-pooler.c-2.eu-central-1.aws.neon.tech`
- `POSTGRES_PORT=5432`
- `POSTGRES_DB=neondb`

### Вариант B (через CLI `neonctl`)

CLI не обязателен для Render деплоя, но если используете:

```bash
neonctl projects list
neonctl connection-string --project-id <project_id> --database-name neondb --role-name neondb_owner
```

Далее разбираете строку так же, как выше.

## Применение миграций (обязательно)

После того как env-переменные заполнены, нужно применить Alembic миграцию к Neon БД:

```bash
alembic upgrade head
```

Где запустить:
- локально (с теми же env на Neon), либо
- через отдельный one-off job/CI step.

## Как проверить, что всё поднялось

После успешного деплоя на Render:

1. Откройте URL сервиса, например:
   - `https://<your-service>.onrender.com/health`
2. Должен вернуться JSON:
   - `{"status":"ok"}`
3. Далее тест API:
   - `POST /api/v1/dev/seed`
   - `GET /api/v1/dashboard/summary`

## Эндпоинты

- `GET /health`
- `POST /api/v1/leads`
- `GET /api/v1/leads`
- `GET /api/v1/leads/{lead_id}`
- `PATCH /api/v1/leads/{lead_id}`
- `POST /api/v1/bot/events`
- `POST /api/v1/crm/events`
- `GET /api/v1/dashboard/summary`
- `POST /api/v1/dev/seed`
