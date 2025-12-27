"""
Ostrich Service Mobile API with Swagger UI
Professional Flask application for service technicians with fallback data
"""

import os
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from sqlalchemy import create_engine, text
from datetime import datetime
import re

# ============================================================================
# APPLICATION SETUP
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://username:password@host:port/database')

app = Flask(__name__)
CORS(app)

# Swagger API setup
api = Api(app, 
    version='1.0.0',
    title='Ostrich Service Support API',
    description='Complete API for service technician mobile application',
    doc='/swagger/',
    prefix='/api'
)

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
# API MODELS
# ============================================================================

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username', example='service1'),
    'password': fields.String(required=True, description='Password', example='admin123')
})

ticket_model = api.model('Ticket', {
    'customer_id': fields.Integer(required=True, description='Customer ID'),
    'product_id': fields.Integer(required=True, description='Product ID'),
    'issue_description': fields.String(required=True, description='Issue description'),
    'priority': fields.String(description='Priority level', enum=['low', 'medium', 'high'], default='medium'),
    'assigned_technician_id': fields.Integer(description='Assigned technician ID')
})

location_model = api.model('Location', {
    'latitude': fields.Float(required=True, description='Latitude'),
    'longitude': fields.Float(required=True, description='Longitude'),
    'ticket_id': fields.Integer(description='Related ticket ID')
})

# ============================================================================
# NAMESPACES
# ============================================================================

auth_ns = api.namespace('auth', description='Authentication operations')
dashboard_ns = api.namespace('dashboard', description='Dashboard operations')
tickets_ns = api.namespace('tickets', description='Ticket operations')
customers_ns = api.namespace('customers', description='Customer operations')
products_ns = api.namespace('products', description='Product operations')
technicians_ns = api.namespace('technicians', description='Technician operations')
notifications_ns = api.namespace('notifications', description='Notification operations')
location_ns = api.namespace('location', description='Location operations')
reports_ns = api.namespace('reports', description='Report operations')

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
    return {
        "message": "Ostrich Service Support API",
        "version": "1.0.0",
        "status": "operational",
        "swagger_ui": "/swagger/",
        "documentation": "/docs"
    }

@app.route('/health')
def health_check():
    """Health Check"""
    db_status = "connected" if DB_CONNECTED else "disconnected"
    return {
        "status": "healthy",
        "service": "ostrich-service-api",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.route('/docs')
def api_docs():
    """Legacy API Documentation"""
    return {
        "title": "Ostrich Service Support API",
        "version": "1.0.0",
        "description": "Complete API for service technician mobile application",
        "swagger_ui": "/swagger/",
        "demo_credentials": {
            "username": "service1",
            "password": "admin123"
        }
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('login')
    def post(self):
        """Service technician login"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            api.abort(400, "Missing username or password")
        
        # Demo login - accept service1/admin123
        if username == "service1" and password == "admin123":
            if not DB_CONNECTED:
                return {
                    "access_token": "token_service1",
                    "user": {"id": 1, "username": "service1", "name": "John Technician", "role": "technician"}
                }
            
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT id, username, name, role 
                    FROM users 
                    WHERE username = :username AND password = :password AND role = 'service'
                """), {"username": username, "password": password})
                user = result.fetchone()
                
                if user:
                    return {
                        "access_token": f"token_{username}",
                        "user": dict(user._mapping)
                    }
        
        api.abort(401, "Invalid credentials")

@auth_ns.route('/logout')
class Logout(Resource):
    @auth_ns.doc('logout')
    def post(self):
        """Logout service technician"""
        return {"message": "Logout successful"}

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@dashboard_ns.route('/stats')
class DashboardStats(Resource):
    @dashboard_ns.doc('get_dashboard_stats')
    @dashboard_ns.param('technician_id', 'Technician ID', type='integer')
    def get(self):
        """Get dashboard statistics"""
        technician_id = request.args.get('technician_id', 1)
        
        if not DB_CONNECTED:
            return {
                "total_tickets": 15,
                "open_tickets": 8,
                "in_progress_tickets": 4,
                "closed_tickets": 3,
                "assigned_to_me": 5,
                "completed_today": 2
            }
        
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
            
            return {
                "total_tickets": result.total_tickets if result else 0,
                "open_tickets": result.open_tickets if result else 0,
                "in_progress_tickets": result.in_progress_tickets if result else 0,
                "closed_tickets": result.closed_tickets if result else 0,
                "assigned_to_me": my_result.assigned_to_me if my_result else 0,
                "completed_today": my_result.completed_today if my_result else 0
            }

# ============================================================================
# TICKET ENDPOINTS
# ============================================================================

@tickets_ns.route('/')
class TicketList(Resource):
    @tickets_ns.doc('get_tickets')
    @tickets_ns.param('status', 'Filter by status')
    @tickets_ns.param('technician_id', 'Filter by technician ID', type='integer')
    @tickets_ns.param('priority', 'Filter by priority')
    def get(self):
        """Get service tickets with filters"""
        status = request.args.get('status')
        technician_id = request.args.get('technician_id')
        priority = request.args.get('priority')
        
        if not DB_CONNECTED:
            return [
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
            ]
        
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
            return tickets

    @tickets_ns.expect(ticket_model)
    @tickets_ns.doc('create_ticket')
    def post(self):
        """Create new service ticket"""
        data = request.get_json()
        customer_id = data.get('customer_id')
        product_id = data.get('product_id')
        issue_description = data.get('issue_description', '').strip()
        priority = data.get('priority', 'medium')
        assigned_technician_id = data.get('assigned_technician_id')
        
        if not customer_id or not product_id or not issue_description:
            api.abort(400, "Missing required fields")
        
        if len(issue_description) < 10:
            api.abort(400, "Issue description must be at least 10 characters")
        
        if not DB_CONNECTED:
            return {"message": "Ticket created successfully", "id": 123}, 201
        
        with engine.connect() as conn:
            # Verify customer and product exist
            customer_check = conn.execute(text("SELECT id FROM customers WHERE id = :id"), {"id": customer_id})
            if not customer_check.fetchone():
                api.abort(404, "Customer not found")
            
            product_check = conn.execute(text("SELECT id FROM products WHERE id = :id"), {"id": product_id})
            if not product_check.fetchone():
                api.abort(404, "Product not found")
            
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
            
            return {"message": "Ticket created successfully", "id": result.lastrowid}, 201

@tickets_ns.route('/<int:ticket_id>')
class Ticket(Resource):
    @tickets_ns.doc('get_ticket')
    def get(self, ticket_id):
        """Get ticket details"""
        if not DB_CONNECTED:
            return {
                "id": ticket_id,
                "customer_name": "John Smith",
                "customer_phone": "(555) 123-4567",
                "product_name": "CityRider Scooter",
                "issue_description": "Motor not functioning properly",
                "status": "open",
                "priority": "high",
                "created_at": "2024-01-15T10:00:00",
                "address": "123 Main St, Downtown"
            }
        
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
                api.abort(404, "Ticket not found")
            
            return dict(ticket._mapping)

    @tickets_ns.doc('update_ticket')
    def put(self, ticket_id):
        """Update ticket status and details"""
        data = request.get_json()
        
        if not DB_CONNECTED:
            return {"message": "Ticket updated successfully"}
        
        with engine.connect() as conn:
            # Check if ticket exists
            check = conn.execute(text("SELECT id FROM service_tickets WHERE id = :id"), {"id": ticket_id})
            if not check.fetchone():
                api.abort(404, "Ticket not found")
            
            # Build update query
            updates = []
            params = {"id": ticket_id}
            
            if data.get('status'):
                updates.append("status = :status")
                params["status"] = data['status']
            
            if data.get('priority'):
                updates.append("priority = :priority")
                params["priority"] = data['priority']
            
            if data.get('assigned_technician_id'):
                updates.append("assigned_technician_id = :technician_id")
                params["technician_id"] = data['assigned_technician_id']
            
            if data.get('notes'):
                updates.append("notes = :notes")
                params["notes"] = data['notes']
            
            if updates:
                updates.append("updated_at = NOW()")
                query = f"UPDATE service_tickets SET {', '.join(updates)} WHERE id = :id"
                conn.execute(text(query), params)
                conn.commit()
            
            return {"message": "Ticket updated successfully"}

@tickets_ns.route('/assigned')
class AssignedTickets(Resource):
    @tickets_ns.doc('get_assigned_tickets')
    @tickets_ns.param('technician_id', 'Technician ID', type='integer')
    def get(self):
        """Get tickets assigned to technician"""
        technician_id = request.args.get('technician_id', 1)
        
        if not DB_CONNECTED:
            return [{
                "id": 1,
                "customer_name": "John Smith",
                "product_name": "CityRider Scooter",
                "status": "assigned",
                "priority": "high",
                "scheduled_date": "2024-01-16T10:00:00"
            }]
        
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
            return tickets

@tickets_ns.route('/completed')
class CompletedTickets(Resource):
    @tickets_ns.doc('get_completed_tickets')
    @tickets_ns.param('technician_id', 'Technician ID', type='integer')
    def get(self):
        """Get completed tickets"""
        technician_id = request.args.get('technician_id')
        
        if not DB_CONNECTED:
            return [{
                "id": 3,
                "customer_name": "Mike Wilson",
                "product_name": "PowerPro Wheelchair",
                "status": "completed",
                "completed_at": "2024-01-10T15:30:00"
            }]
        
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
            return tickets

# ============================================================================
# OTHER ENDPOINTS
# ============================================================================

@customers_ns.route('/')
class CustomerList(Resource):
    @customers_ns.doc('get_customers')
    @customers_ns.param('search', 'Search term')
    def get(self):
        """Get customer list with search"""
        search = request.args.get('search', '')
        
        if not DB_CONNECTED:
            return [{"id": 1, "name": "John Smith", "phone": "(555) 123-4567", "email": "john@example.com"}]
        
        with engine.connect() as conn:
            query = "SELECT id, name, phone, email, address FROM customers"
            params = {}
            
            if search:
                query += " WHERE name LIKE :search OR phone LIKE :search OR email LIKE :search"
                params['search'] = f"%{search}%"
            
            query += " ORDER BY name LIMIT 50"
            
            result = conn.execute(text(query), params)
            customers = [dict(row._mapping) for row in result]
            return customers

@products_ns.route('/')
class ProductList(Resource):
    @products_ns.doc('get_products')
    @products_ns.param('category', 'Product category')
    def get(self):
        """Get product catalog"""
        category = request.args.get('category')
        
        if not DB_CONNECTED:
            return [
                {"id": 1, "name": "CityRider Scooter", "category": "Mobility Scooters", "model": "CR-2023"},
                {"id": 2, "name": "ComfortLift Chair", "category": "Lift Chairs", "model": "CL-2023"},
                {"id": 3, "name": "PowerPro Wheelchair", "category": "Wheelchairs", "model": "PP-2023"}
            ]
        
        with engine.connect() as conn:
            query = "SELECT id, name, category, model, price FROM products WHERE status = 'active'"
            params = {}
            
            if category:
                query += " AND category = :category"
                params['category'] = category
            
            query += " ORDER BY name"
            
            result = conn.execute(text(query), params)
            products = [dict(row._mapping) for row in result]
            return products

@technicians_ns.route('/')
class TechnicianList(Resource):
    @technicians_ns.doc('get_technicians')
    def get(self):
        """Get list of service technicians"""
        if not DB_CONNECTED:
            return [{"id": 1, "username": "service1", "name": "John Technician", "role": "technician", "status": "active"}]
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, username, name, email, phone, status
                FROM users 
                WHERE role = 'service' AND status = 'active'
                ORDER BY name
            """))
            technicians = [dict(row._mapping) for row in result]
            return technicians

@location_ns.route('/capture')
class LocationCapture(Resource):
    @location_ns.expect(location_model)
    @location_ns.doc('capture_location')
    def post(self):
        """Capture technician location for ticket"""
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        ticket_id = data.get('ticket_id')
        
        if not latitude or not longitude:
            api.abort(400, "Missing location coordinates")
        
        if not DB_CONNECTED:
            return {
                "message": "Location captured successfully",
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": datetime.now().isoformat()
            }
        
        with engine.connect() as conn:
            # Update ticket with location if ticket_id provided
            if ticket_id:
                conn.execute(text("""
                    UPDATE service_tickets 
                    SET latitude = :lat, longitude = :lng, location_updated_at = NOW()
                    WHERE id = :ticket_id
                """), {"lat": latitude, "lng": longitude, "ticket_id": ticket_id})
                conn.commit()
            
            return {
                "message": "Location captured successfully",
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": datetime.now().isoformat()
            }

# ============================================================================
# APPLICATION RUNNER
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8003))
    app.run(host="0.0.0.0", port=port, debug=True)
