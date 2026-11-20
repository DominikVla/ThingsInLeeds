CREATE DATABASE IF NOT EXISTS things_in_leeds
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE things_in_leeds;

CREATE TABLE venues (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    venue_type ENUM('hospitality','attraction','accommodation') NOT NULL,
    description TEXT,
    neighbourhood VARCHAR(100),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    address VARCHAR(255),
    postcode VARCHAR(12),
    price_tier TINYINT UNSIGNED,
    website_url VARCHAR(500),
    PRIMARY KEY (id),
    UNIQUE KEY uq_venue_name_address (name, address),
    CONSTRAINT chk_venue_price_tier CHECK (price_tier BETWEEN 1 AND 4)
);

CREATE TABLE opening_hours (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    venue_id BIGINT UNSIGNED NOT NULL,
    day_of_week TINYINT UNSIGNED NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_opening_venue FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE,
    CONSTRAINT chk_day_of_week CHECK (day_of_week BETWEEN 1 AND 7)
);

CREATE TABLE accommodation_details (
    venue_id BIGINT UNSIGNED NOT NULL,
    star_rating TINYINT UNSIGNED,
    avg_nightly_rate_gbp DECIMAL(8,2),
    check_in_time TIME,
    check_out_time TIME,
    PRIMARY KEY (venue_id),
    CONSTRAINT fk_accommodation_venue FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE,
    CONSTRAINT chk_star_rating CHECK (star_rating BETWEEN 1 AND 5)
);

CREATE TABLE attraction_details (
    venue_id BIGINT UNSIGNED NOT NULL,
    entry_fee_gbp DECIMAL(8,2),
    is_free BOOLEAN NOT NULL DEFAULT FALSE,
    avg_duration_mins SMALLINT UNSIGNED,
    booking_required BOOLEAN NOT NULL DEFAULT FALSE,
    family_friendly BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (venue_id),
    CONSTRAINT fk_attraction_venue FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE,
    CONSTRAINT chk_entry_fee CHECK (entry_fee_gbp >= 0)
);

CREATE TABLE events (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    venue_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(200) NOT NULL,
    event_type VARCHAR(100),
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,
    ticket_price_gbp DECIMAL(8,2),
    PRIMARY KEY (id),
    CONSTRAINT fk_event_venue FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE,
    CONSTRAINT chk_event_dates CHECK (end_datetime >= start_datetime),
    CONSTRAINT chk_ticket_price CHECK (ticket_price_gbp >= 0)
);

CREATE TABLE categories (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_category_name (name)
);

CREATE TABLE venue_categories (
    venue_id BIGINT UNSIGNED NOT NULL,
    category_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (venue_id, category_id),
    CONSTRAINT fk_vc_venue FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE,
    CONSTRAINT fk_vc_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);
