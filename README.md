API организационной структуры

https://docs.google.com/document/d/1MB0wtk2fC3uHOHwIuOOjk9az0gtyx2Xovmn-A0E7NBU/edit?tab=t.0

стэк: Python 3.13 + Django(DRF) + PostgreSQL + Docker + Gunicorn

запуск проекта:
1) в корне проекта создать .env по типу .env.example
2) docker-compose up --build
3) прогнать тесты docker-compose exec web pytest


Миграции будут применены автоматически

Создать суперпользователя: docker-compose exec web python manage.py createsuperuser (если нужно)

Админка: http://127.0.0.1:8000/admin/

OpenAPI: http://127.0.0.1:8000/schema/

