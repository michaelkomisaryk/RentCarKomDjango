-- Схема rentCarKom. Файл бази: db.sqlite3
-- Таблиці вже створені міграціями Django. Цей файл описує схему,
-- його не потрібно виконувати повторно на існуючій базі.

CREATE TABLE accounts_user (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    password varchar(128) NOT NULL,
    last_login datetime NULL,
    is_superuser bool NOT NULL,
    first_name varchar(150) NOT NULL,
    last_name varchar(150) NOT NULL,
    is_staff bool NOT NULL,
    is_active bool NOT NULL,
    date_joined datetime NOT NULL,
    email varchar(254) NOT NULL UNIQUE,
    name varchar(150) NOT NULL,
    phone varchar(20) NOT NULL,
    rnokpp varchar(10) NOT NULL,
    driver_license varchar(16) NOT NULL,
    role varchar(20) NOT NULL
);

CREATE TABLE fleet_car (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    brand varchar(100) NOT NULL,
    model varchar(100) NOT NULL,
    year integer NOT NULL CHECK (year >= 0),
    price decimal NOT NULL,
    seats smallint NOT NULL CHECK (seats >= 0),
    transmission varchar(20) NOT NULL,
    fuel varchar(20) NOT NULL,
    car_class varchar(20) NOT NULL,
    plate varchar(32) NOT NULL UNIQUE,
    color varchar(50) NOT NULL,
    mileage integer NOT NULL CHECK (mileage >= 0),
    description text NOT NULL,
    added_by_id integer NULL REFERENCES accounts_user (id)
);

CREATE TABLE fleet_carphoto (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    image varchar(100) NOT NULL,
    created_at datetime NOT NULL,
    car_id integer NOT NULL REFERENCES fleet_car (id)
);

CREATE TABLE rentals_rental (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    car_id integer NOT NULL REFERENCES fleet_car (id),
    car_brand varchar(100) NOT NULL,
    car_model varchar(100) NOT NULL,
    car_plate varchar(32) NOT NULL,
    user_id integer NOT NULL REFERENCES accounts_user (id),
    user_email varchar(254) NOT NULL,
    renter_name varchar(150) NOT NULL,
    renter_phone varchar(20) NOT NULL,
    renter_rnokpp varchar(10) NOT NULL,
    renter_license varchar(16) NOT NULL,
    start_datetime datetime NOT NULL,
    end_datetime datetime NOT NULL,
    days integer NOT NULL CHECK (days >= 0),
    price_per_day decimal NOT NULL,
    total_price decimal NOT NULL,
    status varchar(20) NOT NULL,
    created_at datetime NOT NULL
);

CREATE INDEX fleet_car_added_by_id ON fleet_car (added_by_id);
CREATE INDEX fleet_carphoto_car_id ON fleet_carphoto (car_id);
CREATE INDEX rentals_rental_car_id ON rentals_rental (car_id);
CREATE INDEX rentals_rental_user_id ON rentals_rental (user_id);

-- Одне авто не може мати дві активні оренди одночасно.
CREATE UNIQUE INDEX one_active_rental_per_car
    ON rentals_rental (car_id)
    WHERE status = 'active';
