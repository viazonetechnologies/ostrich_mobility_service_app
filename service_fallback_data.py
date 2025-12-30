"""
Enhanced Service App Fallback Data Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_fallback_data import *
from datetime import datetime, timedelta
import random

class ServiceAppData:
    def __init__(self):
        self.technicians = {u["username"]: u for u in USERS_DATA if u["role"] == "technician"}
        self.customers = CUSTOMERS_DATA
        self.products = PRODUCTS_DATA
        self.services = SERVICES_DATA
        
    def get_technician_by_username(self, username):
        return self.technicians.get(username)
    
    def get_technician_dashboard(self, technician_id):
        technician = next((u for u in USERS_DATA if u["id"] == technician_id), None)
        if not technician:
            return None
            
        # Get assigned tickets
        assigned_tickets = [s for s in self.services if s["technician_id"] == technician_id and s["status"] in ["SCHEDULED", "IN_PROGRESS"]]
        completed_tickets = [s for s in self.services if s["technician_id"] == technician_id and s["status"] == "COMPLETED"]
        
        # Enhance tickets with customer and product info
        for ticket in assigned_tickets:
            customer = next((c for c in self.customers if c["id"] == ticket["customer_id"]), {})
            product = next((p for p in self.products if p["id"] == ticket["product_id"]), {})
            
            ticket.update({
                "customer_name": customer.get("contact_person", "Unknown"),
                "customer_phone": customer.get("phone", "N/A"),
                "customer_address": customer.get("address", "N/A"),
                "product_name": product.get("name", "Unknown Product"),
                "assigned_technician_id": technician_id,
                "latitude": 19.0760 + random.uniform(-0.1, 0.1),  # Mumbai area
                "longitude": 72.8777 + random.uniform(-0.1, 0.1),
                "distance_km": round(random.uniform(1, 15), 1),
                "created_at": ticket["created_date"],
                "updated_at": ticket["scheduled_date"]
            })
        
        return {
            "technician_name": f"{technician['first_name']} {technician['last_name']}",
            "technician_id": technician_id,
            "stats": {
                "total_assigned": len(assigned_tickets),
                "pending_tickets": len([t for t in assigned_tickets if t["status"] == "SCHEDULED"]),
                "in_progress_tickets": len([t for t in assigned_tickets if t["status"] == "IN_PROGRESS"]),
                "completed_today": len([t for t in completed_tickets if t["created_date"] == datetime.now().strftime("%Y-%m-%d")])
            },
            "assigned_tickets": assigned_tickets[:5],  # Latest 5
            "recent_completed": completed_tickets[-3:]  # Last 3 completed
        }
    
    def get_assigned_tickets(self, technician_id=None, status=None, priority=None):
        tickets = self.services.copy()
        
        if technician_id:
            tickets = [t for t in tickets if t["technician_id"] == technician_id]
        if status:
            tickets = [t for t in tickets if t["status"] == status]
        if priority:
            tickets = [t for t in tickets if t["priority"] == priority]
            
        # Enhance with customer and product info
        for ticket in tickets:
            customer = next((c for c in self.customers if c["id"] == ticket["customer_id"]), {})
            product = next((p for p in self.products if p["id"] == ticket["product_id"]), {})
            
            ticket.update({
                "customer_name": customer.get("contact_person", "Unknown"),
                "customer_phone": customer.get("phone", "N/A"),
                "customer_address": customer.get("address", "N/A"),
                "product_name": product.get("name", "Unknown Product"),
                "created_at": ticket["created_date"],
                "updated_at": ticket["scheduled_date"]
            })
        
        return tickets
    
    def get_ticket_details(self, ticket_id):
        ticket = next((s for s in self.services if s["id"] == ticket_id), None)
        if not ticket:
            return None
            
        customer = next((c for c in self.customers if c["id"] == ticket["customer_id"]), {})
        product = next((p for p in self.products if p["id"] == ticket["product_id"]), {})
        technician = next((u for u in USERS_DATA if u["id"] == ticket["technician_id"]), {})
        
        return {
            **ticket,
            "customer_name": customer.get("contact_person", "Unknown"),
            "customer_phone": customer.get("phone", "N/A"),
            "customer_address": customer.get("address", "N/A"),
            "customer_email": customer.get("email", "N/A"),
            "product_name": product.get("name", "Unknown Product"),
            "product_model": product.get("model", "N/A"),
            "technician_name": f"{technician.get('first_name', '')} {technician.get('last_name', '')}".strip(),
            "created_at": ticket["created_date"],
            "updated_at": ticket["scheduled_date"],
            "completion_notes": None
        }
    
    def get_notifications(self, technician_id):
        return [
            {
                "id": 1,
                "title": "New Ticket Assigned",
                "message": "You have been assigned a new service ticket",
                "type": "assignment",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "is_read": False
            },
            {
                "id": 2,
                "title": "Ticket Updated",
                "message": "Priority changed for ticket TKT000123",
                "type": "update",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "is_read": False
            },
            {
                "id": 3,
                "title": "Schedule Reminder",
                "message": "You have 3 tickets scheduled for tomorrow",
                "type": "reminder",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "is_read": True
            }
        ]

# Initialize service app data
service_app_data = ServiceAppData()