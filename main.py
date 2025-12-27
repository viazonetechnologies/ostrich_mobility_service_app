import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from datetime import datetime
from functools import wraps

def validate_username(username):
    if not username or not isinstance(username, str):
        return False
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return re.match(pattern, username) is not None

def validate_password(password):
    if not password or not isinstance(password, str):
        return False
    return len(password) >= 6

def validate_string(value, min_length=1, max_length=255, required=True):
    if not required and (value is None or value == ''):
        return True
    if not value or not isinstance(value, str):
        return False
    return min_length <= len(value.strip()) <= max_length

def validate_integer(value, min_val=None, max_val=None, required=True):
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
    valid_statuses = ['open', 'in_progress', 'completed', 'closed', 'pending']
    return status in valid_statuses

def validate_priority(priority):
    valid_priorities = ['low', 'medium', 'high', 'urgent']
    return priority in valid_priorities

def sanitize_input(value):
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

DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
CORS(app)

engine = None
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        print("Database connected successfully")
    except Exception as e:
        print(f"Database connection error: {e}")

@app.route('/')
def root():
    return {
        "message": "Ostrich Service Technician API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

@app.route('/health')
def health_check():
    db_status = "connected" if engine else "disconnected"
    return {
        "status": "healthy",
        "service": "ostrich-service-api",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.route('/docs')
def docs():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ostrich Service API Documentation</title>
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
        "info": {"title": "Ostrich Service API", "version": "1.0.0"},
        "paths": {
            "/auth/login": {
                "post": {
                    "tags": ["Authentication"],
                    "requestBody": {
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
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "example": {"access_token": "token_service1", "user": {"id": 1, "username": "service1", "role": "technician"}}
                                }
                            }
                        }
                    }
                }
            },
            "/auth/logout": {
                "post": {
                    "tags": ["Authentication"],
                    "responses": {
                        "200": {
                            "description": "Logout successful",
                            "content": {
                                "application/json": {
                                    "example": {"message": "Logout successful"}
                                }
                            }
                        }
                    }
                }
            },
            "/dashboard/stats": {
                "get": {
                    "tags": ["Dashboard"],
                    "parameters": [{"name": "technician_id", "in": "query", "schema": {"type": "integer"}}],
                    "responses": {
                        "200": {
                            "description": "Dashboard stats",
                            "content": {
                                "application/json": {
                                    "example": {"total_tickets": 15, "open_tickets": 8}
                                }
                            }
                        }
                    }
                }
            },
            "/tickets": {
                "get": {
                    "tags": ["Tickets"],
                    "parameters": [
                        {"name": "status", "in": "query", "schema": {"type": "string"}},
                        {"name": "technician_id", "in": "query", "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Ticket list",
                            "content": {
                                "application/json": {
                                    "example": [{"id": 1, "customer_name": "John Smith", "status": "open"}]
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Tickets"],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "customer_id": {"type": "integer"},
                                        "product_id": {"type": "integer"},
                                        "issue_description": {"type": "string"},
                                        "priority": {"type": "string"}
                                    },
                                    "required": ["customer_id", "product_id", "issue_description"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Ticket created",
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
                    "parameters": [{"name": "ticket_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {
                        "200": {
                            "description": "Ticket details",
                            "content": {
                                "application/json": {
                                    "example": {"id": 1, "customer_name": "John Smith", "status": "open"}
                                }
                            }
                        }
                    }
                },
                "put": {
                    "tags": ["Tickets"],
                    "parameters": [{"name": "ticket_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "priority": {"type": "string"},
                                        "notes": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Ticket updated",
                            "content": {
                                "application/json": {
                                    "example": {"message": "Ticket updated successfully"}
                                }
                            }
                        }
                    }
                }
            },
            "/customers": {
                "get": {
                    "tags": ["Customers"],
                    "parameters": [{"name": "search", "in": "query", "schema": {"type": "string"}}],
                    "responses": {
                        "200": {
                            "description": "Customer list",
                            "content": {
                                "application/json": {
                                    "example": [{"id": 1, "name": "John Smith", "phone": "(555) 123-4567"}]
                                }
                            }
                        }
                    }
                }
            },
            "/customers/{customer_id}": {
                "get": {
                    "tags": ["Customers"],
                    "parameters": [{"name": "customer_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {
                        "200": {
                            "description": "Customer details",
                            "content": {
                                "application/json": {
                                    "example": {"id": 1, "name": "John Smith", "phone": "(555) 123-4567"}
                                }
                            }
                        }
                    }
                }
            },
            "/products": {
                "get": {
                    "tags": ["Products"],
                    "parameters": [{"name": "category", "in": "query", "schema": {"type": "string"}}],
                    "responses": {
                        "200": {
                            "description": "Product list",
                            "content": {
                                "application/json": {
                                    "example": [{"id": 1, "name": "CityRider Scooter", "category": "Mobility Scooters"}]
                                }
                            }
                        }
                    }
                }
            },
            "/notifications": {
                "get": {
                    "tags": ["Notifications"],
                    "parameters": [{"name": "technician_id", "in": "query", "schema": {"type": "integer"}}],
                    "responses": {
                        "200": {
                            "description": "Notifications",
                            "content": {
                                "application/json": {
                                    "example": [{"id": 1, "title": "New Ticket", "message": "You have a new assignment"}]
                                }
                            }
                        }
                    }
                }
            },
            "/location/capture": {
                "post": {
                    "tags": ["Location"],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "latitude": {"type": "number"},
                                        "longitude": {"type": "number"},
                                        "ticket_id": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Location captured",
                            "content": {
                                "application/json": {
                                    "example": {"message": "Location captured successfully"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

@app.route('/auth/login', methods=['POST'])
@validate_request_data(required_fields=['username', 'password'])
def login():
    data = request.validated_data
    username = data['username']
    password = data['password']
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username format"}), 400
    
    if not validate_password(password):
        return jsonify({"error": "Invalid password"}), 400
    
    if username == "service1" and password == "admin123":
        return jsonify({
            "access_token": "token_service1",
            "user": {"id": 1, "username": "service1", "role": "technician"}
        })
    
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT id, username, role FROM users WHERE username = :username AND password = :password AND role = 'technician'"), {"username": username, "password": password})
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
    return jsonify({"message": "Logout successful"})

@app.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    technician_id = request.args.get('technician_id')
    
    if technician_id and not validate_integer(technician_id, min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    stats = {
        "total_tickets": 15,
        "open_tickets": 8,
        "in_progress_tickets": 4,
        "closed_tickets": 3,
        "assigned_to_me": 5,
        "completed_today": 2
    }
    
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT status, COUNT(*) as count FROM service_tickets GROUP BY status"))
                ticket_stats = {row[0]: row[1] for row in result}
                
                total_tickets = conn.execute(text("SELECT COUNT(*) FROM service_tickets")).scalar()
                
                stats.update({
                    "total_tickets": total_tickets or 0,
                    "open_tickets": ticket_stats.get('open', 0),
                    "in_progress_tickets": ticket_stats.get('in_progress', 0),
                    "closed_tickets": ticket_stats.get('closed', 0)
                })
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(stats)

@app.route('/tickets', methods=['GET'])
def get_tickets():
    status = request.args.get('status')
    technician_id = request.args.get('technician_id')
    
    if status and not validate_status(status):
        return jsonify({"error": "Invalid status parameter"}), 400
    
    if technician_id and not validate_integer(technician_id, min_val=1):
        return jsonify({"error": "Invalid technician ID"}), 400
    
    tickets = [
        {"id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter", "status": "open", "priority": "high"},
        {"id": 2, "customer_name": "Sarah Johnson", "product_name": "ComfortLift Chair", "status": "in_progress", "priority": "medium"}
    ]
    
    if status:
        tickets = [t for t in tickets if t['status'] == status]
    
    if engine:
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
                
                query += " ORDER BY st.priority DESC, st.created_at DESC"
                
                result = conn.execute(text(query), params)
                db_tickets = []
                for row in result:
                    db_tickets.append({
                        "id": row[0], "customer_id": row[1], "product_id": row[2],
                        "issue_description": row[3], "status": row[4], "priority": row[5],
                        "created_at": str(row[6]), "assigned_technician_id": row[7],
                        "customer_name": row[8], "product_name": row[9]
                    })
                if db_tickets:
                    tickets = db_tickets
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(tickets)

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket_details(ticket_id):
    if not validate_integer(ticket_id, min_val=1):
        return jsonify({"error": "Invalid ticket ID"}), 400
    
    ticket_details = {
        "id": ticket_id,
        "customer_name": "John Smith",
        "customer_phone": "(555) 123-4567",
        "customer_address": "123 Main Street",
        "product_name": "CityRider Scooter",
        "issue_description": "Motor not functioning properly",
        "status": "open",
        "priority": "high"
    }
    
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT st.id, st.customer_id, st.product_id, st.issue_description, st.status, st.priority,
                           st.created_at, st.assigned_technician_id, c.name as customer_name, 
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
                        "created_at": str(ticket[6]), "assigned_technician_id": ticket[7],
                        "customer_name": ticket[8], "customer_phone": ticket[9],
                        "customer_address": ticket[10], "product_name": ticket[11]
                    }
                else:
                    return jsonify({"error": "Ticket not found"}), 404
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(ticket_details)

@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
@validate_request_data()
def update_ticket(ticket_id):
    data = request.validated_data
    
    if not validate_integer(ticket_id, min_val=1):
        return jsonify({"error": "Invalid ticket ID"}), 400
    
    if 'status' in data and not validate_status(data['status']):
        return jsonify({"error": "Invalid status"}), 400
    
    if 'priority' in data and not validate_priority(data['priority']):
        return jsonify({"error": "Invalid priority"}), 400
    
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

@app.route('/customers', methods=['GET'])
def get_customers():
    search = request.args.get('search')
    
    customers = [
        {"id": 1, "name": "John Smith", "phone": "(555) 123-4567", "email": "john@example.com"},
        {"id": 2, "name": "Sarah Johnson", "phone": "(555) 456-7890", "email": "sarah@example.com"}
    ]
    
    if search:
        search_lower = search.lower()
        customers = [c for c in customers if 
                    search_lower in c['name'].lower() or 
                    search_lower in c['phone'] or 
                    search_lower in c['email'].lower()]
    
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
    if not validate_integer(customer_id, min_val=1):
        return jsonify({"error": "Invalid customer ID"}), 400
    
    customer_details = {
        "id": customer_id,
        "name": "John Smith",
        "phone": "(555) 123-4567",
        "email": "john@example.com",
        "address": "123 Main Street"
    }
    
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT id, name, phone, email, address FROM customers WHERE id = :customer_id"), {"customer_id": customer_id})
                customer = result.fetchone()
                
                if customer:
                    customer_details = {
                        "id": customer[0], "name": customer[1], "phone": customer[2],
                        "email": customer[3], "address": customer[4]
                    }
                else:
                    return jsonify({"error": "Customer not found"}), 404
        except Exception as e:
            print(f"Database error: {e}")
    
    return jsonify(customer_details)

@app.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    
    products = [
        {"id": 1, "name": "CityRider Scooter", "category": "Mobility Scooters"},
        {"id": 2, "name": "ComfortLift Chair", "category": "Home Care"},
        {"id": 3, "name": "PowerPro Wheelchair", "category": "Wheelchairs"}
    ]
    
    if category:
        products = [p for p in products if p['category'] == category]
    
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

@app.route('/notifications', methods=['GET'])
def get_notifications():
    technician_id = request.args.get('technician_id')
    
    notifications = [
        {"id": 1, "title": "New High Priority Ticket", "message": "Urgent ticket assigned to you", "type": "assignment", "read": False},
        {"id": 2, "title": "Schedule Update", "message": "Your afternoon appointments have been rescheduled", "type": "schedule", "read": False}
    ]
    
    return jsonify(notifications)

@app.route('/location/capture', methods=['POST'])
@validate_request_data()
def capture_location():
    data = request.validated_data
    
    if 'latitude' in data:
        try:
            lat = float(data['latitude'])
            if not (-90 <= lat <= 90):
                return jsonify({"error": "Invalid latitude"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid latitude format"}), 400
    
    if 'longitude' in data:
        try:
            lng = float(data['longitude'])
            if not (-180 <= lng <= 180):
                return jsonify({"error": "Invalid longitude"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid longitude format"}), 400
    
    return jsonify({
        "message": "Location captured successfully",
        "latitude": data.get('latitude', 40.7128),
        "longitude": data.get('longitude', -74.0060),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    debug_mode = os.getenv("FLASK_ENV") == "development"
    
    print(f"Starting Ostrich Service API on port {port}")
    print(f"API Documentation: http://localhost:{port}/docs")
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
