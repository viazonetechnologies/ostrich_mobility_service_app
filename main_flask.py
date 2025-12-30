from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
import pymysql
from contextlib import contextmanager

app = Flask(__name__)
CORS(app)

# Swagger API setup
api = Api(app, 
    version='1.0', 
    title='Ostrich Service API',
    description='Service technician mobile app API for Ostrich Product & Service Management System',
    doc='/docs/'
)

# Namespaces
auth_ns = api.namespace('api/v1/auth', description='Authentication operations')
dashboard_ns = api.namespace('api/v1/dashboard', description='Dashboard operations')
tickets_ns = api.namespace('api/v1/tickets', description='Ticket operations')
notifications_ns = api.namespace('api/v1/notifications', description='Notifications operations')
schedule_ns = api.namespace('api/v1/schedule', description='Schedule operations')
profile_ns = api.namespace('api/v1/profile', description='Profile operations')
reports_ns = api.namespace('api/v1/reports', description='Reports operations')
inventory_ns = api.namespace('api/v1/inventory', description='Inventory operations')

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'service-secret-key')
app.config['SECRET_KEY'] = SECRET_KEY

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'your_password_here'),
    'database': os.getenv('DB_NAME', 'ostrich_db'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4'
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

# Auth decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
            payload = verify_token(token)
            if payload:
                return f(current_user=payload, *args, **kwargs)
        return jsonify({'error': 'Token required'}), 401
    return decorated

# Fallback data for testing
FALLBACK_DATA = {
    "technicians": [
        {"id": 1, "employee_id": "EMP001", "full_name": "John Technician", "email": "john.tech@ostrich.com", "phone": "9876543220", "role": "technician"},
        {"id": 2, "employee_id": "EMP002", "full_name": "Jane Tech", "email": "jane.tech@ostrich.com", "phone": "9876543221", "role": "technician"},
        {"id": 3, "employee_id": "EMP003", "full_name": "Bob Service", "email": "bob.tech@ostrich.com", "phone": "9876543222", "role": "technician"}
    ],
    "tickets": [
        {"id": 1, "ticket_number": "TKT000001", "customer_name": "John Customer", "customer_phone": "9876543210", "product_name": "3HP Motor", "issue_description": "Motor not starting", "status": "SCHEDULED", "priority": "HIGH", "assigned_technician_id": 1},
        {"id": 2, "ticket_number": "TKT000002", "customer_name": "Jane Smith", "customer_phone": "9876543211", "product_name": "5HP Pump", "issue_description": "Pump maintenance", "status": "IN_PROGRESS", "priority": "MEDIUM", "assigned_technician_id": 1},
        {"id": 3, "ticket_number": "TKT000003", "customer_name": "Bob Wilson", "customer_phone": "9876543212", "product_name": "7HP Generator", "issue_description": "Generator repair", "status": "COMPLETED", "priority": "HIGH", "assigned_technician_id": 2}
    ],
    "notifications": [
        {"id": 1, "technician_id": 1, "title": "New Ticket Assigned", "message": "Ticket TKT000004 assigned", "type": "info", "is_read": False, "created_at": "2025-01-15T10:00:00"},
        {"id": 2, "technician_id": 1, "title": "Urgent Ticket", "message": "High priority ticket needs attention", "type": "urgent", "is_read": False, "created_at": "2025-01-15T09:30:00"}
    ]
}

# Database helper functions
def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """Execute database query with fallback"""
    try:
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(query, params or [])
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
    except Exception as e:
        print(f"Database query failed: {e}")
    return None

def get_technician_data(technician_id):
    """Get technician data with fallback"""
    result = execute_query("SELECT * FROM users WHERE id = %s AND role = 'service_staff'", [technician_id], fetch_one=True)
    if result:
        return result
    return next((t for t in FALLBACK_DATA["technicians"] if t["id"] == int(technician_id)), FALLBACK_DATA["technicians"][0])

def get_technician_tickets(technician_id, status=None):
    """Get technician tickets with fallback"""
    query = "SELECT * FROM service_tickets WHERE assigned_staff_id = %s"
    params = [technician_id]
    if status:
        query += " AND status = %s"
        params.append(status)
    
    result = execute_query(query, params)
    if result:
        return result
    
    tickets = [t for t in FALLBACK_DATA["tickets"] if t["assigned_technician_id"] == int(technician_id)]
    if status:
        tickets = [t for t in tickets if t["status"].lower() == status.lower()]
    return tickets

# Models
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

signup_model = api.model('Signup', {
    'full_name': fields.String(required=True, description='Full name'),
    'employee_id': fields.String(required=True, description='Employee ID')
})

otp_model = api.model('OTP', {
    'contact': fields.String(required=True, description='Contact number')
})

verify_otp_model = api.model('VerifyOTP', {
    'otp': fields.String(required=True, description='OTP code')
})

# Basic routes
@app.route('/')
def read_root():
    return jsonify({
        "message": "Ostrich Service Support API",
        "version": "1.0.0",
        "docs": "/docs/",
        "status": "running"
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "ostrich-service-api"
    })

# Authentication endpoints
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        """Technician login with username/password"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username == "demo.tech" and password == "password123":
            access_token = create_access_token({"sub": "1", "username": username})
            return {
                "access_token": access_token,
                "technician_id": 1,
                "full_name": "John Technician",
                "role": "technician"
            }
        return {"detail": "Invalid username or password"}, 401

@auth_ns.route('/signup')
class Signup(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        """Register new technician"""
        data = request.get_json()
        full_name = data.get('full_name')
        employee_id = data.get('employee_id')
        
        access_token = create_access_token({"sub": "2", "employee_id": employee_id})
        return {
            "access_token": access_token,
            "technician_id": 2,
            "full_name": full_name,
            "role": "technician"
        }

@auth_ns.route('/send-otp')
class SendOTP(Resource):
    @auth_ns.expect(otp_model)
    def post(self):
        """Send OTP to technician"""
        data = request.get_json()
        contact = data.get('contact')
        return {
            "message": "OTP sent successfully",
            "contact": contact,
            "otp": "123456"
        }

@auth_ns.route('/verify-otp')
class VerifyOTP(Resource):
    @auth_ns.expect(verify_otp_model)
    def post(self):
        """Verify OTP and authenticate"""
        data = request.get_json()
        otp = data.get('otp')
        
        if otp == "123456":
            access_token = create_access_token({"sub": "3", "otp_verified": True})
            return {
                "access_token": access_token,
                "technician_id": 3,
                "full_name": "OTP Verified Tech",
                "role": "technician"
            }
        return {"detail": "Invalid OTP"}, 400

@dashboard_ns.route('/')
class Dashboard(Resource):
    @dashboard_ns.doc('get_dashboard')
    @token_required
    def get(self, current_user):
        """Get technician dashboard with real data and fallback"""
        technician_id = current_user.get('sub', '1')
        technician = get_technician_data(technician_id)
        assigned_tickets = get_technician_tickets(technician_id, 'SCHEDULED')
        in_progress_tickets = get_technician_tickets(technician_id, 'IN_PROGRESS')
        completed_tickets = get_technician_tickets(technician_id, 'COMPLETED')
        
        return {
            "stats": {
                "assigned_tickets": len(assigned_tickets),
                "completed_today": len([t for t in completed_tickets if t.get('completed_date', '').startswith(datetime.now().strftime('%Y-%m-%d'))]),
                "pending_tickets": len(assigned_tickets),
                "in_progress": len(in_progress_tickets),
                "total_completed_this_month": len(completed_tickets)
            },
            "recent_tickets": (assigned_tickets + in_progress_tickets)[:5],
            "performance": {
                "avg_resolution_time": "2.5 hours",
                "customer_rating": 4.7,
                "completion_rate": 95.5
            }
        }

@tickets_ns.route('/assigned')
class AssignedTickets(Resource):
    @tickets_ns.doc('get_assigned_tickets')
    @token_required
    def get(self, current_user):
        """Get tickets assigned to technician with real data and fallback"""
        technician_id = current_user.get('sub', '1')
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        tickets = get_technician_tickets(technician_id)
        
        if status:
            tickets = [t for t in tickets if t.get('status', '').lower() == status.lower()]
        if priority:
            tickets = [t for t in tickets if t.get('priority', '').lower() == priority.lower()]
        
        return {
            "tickets": tickets,
            "total_count": len(tickets)
        }

# ========== DASHBOARD ENDPOINTS ==========
@app.route('/api/v1/dashboard/')
@token_required
def get_dashboard(current_user):
    return jsonify({
        "stats": {
            "assigned_tickets": 8,
            "completed_today": 3,
            "pending_tickets": 5,
            "in_progress": 2,
            "total_completed_this_month": 45
        },
        "recent_tickets": [
            {
                "id": 1,
                "ticket_number": "TKT000001",
                "customer_name": "John Customer",
                "status": "in_progress",
                "priority": "high",
                "scheduled_time": datetime.now().isoformat()
            },
            {
                "id": 2,
                "ticket_number": "TKT000002",
                "customer_name": "Jane Smith",
                "status": "scheduled",
                "priority": "medium",
                "scheduled_time": (datetime.now() + timedelta(hours=2)).isoformat()
            }
        ],
        "performance": {
            "avg_resolution_time": "2.5 hours",
            "customer_rating": 4.7,
            "completion_rate": 95.5
        }
    })

@app.route('/api/v1/dashboard/overview')
@token_required
def get_dashboard_overview(current_user):
    return jsonify({
        "technician_info": {
            "name": "John Technician",
            "employee_id": "EMP001",
            "technician_id": current_user.get('sub', '1')
        },
        "assigned_tickets": {
            "total": 8,
            "high_priority": 3,
            "medium_priority": 4,
            "low_priority": 1,
            "overdue": 1
        },
        "stats": {
            "completed_today": 3,
            "completed_this_week": 15,
            "completed_this_month": 45,
            "avg_completion_time": "2.5 hours"
        },
        "completed_work": {
            "today": [
                {"ticket": "TKT000003", "customer": "Bob Wilson", "time": "2 hours"}
            ],
            "this_week": 15,
            "customer_rating": 4.8
        },
        "upcoming_appointments": [
            {
                "ticket_number": "TKT000001",
                "customer_name": "John Customer",
                "scheduled_time": datetime.now().isoformat(),
                "priority": "high"
            }
        ]
    })

# ========== TICKETS ENDPOINTS ==========
@app.route('/api/v1/tickets/assigned')
@token_required
def get_assigned_tickets(current_user):
    status = request.args.get('status')
    priority = request.args.get('priority')
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    tickets = [
        {
            "id": 1,
            "ticket_number": "TKT000001",
            "customer_name": "John Customer",
            "customer_phone": "9876543210",
            "customer_address": "123 Main St, Mumbai, Maharashtra",
            "product_name": "3HP Motor",
            "issue_description": "Motor not starting, making unusual noise",
            "status": "SCHEDULED",
            "priority": "HIGH",
            "scheduled_date": datetime.now().isoformat(),
            "assigned_technician_id": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 2,
            "ticket_number": "TKT000002",
            "customer_name": "Jane Smith",
            "customer_phone": "9876543211",
            "customer_address": "456 Service Ave, Delhi",
            "product_name": "5HP Pump",
            "issue_description": "Pump not priming properly",
            "status": "IN_PROGRESS",
            "priority": "MEDIUM",
            "scheduled_date": (datetime.now() + timedelta(hours=1)).isoformat(),
            "assigned_technician_id": 1,
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    # Apply filters
    if status:
        tickets = [t for t in tickets if t['status'].lower() == status.lower()]
    if priority:
        tickets = [t for t in tickets if t['priority'].lower() == priority.lower()]
    
    # Apply pagination
    total_count = len(tickets)
    tickets = tickets[offset:offset + limit]
    
    return jsonify({
        "tickets": tickets,
        "total_count": total_count
    })

@app.route('/api/v1/tickets/completed')
@token_required
def get_completed_tickets(current_user):
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    tickets = [
        {
            "id": 3,
            "ticket_number": "TKT000003",
            "customer_name": "Bob Wilson",
            "customer_phone": "9876543212",
            "customer_address": "789 Repair Rd, Bangalore",
            "product_name": "7HP Generator",
            "issue_description": "Generator not starting",
            "status": "COMPLETED",
            "priority": "HIGH",
            "scheduled_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "assigned_technician_id": 1,
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "updated_at": (datetime.now() - timedelta(hours=6)).isoformat()
        }
    ]
    
    return jsonify({
        "tickets": tickets[offset:offset + limit],
        "total_count": len(tickets)
    })

@app.route('/api/v1/tickets/<int:ticket_id>')
@token_required
def get_ticket_details(ticket_id, current_user):
    return jsonify({
        "id": ticket_id,
        "ticket_number": "TKT000001",
        "customer_name": "John Customer",
        "customer_phone": "9876543210",
        "customer_address": "123 Main St, Mumbai, Maharashtra",
        "customer_email": "john@example.com",
        "product_name": "3HP Motor",
        "product_model": "OST-3HP-SP",
        "product_serial": "SN123456789",
        "issue_description": "Motor not starting, making unusual noise when attempting to start",
        "status": "SCHEDULED",
        "priority": "HIGH",
        "scheduled_date": datetime.now().isoformat(),
        "assigned_technician_id": 1,
        "technician_name": "John Technician",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "completion_notes": None,
        "customer_signature": None,
        "parts_used": [],
        "work_performed": None,
        "photos": []
    })

@app.route('/api/v1/tickets/<int:ticket_id>/status', methods=['PUT'])
@token_required
def update_ticket_status(ticket_id, current_user):
    data = request.get_json()
    status = data.get('status', '').upper()
    notes = data.get('notes', '')
    work_performed = data.get('work_performed', '')
    parts_used = data.get('parts_used', [])
    
    return jsonify({
        "message": "Ticket status updated successfully",
        "ticket_id": ticket_id,
        "new_status": status,
        "updated_at": datetime.now().isoformat(),
        "notes": notes
    })

@app.route('/api/v1/tickets/<int:ticket_id>/location', methods=['POST'])
@token_required
def capture_location(ticket_id, current_user):
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    
    return jsonify({
        "message": "Location captured successfully",
        "ticket_id": ticket_id,
        "latitude": latitude,
        "longitude": longitude,
        "captured_at": datetime.now().isoformat(),
        "address": "Approximate address based on coordinates"
    })

@app.route('/api/v1/tickets/<int:ticket_id>/photos', methods=['POST'])
@token_required
def upload_ticket_photos(ticket_id, current_user):
    return jsonify({
        "message": "Photos uploaded successfully",
        "ticket_id": ticket_id,
        "photo_count": 3,
        "photo_urls": [
            f"https://example.com/photos/{ticket_id}_1.jpg",
            f"https://example.com/photos/{ticket_id}_2.jpg",
            f"https://example.com/photos/{ticket_id}_3.jpg"
        ]
    })

@app.route('/api/v1/tickets/<int:ticket_id>/signature', methods=['POST'])
@token_required
def capture_signature(ticket_id, current_user):
    return jsonify({
        "message": "Customer signature captured successfully",
        "ticket_id": ticket_id,
        "signature_url": f"https://example.com/signatures/{ticket_id}_signature.png",
        "captured_at": datetime.now().isoformat()
    })

@app.route('/api/v1/tickets/<int:ticket_id>/parts', methods=['POST'])
@token_required
def add_parts_used(ticket_id, current_user):
    data = request.get_json()
    parts = data.get('parts', [])
    
    return jsonify({
        "message": "Parts information updated successfully",
        "ticket_id": ticket_id,
        "parts_added": len(parts),
        "total_cost": sum(part.get('cost', 0) for part in parts)
    })

# ========== NOTIFICATIONS ENDPOINTS ==========
@app.route('/api/v1/notifications/')
@token_required
def get_notifications(current_user):
    return jsonify([
        {
            "id": 1,
            "title": "New Ticket Assigned",
            "message": "You have been assigned ticket TKT000004 for motor repair",
            "type": "info",
            "is_read": False,
            "created_at": datetime.now().isoformat(),
            "ticket_id": 4
        },
        {
            "id": 2,
            "title": "Urgent Ticket",
            "message": "High priority ticket TKT000005 requires immediate attention",
            "type": "urgent",
            "is_read": False,
            "created_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "ticket_id": 5
        },
        {
            "id": 3,
            "title": "Schedule Update",
            "message": "Your schedule for tomorrow has been updated",
            "type": "info",
            "is_read": True,
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "ticket_id": None
        }
    ])

@app.route('/api/v1/notifications/<int:notification_id>/read', methods=['PUT'])
@token_required
def mark_notification_read(notification_id, current_user):
    return jsonify({
        "message": "Notification marked as read",
        "notification_id": notification_id
    })

@app.route('/api/v1/notifications/unread-count')
@token_required
def get_unread_count(current_user):
    return jsonify({
        "unread_count": 2
    })

# ========== SCHEDULE ENDPOINTS ==========
@app.route('/api/v1/schedule/')
@token_required
def get_schedule(current_user):
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    return jsonify({
        "date": date,
        "appointments": [
            {
                "id": 1,
                "ticket_number": "TKT000001",
                "customer_name": "John Customer",
                "start_time": "09:00",
                "end_time": "11:00",
                "status": "scheduled",
                "address": "123 Main St, Mumbai",
                "priority": "high"
            },
            {
                "id": 2,
                "ticket_number": "TKT000002",
                "customer_name": "Jane Smith",
                "start_time": "14:00",
                "end_time": "16:00",
                "status": "scheduled",
                "address": "456 Service Ave, Delhi",
                "priority": "medium"
            }
        ],
        "total_appointments": 2,
        "working_hours": {
            "start": "08:00",
            "end": "18:00"
        }
    })

# ========== PROFILE ENDPOINTS ==========
@app.route('/api/v1/profile/')
@token_required
def get_profile(current_user):
    return jsonify({
        "id": 1,
        "employee_id": "EMP001",
        "full_name": "John Technician",
        "email": "john.tech@ostrich.com",
        "phone": "9876543220",
        "role": "technician",
        "department": "Field Service",
        "experience_years": 5,
        "specializations": ["Motors", "Pumps", "Generators"],
        "certification_level": "Senior Technician",
        "join_date": "2020-01-15",
        "performance_rating": 4.8,
        "completed_tickets_total": 1250
    })

@app.route('/api/v1/profile/', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    return jsonify({
        "message": "Profile updated successfully",
        "updated_fields": list(data.keys())
    })

# ========== REPORTS ENDPOINTS ==========
@app.route('/api/v1/reports/performance')
@token_required
def get_performance_report(current_user):
    period = request.args.get('period', 'month')  # day, week, month, year
    
    return jsonify({
        "period": period,
        "tickets_completed": 45,
        "avg_resolution_time": "2.5 hours",
        "customer_satisfaction": 4.7,
        "efficiency_score": 92.5,
        "on_time_completion": 95.2,
        "breakdown_by_type": {
            "motor_repair": 20,
            "pump_service": 15,
            "generator_maintenance": 10
        },
        "daily_stats": [
            {"date": "2025-12-01", "completed": 3, "avg_time": "2.2h"},
            {"date": "2025-12-02", "completed": 4, "avg_time": "2.8h"},
            {"date": "2025-12-03", "completed": 2, "avg_time": "1.9h"}
        ]
    })

# ========== INVENTORY ENDPOINTS ==========
@app.route('/api/v1/inventory/')
@token_required
def get_inventory(current_user):
    return jsonify([
        {
            "id": 1,
            "part_number": "BRG001",
            "name": "Motor Bearing",
            "category": "Bearings",
            "quantity_available": 15,
            "unit_cost": 250.0,
            "location": "Van Inventory"
        },
        {
            "id": 2,
            "part_number": "WND001",
            "name": "Motor Winding",
            "category": "Electrical",
            "quantity_available": 5,
            "unit_cost": 1500.0,
            "location": "Warehouse"
        }
    ])

@app.route('/api/v1/inventory/request', methods=['POST'])
@token_required
def request_parts(current_user):
    data = request.get_json()
    parts = data.get('parts', [])
    
    return jsonify({
        "message": "Parts request submitted successfully",
        "request_id": "REQ000123",
        "parts_requested": len(parts),
        "estimated_delivery": "2025-12-12",
        "status": "pending_approval"
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8002))
    app.run(host="0.0.0.0", port=port, debug=False)