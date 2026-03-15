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
└── requirements.txt
```

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Запуск миграций:

```bash
alembic upgrade head
```

Запуск API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

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

## Логика обновлений

- Bot event обновляет `matter_type`, `ai_score`, `status=bot_qualified`.
- CRM event обновляет `crm_deal_id`, `status`, `revenue`, `estimated_ltv`.
- Dashboard summary считает:
  - `total_leads`
  - `qualified_leads`
  - `active_leads`
  - `paid_leads`
  - `total_revenue`
  - `avg_ai_score`
  - `by_channel`

## Архитектурные решения

- **Чёткое разделение слоёв**: API -> services -> repositories -> DB.
- **Минимум магии**: синхронный `Session`, явные зависимости через `Depends`.
- **Готовность к интеграциям**: события bot/CRM хранятся отдельно, а сквозные связи дублируются в `lead_touchpoints` для аналитики каналов.
- **Сохранена продуктовая модель**: статусы и справочники не переизобретались, только перенесены в модульную структуру.
