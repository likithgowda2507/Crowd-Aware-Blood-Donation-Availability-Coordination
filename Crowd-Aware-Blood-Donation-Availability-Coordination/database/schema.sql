-- BloodConnect Database Schema
-- MySQL Database for Blood Donation Coordination Platform

-- Create Database
CREATE DATABASE IF NOT EXISTS bloodconnect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bloodconnect;

-- =============================================
-- USER TABLES
-- =============================================

-- Donors Table
CREATE TABLE donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    age INT NOT NULL CHECK (age BETWEEN 18 AND 65),
    gender ENUM('male', 'female', 'other') NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    pincode VARCHAR(6) NOT NULL,
    last_donation_date DATE,
    health_status ENUM('excellent', 'good', 'fair') NOT NULL,
    medical_conditions JSON,
    is_eligible BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_blood_group (blood_group),
    INDEX idx_city (city),
    INDEX idx_is_eligible (is_eligible)
) ENGINE=InnoDB;

-- Blood Banks Table
CREATE TABLE blood_banks (
    bank_id INT AUTO_INCREMENT PRIMARY KEY,
    bank_name VARCHAR(150) NOT NULL,
    license_id VARCHAR(50) UNIQUE NOT NULL,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    pincode VARCHAR(6) NOT NULL,
    country VARCHAR(50) DEFAULT 'India',
    capacity INT NOT NULL,
    operating_hours VARCHAR(50) NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_city (city),
    INDEX idx_location (latitude, longitude)
) ENGINE=InnoDB;

-- Hospitals Table
CREATE TABLE hospitals (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_name VARCHAR(150) NOT NULL,
    registration_id VARCHAR(50) UNIQUE NOT NULL,
    hospital_type ENUM('government', 'private', 'trust') NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    emergency_contact VARCHAR(15) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    pincode VARCHAR(6) NOT NULL,
    country VARCHAR(50) DEFAULT 'India',
    number_of_beds INT NOT NULL,
    specializations TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_city (city),
    INDEX idx_location (latitude, longitude)
) ENGINE=InnoDB;

-- =============================================
-- BLOOD INVENTORY
-- =============================================

-- Blood Inventory Table
CREATE TABLE blood_inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    bank_id INT NOT NULL,
    bag_id VARCHAR(50) UNIQUE NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    component_type ENUM('whole_blood', 'packed_rbc', 'platelets', 'plasma', 'cryo') DEFAULT 'whole_blood',
    volume INT NOT NULL COMMENT 'Volume in ml',
    collection_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    status ENUM('available', 'reserved', 'used', 'expired', 'discarded') DEFAULT 'available',
    donor_id INT,
    qr_code_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE SET NULL,
    INDEX idx_blood_group (blood_group),
    INDEX idx_status (status),
    INDEX idx_expiry (expiry_date),
    INDEX idx_bank (bank_id)
) ENGINE=InnoDB;

-- =============================================
-- DONATION CAMPS
-- =============================================

-- Donation Camps Table
CREATE TABLE donation_camps (
    camp_id INT AUTO_INCREMENT PRIMARY KEY,
    bank_id INT NOT NULL,
    camp_name VARCHAR(150) NOT NULL,
    location TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    camp_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    total_slots INT NOT NULL,
    booked_slots INT DEFAULT 0,
    slot_duration INT DEFAULT 30 COMMENT 'Duration in minutes',
    description TEXT,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    INDEX idx_camp_date (camp_date),
    INDEX idx_city (city),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Camp Bookings Table
CREATE TABLE camp_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    camp_id INT NOT NULL,
    donor_id INT NOT NULL,
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    slot_time TIME NOT NULL,
    status ENUM('confirmed', 'completed', 'cancelled', 'no_show') DEFAULT 'confirmed',
    donation_status ENUM('pending', 'donated', 'deferred') DEFAULT 'pending',
    units_collected INT DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (camp_id) REFERENCES donation_camps(camp_id) ON DELETE CASCADE,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE CASCADE,
    INDEX idx_donor (donor_id),
    INDEX idx_camp (camp_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- =============================================
-- HOSPITAL REQUESTS
-- =============================================

-- Blood Requests Table
CREATE TABLE blood_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    bank_id INT NOT NULL,
    request_reference VARCHAR(50) UNIQUE NOT NULL,
    patient_id VARCHAR(50) NOT NULL,
    patient_name VARCHAR(100) NOT NULL,
    patient_age INT NOT NULL,
    patient_gender ENUM('male', 'female', 'other') NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    component_type ENUM('whole_blood', 'packed_rbc', 'platelets', 'plasma', 'cryo') NOT NULL,
    units_required INT NOT NULL,
    priority ENUM('emergency', 'urgent', 'routine') NOT NULL,
    purpose ENUM('surgery', 'accident', 'anemia', 'cancer', 'pregnancy', 'other') NOT NULL,
    required_by DATETIME NOT NULL,
    status ENUM('pending', 'approved', 'partially_fulfilled', 'fulfilled', 'rejected', 'cancelled') DEFAULT 'pending',
    units_fulfilled INT DEFAULT 0,
    notes TEXT,
    rejection_reason TEXT,
    approved_at DATETIME,
    fulfilled_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id) ON DELETE CASCADE,
    FOREIGN KEY (bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    INDEX idx_hospital (hospital_id),
    INDEX idx_bank (bank_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_blood_group (blood_group)
) ENGINE=InnoDB;

-- Request Fulfillment Details
CREATE TABLE request_fulfillments (
    fulfillment_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    inventory_id INT NOT NULL,
    quantity INT NOT NULL,
    fulfilled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES blood_requests(request_id) ON DELETE CASCADE,
    FOREIGN KEY (inventory_id) REFERENCES blood_inventory(inventory_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================
-- DONATION HISTORY
-- =============================================

-- Donation Records Table
CREATE TABLE donation_records (
    donation_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    bank_id INT NOT NULL,
    camp_id INT,
    booking_id INT,
    donation_date DATE NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    volume INT NOT NULL COMMENT 'Volume in ml',
    donation_type ENUM('camp', 'walk_in') NOT NULL,
    bag_id VARCHAR(50),
    certificate_path VARCHAR(255),
    hemoglobin_level DECIMAL(4,2),
    blood_pressure VARCHAR(20),
    status ENUM('successful', 'deferred', 'rejected') DEFAULT 'successful',
    deferral_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE CASCADE,
    FOREIGN KEY (bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    FOREIGN KEY (camp_id) REFERENCES donation_camps(camp_id) ON DELETE SET NULL,
    FOREIGN KEY (booking_id) REFERENCES camp_bookings(booking_id) ON DELETE SET NULL,
    INDEX idx_donor (donor_id),
    INDEX idx_bank (bank_id),
    INDEX idx_date (donation_date)
) ENGINE=InnoDB;

-- =============================================
-- NOTIFICATIONS & ALERTS
-- =============================================

-- Notifications Table
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_type ENUM('donor', 'bank', 'hospital') NOT NULL,
    user_id INT NOT NULL,
    notification_type ENUM('shortage', 'emergency', 'camp', 'booking', 'request', 'general') NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    is_read BOOLEAN DEFAULT FALSE,
    related_id INT COMMENT 'ID of related entity (camp_id, request_id, etc)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_type, user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- Shortage Alerts Table
CREATE TABLE shortage_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    bank_id INT NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    current_stock INT NOT NULL,
    threshold_level INT NOT NULL,
    alert_level ENUM('low', 'critical') NOT NULL,
    donors_notified INT DEFAULT 0,
    status ENUM('active', 'resolved') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    INDEX idx_bank (bank_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- =============================================
-- BLOOD BANK NETWORK
-- =============================================

-- Blood Bank Connections
CREATE TABLE bank_connections (
    connection_id INT AUTO_INCREMENT PRIMARY KEY,
    bank_id_1 INT NOT NULL,
    bank_id_2 INT NOT NULL,
    connection_status ENUM('pending', 'active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id_1) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    FOREIGN KEY (bank_id_2) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    UNIQUE KEY unique_connection (bank_id_1, bank_id_2),
    INDEX idx_bank1 (bank_id_1),
    INDEX idx_bank2 (bank_id_2)
) ENGINE=InnoDB;

-- Inter-Bank Stock Sharing
CREATE TABLE inter_bank_transfers (
    transfer_id INT AUTO_INCREMENT PRIMARY KEY,
    from_bank_id INT NOT NULL,
    to_bank_id INT NOT NULL,
    inventory_id INT NOT NULL,
    request_id INT,
    transfer_date DATETIME NOT NULL,
    status ENUM('pending', 'in_transit', 'completed', 'cancelled') DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    FOREIGN KEY (to_bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    FOREIGN KEY (inventory_id) REFERENCES blood_inventory(inventory_id) ON DELETE CASCADE,
    FOREIGN KEY (request_id) REFERENCES blood_requests(request_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- =============================================
-- AI/ML PREDICTIONS
-- =============================================

-- Demand Predictions Table
CREATE TABLE demand_predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    bank_id INT NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_demand INT NOT NULL,
    confidence_score DECIMAL(5,2) COMMENT 'Confidence percentage',
    model_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES blood_banks(bank_id) ON DELETE CASCADE,
    INDEX idx_bank (bank_id),
    INDEX idx_date (prediction_date)
) ENGINE=InnoDB;

-- =============================================
-- SYSTEM LOGS
-- =============================================

-- Activity Logs
CREATE TABLE activity_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_type ENUM('donor', 'bank', 'hospital', 'admin') NOT NULL,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_type, user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- =============================================
-- INITIAL DATA / TRIGGERS
-- =============================================

-- Trigger to update donor eligibility after donation
DELIMITER //
CREATE TRIGGER update_donor_eligibility 
AFTER INSERT ON donation_records
FOR EACH ROW
BEGIN
    UPDATE donors 
    SET last_donation_date = NEW.donation_date,
        is_eligible = FALSE
    WHERE donor_id = NEW.donor_id;
END//

DELIMITER ;

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Additional composite indexes for common queries
CREATE INDEX idx_donor_location ON donors(city, blood_group, is_eligible);
CREATE INDEX idx_inventory_available ON blood_inventory(bank_id, blood_group, status, expiry_date);
CREATE INDEX idx_request_pending ON blood_requests(bank_id, status, priority, created_at);
CREATE INDEX idx_camp_upcoming ON donation_camps(camp_date, status, city);

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- View: Available Blood Stock by Bank and Group
CREATE VIEW v_blood_stock_summary AS
SELECT 
    bi.bank_id,
    bb.bank_name,
    bi.blood_group,
    bi.component_type,
    COUNT(*) as total_units,
    SUM(CASE WHEN bi.status = 'available' THEN 1 ELSE 0 END) as available_units,
    SUM(CASE WHEN bi.status = 'reserved' THEN 1 ELSE 0 END) as reserved_units,
    MIN(bi.expiry_date) as earliest_expiry,
    COUNT(CASE WHEN DATEDIFF(bi.expiry_date, CURDATE()) <= 7 THEN 1 END) as expiring_soon
FROM blood_inventory bi
JOIN blood_banks bb ON bi.bank_id = bb.bank_id
WHERE bi.status IN ('available', 'reserved')
GROUP BY bi.bank_id, bi.blood_group, bi.component_type;

-- View: Donor Statistics
CREATE VIEW v_donor_stats AS
SELECT 
    d.donor_id,
    d.full_name,
    d.blood_group,
    COUNT(dr.donation_id) as total_donations,
    MAX(dr.donation_date) as last_donation_date,
    d.is_eligible,
    DATEDIFF(CURDATE(), MAX(dr.donation_date)) as days_since_last_donation
FROM donors d
LEFT JOIN donation_records dr ON d.donor_id = dr.donor_id
GROUP BY d.donor_id;

-- View: Hospital Request Summary
CREATE VIEW v_hospital_request_summary AS
SELECT 
    h.hospital_id,
    h.hospital_name,
    COUNT(br.request_id) as total_requests,
    SUM(CASE WHEN br.status = 'pending' THEN 1 ELSE 0 END) as pending_requests,
    SUM(CASE WHEN br.status = 'fulfilled' THEN 1 ELSE 0 END) as fulfilled_requests,
    SUM(CASE WHEN br.priority = 'emergency' THEN 1 ELSE 0 END) as emergency_requests,
    SUM(br.units_required) as total_units_requested,
    SUM(br.units_fulfilled) as total_units_received
FROM hospitals h
LEFT JOIN blood_requests br ON h.hospital_id = br.hospital_id
GROUP BY h.hospital_id;

-- =============================================
-- SAMPLE DATA (for testing)
-- =============================================

-- Insert sample blood bank
INSERT INTO blood_banks (bank_name, license_id, registration_number, email, password_hash, phone, contact_person, address, city, state, pincode, capacity, operating_hours, latitude, longitude) 
VALUES 
('City Blood Bank', 'LIC-001', 'REG-001', 'city@bloodbank.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfq8UyJZy2', '9876543210', 'Dr. Kumar', 'Main Road', 'Pollachi', 'Tamil Nadu', '642001', 500, '24/7', 10.6580, 77.0081);

-- Insert sample hospital
INSERT INTO hospitals (hospital_name, registration_id, hospital_type, email, password_hash, phone, emergency_contact, contact_person, address, city, state, pincode, number_of_beds, latitude, longitude)
VALUES
('City Hospital', 'HOSP-001', 'private', 'city@hospital.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfq8UyJZy2', '9876543211', '9876543299', 'Dr. Sharma', 'Hospital Road', 'Pollachi', 'Tamil Nadu', '642001', 100, 10.6600, 77.0100);

-- Note: Password hash is for 'password123' - change in production!
