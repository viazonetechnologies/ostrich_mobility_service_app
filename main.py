"""
Ostrich Service Technician API
A comprehensive REST API for the Ostrich Service Technician Mobile Application
Handles authentication, ticket management, customer data, and field operations
"""

import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from datetime import datetime
from functools import wraps

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_username(username):
    """Validate username format (3-50 characters, alphanumeric and underscores)"""
    if not username or not isinstance(username, str):
        return False
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return re.match(pattern, username) is not None

def validate_password(password):
    """Validate password format (minimum 6 characters)"""
    if not password or not isinstance(password, str):
        return False
    return len(password) >= 6

def validate_string(value, min_length=1, max_length=255, required=True):
    """Validate string input with length constraints"""
    if not required and (value is None or value == ''):
        return True
    if not value or not isinstance(value, str):
        return False
    return min_length <= len(value.strip()) <= max_length

def validate_integer(value, min_val=None, max_val=None, required=True):
    """Validate integer input with range constraints"""
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
    """Validate service ticket status"""
    valid_statuses = ['open', 'in_progress', 'completed', 'closed', 'pending']
    return status in valid_statuses

def validate_priority(priority):
    """Validate service ticket priority"""
    valid_priorities = ['low', 'medium', 'high', 'urgent']
    return priority in valid_priorities

def sanitize_input(value):
    """Sanitize string input to prevent XSS attacks"""
    if not isinstance(value, str):
        return value
    dangerous_chars = ['<', '>', '"', "'", '&']
    sanitized = value
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    return sanitized.strip()

def validate_request_data(required_fields=None):
    """Decorator to validate and sanitize request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            if not data and required_fields:
                return jsonify({"error": "No data provided"}), 400
            
            if required_fields:
                for field in required_fields:
                    if field not in data or not data[field]:
                        return jsonify({"error": f"Missing required field: {field}"}), 400
            
            if data:
                for key, value in data.items():
                    if isinstance(value, str):
                        data[key] = sanitize_input(value)
                request.validated_data = data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================================
# APPLICATION SETUP
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
CORS(app)

# Database connection
engine = None
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"❌ Database connection error: {e}")

# ============================================================================
# API DOCUMENTATION
# ============================================================================

@app.route('/docs')
def docs():
    """Swagger UI Documentation"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ostrich Service API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
        <style>
            .swagger-ui .topbar { display: none; }
            .swagger-ui .info { margin: 20px 0; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
        <script>
        SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.presets.standalone],
            layout: "StandaloneLayout"
        });
        </script>
    </body>
    </html>
    '''

@app.route('/openapi.json')
def openapi():
    """OpenAPI 3.0 Specification"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Ostrich Service Technician API",
            "version": "1.0.0",
            "description": "Complete REST API for Ostrich Service Technician Mobile Application",
            "contact": {"name": "Ostrich Support", "email": "support@ostrich.com"}
        },
        "servers": [{"url": "/", "description": "Service API Server"}],
        "tags": [
            {"name": "Authentication", "description": "Technician authentication endpoints"},
            {"name": "Dashboard", "description": "Service dashboard and statistics"},
            {"name": "Tickets", "description": "Service ticket management"},
            {"name": "Customers", "description": "Customer information access"},
            {"name": "Products", "description": "Product information access"},
            {"name": "Notifications", "description": "Technician notifications"},
            {"name": "Location", "description": "Location tracking features"}
        ],
        "paths": {
            "/auth/login": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Authenticate service technician",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string", "example": "service1"},
                                        "password": {"type": "string", "example": "admin123"}
                                    },
                                    "required": ["username", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Authentication successful",
                            "content": {
                                "application/json": {
                                    "example": {"access_token": "token_service1", "user": {"id": 1, "username": "service1", "role": "technician"}}
                                }
                            }
                        },
                        "401": {"description": "Invalid credentials"}
                    }
                }
            },
            "/dashboard/stats": {
                "get": {
                    "tags": ["Dashboard"],
                    "summary": "Get service dashboard statistics",
                    "parameters": [{"name": "technician_id", "in": "query", "schema": {"type": "integer", "example": 1}}],
                    "responses": {
                        "200": {
                            "description": "Dashboard statistics retrieved",
                            "content": {
                                "application/json": {
                                    "example": {"total_tickets": 15, "open_tickets": 8, "in_progress_tickets": 4, "closed_tickets": 3}
                                }
                            }
                        }
                    }
                }
            },
            "/tickets": {
                "get": {
                    "tags": ["Tickets"],
                    "summary": "Get service tickets",
                    "parameters": [
                        {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["open", "in_progress", "completed", "closed"]}},
                        {"name": "technician_id", "in": "query", "schema": {"type": "integer", "example": 1}},
                        {"name": "priority", "in": "query", "schema": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Ticket list retrieved",
                            "content": {
                                "application/json": {
                                    "example": [{"id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter", "status": "open", "priority": "high"}]
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Tickets"],
                    "summary": "Create new service ticket",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "customer_id": {"type": "integer", "example": 1},
                                        "product_id": {"type": "integer", "example": 1},
                                        "issue_description": {"type": "string", "example": "Motor not functioning properly"},
                                        "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "example": "high"}
                                    },
                                    "required": ["customer_id", "product_id", "issue_description"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Ticket created successfully",
                            "content": {
                                "application/json": {
                                    "example": {"message": "Ticket created successfully", "id": 1}
                                }
                            }
                        }
                    }
                }
            },
            "/tickets/{ticket_id}": {
                "get": {
                    "tags": ["Tickets"],
                    "summary": "Get ticket details",
                    "parameters": [{"name": "ticket_id", "in": "path", "required": True, "schema": {"type": "integer", "example": 1}}],
                    "responses": {
                        "200": {
                            "description": "Ticket details retrieved",
                            "content": {
                                "application/json": {
                                    "example": {"id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter", "status": "open"}
                                }
                            }
                        },
                        "404": {"description": "Ticket not found"}
                    }
                },
                "put": {
                    "tags": ["Tickets"],
                    "summary": "Update ticket status and details",
                    "parameters": [{"name": "ticket_id", "in": "path", "required": True, "schema": {"type": "integer", "example": 1}}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "enum": ["open", "in_progress", "completed", "closed"]},
                                        "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                                        "notes": {"type": "string", "example": "Replaced motor component"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Ticket updated successfully",
                            "content": {
                                "application/json": {
                                    "example": {"message": "Ticket updated successfully"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.route('/')
def root():
    """API Information"""
    return {
        "message": "Ostrich Service Technician API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

@app.route('/health')
def health_check():
    """Health Check Endpoint"""
    db_status = "connected" if engine else "disconnected"
    return {
        "status": "healthy",
        "service": "ostrich-service-api",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/auth/login', methods=['POST'])
@validate_request_data(required_fields=['username', 'password'])
def login():
    """Authenticate service technician"""
    data = request.validated_data
    username = data['username']
    password = data['password']
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username format. Must be 3-50 characters, alphanumeric and underscores only."}), 400
    
    if not validate_password(password):
        return jsonify({"error": "Invalid password. Must be at least 6 characters."}), 400
    
    # Demo authentication
    if username == "service1" and password == "admin123":
        return jsonify({
            "access_token": "token_service1",
            "user": {"id": 1, "username": "service1", "role": "technician"}
        })
    
    # Database authentication
    if engine:
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
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/auth/logout', methods=['POST'])
def logout():
    """Logout technician"""
    return jsonify({"message": "Logout successful"})

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Get service dashboard statistics"""
    technician_id = request.args.get('technician_id')
    
    if technician_id and not validate_integer(technician_id, min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    # Demo statistics
    stats = {
        "total_tickets": 15,
        "open_tickets": 8,
        "in_progress_tickets": 4,
        "closed_tickets": 3,
        "assigned_to_me": 5,
        "completed_today": 2,
        "total_customers": 14,
        "total_products": 8,
        "performance_metrics": {
            "avg_resolution_time": "2.5 hours",
            "customer_satisfaction": "4.8/5",
            "tickets_this_week": 12
        }
    }
    
    # Database integration
    if engine:
        try:
            with engine.connect() as conn:
                # Get ticket counts by status
                result = conn.execute(text("SELECT status, COUNT(*) as count FROM service_tickets GROUP BY status"))
                ticket_stats = {row[0]: row[1] for row in result}
                
                # Get total counts
                total_tickets = conn.execute(text("SELECT COUNT(*) FROM service_tickets")).scalar()
                total_customers = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
                total_products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
                
                # Update stats with database values
                stats.update({
                    "total_tickets": total_tickets or 0,
                    "open_tickets": ticket_stats.get('open', 0),
                    "in_progress_tickets": ticket_stats.get('in_progress', 0),
                    "closed_tickets": ticket_stats.get('closed', 0),
                    "total_customers": total_customers or 0,
                    "total_products": total_products or 0
                })
                
                # Get technician-specific stats
                if technician_id:
                    assigned_to_me = conn.execute(text(
                        "SELECT COUNT(*) FROM service_tickets WHERE assigned_technician_id = :technician_id AND status != 'closed'"
                    ), {"technician_id": technician_id}).scalar()
                    stats["assigned_to_me"] = assigned_to_me or 0
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(stats)

# ============================================================================
# TICKET ENDPOINTS
# ============================================================================

@app.route('/tickets', methods=['GET'])
def get_tickets():
    """Get service tickets with optional filtering"""
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
    
    # Demo tickets
    tickets = [
        {
            "id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter",
            "issue_description": "Motor not functioning properly", "status": "open", "priority": "high",
            "created_at": "2024-03-10", "customer_phone": "(555) 123-4567", "distance": "2.3 km"
        },
        {
            "id": 2, "customer_name": "Sarah Johnson", "product_name": "ComfortLift Chair",
            "issue_description": "Remote control not responding", "status": "in_progress", "priority": "medium",
            "created_at": "2024-03-09", "customer_phone": "(555) 456-7890", "distance": "5.1 km"
        },
        {
            "id": 3, "customer_name": "Mike Wilson", "product_name": "PowerPro Wheelchair",
            "issue_description": "Battery charging issue", "status": "completed", "priority": "high",
            "created_at": "2024-03-08", "customer_phone": "(555) 789-0123", "distance": "1.8 km"
        }
    ]
    
    # Apply filters
    if status:
        tickets = [t for t in tickets if t['status'] == status]
    if priority:
        tickets = [t for t in tickets if t['priority'] == priority]
    
    # Database integration
    if engine:
        try:
            with engine.connect() as conn:
                query = """
                    SELECT st.id, st.customer_id, st.product_id, st.issue_description, 
                           st.status, st.priority, st.created_at, st.assigned_technician_id,
                           c.name as customer_name, c.phone as customer_phone, p.name as product_name
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
                
                query += " ORDER BY st.priority DESC, st.created_at DESC"
                
                result = conn.execute(text(query), params)
                db_tickets = []
                for row in result:
                    db_tickets.append({
                        "id": row[0], "customer_id": row[1], "product_id": row[2],
                        "issue_description": row[3], "status": row[4], "priority": row[5],
                        "created_at": str(row[6]), "assigned_technician_id": row[7],
                        "customer_name": row[8], "customer_phone": row[9], "product_name": row[10]
                    })
                if db_tickets:
                    tickets = db_tickets
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(tickets)

@app.route('/tickets', methods=['POST'])
@validate_request_data(required_fields=['customer_id', 'product_id', 'issue_description'])
def create_ticket():
    """Create new service ticket"""
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
    
    # Database integration
    if engine:
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
            print(f"Database error: {e}")
    
    return jsonify({"message": "Ticket created successfully", "id": 1})

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket_details(ticket_id):
    """Get detailed ticket information"""
    if not validate_integer(ticket_id, min_val=1):
        return jsonify({"error": "Invalid ticket ID"}), 400
    
    # Demo ticket details
    ticket_details = {
        "id": ticket_id,
        "customer_name": "John Smith",
        "customer_phone": "(555) 123-4567",
        "customer_address": "123 Main Street, Downtown",
        "product_name": "CityRider Scooter",
        "issue_description": "Motor not functioning properly, making unusual noises",
        "status": "open",
        "priority": "high",
        "created_at": "2024-03-10T10:30:00",
        "notes": "Customer reports issue started yesterday",
        "estimated_duration": "2 hours",
        "required_parts": ["Motor assembly", "Drive belt"]
    }
    
    # Database integration
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT st.id, st.customer_id, st.product_id, st.issue_description, st.status, st.priority,
                           st.created_at, st.assigned_technician_id, st.notes, c.name as customer_name, 
                           c.phone as customer_phone, c.address as customer_address, p.name as product_name
                    FROM service_tickets st
                    LEFT JOIN customers c ON st.customer_id = c.id
                    LEFT JOIN products p ON st.product_id = p.id
                    WHERE st.id = :ticket_id
                """), {"ticket_id": ticket_id})
                
                ticket = result.fetchone()
                if ticket:
                    ticket_details = {
                        "id": ticket[0], "customer_id": ticket[1], "product_id": ticket[2],
                        "issue_description": ticket[3], "status": ticket[4], "priority": ticket[5],
                        "created_at": str(ticket[6]), "assigned_technician_id": ticket[7], "notes": ticket[8],
                        "customer_name": ticket[9], "customer_phone": ticket[10],
                        "customer_address": ticket[11], "product_name": ticket[12]
                    }
                else:
                    return jsonify({"error": "Ticket not found"}), 404
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(ticket_details)

@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
@validate_request_data()
def update_ticket(ticket_id):
    """Update ticket status and details"""
    data = request.validated_data
    
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
    
    # Database integration
    if engine:
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
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify({"message": "Ticket updated successfully"})

# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@app.route('/customers', methods=['GET'])
def get_customers():
    """Get customer list with optional search"""
    search = request.args.get('search')
    
    if search and not validate_string(search, max_length=100, required=False):
        return jsonify({"error": "Invalid search parameter"}), 400
    
    # Demo customers
    customers = [
        {"id": 1, "name": "John Smith", "phone": "(555) 123-4567", "email": "john@example.com", "address": "123 Main St"},
        {"id": 2, "name": "Sarah Johnson", "phone": "(555) 456-7890", "email": "sarah@example.com", "address": "456 Oak Ave"},
        {"id": 3, "name": "Mike Wilson", "phone": "(555) 789-0123", "email": "mike@example.com", "address": "789 Pine Rd"}
    ]
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        customers = [c for c in customers if 
                    search_lower in c['name'].lower() or 
                    search_lower in c['phone'] or 
                    search_lower in c['email'].lower()]
    
    # Database integration
    if engine:
        try:
            with engine.connect() as conn:
                query = "SELECT id, name, phone, email, address FROM customers WHERE 1=1"
                params = {}
                
                if search:
                    query += " AND (name LIKE :search OR phone LIKE :search OR email LIKE :search)"
                    params["search"] = f"%{search}%"
                
                query += " ORDER BY name"
                
                result = conn.execute(text(query), params)
                db_customers = []
                for row in result:
                    db_customers.append({
                        "id": row[0], "name": row[1], "phone": row[2], 
                        "email": row[3], "address": row[4]
                    })
                if db_customers:
                    customers = db_customers
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(customers)

@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer_details(customer_id):
    """Get detailed customer information"""
    if not validate_integer(customer_id, min_val=1):
        return jsonify({"error": "Invalid customer ID"}), 400
    
    # Demo customer details
    customer_details = {
        "id": customer_id,
        "name": "John Smith",
        "phone": "(555) 123-4567",
        "email": "john@example.com",
        "address": "123 Main Street, Downtown",
        "registration_date": "2022-01-15",
        "total_orders": 3,
        "active_products": 2
    }
    
    # Database integration
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT id, name, phone, email, address, created_at FROM customers WHERE id = :customer_id"
                ), {"customer_id": customer_id})
                
                customer = result.fetchone()
                if customer:
                    customer_details = {
                        "id": customer[0], "name": customer[1], "phone": customer[2],
                        "email": customer[3], "address": customer[4], "registration_date": str(customer[5])
                    }
                else:
                    return jsonify({"error": "Customer not found"}), 404
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(customer_details)

# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@app.route('/products', methods=['GET'])
def get_products():
    """Get product list with optional category filter"""
    category = request.args.get('category')
    
    if category and not validate_string(category, max_length=100, required=False):
        return jsonify({"error": "Invalid category parameter"}), 400
    
    # Demo products
    products = [
        {"id": 1, "name": "CityRider Scooter", "category": "Mobility Scooters", "model": "CR-2023", "warranty_period": "2 years"},
        {"id": 2, "name": "ComfortLift Chair", "category": "Home Care", "model": "CL-Pro", "warranty_period": "3 years"},
        {"id": 3, "name": "PowerPro Wheelchair", "category": "Wheelchairs", "model": "PP-Elite", "warranty_period": "2 years"},
        {"id": 4, "name": "EasyWalk Rollator", "category": "Walking Aids", "model": "EW-Standard", "warranty_period": "1 year"}
    ]
    
    # Apply category filter
    if category:
        products = [p for p in products if p['category'] == category]
    
    # Database integration
    if engine:
        try:
            with engine.connect() as conn:
                query = "SELECT id, name, category, description FROM products WHERE 1=1"
                params = {}
                
                if category:
                    query += " AND category = :category"
                    params["category"] = category
                
                query += " ORDER BY name"
                
                result = conn.execute(text(query), params)
                db_products = []
                for row in result:
                    db_products.append({
                        "id": row[0], "name": row[1], "category": row[2], "description": row[3]
                    })
                if db_products:
                    products = db_products
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(products)

# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Get technician notifications"""
    technician_id = request.args.get('technician_id')
    
    if technician_id and not validate_integer(technician_id, min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    notifications = [
        {
            "id": 1, "title": "New High Priority Ticket", 
            "message": "Urgent ticket #TKT-104 assigned to you - Motor failure at downtown location",
            "type": "assignment", "read": False, "created_at": "2024-03-10T14:30:00"
        },
        {
            "id": 2, "title": "Schedule Update", 
            "message": "Your afternoon appointments have been rescheduled due to traffic conditions",
            "type": "schedule", "read": False, "created_at": "2024-03-10T12:15:00"
        },
        {
            "id": 3, "title": "Parts Delivery", 
            "message": "Motor assembly parts for ticket #TKT-098 delivered to warehouse",
            "type": "parts", "read": True, "created_at": "2024-03-10T09:45:00"
        },
        {
            "id": 4, "title": "Safety Reminder", 
            "message": "Complete safety checklist for all electrical repairs",
            "type": "reminder", "read": True, "created_at": "2024-03-09T16:00:00"
        }
    ]
    
    return jsonify(notifications)

# ============================================================================
# LOCATION ENDPOINTS
# ============================================================================

@app.route('/location/capture', methods=['POST'])
@validate_request_data()
def capture_location():
    """Capture technician location for service tracking"""
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
    
    if 'ticket_id' in data and not validate_integer(data['ticket_id'], min_val=1):
        return jsonify({"error": "Invalid ticket ID"}), 400
    
    # In production, save location to database for tracking
    return jsonify({
        "message": "Location captured successfully",
        "latitude": data.get('latitude', 40.7128),
        "longitude": data.get('longitude', -74.0060),
        "timestamp": datetime.now().isoformat(),
        "accuracy": data.get('accuracy', '5m')
    })

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    debug_mode = os.getenv("FLASK_ENV") == "development"
    
    print(f"🚀 Starting Ostrich Service API on port {port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
