# REST API to YamDB service
Stack: Django, Django REST Framework, PostgreSQL, Simple-JWT, Gunicorn, Docker, nginx, git

This app provides API for creating titles with reviews.
You shall run the following commands in project folder to startup the app.

To test functionality:
### 1. Prepare workspace
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create project database and migrate it
```bash
python manage.py migrate
```

### 3. FIll the database with default data
```bash
python manage.py import_data
```

### 4. Create admin
```bash
python manage.py createsuperuser
```

### 5. Start the app
```bash
python manage.py runserver
```
### 6. Enjoy!

See documentation to REST API on http://localhost:8000/redoc
