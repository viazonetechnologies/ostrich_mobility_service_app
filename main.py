"""
Ostrich Service Mobile API
Professional Flask application for service technicians with fallback data
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
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

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    clean_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    return len(clean_phone) >= 10 and clean_phone.isdigit()

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
        
        # Get technician-specific stats
        my_stats = conn.execute(text("""
            SELECT 
                COUNT(*) as assigned_to_me,
                SUM(CASE WHEN status = 'Completed' AND DATE(updated_at) = CURDATE() THEN 1 ELSE 0 END) as completed_today
            FROM service_tickets 
            WHERE assigned_technician_id = :technician_id
        """), {"technician_id": technician_id})
        
        result = stats.fetchone()
        my_result = my_stats.fetchone()
        
        return jsonify({
            "total_tickets": result.total_tickets if result else 0,
            "open_tickets": result.open_tickets if result else 0,
            "in_progress_tickets": result.in_progress_tickets if result else 0,
            "closed_tickets": result.closed_tickets if result else 0,
            "assigned_to_me": my_result.assigned_to_me if my_result else 0,
            "completed_today": my_result.completed_today if my_result else 0
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
                "created_at": "2024-01-15T10:00:00",
                "scheduled_date": "2024-01-16T10:00:00"
            },
            {
                "id": 2,
                "customer_name": "Sarah Johnson",
                "customer_phone": "(555) 234-5678",
                "product_name": "ComfortLift Chair",
                "issue_description": "Switch malfunction",
                "status": "in_progress",
                "priority": "medium",
                "created_at": "2024-01-15T14:00:00",
                "scheduled_date": "2024-01-16T14:00:00"
            }
        ])
    
    with engine.connect() as conn:
        query = """
            SELECT st.*, c.name as customer_name, c.phone as customer_phone, c.address,
                   p.name as product_name, u.name as technician_name
            FROM service_tickets st
            LEFT JOIN customers c ON st.customer_phone = c.phone
            LEFT JOIN products p ON st.product_id = p.id
            LEFT JOIN users u ON st.assigned_technician_id = u.id
            WHERE 1=1
        """
        params = {}
        
        if status:
            query += " AND st.status = :status"
            params['status'] = status
        
        if technician_id:
            query += " AND st.assigned_technician_id = :technician_id"
            params['technician_id'] = technician_id
        
        if priority:
            query += " AND st.priority = :priority"
            params['priority'] = priority
        
        query += " ORDER BY st.created_at DESC"
        
        result = conn.execute(text(query), params)
        tickets = [dict(row._mapping) for row in result]
        return jsonify(tickets)

@app.route('/tickets', methods=['POST'])
def create_ticket():
    """Create new service ticket"""
    data = request.get_json()
    customer_id = data.get('customer_id')
    product_id = data.get('product_id')
    issue_description = data.get('issue_description', '').strip()
    priority = data.get('priority', 'medium')
    assigned_technician_id = data.get('assigned_technician_id')
    
    if not customer_id or not product_id or not issue_description:
        return jsonify({"error": "Missing required fields"}), 400
    
    if len(issue_description) < 10:
        return jsonify({"error": "Issue description must be at least 10 characters"}), 400
    
    if not DB_CONNECTED:
        return jsonify({
            "message": "Ticket created successfully",
            "id": 123
        }), 201
    
    with engine.connect() as conn:
        # Verify customer and product exist
        customer_check = conn.execute(text("SELECT id FROM customers WHERE id = :id"), {"id": customer_id})
        if not customer_check.fetchone():
            return jsonify({"error": "Customer not found"}), 404
        
        product_check = conn.execute(text("SELECT id FROM products WHERE id = :id"), {"id": product_id})
        if not product_check.fetchone():
            return jsonify({"error": "Product not found"}), 404
        
        # Create ticket
        result = conn.execute(text("""
            INSERT INTO service_tickets (customer_id, product_id, description, priority, 
                                       assigned_technician_id, status, created_at) 
            VALUES (:customer_id, :product_id, :description, :priority, :technician_id, 'Open', NOW())
        """), {
            "customer_id": customer_id,
            "product_id": product_id,
            "description": issue_description,
            "priority": priority,
            "technician_id": assigned_technician_id
        })
        conn.commit()
        
        return jsonify({
            "message": "Ticket created successfully",
            "id": result.lastrowid
        }), 201

@app.route('/tickets/<int:ticket_id>')
def get_ticket(ticket_id):
    """Get ticket details"""
    if not DB_CONNECTED:
        return jsonify({
            "id": ticket_id,
            "customer_name": "John Smith",
            "customer_phone": "(555) 123-4567",
            "product_name": "CityRider Scooter",
            "issue_description": "Motor not functioning properly",
            "status": "open",
            "priority": "high",
            "created_at": "2024-01-15T10:00:00",
            "address": "123 Main St, Downtown"
        })
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT st.*, c.name as customer_name, c.phone as customer_phone, 
                   c.email, c.address, p.name as product_name, u.name as technician_name
            FROM service_tickets st
            LEFT JOIN customers c ON st.customer_phone = c.phone
            LEFT JOIN products p ON st.product_id = p.id
            LEFT JOIN users u ON st.assigned_technician_id = u.id
            WHERE st.id = :id
        """), {"id": ticket_id})
        ticket = result.fetchone()
        
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        
        return jsonify(dict(ticket._mapping))

@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """Update ticket status and details"""
    data = request.get_json()
    status = data.get('status')
    priority = data.get('priority')
    assigned_technician_id = data.get('assigned_technician_id')
    notes = data.get('notes', '')
    
    if not DB_CONNECTED:
        return jsonify({"message": "Ticket updated successfully"})
    
    with engine.connect() as conn:
        # Check if ticket exists
        check = conn.execute(text("SELECT id FROM service_tickets WHERE id = :id"), {"id": ticket_id})
        if not check.fetchone():
            return jsonify({"error": "Ticket not found"}), 404
        
        # Build update query
        updates = []
        params = {"id": ticket_id}
        
        if status:
            updates.append("status = :status")
            params["status"] = status
        
        if priority:
            updates.append("priority = :priority")
            params["priority"] = priority
        
        if assigned_technician_id:
            updates.append("assigned_technician_id = :technician_id")
            params["technician_id"] = assigned_technician_id
        
        if notes:
            updates.append("notes = :notes")
            params["notes"] = notes
        
        if updates:
            updates.append("updated_at = NOW()")
            query = f"UPDATE service_tickets SET {', '.join(updates)} WHERE id = :id"
            conn.execute(text(query), params)
            conn.commit()
        
        return jsonify({"message": "Ticket updated successfully"})

@app.route('/tickets/assigned')
def get_assigned_tickets():
    """Get tickets assigned to technician"""
    technician_id = request.args.get('technician_id', 1)
    
    if not DB_CONNECTED:
        return jsonify([
            {
                "id": 1,
                "customer_name": "John Smith",
                "product_name": "CityRider Scooter",
                "status": "assigned",
                "priority": "high",
                "scheduled_date": "2024-01-16T10:00:00"
            }
        ])
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT st.*, c.name as customer_name, c.phone as customer_phone, 
                   p.name as product_name
            FROM service_tickets st
            LEFT JOIN customers c ON st.customer_phone = c.phone
            LEFT JOIN products p ON st.product_id = p.id
            WHERE st.assigned_technician_id = :technician_id
            AND st.status IN ('Open', 'In Progress')
            ORDER BY st.created_at DESC
        """), {"technician_id": technician_id})
        
        tickets = [dict(row._mapping) for row in result]
        return jsonify(tickets)

@app.route('/tickets/completed')
def get_completed_tickets():
    """Get completed tickets"""
    technician_id = request.args.get('technician_id')
    
    if not DB_CONNECTED:
        return jsonify([
            {
                "id": 3,
                "customer_name": "Mike Wilson",
                "product_name": "PowerPro Wheelchair",
                "status": "completed",
                "completed_at": "2024-01-10T15:30:00"
            }
        ])
    
    with engine.connect() as conn:
        query = """
            SELECT st.*, c.name as customer_name, c.phone as customer_phone, 
                   p.name as product_name
            FROM service_tickets st
            LEFT JOIN customers c ON st.customer_phone = c.phone
            LEFT JOIN products p ON st.product_id = p.id
            WHERE st.status = 'Completed'
        """
        params = {}
        
        if technician_id:
            query += " AND st.assigned_technician_id = :technician_id"
            params["technician_id"] = technician_id
        
        query += " ORDER BY st.updated_at DESC LIMIT 20"
        
        result = conn.execute(text(query), params)
        tickets = [dict(row._mapping) for row in result]
        return jsonify(tickets)

# ============================================================================
# TECHNICIAN ENDPOINTS
# ============================================================================

@app.route('/technicians')
def get_technicians():
    """Get list of service technicians"""
    if not DB_CONNECTED:
        return jsonify([
            {"id": 1, "username": "service1", "name": "John Technician", "role": "technician", "status": "active"}
        ])
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, name, email, phone, status
            FROM users 
            WHERE role = 'service' AND status = 'active'
            ORDER BY name
        """))
        technicians = [dict(row._mapping) for row in result]
        return jsonify(technicians)

# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@app.route('/customers')
def get_customers():
    """Get customer list with search"""
    search = request.args.get('search', '')
    
    if not DB_CONNECTED:
        return jsonify([
            {"id": 1, "name": "John Smith", "phone": "(555) 123-4567", "email": "john@example.com"}
        ])
    
    with engine.connect() as conn:
        query = "SELECT id, name, phone, email, address FROM customers"
        params = {}
        
        if search:
            query += " WHERE name LIKE :search OR phone LIKE :search OR email LIKE :search"
            params['search'] = f"%{search}%"
        
        query += " ORDER BY name LIMIT 50"
        
        result = conn.execute(text(query), params)
        customers = [dict(row._mapping) for row in result]
        return jsonify(customers)

@app.route('/customers/<int:customer_id>')
def get_customer(customer_id):
    """Get customer details"""
    if not DB_CONNECTED:
        return jsonify({
            "id": customer_id,
            "name": "John Smith",
            "phone": "(555) 123-4567",
            "email": "john@example.com",
            "address": "123 Main St"
        })
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM customers WHERE id = :id"), {"id": customer_id})
        customer = result.fetchone()
        
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        return jsonify(dict(customer._mapping))

# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@app.route('/products')
def get_products():
    """Get product catalog"""
    category = request.args.get('category')
    
    if not DB_CONNECTED:
        return jsonify([
            {"id": 1, "name": "CityRider Scooter", "category": "Mobility Scooters", "model": "CR-2023"},
            {"id": 2, "name": "ComfortLift Chair", "category": "Lift Chairs", "model": "CL-2023"},
            {"id": 3, "name": "PowerPro Wheelchair", "category": "Wheelchairs", "model": "PP-2023"}
        ])
    
    with engine.connect() as conn:
        query = "SELECT id, name, category, model, price FROM products WHERE status = 'active'"
        params = {}
        
        if category:
            query += " AND category = :category"
            params['category'] = category
        
        query += " ORDER BY name"
        
        result = conn.execute(text(query), params)
        products = [dict(row._mapping) for row in result]
        return jsonify(products)

# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@app.route('/notifications')
def get_notifications():
    """Get notifications for technician"""
    technician_id = request.args.get('technician_id', 1)
    
    if not DB_CONNECTED:
        return jsonify([
            {
                "id": 1,
                "title": "New Ticket Assigned",
                "message": "You have been assigned a new high priority ticket",
                "type": "assignment",
                "read": False,
                "created_at": "2024-01-15T10:00:00"
            }
        ])
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, title, message, type, is_read as read, created_at
            FROM notifications 
            WHERE technician_id = :technician_id 
            ORDER BY created_at DESC LIMIT 20
        """), {"technician_id": technician_id})
        
        notifications = [dict(row._mapping) for row in result]
        return jsonify(notifications)

@app.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    if not DB_CONNECTED:
        return jsonify({"message": "Notification marked as read"})
    
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE notifications 
            SET is_read = 1 
            WHERE id = :id
        """), {"id": notification_id})
        conn.commit()
        
        return jsonify({"message": "Notification marked as read"})

# ============================================================================
# LOCATION ENDPOINTS
# ============================================================================

@app.route('/location/capture', methods=['POST'])
def capture_location():
    """Capture technician location for ticket"""
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    ticket_id = data.get('ticket_id')
    
    if not latitude or not longitude:
        return jsonify({"error": "Missing location coordinates"}), 400
    
    if not DB_CONNECTED:
        return jsonify({
            "message": "Location captured successfully",
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.now().isoformat()
        })
    
    with engine.connect() as conn:
        # Update ticket with location if ticket_id provided
        if ticket_id:
            conn.execute(text("""
                UPDATE service_tickets 
                SET latitude = :lat, longitude = :lng, location_updated_at = NOW()
                WHERE id = :ticket_id
            """), {"lat": latitude, "lng": longitude, "ticket_id": ticket_id})
            conn.commit()
        
        return jsonify({
            "message": "Location captured successfully",
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.now().isoformat()
        })

# ============================================================================
# REPORT ENDPOINTS
# ============================================================================

@app.route('/reports/daily')
def daily_report():
    """Get daily service report"""
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    technician_id = request.args.get('technician_id')
    
    if not DB_CONNECTED:
        return jsonify({
            "date": date,
            "total_tickets": 8,
            "completed_tickets": 5,
            "open_tickets": 2,
            "in_progress_tickets": 1
        })
    
    with engine.connect() as conn:
        query = """
            SELECT 
                COUNT(*) as total_tickets,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_tickets,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_tickets,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_tickets
            FROM service_tickets 
            WHERE DATE(created_at) = :date
        """
        params = {"date": date}
        
        if technician_id:
            query += " AND assigned_technician_id = :technician_id"
            params["technician_id"] = technician_id
        
        result = conn.execute(text(query), params)
        report = result.fetchone()
        
        data = dict(report._mapping) if report else {
            "total_tickets": 0,
            "completed_tickets": 0,
            "open_tickets": 0,
            "in_progress_tickets": 0
        }
        data['date'] = date
        return jsonify(data)

# ============================================================================
# API DOCUMENTATION
# ============================================================================

@app.route('/docs')
def api_docs():
    """API Documentation"""
    endpoints = {
        "Authentication": {
            "POST /auth/login": "Login with username + password",
            "POST /auth/logout": "Logout user"
        },
        "Dashboard": {
            "GET /dashboard/stats": "Dashboard statistics"
        },
        "Tickets": {
            "GET /tickets": "List tickets with filters",
            "POST /tickets": "Create new ticket",
            "GET /tickets/{id}": "Get ticket details",
            "PUT /tickets/{id}": "Update ticket",
            "GET /tickets/assigned": "Get assigned tickets",
            "GET /tickets/completed": "Get completed tickets"
        },
        "Technicians": {
            "GET /technicians": "List technicians"
        },
        "Customers": {
            "GET /customers": "List customers with search",
            "GET /customers/{id}": "Get customer details"
        },
        "Products": {
            "GET /products": "List products"
        },
        "Notifications": {
            "GET /notifications": "Get notifications",
            "PUT /notifications/{id}/read": "Mark as read"
        },
        "Location": {
            "POST /location/capture": "Capture location"
        },
        "Reports": {
            "GET /reports/daily": "Daily report"
        }
    }
    
    return jsonify({
        "title": "Ostrich Service Support API",
        "version": "1.0.0",
        "description": "Complete API for service technician mobile application",
        "endpoints": endpoints,
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
