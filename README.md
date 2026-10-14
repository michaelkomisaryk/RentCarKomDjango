# rentCarKom

Car rental app rebuilt with Django. The temporary pages cover the same roles and flows as the original Flet app. The layout is meant to be replaced later.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_users
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Accounts

| Role    | Email                  | Password   |
|---------|------------------------|------------|
| Admin   | admin@rentcarkom.com   | admin123   |
| Manager | manager@rentcarkom.com | manager123 |

Passwords are stored hashed. Registration, added later, creates a client.
