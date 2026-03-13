# Organization Directory API

REST API для справочника организаций, зданий и видов деятельности.

## Стек
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Docker

## Запуск
1. Скопируйте `.env.example` в `.env` и укажите свои значения.
2. Выполните `docker-compose up --build`.
3. Документация доступна по адресу `http://localhost:8000/docs`.

## Тестовые данные
Для заполнения БД тестовыми данными выполните:
```bash
docker exec -it <container_name> python -m app.seed
