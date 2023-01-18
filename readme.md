Fastapi test project

Установка:

Заходим в репозиторий с проектом

Создаем виртуальное окружение:
python -m venv venv .

Активируем виртуальное окружение:
/venv/Scripts/activate

Устанавливаем зависимости:
pip install -r requirements.txt

Переходим в файл с настройками:
services -> settings.py

В файле settings.py прописываем пусть к БД:
DATABASE_URL = 'postgresql://postgres:password@127.0.0.1:5432/menu_test'

Запуск проекта:
python main.py
