# Barter Service

Сервис для обмена товарами между пользователями

## Запуск проекта

### 1. Копируйте репозиторий
```bash
git clone https://github.com/lexasidorov/django_barter_service.git
cd barter-service
```

### 2. Запуск в Docker(рекомендуется)
Настройте файл `.env`. Шаблон файла находится в корне репозитория.

Затем запустите сборку контейнеров.
```bash
docker-compose up --build
```



### После запуска
* API доступно на http://localhost:8000     
* Документация API: http://localhost:8000/api/docs/


### 3. Запуск без Docker
Требования: Python 3.9+, PostgreSQL

1. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate (Windows)
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```
3. Настройте проект в `core/settings.py`.
Необходимые для настройки переменные лежат в шаблоне `.env-mock`

4. Запустите сервер:

```bash
python manage.py migrate
python manage.py runserver
```

### 4. Запуск тестов

```bash
# В Docker:
docker-compose exec web pytest
# В Docker из консоли контейнера:
pytest
# Без Docker:
pytest
```