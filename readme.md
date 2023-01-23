Пример бэкенда для сайта ресторана, написанного на FastAPI


В репозитории с проектом создаем файл .env и заполняем его переменными окружения:
-

>PGUSER: "postgres"\
>POSTGRES_USER: "postgres"\
>POSTGRES_PASSWORD = "passwd"
>
>TEST_DATABASE_URL = "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@test_postgres_ylab:5432/test_ylab"\
>PROD_DATABASE_URL = "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres_ylab:5432/ylab"\
>DATABASE_URL = "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/menu_test"

Запуск проекта в докер-контейнере:
-
```shell
docker-compose -f docker-compose.yml up -d
```
Запуск докер-контейнера с тестами:
-
```shell
docker-compose -f docker-compose.test.yml up -d
```

*Полная установка:*
-

Заходим в репозиторий с проектом

Создаем виртуальное окружение:
```shell
python -m venv venv .
```

Активируем виртуальное окружение:
```shell
./venv/Scripts/activate
```
Устанавливаем зависимости:
```shell
pip install -r requirements.txt
```

Запуск проекта:
-
```shell
uvicorn main:app --host 0.0.0.0 --port 8000
```




