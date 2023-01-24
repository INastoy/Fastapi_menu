Пример бэкенда для сайта ресторана, написанного на FastAPI
-
Стек технологий: 
`FastAPI` `PostgreSQL` `SQLAlchemy` `Pytest`

*Запуск в docker контейнере:*
-
1. В репозитории уже создан .env с переменными окружения

2. Запуск проекта в докер-контейнере:

```shell
docker-compose -f docker-compose.yml up -d
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

6. Запуск проекта:

```shell
uvicorn main:app --host 127.0.0.1 --port 8000
```
7. Документация к проекту будет доступна по адресу:
<http://127.0.0.1:8000/docs>


