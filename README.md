# rentCarKom

Car rental site built with Django. Guests browse the fleet, clients book a car, and staff manage rentals.

## Setup

The app uses MySQL 8.0.46. The database name is `rentcarkom`. Connection settings live in `.env`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_users
python manage.py seed_cars
python manage.py runserver
```

Open http://127.0.0.1:8000/

In MySQL Workbench, connect to `127.0.0.1:3306` as `root` and open the schema `rentcarkom`.

## Accounts

| Role    | Email                  | Password   |
|---------|------------------------|------------|
| Admin   | admin@rentcarkom.com   | admin123   |
| Manager | manager@rentcarkom.com | manager123 |

Passwords are stored hashed. Registration creates a client. Guests can browse without an account.

## Who can do what

- Everyone can browse cars and open a car page.
- Clients, managers, and admins can rent a free car.
- Managers and admins see fleet stats and can complete or cancel rentals.
- Admins can add cars, upload photos, and delete cars.
