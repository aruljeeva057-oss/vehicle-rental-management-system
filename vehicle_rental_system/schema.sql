CREATE DATABASE IF NOT EXISTS vehicle_rental;
USE vehicle_rental;

CREATE TABLE IF NOT EXISTS vehicles (
    id                  INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    registration_no     VARCHAR(20) NOT NULL UNIQUE,
    make                VARCHAR(50) NOT NULL,
    model               VARCHAR(80) NOT NULL,
    manufacture_year    SMALLINT UNSIGNED NOT NULL,
    vehicle_type        ENUM('CAR', 'BIKE', 'SUV', 'VAN') NOT NULL,
    seating_capacity    SMALLINT UNSIGNED NOT NULL,
    rental_rate_per_day DECIMAL(12,2) UNSIGNED NOT NULL,
    operational_status  ENUM('ACTIVE', 'MAINTENANCE', 'RETIRED')
                        NOT NULL DEFAULT 'ACTIVE',
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
                COMMENT 'Customer ID',
    full_name   VARCHAR(150) NOT NULL,
    phone       VARCHAR(25) NOT NULL UNIQUE,
    email       VARCHAR(254) NOT NULL UNIQUE,
    address     VARCHAR(300) NOT NULL,
    licence_no  VARCHAR(40) NOT NULL UNIQUE,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id                INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
                      COMMENT 'Booking ID',
    customer_id       INT UNSIGNED NOT NULL,
    vehicle_id        INT UNSIGNED NOT NULL,
    rental_start      DATE NOT NULL COMMENT 'Inclusive: first rental day',
    rental_end        DATE NOT NULL COMMENT 'Exclusive: day after last rental day',
    daily_rate        DECIMAL(12,2) UNSIGNED NOT NULL,
    security_deposit  DECIMAL(12,2) UNSIGNED NOT NULL DEFAULT 0.00,
    status            ENUM('RESERVED', 'ACTIVE', 'COMPLETED', 'CANCELLED')
                      NOT NULL DEFAULT 'RESERVED',
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                      ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bookings_customer
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON UPDATE CASCADE,
    CONSTRAINT fk_bookings_vehicle
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON UPDATE CASCADE,
    CONSTRAINT chk_booking_dates CHECK (rental_end > rental_start)
);
CREATE TABLE IF NOT EXISTS bills (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
                    COMMENT 'Bill ID',
    booking_id      INT UNSIGNED NOT NULL UNIQUE,
    rental_days     SMALLINT UNSIGNED NOT NULL,
    base_amount     DECIMAL(12,2) UNSIGNED NOT NULL,
    late_fee        DECIMAL(12,2) UNSIGNED NOT NULL DEFAULT 0.00,
    gst_amount      DECIMAL(12,2) UNSIGNED NOT NULL DEFAULT 0.00,
    deposit         DECIMAL(12,2) UNSIGNED NOT NULL DEFAULT 0.00,
    deposit_status  ENUM('NOT_SETTLED', 'APPLIED', 'REFUNDED')
                    NOT NULL DEFAULT 'NOT_SETTLED',
    total_due       DECIMAL(12,2) UNSIGNED NOT NULL,
    amount_paid     DECIMAL(12,2) UNSIGNED NOT NULL DEFAULT 0.00,
    status          ENUM('UNPAID', 'PARTIALLY_PAID', 'PAID')
                    NOT NULL DEFAULT 'UNPAID',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bills_booking
        FOREIGN KEY (booking_id) REFERENCES bookings(id) ON UPDATE CASCADE
);
