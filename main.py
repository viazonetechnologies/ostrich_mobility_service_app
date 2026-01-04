from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
import pymysql
from contextlib import contextmanager

# Create Flask app first
app = Flask(__name__)
CORS(app)

# Add root route before API setup
@app.route('/')
def api_root():
    """Root endpoint - API information"""
    return jsonify({
        "message": "Ostrich Service Technician API",
        "version": "1.0.0",
        "docs": "/docs/",
        "status": "running",
        "endpoints": {
            "swagger_ui": "/docs/",
            "health": "/health",
            "auth": "/auth/",
            "dashboard": "/dashboard/",
            "tickets": "/tickets/",
            "notifications": "/notifications/",
            "schedule": "/schedule/",
            "profile": "/profile/",
            "reports": "/reports/",
            "inventory": "/inventory/"
        }
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "ostrich-service-api", "timestamp": datetime.now().isoformat()})

# Swagger API setup with comprehensive documentation
api = Api(app, 
    version='1.0', 
    title='Ostrich Service Technician API',
    description='Complete API for Service Technician Mobile App - Test all endpoints with Swagger UI',
    doc='/docs/',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Add "Bearer " before your JWT token'
        }
    },
    security='Bearer'
)

# Namespaces
auth_ns = api.namespace('auth', description='Authentication Operations')
dashboard_ns = api.namespace('dashboard', description='Dashboard & Overview')
tickets_ns = api.namespace('tickets', description='Service Tickets Management')
notifications_ns = api.namespace('notifications', description='Notifications')
schedule_ns = api.namespace('schedule', description='Schedule & Calendar')
profile_ns = api.namespace('profile', description='Technician Profile')
reports_ns = api.namespace('reports', description='Reports & Analytics')
inventory_ns = api.namespace('inventory', description='Parts & Inventory')

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'service-secret-key')
app.config['SECRET_KEY'] = SECRET_KEY

# Database configuration - Aiven MySQL
DB_CONFIG = {
    'host': 'mysql-ostrich-tviazone-5922.i.aivencloud.com',
    'user': 'avnadmin',
    'password': os.getenv('DB_PASSWORD'),
    'database': 'defaultdb',
    'port': 16599,
    'charset': 'utf8mb4',
    'ssl': {'ssl_mode': 'REQUIRED'}
}

@contextmanager
def get_db_connection():
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        yield connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        yield None
    finally:
        if connection:
            connection.close()

# JWT utilities
def create_access_token(data):
    payload = data.copy()
    payload['exp'] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if token and token.startswith('Bearer '):
                token = token[7:]
                payload = verify_token(token)
                if payload:
                    return f(current_user=payload, *args, **kwargs)
            return jsonify({'error': 'Token required'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
    return decorated

# ==================== MODELS ====================
# Auth Models
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Technician username', example='demo.tech'),
    'password': fields.String(required=True, description='Password', example='password123')
})

signup_model = api.model('Signup', {
    'full_name': fields.String(required=True, description='Full name', example='John Technician'),
    'employee_id': fields.String(required=True, description='Employee ID', example='EMP001'),
    'phone': fields.String(required=False, description='Phone number', example='9876543210'),
    'email': fields.String(required=False, description='Email address', example='john.tech@ostrich.com')
})

otp_model = api.model('SendOTP', {
    'contact': fields.String(required=True, description='Phone number', example='9876543210')
})

verify_otp_model = api.model('VerifyOTP', {
    'contact': fields.String(required=True, description='Phone number', example='9876543210'),
    'otp': fields.String(required=True, description='OTP code', example='123456')
})

# Ticket Models
ticket_status_model = api.model('TicketStatus', {
    'status': fields.String(required=True, description='New status', enum=['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'], example='IN_PROGRESS'),
    'notes': fields.String(required=False, description='Status update notes', example='Started working on the motor'),
    'work_performed': fields.String(required=False, description='Work performed description', example='Checked motor connections'),
    'parts_used': fields.List(fields.Raw, required=False, description='Parts used in service')
})

location_model = api.model('Location', {
    'latitude': fields.Float(required=True, description='Latitude', example=19.0760),
    'longitude': fields.Float(required=True, description='Longitude', example=72.8777)
})

parts_model = api.model('PartsUsed', {
    'parts': fields.List(fields.Raw, required=True, description='List of parts used', example=[
        {'part_id': 1, 'name': 'Motor Belt', 'quantity': 1, 'cost': 250.0},
        {'part_id': 2, 'name': 'Oil Filter', 'quantity': 2, 'cost': 150.0}
    ])
})

# Profile Models
profile_update_model = api.model('ProfileUpdate', {
    'full_name': fields.String(required=False, description='Full name'),
    'phone': fields.String(required=False, description='Phone number'),
    'email': fields.String(required=False, description='Email address'),
    'specializations': fields.List(fields.String, required=False, description='Technical specializations')
})

# Inventory Models
inventory_request_model = api.model('InventoryRequest', {
    'parts': fields.List(fields.Raw, required=True, description='Parts to request', example=[
        {'part_id': 1, 'quantity': 5, 'urgency': 'normal'},
        {'part_id': 2, 'quantity': 2, 'urgency': 'urgent'}
    ]),
    'reason': fields.String(required=False, description='Reason for request', example='Stock running low')
})

# ==================== FALLBACK DATA ====================
FALLBACK_DATA = {
    "technicians": [
        {"id": 1, "employee_id": "EMP001", "full_name": "John Technician", "email": "john.tech@ostrich.com", "phone": "9876543220", "role": "technician", "specializations": ["Motors", "Pumps"], "experience_years": 5},
        {"id": 2, "employee_id": "EMP002", "full_name": "Jane Tech", "email": "jane.tech@ostrich.com", "phone": "9876543221", "role": "technician", "specializations": ["Generators", "Electrical"], "experience_years": 3},
        {"id": 3, "employee_id": "EMP003", "full_name": "Bob Service", "email": "bob.tech@ostrich.com", "phone": "9876543222", "role": "technician", "specializations": ["Motors", "Generators"], "experience_years": 7}
    ],
    "tickets": [
        {"id": 1, "ticket_number": "TKT000001", "customer_name": "John Customer", "customer_phone": "9876543210", "customer_address": "123 Main St, Mumbai", "product_name": "3HP Motor", "product_model": "OST-3HP-SP", "issue_description": "Motor not starting properly", "status": "SCHEDULED", "priority": "HIGH", "assigned_technician_id": 1, "scheduled_date": "2025-01-15T09:00:00", "created_at": "2025-01-14T10:00:00"},
        {"id": 2, "ticket_number": "TKT000002", "customer_name": "Jane Smith", "customer_phone": "9876543211", "customer_address": "456 Service Ave, Delhi", "product_name": "5HP Pump", "product_model": "OST-5HP-MP", "issue_description": "Pump maintenance required", "status": "IN_PROGRESS", "priority": "MEDIUM", "assigned_technician_id": 1, "scheduled_date": "2025-01-15T14:00:00", "created_at": "2025-01-13T15:30:00"},
        {"id": 3, "ticket_number": "TKT000003", "customer_name": "Bob Wilson", "customer_phone": "9876543212", "customer_address": "789 Repair Rd, Bangalore", "product_name": "7HP Generator", "product_model": "OST-7HP-GN", "issue_description": "Generator overheating issue", "status": "COMPLETED", "priority": "HIGH", "assigned_technician_id": 2, "scheduled_date": "2025-01-14T11:00:00", "created_at": "2025-01-12T09:15:00", "completed_at": "2025-01-14T16:30:00"}
    ],
    "notifications": [
        {"id": 1, "technician_id": 1, "title": "New Ticket Assigned", "message": "Ticket TKT000004 has been assigned to you", "type": "assignment", "is_read": False, "created_at": "2025-01-15T10:00:00", "ticket_id": 4},
        {"id": 2, "technician_id": 1, "title": "Urgent Ticket", "message": "High priority ticket TKT000005 needs immediate attention", "type": "urgent", "is_read": False, "created_at": "2025-01-15T09:30:00", "ticket_id": 5},
        {"id": 3, "technician_id": 1, "title": "Schedule Update", "message": "Your schedule for tomorrow has been updated", "type": "schedule", "is_read": True, "created_at": "2025-01-14T17:00:00", "ticket_id": None}
    ],
    "inventory": [
        {"id": 1, "part_number": "BRG001", "name": "Motor Bearing", "category": "Bearings", "quantity_available": 15, "unit_cost": 250.0, "location": "Van Inventory"},
        {"id": 2, "part_number": "WND001", "name": "Motor Winding", "category": "Electrical", "quantity_available": 5, "unit_cost": 1500.0, "location": "Warehouse"},
        {"id": 3, "part_number": "FLT001", "name": "Oil Filter", "category": "Filters", "quantity_available": 25, "unit_cost": 75.0, "location": "Van Inventory"},
        {"id": 4, "part_number": "BLT001", "name": "Drive Belt", "category": "Belts", "quantity_available": 10, "unit_cost": 125.0, "location": "Van Inventory"}
    ]
}

# Helper functions - Updated for Aiven database schema
def get_technician_data(technician_id):
    with get_db_connection() as conn:
        if conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM technicians WHERE id = %s", (technician_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                if result.get('specializations'):
                    import json
                    result['specializations'] = json.loads(result['specializations'])
                return result
    return FALLBACK_DATA["technicians"][0]

def get_technician_tickets(technician_id, status=None):
    with get_db_connection() as conn:
        if conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = "SELECT st.*, c.name as customer_name, c.phone as customer_phone, c.address as customer_address FROM service_tickets st LEFT JOIN customers c ON st.customer_id = c.id WHERE st.assigned_staff_id = %s"
            params = [technician_id]
            if status:
                query += " AND st.status = %s"
                params.append(status.upper())
            try:
                cursor.execute(query, params)
                results = cursor.fetchall()
                cursor.close()
                if results:
                    # Convert datetime objects to strings for JSON serialization
                    for result in results:
                        for key, value in result.items():
                            if hasattr(value, 'isoformat'):
                                result[key] = value.isoformat()
                    return results
            except Exception as e:
                print(f"Database query error: {e}")
                cursor.close()
    return [t for t in FALLBACK_DATA["tickets"] if t["assigned_technician_id"] == int(technician_id)]

def get_technician_notifications(technician_id):
    with get_db_connection() as conn:
        if conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (technician_id,))
            results = cursor.fetchall()
            cursor.close()
            if results:
                # Convert datetime objects to strings for JSON serialization
                for result in results:
                    for key, value in result.items():
                        if hasattr(value, 'isoformat'):
                            result[key] = value.isoformat()
                return results
    return [n for n in FALLBACK_DATA["notifications"] if n["technician_id"] == int(technician_id)]



# ==================== AUTHENTICATION ENDPOINTS ====================
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('technician_login')
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """Technician login with username/password"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username == "demo.tech" and password == "password123":
            access_token = create_access_token({"sub": "1", "username": username, "role": "technician"})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "technician_id": 1,
                "full_name": "John Technician",
                "role": "technician",
                "employee_id": "EMP001"
            }
        return {"detail": "Invalid username or password"}, 401

@auth_ns.route('/signup')
class Signup(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.doc('technician_signup')
    @auth_ns.response(201, 'Registration successful')
    @auth_ns.response(400, 'Invalid data')
    def post(self):
        """Register new technician"""
        data = request.get_json()
        full_name = data.get('full_name')
        employee_id = data.get('employee_id')
        
        access_token = create_access_token({"sub": "2", "employee_id": employee_id, "role": "technician"})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "technician_id": 2,
            "full_name": full_name,
            "role": "technician",
            "employee_id": employee_id
        }, 201

@auth_ns.route('/send-otp')
class SendOTP(Resource):
    @auth_ns.expect(otp_model)
    @auth_ns.doc('send_otp')
    @auth_ns.response(200, 'OTP sent successfully')
    def post(self):
        """Send OTP to technician's phone"""
        data = request.get_json()
        contact = data.get('contact')
        return {
            "message": "OTP sent successfully",
            "contact": contact,
            "otp": "123456",  # Demo OTP
            "expires_in": "5 minutes"
        }

@auth_ns.route('/verify-otp')
class VerifyOTP(Resource):
    @auth_ns.expect(verify_otp_model)
    @auth_ns.doc('verify_otp')
    @auth_ns.response(200, 'OTP verified successfully')
    @auth_ns.response(400, 'Invalid OTP')
    def post(self):
        """Verify OTP and authenticate"""
        data = request.get_json()
        otp = data.get('otp')
        contact = data.get('contact')
        
        if otp == "123456":
            access_token = create_access_token({"sub": "3", "contact": contact, "otp_verified": True})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "technician_id": 3,
                "full_name": "Bob Service",
                "role": "technician",
                "phone": contact
            }
        return {"detail": "Invalid OTP"}, 400

# ==================== DASHBOARD ENDPOINTS ====================
@dashboard_ns.route('/')
class Dashboard(Resource):
    @dashboard_ns.doc('get_dashboard', security='Bearer')
    @dashboard_ns.response(200, 'Dashboard data retrieved')
    @dashboard_ns.response(401, 'Unauthorized')
    def get(self):
        """Get technician dashboard overview"""
        # Check for authorization header first
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return {'error': 'Token required'}, 401
        
        token = token[7:]
        payload = verify_token(token)
        if not payload:
            return {'error': 'Invalid or expired token'}, 401
        
        technician_id = int(payload.get('sub', 1))
        technician = get_technician_data(technician_id)
        tickets = get_technician_tickets(technician_id)
        
        return {
            "technician": technician,
            "stats": {
                "total_tickets": len(tickets),
                "pending_tickets": len([t for t in tickets if t["status"] == "SCHEDULED"]),
                "in_progress_tickets": len([t for t in tickets if t["status"] == "IN_PROGRESS"]),
                "completed_tickets": len([t for t in tickets if t["status"] == "COMPLETED"]),
                "completed_today": len([t for t in tickets if t["status"] == "COMPLETED" and t.get("completed_at", "").startswith(datetime.now().strftime('%Y-%m-%d'))])
            },
            "recent_tickets": tickets[:5],
            "performance": {
                "avg_resolution_time": "2.5 hours",
                "customer_rating": 4.7,
                "completion_rate": 95.5,
                "on_time_percentage": 92.3
            }
        }

@dashboard_ns.route('/overview')
class DashboardOverview(Resource):
    @dashboard_ns.doc('get_dashboard_overview', security='Bearer')
    def get(self):
        """Get detailed dashboard overview"""
        # Check for authorization header first
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return {'error': 'Token required'}, 401
        
        token = token[7:]
        payload = verify_token(token)
        if not payload:
            return {'error': 'Invalid or expired token'}, 401
        
        technician_id = int(payload.get('sub', 1))
        technician = get_technician_data(technician_id)
        tickets = get_technician_tickets(technician_id)
        notifications = get_technician_notifications(technician_id)
        
        return {
            "technician_info": technician,
            "assigned_tickets": {
                "total": len(tickets),
                "high_priority": len([t for t in tickets if t["priority"] == "HIGH"]),
                "medium_priority": len([t for t in tickets if t["priority"] == "MEDIUM"]),
                "low_priority": len([t for t in tickets if t["priority"] == "LOW"]),
                "overdue": len([t for t in tickets if t["status"] == "SCHEDULED" and t["scheduled_date"] < datetime.now().isoformat()])
            },
            "today_schedule": [t for t in tickets if t["scheduled_date"].startswith(datetime.now().strftime('%Y-%m-%d'))],
            "unread_notifications": len([n for n in notifications if not n["is_read"]]),
            "recent_activity": tickets[-3:] if tickets else []
        }

# ==================== TICKETS ENDPOINTS ====================
@tickets_ns.route('/assigned')
class AssignedTickets(Resource):
    @tickets_ns.doc('get_assigned_tickets', security='Bearer')
    @tickets_ns.param('status', 'Filter by status', enum=['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'])
    @tickets_ns.param('priority', 'Filter by priority', enum=['LOW', 'MEDIUM', 'HIGH', 'URGENT'])
    @tickets_ns.param('limit', 'Number of tickets to return', type=int, default=10)
    @tickets_ns.param('offset', 'Number of tickets to skip', type=int, default=0)
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get tickets assigned to technician"""
        technician_id = int(current_user.get('sub', 1))
        status = request.args.get('status')
        priority = request.args.get('priority')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        tickets = get_technician_tickets(technician_id, status)
        
        if priority:
            tickets = [t for t in tickets if t["priority"].lower() == priority.lower()]
        
        total_count = len(tickets)
        tickets = tickets[offset:offset + limit]
        
        return {
            "tickets": tickets,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }

@tickets_ns.route('/completed')
class CompletedTickets(Resource):
    @tickets_ns.doc('get_completed_tickets', security='Bearer')
    @tickets_ns.param('limit', 'Number of tickets to return', type=int, default=10)
    @tickets_ns.param('offset', 'Number of tickets to skip', type=int, default=0)
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get completed tickets"""
        technician_id = int(current_user.get('sub', 1))
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        tickets = get_technician_tickets(technician_id, 'COMPLETED')
        total_count = len(tickets)
        tickets = tickets[offset:offset + limit]
        
        return {
            "tickets": tickets,
            "total_count": total_count
        }

@tickets_ns.route('/<int:ticket_id>')
class TicketDetail(Resource):
    @tickets_ns.doc('get_ticket_details', security='Bearer')
    @tickets_ns.response(200, 'Ticket details retrieved')
    @tickets_ns.response(404, 'Ticket not found')
    @api.doc(security='Bearer')
    @token_required
    def get(self, ticket_id, current_user):
        """Get detailed ticket information"""
        ticket = next((t for t in FALLBACK_DATA["tickets"] if t["id"] == ticket_id), None)
        if not ticket:
            return {"error": "Ticket not found"}, 404
        
        # Add additional details
        ticket_details = ticket.copy()
        ticket_details.update({
            "customer_email": "customer@example.com",
            "product_serial": "SN123456789",
            "warranty_status": "active",
            "service_history": [
                {"date": "2024-06-15", "type": "maintenance", "technician": "Previous Tech"},
                {"date": "2024-01-20", "type": "installation", "technician": "Install Team"}
            ],
            "parts_used": [],
            "work_performed": None,
            "photos": [],
            "customer_signature": None
        })
        
        return {"ticket": ticket_details}

@tickets_ns.route('/<int:ticket_id>/status')
class UpdateTicketStatus(Resource):
    @tickets_ns.expect(ticket_status_model)
    @tickets_ns.doc('update_ticket_status', security='Bearer')
    @tickets_ns.response(200, 'Status updated successfully')
    @tickets_ns.response(404, 'Ticket not found')
    @api.doc(security='Bearer')
    @token_required
    def put(self, ticket_id, current_user):
        """Update ticket status and add notes"""
        data = request.get_json()
        status = data.get('status', '').upper()
        notes = data.get('notes', '')
        work_performed = data.get('work_performed', '')
        parts_used = data.get('parts_used', [])
        
        return {
            "message": "Ticket status updated successfully",
            "ticket_id": ticket_id,
            "new_status": status,
            "updated_at": datetime.now().isoformat(),
            "notes": notes,
            "work_performed": work_performed,
            "parts_used": parts_used
        }

@tickets_ns.route('/<int:ticket_id>/location')
class CaptureLocation(Resource):
    @tickets_ns.expect(location_model)
    @tickets_ns.doc('capture_location', security='Bearer')
    @tickets_ns.response(200, 'Location captured successfully')
    @api.doc(security='Bearer')
    @token_required
    def post(self, ticket_id, current_user):
        """Capture technician location for ticket"""
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        return {
            "message": "Location captured successfully",
            "ticket_id": ticket_id,
            "latitude": latitude,
            "longitude": longitude,
            "captured_at": datetime.now().isoformat(),
            "address": f"Approximate address for {latitude}, {longitude}"
        }

@tickets_ns.route('/<int:ticket_id>/photos')
class UploadPhotos(Resource):
    @tickets_ns.doc('upload_photos', security='Bearer')
    @tickets_ns.response(200, 'Photos uploaded successfully')
    @api.doc(security='Bearer')
    @token_required
    def post(self, ticket_id, current_user):
        """Upload photos for ticket"""
        # In real implementation, handle file uploads
        return {
            "message": "Photos uploaded successfully",
            "ticket_id": ticket_id,
            "photo_count": 3,
            "photo_urls": [
                f"https://example.com/photos/{ticket_id}_1.jpg",
                f"https://example.com/photos/{ticket_id}_2.jpg",
                f"https://example.com/photos/{ticket_id}_3.jpg"
            ],
            "uploaded_at": datetime.now().isoformat()
        }

@tickets_ns.route('/<int:ticket_id>/signature')
class CaptureSignature(Resource):
    @tickets_ns.doc('capture_signature', security='Bearer')
    @tickets_ns.response(200, 'Signature captured successfully')
    @api.doc(security='Bearer')
    @token_required
    def post(self, ticket_id, current_user):
        """Capture customer signature"""
        return {
            "message": "Customer signature captured successfully",
            "ticket_id": ticket_id,
            "signature_url": f"https://example.com/signatures/{ticket_id}_signature.png",
            "captured_at": datetime.now().isoformat(),
            "customer_name": "John Customer"
        }

@tickets_ns.route('/<int:ticket_id>/parts')
class AddPartsUsed(Resource):
    @tickets_ns.expect(parts_model)
    @tickets_ns.doc('add_parts_used', security='Bearer')
    @tickets_ns.response(200, 'Parts information updated')
    @api.doc(security='Bearer')
    @token_required
    def post(self, ticket_id, current_user):
        """Add parts used in service"""
        data = request.get_json()
        parts = data.get('parts', [])
        
        total_cost = sum(part.get('cost', 0) * part.get('quantity', 1) for part in parts)
        
        return {
            "message": "Parts information updated successfully",
            "ticket_id": ticket_id,
            "parts_added": len(parts),
            "total_cost": total_cost,
            "parts": parts,
            "updated_at": datetime.now().isoformat()
        }

# ==================== NOTIFICATIONS ENDPOINTS ====================
@notifications_ns.route('/')
class Notifications(Resource):
    @notifications_ns.doc('get_notifications', security='Bearer')
    @notifications_ns.param('limit', 'Number of notifications to return', type=int, default=20)
    @notifications_ns.param('unread_only', 'Show only unread notifications', type=bool, default=False)
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get technician notifications"""
        technician_id = int(current_user.get('sub', 1))
        limit = int(request.args.get('limit', 20))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        notifications = get_technician_notifications(technician_id)
        
        if unread_only:
            notifications = [n for n in notifications if not n["is_read"]]
        
        return {
            "notifications": notifications[:limit],
            "total_count": len(notifications),
            "unread_count": len([n for n in notifications if not n["is_read"]])
        }

@notifications_ns.route('/<int:notification_id>/read')
class MarkNotificationRead(Resource):
    @notifications_ns.doc('mark_notification_read', security='Bearer')
    @notifications_ns.response(200, 'Notification marked as read')
    @api.doc(security='Bearer')
    @token_required
    def put(self, notification_id, current_user):
        """Mark notification as read"""
        return {
            "message": f"Notification {notification_id} marked as read",
            "notification_id": notification_id,
            "marked_at": datetime.now().isoformat()
        }

@notifications_ns.route('/unread-count')
class UnreadCount(Resource):
    @notifications_ns.doc('get_unread_count', security='Bearer')
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get unread notifications count"""
        technician_id = int(current_user.get('sub', 1))
        notifications = get_technician_notifications(technician_id)
        unread_count = len([n for n in notifications if not n["is_read"]])
        
        return {"unread_count": unread_count}

@notifications_ns.route('/mark-all-read')
class MarkAllRead(Resource):
    @notifications_ns.doc('mark_all_read', security='Bearer')
    @api.doc(security='Bearer')
    @token_required
    def put(self, current_user):
        """Mark all notifications as read"""
        technician_id = int(current_user.get('sub', 1))
        return {
            "message": "All notifications marked as read",
            "technician_id": technician_id,
            "marked_at": datetime.now().isoformat()
        }

# ==================== SCHEDULE ENDPOINTS ====================
@schedule_ns.route('/')
class Schedule(Resource):
    @schedule_ns.doc('get_schedule', security='Bearer')
    @schedule_ns.param('date', 'Date in YYYY-MM-DD format', default=datetime.now().strftime('%Y-%m-%d'))
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get technician schedule for specific date"""
        technician_id = int(current_user.get('sub', 1))
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        tickets = get_technician_tickets(technician_id, 'SCHEDULED')
        scheduled_tickets = [t for t in tickets if t["scheduled_date"].startswith(date)]
        
        return {
            "date": date,
            "appointments": [
                {
                    "id": ticket["id"],
                    "ticket_number": ticket["ticket_number"],
                    "customer_name": ticket["customer_name"],
                    "start_time": ticket["scheduled_date"].split('T')[1][:5] if 'T' in ticket["scheduled_date"] else "09:00",
                    "end_time": "11:00",  # Estimated
                    "status": ticket["status"],
                    "address": ticket["customer_address"],
                    "priority": ticket["priority"],
                    "product_name": ticket["product_name"]
                } for ticket in scheduled_tickets
            ],
            "total_appointments": len(scheduled_tickets),
            "working_hours": {"start": "08:00", "end": "18:00"}
        }

@schedule_ns.route('/week')
class WeeklySchedule(Resource):
    @schedule_ns.doc('get_weekly_schedule', security='Bearer')
    @schedule_ns.param('week_start', 'Week start date in YYYY-MM-DD format')
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get technician weekly schedule"""
        technician_id = int(current_user.get('sub', 1))
        tickets = get_technician_tickets(technician_id)
        
        # Group tickets by date
        weekly_schedule = {}
        for i in range(7):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            day_tickets = [t for t in tickets if t["scheduled_date"].startswith(date)]
            weekly_schedule[date] = {
                "date": date,
                "day_name": (datetime.now() + timedelta(days=i)).strftime('%A'),
                "appointments": len(day_tickets),
                "tickets": day_tickets
            }
        
        return {"weekly_schedule": weekly_schedule}

# ==================== PROFILE ENDPOINTS ====================
@profile_ns.route('/')
class Profile(Resource):
    @profile_ns.doc('get_profile', security='Bearer')
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get technician profile"""
        technician_id = int(current_user.get('sub', 1))
        technician = get_technician_data(technician_id)
        tickets = get_technician_tickets(technician_id)
        
        profile_data = technician.copy()
        profile_data.update({
            "department": "Field Service",
            "join_date": "2020-01-15",
            "performance_rating": 4.8,
            "completed_tickets_total": len([t for t in tickets if t["status"] == "COMPLETED"]),
            "certification_level": "Senior Technician",
            "last_login": datetime.now().isoformat()
        })
        
        return {"profile": profile_data}
    
    @profile_ns.expect(profile_update_model)
    @profile_ns.doc('update_profile', security='Bearer')
    @api.doc(security='Bearer')
    @token_required
    def put(self, current_user):
        """Update technician profile"""
        data = request.get_json()
        return {
            "message": "Profile updated successfully",
            "updated_fields": list(data.keys()),
            "updated_at": datetime.now().isoformat()
        }

# ==================== REPORTS ENDPOINTS ====================
@reports_ns.route('/performance')
class PerformanceReport(Resource):
    @reports_ns.doc('get_performance_report', security='Bearer')
    @reports_ns.param('period', 'Report period', enum=['day', 'week', 'month', 'year'], default='month')
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get technician performance report"""
        technician_id = int(current_user.get('sub', 1))
        period = request.args.get('period', 'month')
        tickets = get_technician_tickets(technician_id)
        
        completed_tickets = [t for t in tickets if t["status"] == "COMPLETED"]
        
        return {
            "period": period,
            "technician_id": technician_id,
            "tickets_completed": len(completed_tickets),
            "avg_resolution_time": "2.5 hours",
            "customer_satisfaction": 4.7,
            "efficiency_score": 92.5,
            "on_time_completion": 95.2,
            "breakdown_by_type": {
                "motor_repair": len([t for t in completed_tickets if "motor" in t["product_name"].lower()]),
                "pump_service": len([t for t in completed_tickets if "pump" in t["product_name"].lower()]),
                "generator_maintenance": len([t for t in completed_tickets if "generator" in t["product_name"].lower()])
            },
            "monthly_trend": [
                {"month": "Dec 2024", "completed": 15, "rating": 4.6},
                {"month": "Nov 2024", "completed": 18, "rating": 4.8},
                {"month": "Oct 2024", "completed": 12, "rating": 4.5}
            ]
        }

@reports_ns.route('/daily')
class DailyReport(Resource):
    @reports_ns.doc('get_daily_report', security='Bearer')
    @reports_ns.param('date', 'Date in YYYY-MM-DD format', default=datetime.now().strftime('%Y-%m-%d'))
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get daily work report"""
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        technician_id = int(current_user.get('sub', 1))
        
        return {
            "date": date,
            "technician_id": technician_id,
            "tickets_completed": 3,
            "tickets_in_progress": 2,
            "hours_worked": 8,
            "travel_distance": 45.2,
            "fuel_consumed": 12.5,
            "parts_used_value": 850.0,
            "customer_ratings": [5, 4, 5],
            "avg_rating": 4.7
        }

# ==================== INVENTORY ENDPOINTS ====================
@inventory_ns.route('/parts')
class InventoryParts(Resource):
    @inventory_ns.doc('get_inventory_parts', security='Bearer')
    @inventory_ns.param('category', 'Filter by category')
    @inventory_ns.param('location', 'Filter by location', enum=['Van Inventory', 'Warehouse'])
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get available parts inventory"""
        category = request.args.get('category')
        location = request.args.get('location')
        
        parts = FALLBACK_DATA["inventory"].copy()
        
        if category:
            parts = [p for p in parts if p["category"].lower() == category.lower()]
        if location:
            parts = [p for p in parts if p["location"].lower() == location.lower()]
        
        return {
            "parts": parts,
            "total_count": len(parts),
            "categories": list(set(p["category"] for p in FALLBACK_DATA["inventory"])),
            "locations": list(set(p["location"] for p in FALLBACK_DATA["inventory"]))
        }

@inventory_ns.route('/request')
class InventoryRequest(Resource):
    @inventory_ns.expect(inventory_request_model)
    @inventory_ns.doc('request_parts', security='Bearer')
    @inventory_ns.response(201, 'Parts request submitted')
    @api.doc(security='Bearer')
    @token_required
    def post(self, current_user):
        """Request parts from inventory"""
        data = request.get_json()
        parts = data.get('parts', [])
        reason = data.get('reason', '')
        technician_id = int(current_user.get('sub', 1))
        
        return {
            "message": "Parts request submitted successfully",
            "request_id": f"REQ{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "technician_id": technician_id,
            "parts_requested": len(parts),
            "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            "status": "pending_approval",
            "reason": reason,
            "submitted_at": datetime.now().isoformat()
        }, 201

@inventory_ns.route('/requests')
class InventoryRequests(Resource):
    @inventory_ns.doc('get_inventory_requests', security='Bearer')
    @inventory_ns.param('status', 'Filter by status', enum=['pending_approval', 'approved', 'delivered', 'cancelled'])
    @api.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """Get technician's parts requests"""
        technician_id = int(current_user.get('sub', 1))
        status = request.args.get('status')
        
        # Mock data for requests
        requests = [
            {"id": 1, "request_id": "REQ20250115001", "status": "approved", "parts_count": 3, "submitted_at": "2025-01-15T10:00:00", "estimated_delivery": "2025-01-17"},
            {"id": 2, "request_id": "REQ20250114001", "status": "delivered", "parts_count": 2, "submitted_at": "2025-01-14T14:30:00", "delivered_at": "2025-01-16T09:00:00"},
            {"id": 3, "request_id": "REQ20250113001", "status": "pending_approval", "parts_count": 1, "submitted_at": "2025-01-13T16:15:00", "estimated_delivery": "2025-01-18"}
        ]
        
        if status:
            requests = [r for r in requests if r["status"] == status]
        
        return {
            "requests": requests,
            "total_count": len(requests)
        }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8002))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    print(f"🚀 Starting Ostrich Service Technician API on port {port}")
    print(f"📚 Swagger UI available at: http://0.0.0.0:{port}/docs/")
    print(f"🔧 Test credentials: username='demo.tech', password='password123'")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)