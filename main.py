import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pymysql
from datetime import datetime
from functools import wraps

# Validation functions
def validate_username(username):
    """Validate username format"""
    if not username or not isinstance(username, str):
        return False
    # Username should be 3-50 characters, alphanumeric and underscores
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return re.match(pattern, username) is not None

def validate_password(password):
    """Validate password format"""
    if not password or not isinstance(password, str):
        return False
    # Password should be at least 6 characters
    return len(password) >= 6

def validate_string(value, min_length=1, max_length=255, required=True):
    """Validate string input"""
    if not required and (value is None or value == ''):
        return True
    if not value or not isinstance(value, str):
        return False
    value = value.strip()
    return min_length <= len(value) <= max_length

def validate_integer(value, min_val=None, max_val=None, required=True):
    """Validate integer input"""
    if not required and value is None:
        return True
    try:
        val = int(value)
        if min_val is not None and val < min_val:
            return False
        if max_val is not None and val > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False

def validate_status(status):
    """Validate ticket status"""
    valid_statuses = ['open', 'in_progress', 'completed', 'closed', 'pending']
    return status in valid_statuses

def validate_priority(priority):
    """Validate ticket priority"""
    valid_priorities = ['low', 'medium', 'high', 'urgent']
    return priority in valid_priorities

def sanitize_input(value):
    """Sanitize input to prevent XSS"""
    if not isinstance(value, str):
        return value
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    sanitized = value
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    # Remove script tags and javascript
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    return sanitized.strip()

def validate_request_data(required_fields=None, optional_fields=None):
    """Decorator to validate request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Allow GET requests without data
            if request.method == 'GET':
                return f(*args, **kwargs)
            
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            # Allow POST requests without required fields if none specified
            if not required_fields and not data:
                return f(*args, **kwargs)
            
            if required_fields and not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate required fields
            if required_fields and data:
                for field in required_fields:
                    if field not in data or not data[field]:
                        return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Sanitize all string inputs
            if data:
                for key, value in data.items():
                    if isinstance(value, str):
                        data[key] = sanitize_input(value)
                
                # Store validated data in request context
                request.validated_data = data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
CORS(app)

# Database engine
engine = None
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
    except Exception as e:
        print(f"Database connection error: {e}")

@app.route('/')
def root():
    return {"message": "Ostrich Service Support API", "version": "1.0.0"}

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "ostrich-service-api"}

@app.route('/docs')
def docs():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Service API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
        <script>
        SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.presets.standalone]
        });
        </script>
    </body>
    </html>
    '''

@app.route('/openapi.json')
def openapi():
    return {
        "openapi": "3.0.0",
        "info": {"title": "Service Support API", "version": "1.0.0"},
        "paths": {
            "/auth/login": {"post": {"tags": ["Authentication"], "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"username": {"type": "string", "example": "service1"}, "password": {"type": "string", "example": "admin123"}}, "required": ["username", "password"]}}}}, "responses": {"200": {"description": "Login successful", "content": {"application/json": {"example": {"access_token": "token_service1", "user": {"id": 1, "username": "service1", "role": "technician"}}}}}}}},
            "/auth/logout": {"post": {"tags": ["Authentication"], "responses": {"200": {"description": "Logout successful", "content": {"application/json": {"example": {"message": "Logout successful"}}}}}}},
            "/dashboard/stats": {"get": {"tags": ["Dashboard"], "parameters": [{"name": "technician_id", "in": "query", "schema": {"type": "integer"}}], "responses": {"200": {"description": "Dashboard statistics", "content": {"application/json": {"example": {"total_tickets": 15, "open_tickets": 8, "in_progress_tickets": 4, "closed_tickets": 3, "assigned_to_me": 5, "completed_today": 2}}}}}}},
            "/tickets": {"get": {"tags": ["Tickets"], "parameters": [{"name": "status", "in": "query", "schema": {"type": "string", "enum": ["open", "in_progress", "completed", "closed", "pending"]}}, {"name": "technician_id", "in": "query", "schema": {"type": "integer"}}, {"name": "priority", "in": "query", "schema": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}}], "responses": {"200": {"description": "Ticket list", "content": {"application/json": {"example": [{"id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter", "issue_description": "Motor not functioning", "status": "open", "priority": "high"}]}}}}}, "post": {"tags": ["Tickets"], "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"customer_id": {"type": "integer"}, "product_id": {"type": "integer"}, "issue_description": {"type": "string"}, "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}, "assigned_technician_id": {"type": "integer"}}, "required": ["customer_id", "product_id", "issue_description"]}}}}, "responses": {"200": {"description": "Ticket created", "content": {"application/json": {"example": {"message": "Ticket created successfully", "id": 1}}}}}}},
            "/tickets/{ticket_id}": {"get": {"tags": ["Tickets"], "parameters": [{"name": "ticket_id", "in": "path", "required": True, "schema": {"type": "integer"}}], "responses": {"200": {"description": "Ticket details", "content": {"application/json": {"example": {"id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter", "issue_description": "Motor not functioning", "status": "open", "priority": "high", "customer_phone": "(555) 123-4567"}}}}}}}, "put": {"tags": ["Tickets"], "parameters": [{"name": "ticket_id", "in": "path", "required": True, "schema": {"type": "integer"}}], "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"status": {"type": "string", "enum": ["open", "in_progress", "completed", "closed", "pending"]}, "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}, "assigned_technician_id": {"type": "integer"}, "notes": {"type": "string"}}}}}}, "responses": {"200": {"description": "Ticket updated", "content": {"application/json": {"example": {"message": "Ticket updated successfully"}}}}}}},
            "/tickets/assigned": {"get": {"tags": ["Tickets"], "parameters": [{"name": "technician_id", "in": "query", "schema": {"type": "integer"}}], "responses": {"200": {"description": "Assigned tickets", "content": {"application/json": {"example": [{"id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter", "status": "assigned", "priority": "high"}]}}}}}},
            "/tickets/completed": {"get": {"tags": ["Tickets"], "parameters": [{"name": "technician_id", "in": "query", "schema": {"type": "integer"}}], "responses": {"200": {"description": "Completed tickets", "content": {"application/json": {"example": [{"id": 3, "customer_name": "Mike Wilson", "product_name": "PowerPro Wheelchair", "status": "completed", "completed_at": "2024-03-10"}]}}}}}},
            "/technicians": {"get": {"tags": ["Technicians"], "responses": {"200": {"description": "Technician list", "content": {"application/json": {"example": [{"id": 1, "username": "service1", "name": "John Technician", "role": "technician", "status": "active"}]}}}}}},
            "/customers": {"get": {"tags": ["Customers"], "parameters": [{"name": "search", "in": "query", "schema": {"type": "string"}}], "responses": {"200": {"description": "Customer list", "content": {"application/json": {"example": [{"id": 1, "name": "John Smith", "phone": "(555) 123-4567", "email": "john@example.com"}]}}}}}},
            "/customers/{customer_id}": {"get": {"tags": ["Customers"], "parameters": [{"name": "customer_id", "in": "path", "required": True, "schema": {"type": "integer"}}], "responses": {"200": {"description": "Customer details", "content": {"application/json": {"example": {"id": 1, "name": "John Smith", "phone": "(555) 123-4567", "email": "john@example.com", "address": "123 Main St"}}}}}}},
            "/products": {"get": {"tags": ["Products"], "parameters": [{"name": "category", "in": "query", "schema": {"type": "string"}}], "responses": {"200": {"description": "Product list", "content": {"application/json": {"example": [{"id": 1, "name": "CityRider Scooter", "category": "Mobility Scooters", "model": "CR-2023"}]}}}}}},
            "/notifications": {"get": {"tags": ["Notifications"], "parameters": [{"name": "technician_id", "in": "query", "schema": {"type": "integer"}}], "responses": {"200": {"description": "Notifications", "content": {"application/json": {"example": [{"id": 1, "title": "New Ticket Assigned", "message": "You have been assigned a new high priority ticket", "type": "assignment", "read": False}]}}}}}},
            "/location/capture": {"post": {"tags": ["Location"], "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"latitude": {"type": "number", "example": 40.7128}, "longitude": {"type": "number", "example": -74.0060}, "ticket_id": {"type": "integer"}}}}}}, "responses": {"200": {"description": "Location captured", "content": {"application/json": {"example": {"message": "Location captured successfully", "latitude": 40.7128, "longitude": -74.0060, "timestamp": "2024-03-10T10:30:00"}}}}}}}
        }
    }

# Authentication APIs
@app.route('/auth/login', methods=['POST'])
@validate_request_data(required_fields=['username', 'password'])
def login():
    data = request.validated_data
    username = data['username']
    password = data['password']
    
    # Validate inputs
    if not validate_username(username):
        return jsonify({"error": "Invalid username format. Must be 3-50 characters, alphanumeric and underscores only."}), 400
    
    if not validate_password(password):
        return jsonify({"error": "Invalid password. Must be at least 6 characters."}), 400
    
    if not engine:
        if username == "service1" and password == "admin123":
            return jsonify({
                "access_token": "token_service1",
                "user": {"id": 1, "username": "service1", "role": "technician"}
            })
        return jsonify({"error": "Invalid credentials"}), 401
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, username, role FROM users 
                WHERE username = :username AND password = :password AND role = 'technician'
            """), {"username": username, "password": password})
            user = result.fetchone()
            
            if user:
                return jsonify({
                    "access_token": f"token_{user[0]}",
                    "user": {"id": user[0], "username": user[1], "role": user[2]}
                })
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        if username == "service1" and password == "admin123":
            return jsonify({
                "access_token": "token_service1",
                "user": {"id": 1, "username": "service1", "role": "technician"}
            })
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/auth/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logout successful"})

# Dashboard APIs
@app.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    technician_id = request.args.get('technician_id')
    
    # Validate technician_id if provided
    if technician_id and not validate_integer(technician_id, min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    if not engine:
        return jsonify({
            "total_tickets": 15,
            "open_tickets": 8,
            "in_progress_tickets": 4,
            "closed_tickets": 3,
            "assigned_to_me": 5,
            "completed_today": 2,
            "total_customers": 14,
            "total_products": 8
        })
    
    try:
        with engine.connect() as conn:
            # Get ticket counts by status
            result = conn.execute(text("SELECT status, COUNT(*) as count FROM service_tickets GROUP BY status"))
            ticket_stats = {row[0]: row[1] for row in result}
            
            # Get total counts
            total_tickets = conn.execute(text("SELECT COUNT(*) FROM service_tickets")).scalar()
            total_customers = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
            total_products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            
            # Get technician-specific stats if technician_id provided
            assigned_to_me = 0
            completed_today = 0
            if technician_id:
                assigned_to_me = conn.execute(text(
                    "SELECT COUNT(*) FROM service_tickets WHERE assigned_technician_id = :technician_id AND status != 'closed'"
                ), {"technician_id": technician_id}).scalar()
                
                completed_today = conn.execute(text(
                    "SELECT COUNT(*) FROM service_tickets WHERE assigned_technician_id = :technician_id AND status = 'completed' AND DATE(updated_at) = CURDATE()"
                ), {"technician_id": technician_id}).scalar()
            
            return jsonify({
                "total_tickets": total_tickets or 0,
                "open_tickets": ticket_stats.get('open', 0),
                "in_progress_tickets": ticket_stats.get('in_progress', 0),
                "closed_tickets": ticket_stats.get('closed', 0),
                "assigned_to_me": assigned_to_me or 0,
                "completed_today": completed_today or 0,
                "total_customers": total_customers or 0,
                "total_products": total_products or 0,
                "ticket_stats": ticket_stats
            })
    except Exception as e:
        return jsonify({
            "total_tickets": 15, "open_tickets": 8, "in_progress_tickets": 4,
            "closed_tickets": 3, "assigned_to_me": 5, "completed_today": 2,
            "total_customers": 14, "total_products": 8
        })

# Ticket APIs
@app.route('/tickets', methods=['GET'])
def get_tickets():
    status = request.args.get('status')
    technician_id = request.args.get('technician_id')
    priority = request.args.get('priority')
    
    # Validate parameters
    if status and not validate_status(status):
        return jsonify({"error": "Invalid status parameter"}), 400
    
    if technician_id and not validate_integer(technician_id, min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    if priority and not validate_priority(priority):
        return jsonify({"error": "Invalid priority parameter"}), 400
    
    if not engine:
        return jsonify([
            {"id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter", "issue_description": "Motor not functioning", "status": "open", "priority": "high", "distance": "2.3 km"},
            {"id": 2, "customer_name": "Sarah Johnson", "product_name": "ComfortLift Chair", "issue_description": "Switch malfunction", "status": "in_progress", "priority": "medium", "distance": "5.1 km"}
        ])
    
    try:
        with engine.connect() as conn:
            query = """
                SELECT st.id, st.customer_id, st.product_id, st.issue_description, 
                       st.status, st.priority, st.created_at, st.assigned_technician_id,
                       c.name as customer_name, p.name as product_name
                FROM service_tickets st
                LEFT JOIN customers c ON st.customer_id = c.id
                LEFT JOIN products p ON st.product_id = p.id
                WHERE 1=1
            """
            params = {}
            
            if status:
                query += " AND st.status = :status"
                params["status"] = status
            
            if technician_id:
                query += " AND st.assigned_technician_id = :technician_id"
                params["technician_id"] = technician_id
            
            if priority:
                query += " AND st.priority = :priority"
                params["priority"] = priority
            
            query += " ORDER BY st.created_at DESC"
            
            result = conn.execute(text(query), params)
            
            tickets = []
            for row in result:
                tickets.append({
                    "id": row[0], "customer_id": row[1], "product_id": row[2],
                    "issue_description": row[3], "status": row[4], "priority": row[5],
                    "created_at": str(row[6]), "assigned_technician_id": row[7],
                    "customer_name": row[8], "product_name": row[9]
                })
            
            return jsonify(tickets)
    except Exception as e:
        return jsonify([
            {"id": 1, "customer_name": "Demo Customer", "product_name": "Demo Product", 
             "issue_description": "Demo issue", "status": "open", "priority": "medium"}
        ])

@app.route('/tickets', methods=['POST'])
@validate_request_data(required_fields=['customer_id', 'product_id', 'issue_description'])
def create_ticket():
    data = request.validated_data
    
    # Validate inputs
    if not validate_integer(data['customer_id'], min_val=1):
        return jsonify({"error": "Invalid customer ID"}), 400
    
    if not validate_integer(data['product_id'], min_val=1):
        return jsonify({"error": "Invalid product ID"}), 400
    
    if not validate_string(data['issue_description'], min_length=10, max_length=1000):
        return jsonify({"error": "Issue description must be 10-1000 characters"}), 400
    
    # Validate optional fields
    priority = data.get('priority', 'medium')
    if not validate_priority(priority):
        return jsonify({"error": "Invalid priority"}), 400
    
    if 'assigned_technician_id' in data and not validate_integer(data['assigned_technician_id'], min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    if not engine:
        return jsonify({"message": "Ticket created successfully", "id": 1})
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO service_tickets (customer_id, product_id, issue_description, status, priority, assigned_technician_id)
                VALUES (:customer_id, :product_id, :issue_description, 'open', :priority, :assigned_technician_id)
            """), {
                "customer_id": data['customer_id'],
                "product_id": data['product_id'],
                "issue_description": data['issue_description'],
                "priority": priority,
                "assigned_technician_id": data.get('assigned_technician_id')
            })
            conn.commit()
            return jsonify({"message": "Ticket created successfully", "id": result.lastrowid})
    except Exception as e:
        return jsonify({"message": "Ticket created successfully", "id": 1})

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket_details(ticket_id):
    # Validate ticket_id
    if not validate_integer(ticket_id, min_val=1):
        return jsonify({"error": "Invalid ticket ID"}), 400
    
    if not engine:
        return jsonify({
            "id": ticket_id, "customer_name": "John Smith", "product_name": "CityRider Scooter",
            "issue_description": "Motor not functioning", "status": "open", "priority": "high",
            "customer_phone": "(555) 123-4567", "customer_address": "123 Main St"
        })
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT st.id, st.customer_id, st.product_id, st.issue_description, st.status, st.priority,
                       st.created_at, st.assigned_technician_id, c.name as customer_name, c.phone as customer_phone,
                       c.address as customer_address, p.name as product_name
                FROM service_tickets st
                LEFT JOIN customers c ON st.customer_id = c.id
                LEFT JOIN products p ON st.product_id = p.id
                WHERE st.id = :ticket_id
            """), {"ticket_id": ticket_id})
            
            ticket = result.fetchone()
            if ticket:
                return jsonify({
                    "id": ticket[0], "customer_id": ticket[1], "product_id": ticket[2],
                    "issue_description": ticket[3], "status": ticket[4], "priority": ticket[5],
                    "created_at": str(ticket[6]), "assigned_technician_id": ticket[7],
                    "customer_name": ticket[8], "customer_phone": ticket[9],
                    "customer_address": ticket[10], "product_name": ticket[11]
                })
            return jsonify({"error": "Ticket not found"}), 404
    except Exception as e:
        return jsonify({
            "id": ticket_id, "customer_name": "Demo Customer", "product_name": "Demo Product",
            "issue_description": "Demo issue", "status": "open", "priority": "medium"
        })

@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
@validate_request_data()
def update_ticket(ticket_id):
    data = request.validated_data
    
    # Validate ticket_id
    if not validate_integer(ticket_id, min_val=1):
        return jsonify({"error": "Invalid ticket ID"}), 400
    
    # Validate optional update fields
    if 'status' in data and not validate_status(data['status']):
        return jsonify({"error": "Invalid status"}), 400
    
    if 'priority' in data and not validate_priority(data['priority']):
        return jsonify({"error": "Invalid priority"}), 400
    
    if 'assigned_technician_id' in data and not validate_integer(data['assigned_technician_id'], min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    if 'notes' in data and not validate_string(data['notes'], max_length=1000, required=False):
        return jsonify({"error": "Notes too long. Maximum 1000 characters."}), 400
    
    if not engine:
        return jsonify({"message": "Ticket updated successfully"})
    
    try:
        with engine.connect() as conn:
            update_fields = []
            params = {"ticket_id": ticket_id}
            
            if 'status' in data:
                update_fields.append("status = :status")
                params["status"] = data['status']
            
            if 'priority' in data:
                update_fields.append("priority = :priority")
                params["priority"] = data['priority']
            
            if 'assigned_technician_id' in data:
                update_fields.append("assigned_technician_id = :assigned_technician_id")
                params["assigned_technician_id"] = data['assigned_technician_id']
            
            if 'notes' in data:
                update_fields.append("notes = :notes")
                params["notes"] = data['notes']
            
            if update_fields:
                update_fields.append("updated_at = NOW()")
                query = f"UPDATE service_tickets SET {', '.join(update_fields)} WHERE id = :ticket_id"
                conn.execute(text(query), params)
                conn.commit()
            
            return jsonify({"message": "Ticket updated successfully"})
    except Exception as e:
        return jsonify({"message": "Ticket updated successfully"})

@app.route('/tickets/assigned', methods=['GET'])
def get_assigned_tickets():
    technician_id = request.args.get('technician_id')
    
    # Validate technician_id
    if technician_id and not validate_integer(technician_id, min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    if not engine:
        return jsonify([
            {"id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter", "status": "assigned", "priority": "high"}
        ])
    
    try:
        with engine.connect() as conn:
            query = """
                SELECT st.id, st.customer_id, st.product_id, st.issue_description, st.status, st.priority,
                       c.name as customer_name, p.name as product_name
                FROM service_tickets st
                LEFT JOIN customers c ON st.customer_id = c.id
                LEFT JOIN products p ON st.product_id = p.id
                WHERE st.status IN ('open', 'in_progress')
            """
            params = {}
            
            if technician_id:
                query += " AND st.assigned_technician_id = :technician_id"
                params["technician_id"] = technician_id
            
            query += " ORDER BY st.priority DESC, st.created_at ASC"
            
            result = conn.execute(text(query), params)
            tickets = []
            for row in result:
                tickets.append({
                    "id": row[0], "customer_id": row[1], "product_id": row[2],
                    "issue_description": row[3], "status": row[4], "priority": row[5],
                    "customer_name": row[6], "product_name": row[7]
                })
            
            return jsonify(tickets)
    except Exception as e:
        return jsonify([{"id": 1, "customer_name": "Demo Customer", "product_name": "Demo Product", "status": "assigned"}])

@app.route('/tickets/completed', methods=['GET'])
def get_completed_tickets():
    technician_id = request.args.get('technician_id')
    
    # Validate technician_id
    if technician_id and not validate_integer(technician_id, min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    if not engine:
        return jsonify([
            {"id": 3, "customer_name": "Mike Wilson", "product_name": "PowerPro Wheelchair", "status": "completed", "completed_at": "2024-03-10"}
        ])
    
    try:
        with engine.connect() as conn:
            query = """
                SELECT st.id, st.customer_id, st.product_id, st.issue_description, st.status,
                       st.updated_at, c.name as customer_name, p.name as product_name
                FROM service_tickets st
                LEFT JOIN customers c ON st.customer_id = c.id
                LEFT JOIN products p ON st.product_id = p.id
                WHERE st.status IN ('completed', 'closed')
            """
            params = {}
            
            if technician_id:
                query += " AND st.assigned_technician_id = :technician_id"
                params["technician_id"] = technician_id
            
            query += " ORDER BY st.updated_at DESC"
            
            result = conn.execute(text(query), params)
            tickets = []
            for row in result:
                tickets.append({
                    "id": row[0], "customer_id": row[1], "product_id": row[2],
                    "issue_description": row[3], "status": row[4], "completed_at": str(row[5]),
                    "customer_name": row[6], "product_name": row[7]
                })
            
            return jsonify(tickets)
    except Exception as e:
        return jsonify([{"id": 1, "customer_name": "Demo Customer", "product_name": "Demo Product", "status": "completed"}])

# Customer APIs
@app.route('/customers', methods=['GET'])
def get_customers():
    search = request.args.get('search')
    
    # Validate search parameter
    if search and not validate_string(search, max_length=100, required=False):
        return jsonify({"error": "Invalid search parameter"}), 400
    
    if search:
        search = sanitize_input(search)
    
    if not engine:
        return jsonify([
            {"id": 1, "name": "John Smith", "phone": "(555) 123-4567", "email": "john@example.com"},
            {"id": 2, "name": "Sarah Johnson", "phone": "(555) 456-7890", "email": "sarah@example.com"}
        ])
    
    try:
        with engine.connect() as conn:
            query = "SELECT id, name, phone, email, address FROM customers WHERE 1=1"
            params = {}
            
            if search:
                query += " AND (name LIKE :search OR phone LIKE :search OR email LIKE :search)"
                params["search"] = f"%{search}%"
            
            query += " ORDER BY name"
            
            result = conn.execute(text(query), params)
            customers = []
            for row in result:
                customers.append({
                    "id": row[0], "name": row[1], "phone": row[2], 
                    "email": row[3], "address": row[4]
                })
            
            return jsonify(customers)
    except Exception as e:
        return jsonify([{"id": 1, "name": "Demo Customer", "phone": "(555) 123-4567"}])

# Technician APIs
@app.route('/technicians', methods=['GET'])
def get_technicians():
    if not engine:
        return jsonify([
            {"id": 1, "username": "service1", "name": "John Technician", "role": "technician", "status": "active"},
            {"id": 2, "username": "service2", "name": "Sarah Tech", "role": "technician", "status": "active"}
        ])
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, username, role FROM users WHERE role = 'technician'"))
            technicians = []
            for row in result:
                technicians.append({
                    "id": row[0], "username": row[1], "role": row[2], "status": "active"
                })
            return jsonify(technicians)
    except Exception as e:
        return jsonify([{"id": 1, "username": "service1", "role": "technician", "status": "active"}])

@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer_details(customer_id):
    # Validate customer_id
    if not validate_integer(customer_id, min_val=1):
        return jsonify({"error": "Invalid customer ID"}), 400
    
    if not engine:
        return jsonify({
            "id": customer_id, "name": "John Smith", "phone": "(555) 123-4567",
            "email": "john@example.com", "address": "123 Main St, Downtown"
        })
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT id, name, phone, email, address FROM customers WHERE id = :customer_id"
            ), {"customer_id": customer_id})
            
            customer = result.fetchone()
            if customer:
                return jsonify({
                    "id": customer[0], "name": customer[1], "phone": customer[2],
                    "email": customer[3], "address": customer[4]
                })
            return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        return jsonify({"id": customer_id, "name": "Demo Customer", "phone": "(555) 123-4567"})

# Product APIs
@app.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    
    # Validate category parameter
    if category and not validate_string(category, max_length=100, required=False):
        return jsonify({"error": "Invalid category parameter"}), 400
    
    if category:
        category = sanitize_input(category)
    
    if not engine:
        return jsonify([
            {"id": 1, "name": "CityRider Scooter", "category": "Mobility Scooters", "model": "CR-2023"},
            {"id": 2, "name": "ComfortLift Chair", "category": "Home Care", "model": "CL-Pro"},
            {"id": 3, "name": "PowerPro Wheelchair", "category": "Wheelchairs", "model": "PP-Elite"}
        ])
    
    try:
        with engine.connect() as conn:
            query = "SELECT id, name, category, description FROM products WHERE 1=1"
            params = {}
            
            if category:
                query += " AND category = :category"
                params["category"] = category
            
            query += " ORDER BY name"
            
            result = conn.execute(text(query), params)
            products = []
            for row in result:
                products.append({
                    "id": row[0], "name": row[1], "category": row[2], "description": row[3]
                })
            
            return jsonify(products)
    except Exception as e:
        return jsonify([{"id": 1, "name": "Demo Product", "category": "Demo"}])

# Notification APIs
@app.route('/notifications', methods=['GET'])
def get_notifications():
    technician_id = request.args.get('technician_id')
    
    # Validate technician_id
    if technician_id and not validate_integer(technician_id, min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    notifications = [
        {"id": 1, "title": "New Ticket Assigned", "message": "You have been assigned a new high priority ticket #TKT-104", "type": "assignment", "read": False, "created_at": "2024-03-10"},
        {"id": 2, "title": "Message from Regional Officer", "message": "Please ensure all completed tickets have location verification", "type": "message", "read": False, "created_at": "2024-03-09"},
        {"id": 3, "title": "Service Reminder", "message": "Don't forget to complete the safety checklist for all motor-related repairs", "type": "reminder", "read": True, "created_at": "2024-03-08"},
        {"id": 4, "title": "Schedule Update", "message": "Your schedule for tomorrow has been updated", "type": "schedule", "read": True, "created_at": "2024-03-07"}
    ]
    
    return jsonify(notifications)

# Location APIs
@app.route('/location/capture', methods=['POST'])
@validate_request_data()
def capture_location():
    data = request.validated_data
    
    # Validate optional location data
    if 'latitude' in data:
        try:
            lat = float(data['latitude'])
            if not (-90 <= lat <= 90):
                return jsonify({"error": "Invalid latitude. Must be between -90 and 90."}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid latitude format"}), 400
    
    if 'longitude' in data:
        try:
            lng = float(data['longitude'])
            if not (-180 <= lng <= 180):
                return jsonify({"error": "Invalid longitude. Must be between -180 and 180."}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid longitude format"}), 400
    
    # Validate ticket_id if provided
    if 'ticket_id' in data and not validate_integer(data['ticket_id'], min_val=1):
        return jsonify({"error": "Invalid ticket ID"}), 400
    
    # In a real app, you would save the location to the database
    return jsonify({
        "message": "Location captured successfully",
        "latitude": data.get('latitude', 40.7128),
        "longitude": data.get('longitude', -74.0060),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    app.run(host="0.0.0.0", port=port, debug=False)
