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
        "info": {"title": "Service API", "version": "1.0.0"},
        "paths": {
            "/login": {
                "post": {
                    "summary": "Login technician",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "Success"}}
                }
            },
            "/tickets": {
                "get": {"summary": "Get service tickets", "responses": {"200": {"description": "Success"}}},
                "post": {"summary": "Create ticket", "responses": {"200": {"description": "Success"}}}
            },
            "/tickets/{ticket_id}": {
                "put": {"summary": "Update ticket", "responses": {"200": {"description": "Success"}}}
            },
            "/dashboard/stats": {
                "get": {"summary": "Dashboard statistics", "responses": {"200": {"description": "Success"}}}
            }
        }
    }

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not engine:
        return jsonify({"error": "Database not available"}), 500
    
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
        return jsonify({"error": str(e)}), 500

@app.route('/tickets', methods=['GET'])
def get_tickets():
    if not engine:
        return jsonify({"error": "Database not available"}), 500
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT st.id, st.customer_id, st.product_id, st.issue_description, 
                       st.status, st.priority, st.created_at, st.assigned_technician_id,
                       c.name as customer_name, p.name as product_name
                FROM service_tickets st
                LEFT JOIN customers c ON st.customer_id = c.id
                LEFT JOIN products p ON st.product_id = p.id
                ORDER BY st.created_at DESC
            """))
            
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
        return jsonify({"error": str(e)}), 500

@app.route('/tickets', methods=['POST'])
def create_ticket():
    data = request.get_json()
    
    if not engine:
        return jsonify({"error": "Database not available"}), 500
    
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
        return jsonify({"error": str(e)}), 500

@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    data = request.get_json()
    
    if not engine:
        return jsonify({"error": "Database not available"}), 500
    
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE service_tickets 
                SET status = :status, assigned_technician_id = :technician_id
                WHERE id = :ticket_id
            """), {
                "status": data.get('status'),
                "technician_id": data.get('assigned_technician_id'),
                "ticket_id": ticket_id
            })
            conn.commit()
            return jsonify({"message": "Ticket updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    if not engine:
        return jsonify({"error": "Database not available"}), 500
    
    try:
        with engine.connect() as conn:
            # Get ticket counts by status
            result = conn.execute(text("""
                SELECT status, COUNT(*) as count FROM service_tickets GROUP BY status
            """))
            ticket_stats = {row[0]: row[1] for row in result}
            
            # Get total counts
            total_tickets = conn.execute(text("SELECT COUNT(*) FROM service_tickets")).scalar()
            total_customers = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
            total_products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            
            return jsonify({
                "total_tickets": total_tickets,
                "total_customers": total_customers,
                "total_products": total_products,
                "ticket_stats": ticket_stats
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    app.run(host="0.0.0.0", port=port, debug=False)
