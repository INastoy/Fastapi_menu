Пример бэкенда для сайта ресторана, написанного на FastAPI
-
Стек технологий:
`FastAPI` `PostgreSQL` `SQLAlchemy` `Pytest` `Docker` `Alembic` `Redis` `Celery` `RabbitMQ`

<details>

 <summary>Реализованный функционал</summary>


1. Регистрация и авторизация пользователей с использованием JWT токенов
2. Валидация вводимого email и password
3. Эндпоинты для создания/изменения/просмотра/удаления меню, подменю и блюд
4. Эндпоинт для тестового заполнения БД (menus/fill)
5. Энпоинты для формирования и выгрузки всех меню с подменю и блюдами в Excel документ
6. Написаны тесты для CRUD операций
7. Кэширование данных в Redis при Get запросе и удаление кешированных данных при Post/Patch/Delete запросах
8. Выполнение длительных операций вынесено в Celery task. Доступ к результатам производится по id таска.
9. Весь проект завернут в докер-контейнеры и поднимается одной командой
10. Подробная документация проекта доступна по адресу /docs

</details>

*Запуск в docker контейнере:*
-
1. В репозитории уже создан .env с переменными окружения

2. Запуск проекта в докер-контейнере:

```shell
docker-compose up -d
```
3. Запуск докер-контейнера с тестами:

```shell
docker-compose -f docker-compose.test.yml up -d
```

*Полная установка:*
-

1. Заходим в репозиторий с проектом

2. Создаем виртуальное окружение:
```shell
python -m venv venv
```
3. Активируем виртуальное окружение:
```shell
./venv/Scripts/activate
```
4. Устанавливаем зависимости:
```shell
pip install -r requirements.txt
```
5. В репозитории с проектом создаем файл .env и заполняем его переменными окружения:


>PGUSER: "postgres"\
>POSTGRES_USER: "postgres"\
>POSTGRES_PASSWORD = "passwd"
>
>TEST_DATABASE_URL = "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@test_postgres_ylab:5432/test_ylab"\
>PROD_DATABASE_URL = "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres_ylab:5432/ylab"\
>DATABASE_URL = "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/menu_test"
>
>REDIS_DB_NUM = "0"
>TEST_CACHE_URL = "redis://test_redis_ylab:6379/0"\
>PROD_CACHE_URL = "redis://redis_ylab:6379/0"\
>CACHE_URL = "redis://localhost:6379/0"
>
>PROD_CELERY_BROKER_URL = "pyamqp://guest:guest@rabbitmq_ylab//"\
>CELERY_BROKER_URL = "pyamqp://guest:guest@localhost//"
>
>RABBITMQ_DEFAULT_USER = "guest"\
>RABBITMQ_DEFAULT_PASS = "guest"
>
>JWT_SECRET = "OLzrLAYYMA26jkMkAp737lLJIDUjJUBHA3PVbtgwTdw"

6. Запуск проекта:

```shell
uvicorn main:fastapi_app --host 127.0.0.1 --port 8000
```
7. Документация к проекту будет доступна по адресу:
<http://127.0.0.1:8000/docs>
