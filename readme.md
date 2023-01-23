Пример бэкенда для сайта ресторана, написанного на FastAPI

*Установка:*
-

Заходим в репозиторий с проектом

Создаем виртуальное окружение:
python -m venv venv .

Активируем виртуальное окружение:
/venv/Scripts/activate

Устанавливаем зависимости:
pip install -r requirements.txt

Создаем файл .env и заполняем его переменными окружения:
-

TEST_DATABASE_URL = "postgresql://postgres:passwd@test_postgres_ylab:5432/test_ylab"\
DATABASE_URL = "postgresql://postgres:passwd@postgres_ylab:5432/ylab"\
IS_RUN_TESTS = 0 

Запускаем докер-контейнер:
-
docker-compose -f docker-compose.yml up -d

Запускаем докер-контейнер с тестами:
-
В файле .env меняем значение:
IS_RUN_TESTS = 1

Выполняем команду:
docker-compose -f docker-compose.test.yml up -d 


