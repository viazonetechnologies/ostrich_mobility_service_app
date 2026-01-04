#!/usr/bin/env python3
import pymysql

# Aiven Database configuration
DB_CONFIG = {
    'host': 'mysql-ostrich-tviazone-5922.i.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_c985UhSyW3FZhUdTmI8',
    'database': 'defaultdb',
    'port': 16599,
    'charset': 'utf8mb4',
    'ssl': {'ssl_mode': 'REQUIRED'}
}

def check_and_setup_tables():
    print("Connecting to Aiven MySQL database...")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("PASS: Connected to Aiven database successfully")
        
        # Check existing tables
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        print(f"Existing tables: {existing_tables}")
        
        # Required tables for service API
        required_tables = {
            'technicians': """
                CREATE TABLE technicians (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    employee_id VARCHAR(50) UNIQUE,
                    full_name VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    role VARCHAR(50) DEFAULT 'technician',
                    specializations JSON,
                    experience_years INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'service_tickets': """
                CREATE TABLE service_tickets (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    ticket_number VARCHAR(50) UNIQUE,
                    customer_name VARCHAR(100),
                    customer_phone VARCHAR(20),
                    customer_address TEXT,
                    product_name VARCHAR(100),
                    product_model VARCHAR(50),
                    issue_description TEXT,
                    status ENUM('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') DEFAULT 'SCHEDULED',
                    priority ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT') DEFAULT 'MEDIUM',
                    assigned_technician_id INT,
                    scheduled_date DATETIME,
                    completed_at DATETIME NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'notifications': """
                CREATE TABLE notifications (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    title VARCHAR(200),
                    message TEXT,
                    type VARCHAR(50),
                    is_read BOOLEAN DEFAULT FALSE,
                    ticket_id INT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'inventory': """
                CREATE TABLE inventory (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    part_number VARCHAR(50) UNIQUE,
                    name VARCHAR(100),
                    category VARCHAR(50),
                    quantity_available INT DEFAULT 0,
                    unit_cost DECIMAL(10,2),
                    location VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
        
        # Create missing tables
        for table_name, create_sql in required_tables.items():
            if table_name not in existing_tables:
                print(f"Creating table: {table_name}")
                cursor.execute(create_sql)
            else:
                print(f"PASS: Table {table_name} already exists")
        
        # Insert sample data
        print("Inserting sample data...")
        
        # Sample technicians
        cursor.execute("""
            INSERT IGNORE INTO technicians (employee_id, full_name, email, phone, specializations, experience_years) VALUES
            ('EMP001', 'John Technician', 'john.tech@ostrich.com', '9876543220', '["Motors", "Pumps"]', 5),
            ('EMP002', 'Jane Tech', 'jane.tech@ostrich.com', '9876543221', '["Generators", "Electrical"]', 3),
            ('EMP003', 'Bob Service', 'bob.tech@ostrich.com', '9876543222', '["Motors", "Generators"]', 7)
        """)
        
        # Sample tickets
        cursor.execute("""
            INSERT IGNORE INTO service_tickets (ticket_number, customer_name, customer_phone, customer_address, product_name, product_model, issue_description, status, priority, assigned_technician_id, scheduled_date) VALUES
            ('TKT000001', 'John Customer', '9876543210', '123 Main St, Mumbai', '3HP Motor', 'OST-3HP-SP', 'Motor not starting properly', 'SCHEDULED', 'HIGH', 1, '2025-01-15 09:00:00'),
            ('TKT000002', 'Jane Smith', '9876543211', '456 Service Ave, Delhi', '5HP Pump', 'OST-5HP-MP', 'Pump maintenance required', 'IN_PROGRESS', 'MEDIUM', 1, '2025-01-15 14:00:00'),
            ('TKT000003', 'Bob Wilson', '9876543212', '789 Repair Rd, Bangalore', '7HP Generator', 'OST-7HP-GN', 'Generator overheating issue', 'COMPLETED', 'HIGH', 2, '2025-01-14 11:00:00')
        """)
        
        # Sample notifications
        cursor.execute("""
            INSERT IGNORE INTO notifications (user_id, title, message, type, is_read, ticket_id) VALUES
            (1, 'New Ticket Assigned', 'Ticket TKT000004 has been assigned to you', 'assignment', FALSE, 4),
            (1, 'Urgent Ticket', 'High priority ticket TKT000005 needs immediate attention', 'urgent', FALSE, 5),
            (1, 'Schedule Update', 'Your schedule for tomorrow has been updated', 'schedule', TRUE, NULL)
        """)
        
        # Sample inventory
        cursor.execute("""
            INSERT IGNORE INTO inventory (part_number, name, category, quantity_available, unit_cost, location) VALUES
            ('BRG001', 'Motor Bearing', 'Bearings', 15, 250.0, 'Van Inventory'),
            ('WND001', 'Motor Winding', 'Electrical', 5, 1500.0, 'Warehouse'),
            ('FLT001', 'Oil Filter', 'Filters', 25, 75.0, 'Van Inventory'),
            ('BLT001', 'Drive Belt', 'Belts', 10, 125.0, 'Van Inventory')
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("PASS: Database setup completed successfully")
        return True
        
    except Exception as e:
        print(f"FAIL: Database setup failed: {e}")
        return False

if __name__ == "__main__":
    check_and_setup_tables()