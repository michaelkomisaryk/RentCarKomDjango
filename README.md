# rentCarKom

Сайт оренди авто на Django і MySQL. Гість переглядає автопарк, клієнт бронює вільне авто, менеджер веде журнал оренд, адміністратор додає і редагує власні машини та фото.

Інтерфейс українською і англійською. Ціни в базі зберігаються в доларах: на українській мові сайт показує гривні за курсом `UAH_PER_USD` (зараз 41,50).

## Що потрібно

- Python 3.13
- MySQL 8.0.46, база `rentcarkom`, кодування `utf8mb4`
- Google Chrome, якщо запускаєте тести інтерфейсу

## Запуск

Скопіюйте `.env.example` у `.env` і заповніть його:

```text
MYSQL_DATABASE=rentcarkom
MYSQL_USER=rentcarkom
MYSQL_PASSWORD=пароль
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
SECRET_KEY=довгий-випадковий-рядок
```

Далі:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_users
python manage.py seed_cars
python manage.py runserver
```

Сайт відкривається на http://127.0.0.1:8000/. `seed_cars` створює 40 авто і чіпляє вже завантажені фото. Повторний запуск оновлює ті самі записи, а не дублює їх.

## Облікові записи

| Роль | Пошта | Пароль |
| --- | --- | --- |
| Адміністратор | admin@rentcarkom.com | admin123 |
| Менеджер | manager@rentcarkom.com | manager123 |

Паролі в базі зберігаються хешем. Реєстрація завжди створює клієнта. Гість може дивитися каталог без входу.

Клієнт орендує лише авто з заповненим профілем: телефон, РНОКПП і посвідчення водія. Другу активну оренду того самого авто сайт не створює. Адміністратор змінює лише ті машини, які додав сам.

## Тести

Уся suite, крім вікна Chrome:

```bash
.venv/bin/python manage.py test --keepdb
```

Два тести Selenium самі відкривають Chrome. MySQL має бути запущений. Кожен тест зручно запускати окремо:

```bash
.venv/bin/python manage.py test accounts.browser_tests.RegistrationChromeTests.test_registration_creates_a_client --keepdb
.venv/bin/python manage.py test rentals.browser_tests.BookingChromeTests.test_active_rental_blocks_a_second_booking --keepdb
```

Перший реєструє клієнта і входить під ним. Другий бронює Toyota Yaris на три доби і перевіряє, що другий клієнт уже не може її взяти.

## Склад

- `accounts` — користувач, вхід, реєстрація, профіль, групи і права
- `fleet` — авто, фото, відгуки, каталог
- `rentals` — оренда, журнал, завершення і скасування
- `config` — налаштування, адреси, WSGI
