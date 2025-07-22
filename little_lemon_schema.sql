-- Create database
CREATE DATABASE IF NOT EXISTS little_lemon;
USE little_lemon;

-- Customers table
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20)
);

-- Tables representing restaurant tables
CREATE TABLE IF NOT EXISTS Tables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    capacity INT NOT NULL,
    location VARCHAR(100) -- e.g., Indoor, Outdoor
);

-- Bookings table
CREATE TABLE IF NOT EXISTS Bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    table_id INT NOT NULL,
    booking_datetime DATETIME NOT NULL,
    number_of_guests INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Confirmed',
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (table_id) REFERENCES Tables(table_id)
);
