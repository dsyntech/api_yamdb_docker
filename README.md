# REST API для YamDB
Данное приложение предоставляет REST API для создания произведений с отзывами.

### Технологии
Django, Django REST Framework, PostgreSQL, Simple-JWT, Gunicorn, Docker, nginx, git

## Запуск проекта
### 0. Перейти в директорию проекта с docker-compose.yaml
### 1. Собрать и запустить контейнеры Docker
```bash
docker-compose up --build -d
```

### 2. Создать администратора Django
```bash
docker-compose exec web python manage.py createsuperuser
```
Введите почту и пароль в интерактивном режиме.

### 3. Заполнить базу данных тестовыми данными
```bash
docker-compose exec web python manage.py import_data
```
Дождитесь окончания импорта.

### 4. Открыть браузер
- Корневое представление API по умолчанию: http://localhost/api/v1/
- Админка: http://localhost/admin
- Документация: http://localhost/redoc

### Автор
Илья Боюр
