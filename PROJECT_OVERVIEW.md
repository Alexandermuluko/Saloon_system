# Project Overview — SalonHome

This file summarizes the repository contents, the purpose of the main folders, and the steps to run and deploy the project on Windows PowerShell.

## Project root
- manage.py — Django management entrypoint for migrations, running the server, and custom commands.
- db.sqlite3 — SQLite database used for local development and demo data.
- runserver.out and runserver.err — server logs from local runs.
- PROJECT_OVERVIEW.md — this overview file.
- README.md — project README.

## Main package: saloon_system_chinese/
- config/ — Django project settings and routing
  - __init__.py — package marker
  - asgi.py — ASGI entrypoint
  - wsgi.py — WSGI entrypoint
  - settings.py — Django settings, including the static files config and environment-based deployment settings
  - urls.py — root URL routing
- core/ — the main salon booking app
  - __init__.py
  - apps.py — app configuration
  - admin.py — Django admin configuration
  - models.py — data models for Service, Hairdresser, and Booking
  - forms.py — registration/login and booking forms
  - views.py — views for the customer and staff experience
  - urls.py — app URL patterns
  - management/commands/seed_data.py — demo data generator
  - migrations/ — Django migration history
- templates/ — HTML templates and static assets
  - index.html, register.html, customer-service.html, admin-login.html, admin-dashboard.html, admin-form.html — primary user-facing pages
  - assets/css/styles.css — custom theme styling

## Project purpose
This is a small Django application for salon booking. Customers can register, browse services, submit bookings, and track progress, while staff can manage services, hairdressers, and booking requests from a dashboard.

## How to run locally (Windows PowerShell)
1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install Django:

```powershell
pip install "Django>=6.0,<7"
```

3. Apply migrations:

```powershell
python manage.py migrate
```

4. Seed demo data:

```powershell
python manage.py seed_data
```

5. Create a superuser (optional):

```powershell
python manage.py createsuperuser
```

6. Run the development server:

```powershell
python manage.py runserver 127.0.0.1:8000
```

7. Open the app in a browser:
- Home: http://127.0.0.1:8000/
- Register: http://127.0.0.1:8000/register/
- Login: http://127.0.0.1:8000/login/
- Customer booking page: http://127.0.0.1:8000/bookings/
- Staff dashboard: http://127.0.0.1:8000/dashboard/
- Django admin: http://127.0.0.1:8000/admin/

## Demo credentials
- Staff login: username staffdemo, password demo12345
- Sample customer logins: amanda, liwei, nora, chen with password demo12345

## How to host and deploy
### Option 1: Local deployment for testing
Use the development server above for local testing only. It is not suitable for production.

### Option 2: Deploy to a simple cloud host
A practical production path is:
- Host the Django app on a cloud platform such as Render, Railway, PythonAnywhere, or Azure App Service.
- Use PostgreSQL instead of SQLite for production.
- Serve static files with a cloud storage backend or collectstatic.

### Recommended production checklist
- Set environment variables:
  - SECRET_KEY
  - DEBUG=False
  - ALLOWED_HOSTS=your-domain.com
- Replace SQLite with PostgreSQL.
- Run:

```powershell
python manage.py collectstatic
python manage.py migrate
```

- Set up a web server or platform-managed service to run gunicorn.

### Example production run command
```powershell
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Suggested next steps
- Add a requirements.txt file for pinned dependencies.
- Move the database from SQLite to PostgreSQL.
- Add a production-ready hosting configuration.
- Optionally replace the CDN-based Bootstrap assets with a bundled local setup.
