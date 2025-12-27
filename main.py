"""
Ostrich Service Mobile API - Based on HTML Mockup Requirements
"""

import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sqlalchemy import create_engine, text
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://username:password@host:port/database')

app = Flask(__name__)
CORS(app)

# Database connection
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    DB_CONNECTED = True
except Exception as e:
    print(f"Database connection failed: {e}")
    engine = None
    DB_CONNECTED = False

SWAGGER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ostrich Service API</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: '/swagger.json',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.presets.standalone]
        });
    </script>
</body>
</html>
"""

@app.route('/swagger.json')
def swagger_spec():
    return jsonify({
        "openapi": "3.0.0",
        "info": {
            "title": "Ostrich Service Support API",
            "version": "1.0.0",
            "description": "Service technician mobile application API"
        },
        "paths": {
            "/": {"get": {"tags": ["Info"], "summary": "API Information"}},
            "/auth/login": {"post": {"tags": ["Authentication"], "summary": "Login"}},
            "/dashboard/stats": {"get": {"tags": ["Dashboard"], "summary": "Dashboard stats"}},
            "/tickets": {"get": {"tags": ["Tickets"], "summary": "Get tickets"}},
            "/tickets/{id}": {"get": {"tags": ["Tickets"], "summary": "Get ticket details"}, "put": {"tags": ["Tickets"], "summary": "Update ticket"}},
            "/notifications": {"get": {"tags": ["Notifications"], "summary": "Get notifications"}},
            "/location/capture": {"post": {"tags": ["Location"], "summary": "Capture location"}}
        }
    })

@app.route('/swagger/')
def swagger_ui():
    return render_template_string(SWAGGER_TEMPLATE)

# ============================================================================
# CORE ENDPOINTS BASED ON HTML MOCKUP
# ============================================================================

@app.route('/')
def root():
    return jsonify({
        "message": "Ostrich Service Support API",
        "version": "1.0.0",
        "status": "operational",
        "swagger_ui": "/swagger/",
        "documentation": "/docs"
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "ostrich-service-api",
        "database": "connected" if DB_CONNECTED else "disconnected",
        "timestamp": datetime.now().isoformat()
    })

# LOGIN PAGE ENDPOINTS
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == "service1" and password == "admin123":
        return jsonify({
            "access_token": "token_service1",
            "user": {"id": 1, "username": "service1", "name": "John Technician", "role": "technician"}
        })
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/auth/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logout successful"})

# DASHBOARD SCREEN ENDPOINTS
@app.route('/dashboard/stats')
def get_dashboard_stats():
    return jsonify({
        "total_tickets": 15,
        "open_tickets": 8,
        "in_progress_tickets": 4,
        "closed_tickets": 3,
        "high_priority": 3
    })

@app.route('/tickets')
def get_tickets():
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    tickets = [
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
    ]
    
    # Filter by status if provided
    if status:
        tickets = [t for t in tickets if t['status'] == status]
    
    # Filter by priority if provided  
    if priority:
        tickets = [t for t in tickets if t['priority'] == priority]
    
    return jsonify(tickets)

# TICKET DETAILS SCREEN ENDPOINTS
@app.route('/tickets/<int:ticket_id>')
def get_ticket_details(ticket_id):
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

@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket_status(ticket_id):
    data = request.get_json()
    status = data.get('status')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    return jsonify({
        "message": "Ticket status updated successfully",
        "ticket_id": ticket_id,
        "new_status": status
    })

@app.route('/location/capture', methods=['POST'])
def capture_location():
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

# NOTIFICATIONS SCREEN ENDPOINTS
@app.route('/notifications')
def get_notifications():
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
        },
        {
            "id": 4,
            "title": "Schedule Update",
            "message": "Your schedule for tomorrow has been updated. Check your assigned tickets.",
            "type": "schedule",
            "created_at": "2024-01-13T10:00:00",
            "time_ago": "2 days ago"
        }
    ])

# SYSTEM ENDPOINTS
@app.route('/docs')
def api_docs():
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

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8003))
    app.run(host="0.0.0.0", port=port, debug=True)
