-- Create the cs491 database if not exists
CREATE DATABASE IF NOT EXISTS cs491;

-- Switch to the cs491 database
USE cs491;

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE therapists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    experience INT,
    specialization TEXT,
    on_call BOOLEAN,
);

CREATE TABLE therapistSurvey (
    survey_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    gender ENUM('male', 'female', 'non-binary', 'either') NOT NULL,
    price FLOAT,
    specializations TEXT,
    bio TEXT,
    photo VARCHAR(255),

    FOREIGN KEY (user_id) REFERENCES therapists (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    therapist_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    am_pm ENUM('AM', 'PM') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (therapist_id) REFERENCES therapists (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payments(
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    purpose ENUM('AI Subscription', 'Therapist') NOT NULL,
    date_posted DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
-- NEEDS
-- differentiate user types: user and therapist. decided on registration
-- therapists are able to shcedule meetings
-- One table for all users and have type attribute? or Two tables one for each?
-- Therapist account needs profile pic, certifications, etc,
-- Users can search for therapists based on age range, ethnicity, 
-- Priotize AI
-- Voice over, customizable
-- Mobile friendly, scalable

