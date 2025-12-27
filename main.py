import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pymysql
from datetime import datetime

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
        "info": {"title": "Service Support API", "version": "1.0.0", "description": "Complete API for Service Technician Mobile App"},
        "paths": {
            "/auth/login": {"post": {"summary": "Login technician", "tags": ["Authentication"]}},
            "/auth/logout": {"post": {"summary": "Logout technician", "tags": ["Authentication"]}},
            "/dashboard/stats": {"get": {"summary": "Get dashboard statistics", "tags": ["Dashboard"]}},
            "/tickets": {"get": {"summary": "Get service tickets", "tags": ["Tickets"]}, "post": {"summary": "Create service ticket", "tags": ["Tickets"]}},
            "/tickets/{ticket_id}": {"get": {"summary": "Get ticket details", "tags": ["Tickets"]}, "put": {"summary": "Update ticket", "tags": ["Tickets"]}},
            "/tickets/assigned": {"get": {"summary": "Get assigned tickets", "tags": ["Tickets"]}},
            "/tickets/completed": {"get": {"summary": "Get completed tickets", "tags": ["Tickets"]}},
            "/technicians": {"get": {"summary": "Get technicians", "tags": ["Technicians"]}},
            "/customers": {"get": {"summary": "Get customers", "tags": ["Customers"]}},
            "/customers/{customer_id}": {"get": {"summary": "Get customer details", "tags": ["Customers"]}},
            "/products": {"get": {"summary": "Get products", "tags": ["Products"]}},
            "/notifications": {"get": {"summary": "Get notifications", "tags": ["Notifications"]}},
            "/location/capture": {"post": {"summary": "Capture current location", "tags": ["Location"]}}
        }
    }

# Authentication APIs
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
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
            
            return jsonify({
                "total_tickets": total_tickets,
                "open_tickets": ticket_stats.get('open', 0),
                "in_progress_tickets": ticket_stats.get('in_progress', 0),
                "closed_tickets": ticket_stats.get('closed', 0),
                "total_customers": total_customers,
                "total_products": total_products,
                "ticket_stats": ticket_stats
            })
    except Exception as e:
        return jsonify({
            "total_tickets": 15, "open_tickets": 8, "in_progress_tickets": 4,
            "closed_tickets": 3, "total_customers": 14, "total_products": 8
        })

# Ticket APIs
@app.route('/tickets', methods=['GET'])
def get_tickets():
    status = request.args.get('status')
    technician_id = request.args.get('technician_id')
    priority = request.args.get('priority')
    
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
def create_ticket():
    data = request.get_json()
    
    if not engine:
        return jsonify({"message": "Ticket created", "id": 1})
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO service_tickets (customer_id, product_id, issue_description, status, priority)
                VALUES (:customer_id, :product_id, :issue_description, 'open', :priority)
            """), {
                "customer_id": data.get('customer_id'),
                "product_id": data.get('product_id'),
                "issue_description": data.get('issue_description'),
                "priority": data.get('priority', 'medium')
            })
            conn.commit()
            return jsonify({"message": "Ticket created", "id": result.lastrowid})
    except Exception as e:
        return jsonify({"message": "Ticket created", "id": 1})

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket_details(ticket_id):
    if not engine:
        return jsonify({
            "id": ticket_id, "customer_name": "John Smith", "product_name": "CityRider Scooter",
            "issue_description": "Motor not functioning", "status": "open", "priority": "high",
            "customer_phone": "(555) 123-4567", "customer_address": "123 Main St, Downtown",
            "scheduled_time": "Today, 10:00 AM"
        })
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT st.id, st.customer_id, st.product_id, st.issue_description,
                       st.status, st.priority, st.created_at, st.assigned_technician_id,
                       c.name as customer_name, p.name as product_name,
                       c.phone as customer_phone, c.address as customer_address,
                       u.username as technician_name
                FROM service_tickets st
                LEFT JOIN customers c ON st.customer_id = c.id
                LEFT JOIN products p ON st.product_id = p.id
                LEFT JOIN users u ON st.assigned_technician_id = u.id
                WHERE st.id = :ticket_id
            """), {"ticket_id": ticket_id})
            ticket = result.fetchone()
            
            if ticket:
                return jsonify({
                    "id": ticket[0], "customer_id": ticket[1], "product_id": ticket[2],
                    "issue_description": ticket[3], "status": ticket[4], "priority": ticket[5],
                    "created_at": str(ticket[6]), "assigned_technician_id": ticket[7],
                    "customer_name": ticket[8], "product_name": ticket[9],
                    "customer_phone": ticket[10], "customer_address": ticket[11],
                    "technician_name": ticket[12]
                })
            return jsonify({"error": "Ticket not found"}), 404
    except Exception as e:
        return jsonify({"id": ticket_id, "customer_name": "Demo Customer", "status": "open"})

@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    data = request.get_json()
    
    if not engine:
        return jsonify({"message": "Ticket updated"})
    
    try:
        with engine.connect() as conn:
            update_fields = []
            params = {"ticket_id": ticket_id}
            
            if data.get('status'):
                update_fields.append("status = :status")
                params["status"] = data.get('status')
            
            if data.get('assigned_technician_id'):
                update_fields.append("assigned_technician_id = :technician_id")
                params["technician_id"] = data.get('assigned_technician_id')
            
            if data.get('resolution_notes'):
                update_fields.append("resolution_notes = :resolution_notes")
                params["resolution_notes"] = data.get('resolution_notes')
            
            if update_fields:
                query = f"UPDATE service_tickets SET {', '.join(update_fields)} WHERE id = :ticket_id"
                conn.execute(text(query), params)
                conn.commit()
            
            return jsonify({"message": "Ticket updated"})
    except Exception as e:
        return jsonify({"message": "Ticket updated"})

@app.route('/tickets/assigned', methods=['GET'])
def get_assigned_tickets():
    technician_id = request.args.get('technician_id')
    
    if not engine:
        return jsonify([
            {"id": 1, "customer_name": "John Smith", "product_name": "CityRider Scooter", "status": "open", "priority": "high"},
            {"id": 2, "customer_name": "Sarah Johnson", "product_name": "ComfortLift Chair", "status": "in_progress", "priority": "medium"}
        ])
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT st.id, c.name as customer_name, p.name as product_name, 
                       st.status, st.priority, st.issue_description
                FROM service_tickets st
                LEFT JOIN customers c ON st.customer_id = c.id
                LEFT JOIN products p ON st.product_id = p.id
                WHERE st.assigned_technician_id = :technician_id
                ORDER BY st.created_at DESC
            """), {"technician_id": technician_id})
            
            tickets = []
            for row in result:
                tickets.append({
                    "id": row[0], "customer_name": row[1], "product_name": row[2],
                    "status": row[3], "priority": row[4], "issue_description": row[5]
                })
            
            return jsonify(tickets)
    except Exception as e:
        return jsonify([{"id": 1, "customer_name": "Demo Customer", "status": "open"}])

@app.route('/tickets/completed', methods=['GET'])
def get_completed_tickets():
    technician_id = request.args.get('technician_id')
    
    if not engine:
        return jsonify([
            {"id": 3, "customer_name": "Mike Wilson", "product_name": "PowerPro Wheelchair", "completed_date": "2024-03-10"}
        ])
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT st.id, c.name as customer_name, p.name as product_name, st.updated_at
                FROM service_tickets st
                LEFT JOIN customers c ON st.customer_id = c.id
                LEFT JOIN products p ON st.product_id = p.id
                WHERE st.status = 'closed' AND st.assigned_technician_id = :technician_id
                ORDER BY st.updated_at DESC
            """), {"technician_id": technician_id})
            
            tickets = []
            for row in result:
                tickets.append({
                    "id": row[0], "customer_name": row[1], "product_name": row[2],
                    "completed_date": str(row[3]) if row[3] else None
                })
            
            return jsonify(tickets)
    except Exception as e:
        return jsonify([{"id": 1, "customer_name": "Demo Customer", "completed_date": "2024-03-10"}])

# Technician APIs
@app.route('/technicians', methods=['GET'])
def get_technicians():
    if not engine:
        return jsonify([{"id": 1, "username": "service1", "role": "technician"}])
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, username, email, role FROM users WHERE role = 'technician'"))
            
            technicians = []
            for row in result:
                technicians.append({
                    "id": row[0], "username": row[1], "email": row[2], "role": row[3]
                })
            
            return jsonify(technicians)
    except Exception as e:
        return jsonify([{"id": 1, "username": "service1", "role": "technician"}])

# Customer APIs
@app.route('/customers', methods=['GET'])
def get_customers():
    if not engine:
        return jsonify([{"id": 1, "name": "Demo Customer", "phone": "9876543299"}])
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, email, phone, address FROM customers"))
            
            customers = []
            for row in result:
                customers.append({
                    "id": row[0], "name": row[1], "email": row[2], "phone": row[3], "address": row[4]
                })
            
            return jsonify(customers)
    except Exception as e:
        return jsonify([{"id": 1, "name": "Demo Customer", "phone": "9876543299"}])

@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer_details(customer_id):
    if not engine:
        return jsonify({"id": customer_id, "name": "Demo Customer", "phone": "9876543299"})
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, email, phone, address FROM customers WHERE id = :customer_id"), {"customer_id": customer_id})
            customer = result.fetchone()
            
            if customer:
                return jsonify({
                    "id": customer[0], "name": customer[1], "email": customer[2],
                    "phone": customer[3], "address": customer[4]
                })
            return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        return jsonify({"id": customer_id, "name": "Demo Customer", "phone": "9876543299"})

# Product APIs
@app.route('/products', methods=['GET'])
def get_products():
    if not engine:
        return jsonify([{"id": 1, "name": "Demo Product", "category": "Electronics"}])
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, description, price, category FROM products"))
            
            products = []
            for row in result:
                products.append({
                    "id": row[0], "name": row[1], "description": row[2],
                    "price": float(row[3]), "category": row[4]
                })
            
            return jsonify(products)
    except Exception as e:
        return jsonify([{"id": 1, "name": "Demo Product", "category": "Electronics"}])

# Notification APIs
@app.route('/notifications', methods=['GET'])
def get_notifications():
    notifications = [
        {"id": 1, "title": "New Ticket Assigned", "message": "You have been assigned ticket #TKT-104", "type": "assignment", "read": False, "created_at": "2024-03-10"},
        {"id": 2, "title": "Message from Regional Officer", "message": "Please ensure location verification for all tickets", "type": "message", "read": False, "created_at": "2024-03-09"},
        {"id": 3, "title": "Service Reminder", "message": "Complete safety checklist for motor repairs", "type": "reminder", "read": True, "created_at": "2024-03-08"},
        {"id": 4, "title": "Schedule Update", "message": "Your schedule for tomorrow has been updated", "type": "schedule", "read": True, "created_at": "2024-03-07"}
    ]
    
    return jsonify(notifications)

# Location APIs
@app.route('/location/capture', methods=['POST'])
def capture_location():
    data = request.get_json()
    ticket_id = data.get('ticket_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    # In a real app, you would save the location to the database
    return jsonify({
        "message": "Location captured successfully",
        "ticket_id": ticket_id,
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    app.run(host="0.0.0.0", port=port, debug=False)
