CREATE DATABASE event_management;

USE event_management;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    role ENUM('user', 'admin') DEFAULT 'user'
);

CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    date DATE,
    time TIME,
    location VARCHAR(255),
    image VARCHAR(255),
    category VARCHAR(50),
    is_paid BOOLEAN,
    capacity INT DEFAULT 0
);

CREATE TABLE registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(15),
    tickets INT,
    FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE TABLE saved_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    event_id INT,
    UNIQUE(user_id, event_id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);