# Время — Деньги (Vremya-Dengi)

> Приложение для управления личными финансами с геймификацией и аналитикой.

## Стек технологий

| Слой | Технологии |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Shadcn/UI, Zustand, React Query, Recharts |
| Backend | FastAPI, Python, SQLAlchemy, Alembic |
| БД | PostgreSQL, Redis |
| Фоновые задачи | Celery, Celery Beat |
| Инфра | Docker, GitHub Actions, Netlify |

## Структура проекта

```
vremya-dengi/
├── frontend/              # Next.js приложение
│   ├── app/               # App Router
│   ├── components/        # UI компоненты
│   └── lib/               # Утилиты, stores, API
├── backend/               # FastAPI сервер
│   └── app/
│       ├── api/           # Роуты
│       ├── models/        # Модели
│       ├── services/      # Бизнес-логика
│       └── workers/       # Celery задачи
├── docs/                  # Документация
├── .github/workflows/     # CI/CD
├── docker-compose.yml     # Docker конфигурация
└── netlify.toml           # Netlify конфигурация
```

## Быстрый старт

### Предварительные требования
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Frontend
```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
```

### Docker (всё вместе)
```bash
docker-compose up -d
```

## Документация

- [Архитектура](docs/ARCHITECTURE.md)
- [API документация](docs/API.md)
- [Деплой](docs/DEPLOY.md)
- [Контрибьютинг](CONTRIBUTING.md)

## Лицензия

MIT
