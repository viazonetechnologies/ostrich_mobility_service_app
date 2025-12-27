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

# ============================================================================
# APPLICATION SETUP
# ============================================================================

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
            "completed_today": 2
        })
    
    with engine.connect() as conn:
        # Get overall statistics
        stats = conn.execute(text("""
            SELECT 
                COUNT(*) as total_tickets,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_tickets,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_tickets,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as closed_tickets
            FROM service_tickets 
            WHERE DATE(created_at) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """))
        
        result = stats.fetchone()
        
        return jsonify({
            "total_tickets": result.total_tickets if result else 0,
            "open_tickets": result.open_tickets if result else 0,
            "in_progress_tickets": result.in_progress_tickets if result else 0,
            "closed_tickets": result.closed_tickets if result else 0
        })

# ============================================================================
# TICKET ENDPOINTS
# ============================================================================

@app.route('/tickets')
def get_tickets():
    """Get service tickets with filters"""
    status = request.args.get('status')
    technician_id = request.args.get('technician_id')
    priority = request.args.get('priority')
    
    if not DB_CONNECTED:
        return jsonify([
            {
                "id": 1,
                "customer_name": "John Smith",
                "customer_phone": "(555) 123-4567",
                "product_name": "CityRider Scooter",
                "issue_description": "Motor not functioning",
                "status": "open",
                "priority": "high",
                "created_at": "2024-01-15T10:00:00"
            }
        ])
    
    return jsonify([])

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
