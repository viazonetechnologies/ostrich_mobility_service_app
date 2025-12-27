"""
Ostrich Service Mobile API with Simple Swagger
Professional Flask application for service technicians with fallback data
"""

import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sqlalchemy import create_engine, text
from datetime import datetime
import re

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system env vars

# ============================================================================
# APPLICATION SETUP
# ============================================================================

# Set production database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://username:password@host:port/database')

app = Flask(__name__)
CORS(app)

# Database connection with error handling
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "connect_timeout": 60,
            "read_timeout": 60,
            "write_timeout": 60
        }
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Database connected successfully")
    DB_CONNECTED = True
except Exception as e:
    print(f"Database connection failed: {e}")
    print("API will run with mock data for testing")
    engine = None
    DB_CONNECTED = False

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    clean_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    return len(clean_phone) >= 10 and clean_phone.isdigit()

# ============================================================================
# SWAGGER UI TEMPLATE
# ============================================================================

SWAGGER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ostrich Service API</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: '/swagger.json',
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.presets.standalone
            ]
        });
    </script>
</body>
</html>
"""

# ============================================================================
# SWAGGER SPECIFICATION
# ============================================================================

@app.route('/swagger.json')
def swagger_spec():
    """OpenAPI/Swagger specification"""
    return jsonify({
        "openapi": "3.0.0",
        "info": {
            "title": "Ostrich Service Support API",
            "version": "1.0.0",
            "description": "Complete API for service technician mobile application"
        },
        "servers": [
            {"url": "/", "description": "Current server"}
        ],
        "paths": {
            "/": {
                "get": {
                    "tags": ["Info"],
                    "summary": "API Information",
                    "responses": {
                        "200": {
                            "description": "API info",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "message": "Ostrich Service Support API",
                                        "version": "1.0.0",
                                        "status": "operational"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/auth/login": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Service technician login",
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
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "access_token": "token_service1",
                                        "user": {"id": 1, "username": "service1", "name": "John Technician"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/dashboard/stats": {
                "get": {
                    "tags": ["Dashboard"],
                    "summary": "Get dashboard statistics",
                    "parameters": [
                        {
                            "name": "technician_id",
                            "in": "query",
                            "schema": {"type": "integer"},
                            "description": "Technician ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Dashboard statistics",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "total_tickets": 15,
                                        "open_tickets": 8,
                                        "in_progress_tickets": 4,
                                        "closed_tickets": 3
                                    }
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
                        {"name": "status", "in": "query", "schema": {"type": "string"}},
                        {"name": "technician_id", "in": "query", "schema": {"type": "integer"}},
                        {"name": "priority", "in": "query", "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "List of tickets",
                            "content": {
                                "application/json": {
                                    "example": [
                                        {
                                            "id": 1,
                                            "customer_name": "John Smith",
                                            "product_name": "CityRider Scooter",
                                            "status": "open",
                                            "priority": "high"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Tickets"],
                    "summary": "Create new ticket",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "customer_id": {"type": "integer"},
                                        "product_id": {"type": "integer"},
                                        "issue_description": {"type": "string"},
                                        "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                                    },
                                    "required": ["customer_id", "product_id", "issue_description"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Ticket created",
                            "content": {
                                "application/json": {
                                    "example": {"message": "Ticket created successfully", "id": 123}
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
                    "parameters": [
                        {"name": "ticket_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Ticket details",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "id": 101,
                                        "customer_name": "John Smith",
                                        "customer_phone": "(555) 123-4567",
                                        "customer_address": "123 Main St, Downtown",
                                        "product_name": "CityRider Scooter",
                                        "issue_description": "Motor not functioning",
                                        "status": "pending",
                                        "priority": "high",
                                        "scheduled_time": "2024-01-15T10:00:00",
                                        "latitude": 40.7128,
                                        "longitude": -74.0060
                                    }
                                }
                            }
                        }
                    }
                },
                "put": {
                    "tags": ["Tickets"],
                    "summary": "Update ticket status",
                    "parameters": [
                        {"name": "ticket_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                                        "latitude": {"type": "number"},
                                        "longitude": {"type": "number"}
                                    },
                                    "required": ["status"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Ticket updated",
                            "content": {
                                "application/json": {
                                    "example": {"message": "Ticket status updated successfully"}
                                }
                            }
                        }
                    }
                }
            },
            "/notifications": {
                "get": {
                    "tags": ["Notifications"],
                    "summary": "Get notifications",
                    "parameters": [
                        {"name": "technician_id", "in": "query", "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "List of notifications",
                            "content": {
                                "application/json": {
                                    "example": [
                                        {
                                            "id": 1,
                                            "title": "New Ticket Assigned",
                                            "message": "You have been assigned ticket #TKT-104",
                                            "type": "ticket",
                                            "created_at": "2024-01-15T10:00:00"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }                    }
                }
            },
            "/location/capture": {
                "post": {
                    "tags": ["Location"],
                    "summary": "Capture location",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "latitude": {"type": "number", "example": 40.7128},
                                        "longitude": {"type": "number", "example": -74.0060},
                                        "ticket_id": {"type": "integer"}
                                    },
                                    "required": ["latitude", "longitude"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Location captured",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "message": "Location captured successfully",
                                        "latitude": 40.7128,
                                        "longitude": -74.0060
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Login": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"}
                    },
                    "required": ["username", "password"]
                }
            }
        }
    })

@app.route('/swagger/')
def swagger_ui():
    """Swagger UI"""
    return render_template_string(SWAGGER_TEMPLATE)

# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.route('/')
def root():
    """API Information"""
    return jsonify({
        "message": "Ostrich Service Support API",
        "version": "1.0.0",
        "status": "operational",
        "swagger_ui": "/swagger/",
        "documentation": "/docs"
    })

@app.route('/health')
def health_check():
    """Health Check"""
    db_status = "connected" if DB_CONNECTED else "disconnected"
    return jsonify({
        "status": "healthy",
        "service": "ostrich-service-api",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    })

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/auth/login', methods=['POST'])
def login():
    """Service technician login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    # Demo login - accept service1/admin123
    if username == "service1" and password == "admin123":
        if not DB_CONNECTED:
            return jsonify({
                "access_token": "token_service1",
                "user": {"id": 1, "username": "service1", "name": "John Technician", "role": "technician"}
            })
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, username, name, role 
                FROM users 
                WHERE username = :username AND password = :password AND role = 'service'
            """), {"username": username, "password": password})
            user = result.fetchone()
            
            if user:
                return jsonify({
                    "access_token": f"token_{username}",
                    "user": dict(user._mapping)
                })
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/auth/logout', methods=['POST'])
def logout():
    """Logout service technician"""
    return jsonify({"message": "Logout successful"})

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.route('/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    technician_id = request.args.get('technician_id', 1)
    
    if not DB_CONNECTED:
        return jsonify({
            "total_tickets": 15,
            "open_tickets": 8,
            "in_progress_tickets": 4,
            "closed_tickets": 3,
            "assigned_to_me": 5,
            "completed_today": 2,
            "high_priority": 3,
            "nearby_tickets": 6
        })
    
    with engine.connect() as conn:
        # Get overall statistics
        stats = conn.execute(text("""
            SELECT 
                COUNT(*) as total_tickets,
                SUM(CASE WHEN status = 'Open' OR status = 'pending' THEN 1 ELSE 0 END) as open_tickets,
                SUM(CASE WHEN status = 'In Progress' OR status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_tickets,
                SUM(CASE WHEN status = 'Completed' OR status = 'completed' THEN 1 ELSE 0 END) as closed_tickets,
                SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_priority
            FROM service_tickets 
            WHERE DATE(created_at) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """))
        
        result = stats.fetchone()
        
        return jsonify({
            "total_tickets": result.total_tickets if result else 0,
            "open_tickets": result.open_tickets if result else 0,
            "in_progress_tickets": result.in_progress_tickets if result else 0,
            "closed_tickets": result.closed_tickets if result else 0,
            "high_priority": result.high_priority if result else 0
        })

# ============================================================================
# TICKET ENDPOINTS
# ============================================================================

@app.route('/tickets')
def get_tickets():
    """Get service tickets with filters"""
    status = request.args.get('status')
    technician_id = request.args.get('technician_id', 1)
    priority = request.args.get('priority')
    
    if not DB_CONNECTED:
        return jsonify([
            {
                "id": 101,
                "customer_name": "John Smith",
                "customer_phone": "(555) 123-4567",
                "product_name": "CityRider Scooter - Pro Model",
                "issue_description": "Motor not functioning, battery drainage issue",
                "status": "pending",
                "priority": "high",
                "created_at": "2024-01-15T10:00:00",
                "scheduled_time": "Today, 10:00 AM",
                "distance": "2.3 km away"
            },
            {
                "id": 102,
                "customer_name": "Sarah Johnson",
                "customer_phone": "(555) 234-5678",
                "product_name": "ComfortLift Chair",
                "issue_description": "Switch malfunction, remote control not working",
                "status": "in_progress",
                "priority": "medium",
                "created_at": "2024-01-15T14:00:00",
                "scheduled_time": "Today, 2:00 PM",
                "distance": "5.1 km away"
            },
            {
                "id": 103,
                "customer_name": "Robert Brown",
                "customer_phone": "(555) 345-6789",
                "product_name": "PowerPro Wheelchair",
                "issue_description": "Loose connection, intermittent power loss",
                "status": "pending",
                "priority": "low",
                "created_at": "2024-01-16T09:00:00",
                "scheduled_time": "Tomorrow, 9:00 AM",
                "distance": "1.7 km away"
            }
        ])
    
    with engine.connect() as conn:
        query = """
            SELECT 
                st.id,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                c.phone as customer_phone,
                p.name as product_name,
                st.issue_description,
                st.status,
                st.priority,
                st.created_at,
                st.scheduled_time
            FROM service_tickets st
            JOIN customers c ON st.customer_id = c.id
            JOIN products p ON st.product_id = p.id
            WHERE 1=1
        """
        
        params = {}
        if status:
            query += " AND st.status = :status"
            params['status'] = status
        if priority:
            query += " AND st.priority = :priority"
            params['priority'] = priority
            
        query += " ORDER BY st.created_at DESC"
        
        result = conn.execute(text(query), params)
        tickets = [dict(row._mapping) for row in result.fetchall()]
        
        return jsonify(tickets)

@app.route('/tickets/<int:ticket_id>')
def get_ticket_details(ticket_id):
    """Get detailed ticket information"""
    if not DB_CONNECTED:
        return jsonify({
            "id": ticket_id,
            "customer_name": "John Smith",
            "customer_phone": "(555) 123-4567",
            "customer_address": "123 Main St, Downtown",
            "product_name": "CityRider Scooter - Pro Model",
            "issue_description": "Customer reports motor not functioning properly and rapid battery drainage. The scooter stops working after approximately 30 minutes of use, even with full charge. Suspected issues: Motor controller failure or battery connection problem.",
            "status": "pending",
            "priority": "high",
            "scheduled_time": "Today, 10:00 AM",
            "created_at": "2024-01-15T10:00:00",
            "latitude": 40.7128,
            "longitude": -74.0060
        })
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                st.id,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                c.phone as customer_phone,
                c.address as customer_address,
                p.name as product_name,
                st.issue_description,
                st.status,
                st.priority,
                st.scheduled_time,
                st.created_at,
                st.latitude,
                st.longitude
            FROM service_tickets st
            JOIN customers c ON st.customer_id = c.id
            JOIN products p ON st.product_id = p.id
            WHERE st.id = :ticket_id
        """), {"ticket_id": ticket_id})
        
        ticket = result.fetchone()
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
            
        return jsonify(dict(ticket._mapping))

@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket_status(ticket_id):
    """Update ticket status and location"""
    data = request.get_json()
    status = data.get('status')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not status:
        return jsonify({"error": "Status is required"}), 400
    
    if not DB_CONNECTED:
        return jsonify({"message": "Ticket status updated successfully"})
    
    with engine.connect() as conn:
        update_query = "UPDATE service_tickets SET status = :status"
        params = {"status": status, "ticket_id": ticket_id}
        
        if latitude and longitude:
            update_query += ", latitude = :latitude, longitude = :longitude"
            params.update({"latitude": latitude, "longitude": longitude})
            
        update_query += ", updated_at = NOW() WHERE id = :ticket_id"
        
        conn.execute(text(update_query), params)
        conn.commit()
        
        return jsonify({"message": "Ticket status updated successfully"})

@app.route('/notifications')
def get_notifications():
    """Get technician notifications"""
    technician_id = request.args.get('technician_id', 1)
    
    if not DB_CONNECTED:
        return jsonify([
            {
                "id": 1,
                "title": "New Ticket Assigned",
                "message": "You have been assigned a new high priority ticket #TKT-104 for a PowerPro Wheelchair repair.",
                "type": "ticket",
                "created_at": "2024-01-15T10:00:00",
                "time_ago": "10 minutes ago"
            },
            {
                "id": 2,
                "title": "Message from Regional Officer",
                "message": "Please ensure all completed tickets have location verification before closing.",
                "type": "message",
                "created_at": "2024-01-15T08:00:00",
                "time_ago": "2 hours ago"
            },
            {
                "id": 3,
                "title": "Service Reminder",
                "message": "Don't forget to complete the safety checklist for all motor-related repairs.",
                "type": "reminder",
                "created_at": "2024-01-14T10:00:00",
                "time_ago": "1 day ago"
            }
        ])
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                id,
                title,
                message,
                type,
                created_at
            FROM notifications 
            WHERE user_id = :technician_id OR user_id IS NULL
            ORDER BY created_at DESC
            LIMIT 20
        """), {"technician_id": technician_id})
        
        notifications = [dict(row._mapping) for row in result.fetchall()]
        return jsonify(notifications)

@app.route('/tickets', methods=['POST'])
def create_ticket():
    """Create new service ticket"""
    data = request.get_json()
    
    if not data.get('customer_id') or not data.get('product_id') or not data.get('issue_description'):
        return jsonify({"error": "Missing required fields"}), 400
    
    return jsonify({"message": "Ticket created successfully", "id": 123}), 201

@app.route('/location/capture', methods=['POST'])
def capture_location():
    """Capture technician location for ticket"""
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({"error": "Missing location coordinates"}), 400
    
    return jsonify({
        "message": "Location captured successfully",
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/docs')
def api_docs():
    """Legacy API Documentation"""
    return jsonify({
        "title": "Ostrich Service Support API",
        "version": "1.0.0",
        "description": "Complete API for service technician mobile application",
        "swagger_ui": "/swagger/",
        "demo_credentials": {
            "username": "service1",
            "password": "admin123"
        }
    })

# ============================================================================
# APPLICATION RUNNER
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8003))
    app.run(host="0.0.0.0", port=port, debug=True)
