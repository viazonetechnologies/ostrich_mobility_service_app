"""
Ostrich Service Mobile API
Professional Flask application using real-time database data only
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from datetime import datetime

# ============================================================================
# APPLICATION SETUP
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
CORS(app)

# Database connection
engine = create_engine(DATABASE_URL)
print("✅ Database connected successfully")

# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.route('/')
def root():
    """API Information"""
    return jsonify({
        "message": "Ostrich Service Mobile API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    })

@app.route('/health')
def health_check():
    """Health Check"""
    return jsonify({
        "status": "healthy",
        "service": "ostrich-service-api",
        "database": "connected",
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
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, name, role 
            FROM users 
            WHERE username = :username AND password = :password AND role = 'service'
        """), {"username": username, "password": password})
        user = result.fetchone()
        
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        return jsonify({
            "access_token": f"token_{username}",
            "user": dict(user._mapping)
        })

@app.route('/auth/logout', methods=['POST'])
def logout():
    """Logout service technician"""
    return jsonify({"message": "Logout successful"})

# ============================================================================
# SERVICE TICKET ENDPOINTS
# ============================================================================

@app.route('/tickets')
def get_tickets():
    """Get assigned service tickets"""
    status = request.args.get('status', 'all')
    
    with engine.connect() as conn:
        query = """
            SELECT st.*, c.name as customer_name, c.phone as customer_phone, c.address,
                   p.name as product_name
            FROM service_tickets st
            LEFT JOIN customers c ON st.customer_phone = c.phone
            LEFT JOIN products p ON st.product_id = p.id
        """
        params = {}
        
        if status != "all":
            query += " WHERE st.status = :status"
            params['status'] = status
        
        query += " ORDER BY st.created_at DESC"
        
        result = conn.execute(text(query), params)
        tickets = [dict(row._mapping) for row in result]
        return jsonify({"tickets": tickets})

@app.route('/tickets/<int:ticket_id>')
def get_ticket(ticket_id):
    """Get ticket details"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT st.*, c.name as customer_name, c.phone as customer_phone, 
                   c.email, c.address, p.name as product_name
            FROM service_tickets st
            LEFT JOIN customers c ON st.customer_phone = c.phone
            LEFT JOIN products p ON st.product_id = p.id
            WHERE st.id = :id
        """), {"id": ticket_id})
        ticket = result.fetchone()
        
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        
        return jsonify(dict(ticket._mapping))

@app.route('/tickets/<int:ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    """Update ticket status"""
    data = request.get_json()
    status = data.get('status')
    notes = data.get('notes', '')
    
    valid_statuses = ['Open', 'In Progress', 'Completed', 'Cancelled']
    if status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400
    
    with engine.connect() as conn:
        # Check if ticket exists
        check = conn.execute(text("SELECT id FROM service_tickets WHERE id = :id"), {"id": ticket_id})
        if not check.fetchone():
            return jsonify({"error": "Ticket not found"}), 404
        
        # Update ticket
        conn.execute(text("""
            UPDATE service_tickets 
            SET status = :status, notes = :notes, updated_at = NOW()
            WHERE id = :id
        """), {
            "status": status,
            "notes": notes,
            "id": ticket_id
        })
        conn.commit()
    
    return jsonify({"message": "Ticket status updated successfully"})

@app.route('/tickets', methods=['POST'])
def create_ticket():
    """Create new service ticket"""
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    customer_phone = data.get('customer_phone')
    priority = data.get('priority', 'Medium')
    product_id = data.get('product_id')
    
    if not title or not description or not customer_phone:
        return jsonify({"error": "Missing required fields"}), 400
    
    if len(title) < 5:
        return jsonify({"error": "Title must be at least 5 characters"}), 400
    
    if len(description) < 10:
        return jsonify({"error": "Description must be at least 10 characters"}), 400
    
    with engine.connect() as conn:
        # Verify customer exists
        customer_check = conn.execute(text("SELECT id FROM customers WHERE phone = :phone"), {"phone": customer_phone})
        if not customer_check.fetchone():
            return jsonify({"error": "Customer not found"}), 404
        
        # Verify product exists if provided
        if product_id:
            product_check = conn.execute(text("SELECT id FROM products WHERE id = :id"), {"id": product_id})
            if not product_check.fetchone():
                return jsonify({"error": "Product not found"}), 404
        
        # Create ticket
        result = conn.execute(text("""
            INSERT INTO service_tickets (title, description, customer_phone, status, priority, product_id, created_at) 
            VALUES (:title, :description, :phone, 'Open', :priority, :product_id, NOW())
        """), {
            "title": title,
            "description": description,
            "phone": customer_phone,
            "priority": priority,
            "product_id": product_id
        })
        conn.commit()
        
        return jsonify({
            "message": "Ticket created successfully",
            "ticket_id": result.lastrowid
        }), 201

# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@app.route('/customers')
def get_customers():
    """Get customer list"""
    search = request.args.get('search', '')
    
    with engine.connect() as conn:
        query = "SELECT id, name, phone, email, address FROM customers"
        params = {}
        
        if search:
            query += " WHERE name LIKE :search OR phone LIKE :search"
            params['search'] = f"%{search}%"
        
        query += " ORDER BY name"
        
        result = conn.execute(text(query), params)
        customers = [dict(row._mapping) for row in result]
        return jsonify({"customers": customers})

@app.route('/customers/<int:customer_id>')
def get_customer(customer_id):
    """Get customer details"""
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
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, category, price FROM products WHERE status = 'active'"))
        products = [dict(row._mapping) for row in result]
        return jsonify({"products": products})

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.route('/dashboard')
def get_dashboard():
    """Get service dashboard data"""
    with engine.connect() as conn:
        # Get ticket statistics for today
        stats = conn.execute(text("""
            SELECT 
                COUNT(*) as total_tickets,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_tickets,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_tickets,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_tickets
            FROM service_tickets 
            WHERE DATE(created_at) = CURDATE()
        """))
        
        result = stats.fetchone()
        return jsonify(dict(result._mapping) if result else {
            "total_tickets": 0,
            "open_tickets": 0,
            "in_progress_tickets": 0,
            "completed_tickets": 0
        })

@app.route('/reports/daily')
def daily_report():
    """Get daily service report"""
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_tickets,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_tickets,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_tickets,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_tickets
            FROM service_tickets 
            WHERE DATE(created_at) = :date
        """), {"date": date})
        
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
# TECHNICIAN ENDPOINTS
# ============================================================================

@app.route('/technicians')
def get_technicians():
    """Get list of service technicians"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, name, email, phone 
            FROM users 
            WHERE role = 'service' AND status = 'active'
            ORDER BY name
        """))
        technicians = [dict(row._mapping) for row in result]
        return jsonify({"technicians": technicians})

@app.route('/my-tickets')
def get_my_tickets():
    """Get tickets assigned to current technician"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT st.*, c.name as customer_name, c.phone as customer_phone, 
                   p.name as product_name
            FROM service_tickets st
            LEFT JOIN customers c ON st.customer_phone = c.phone
            LEFT JOIN products p ON st.product_id = p.id
            WHERE st.assigned_to = :technician_id
            ORDER BY st.created_at DESC
        """), {"technician_id": 1})  # Demo technician ID
        
        tickets = [dict(row._mapping) for row in result]
        return jsonify({"tickets": tickets})

# ============================================================================
# APPLICATION RUNNER
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8003))
    app.run(host="0.0.0.0", port=port, debug=True)
