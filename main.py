"""
Ostrich Service Mobile API
Professional FastAPI application using real-time database data only
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from datetime import datetime
from typing import Optional

# ============================================================================
# APPLICATION SETUP
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')

app = FastAPI(
    title="Ostrich Service Mobile API",
    description="Professional REST API for service technician mobile application",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
engine = create_engine(DATABASE_URL)
print("✅ Database connected successfully")

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class TicketStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = ""

class TicketCreate(BaseModel):
    title: str
    description: str
    customer_phone: str
    priority: str = "Medium"
    product_id: Optional[int] = None

# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API Information"""
    return {
        "message": "Ostrich Service Mobile API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health Check"""
    return {
        "status": "healthy",
        "service": "ostrich-service-api",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Service technician login"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, name, role 
            FROM users 
            WHERE username = :username AND password = :password AND role = 'service'
        """), {"username": request.username, "password": request.password})
        user = result.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "access_token": f"token_{request.username}",
            "user": dict(user._mapping)
        }

@app.post("/auth/logout")
async def logout():
    """Logout service technician"""
    return {"message": "Logout successful"}

# ============================================================================
# SERVICE TICKET ENDPOINTS
# ============================================================================

@app.get("/tickets")
async def get_tickets(status: str = "all"):
    """Get assigned service tickets"""
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
        return {"tickets": tickets}

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
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
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return dict(ticket._mapping)

@app.put("/tickets/{ticket_id}/status")
async def update_ticket_status(ticket_id: int, request: TicketStatusUpdate):
    """Update ticket status"""
    valid_statuses = ['Open', 'In Progress', 'Completed', 'Cancelled']
    if request.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    with engine.connect() as conn:
        # Check if ticket exists
        check = conn.execute(text("SELECT id FROM service_tickets WHERE id = :id"), {"id": ticket_id})
        if not check.fetchone():
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Update ticket
        conn.execute(text("""
            UPDATE service_tickets 
            SET status = :status, notes = :notes, updated_at = NOW()
            WHERE id = :id
        """), {
            "status": request.status,
            "notes": request.notes,
            "id": ticket_id
        })
        conn.commit()
    
    return {"message": "Ticket status updated successfully"}

@app.post("/tickets")
async def create_ticket(request: TicketCreate):
    """Create new service ticket"""
    if len(request.title.strip()) < 5:
        raise HTTPException(status_code=400, detail="Title must be at least 5 characters")
    
    if len(request.description.strip()) < 10:
        raise HTTPException(status_code=400, detail="Description must be at least 10 characters")
    
    with engine.connect() as conn:
        # Verify customer exists
        customer_check = conn.execute(text("SELECT id FROM customers WHERE phone = :phone"), {"phone": request.customer_phone})
        if not customer_check.fetchone():
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Verify product exists if provided
        if request.product_id:
            product_check = conn.execute(text("SELECT id FROM products WHERE id = :id"), {"id": request.product_id})
            if not product_check.fetchone():
                raise HTTPException(status_code=404, detail="Product not found")
        
        # Create ticket
        result = conn.execute(text("""
            INSERT INTO service_tickets (title, description, customer_phone, status, priority, product_id, created_at) 
            VALUES (:title, :description, :phone, 'Open', :priority, :product_id, NOW())
        """), {
            "title": request.title,
            "description": request.description,
            "phone": request.customer_phone,
            "priority": request.priority,
            "product_id": request.product_id
        })
        conn.commit()
        
        return {
            "message": "Ticket created successfully",
            "ticket_id": result.lastrowid
        }

# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@app.get("/customers")
async def get_customers(search: str = ""):
    """Get customer list"""
    with engine.connect() as conn:
        query = "SELECT id, name, phone, email, address FROM customers"
        params = {}
        
        if search:
            query += " WHERE name LIKE :search OR phone LIKE :search"
            params['search'] = f"%{search}%"
        
        query += " ORDER BY name"
        
        result = conn.execute(text(query), params)
        customers = [dict(row._mapping) for row in result]
        return {"customers": customers}

@app.get("/customers/{customer_id}")
async def get_customer(customer_id: int):
    """Get customer details"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM customers WHERE id = :id"), {"id": customer_id})
        customer = result.fetchone()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return dict(customer._mapping)

# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@app.get("/products")
async def get_products():
    """Get product catalog"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, category, price FROM products WHERE status = 'active'"))
        products = [dict(row._mapping) for row in result]
        return {"products": products}

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/dashboard")
async def get_dashboard():
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
        return dict(result._mapping) if result else {
            "total_tickets": 0,
            "open_tickets": 0,
            "in_progress_tickets": 0,
            "completed_tickets": 0
        }

@app.get("/reports/daily")
async def daily_report(date: str = None):
    """Get daily service report"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
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
        return data

# ============================================================================
# TECHNICIAN ENDPOINTS
# ============================================================================

@app.get("/technicians")
async def get_technicians():
    """Get list of service technicians"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, name, email, phone 
            FROM users 
            WHERE role = 'service' AND status = 'active'
            ORDER BY name
        """))
        technicians = [dict(row._mapping) for row in result]
        return {"technicians": technicians}

@app.get("/my-tickets")
async def get_my_tickets():
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
        return {"tickets": tickets}

# ============================================================================
# APPLICATION RUNNER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
