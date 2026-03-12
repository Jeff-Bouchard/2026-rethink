#!/usr/bin/env python3
"""
NESS Shop API Server
Sovereign commerce backend with SQLite and XBTSX.NCH payment tracking
"""

import http.server
import socketserver
import json
import sqlite3
import os
import socket
import random
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import hashlib

DB_FILE = 'ness_shop.db'
SCHEMA_FILE = 'schema.sql'

class ShopAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """Send CORS headers for API access"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, message, status=400):
        """Send error response"""
        self.send_json_response({'error': message}, status)
    
    def get_db(self):
        """Get database connection"""
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path.startswith('/api/'):
            self.handle_api_get(path, parsed.query)
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path.startswith('/api/'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self.send_error_response('Invalid JSON')
                return
            
            self.handle_api_post(path, data)
        else:
            self.send_error_response('Not found', 404)
    
    def do_PUT(self):
        """Handle PUT requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path.startswith('/api/'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self.send_error_response('Invalid JSON')
                return
            
            self.handle_api_put(path, data)
        else:
            self.send_error_response('Not found', 404)
    
    def handle_api_get(self, path, query):
        """Handle API GET requests"""
        conn = self.get_db()
        
        try:
            if path == '/api/config':
                config = conn.execute('SELECT * FROM shop_config WHERE id = 1').fetchone()
                if config:
                    self.send_json_response(dict(config))
                else:
                    self.send_json_response({'configured': False})
            
            elif path == '/api/products':
                products = conn.execute('SELECT * FROM products WHERE active = 1 ORDER BY created_at').fetchall()
                self.send_json_response([dict(p) for p in products])
            
            elif path.startswith('/api/orders/'):
                order_id = path.split('/')[-1]
                order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
                if order:
                    items = conn.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
                    payments = conn.execute('SELECT * FROM payments WHERE order_id = ?', (order_id,)).fetchall()
                    
                    result = dict(order)
                    result['items'] = [dict(i) for i in items]
                    result['payments'] = [dict(p) for p in payments]
                    self.send_json_response(result)
                else:
                    self.send_error_response('Order not found', 404)
            
            elif path == '/api/orders':
                orders = conn.execute('SELECT * FROM order_summary ORDER BY created_at DESC LIMIT 100').fetchall()
                self.send_json_response([dict(o) for o in orders])
            
            else:
                self.send_error_response('Not found', 404)
        
        finally:
            conn.close()
    
    def handle_api_post(self, path, data):
        """Handle API POST requests"""
        conn = self.get_db()
        
        try:
            if path == '/api/config':
                required = ['shop_name', 'shop_description', 'payment_address']
                if not all(k in data for k in required):
                    self.send_error_response('Missing required fields')
                    return
                
                conn.execute('''
                    INSERT OR REPLACE INTO shop_config (id, shop_name, shop_description, payment_address, payment_memo_prefix, webhook_url)
                    VALUES (1, ?, ?, ?, ?, ?)
                ''', (
                    data['shop_name'],
                    data['shop_description'],
                    data['payment_address'],
                    data.get('payment_memo_prefix', 'ORDER'),
                    data.get('webhook_url')
                ))
                conn.commit()
                self.send_json_response({'success': True})
            
            elif path == '/api/products':
                required = ['id', 'name', 'price']
                if not all(k in data for k in required):
                    self.send_error_response('Missing required fields')
                    return
                
                conn.execute('''
                    INSERT INTO products (id, emoji, name, description, price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['id'],
                    data.get('emoji', '📦'),
                    data['name'],
                    data.get('description', ''),
                    data['price']
                ))
                conn.commit()
                self.send_json_response({'success': True})
            
            elif path == '/api/orders':
                if 'items' not in data or not data['items']:
                    self.send_error_response('Order must have items')
                    return
                
                config = conn.execute('SELECT * FROM shop_config WHERE id = 1').fetchone()
                if not config:
                    self.send_error_response('Shop not configured', 400)
                    return
                
                order_id = f"ORDER-{int(datetime.now().timestamp() * 1000)}"
                total = sum(item['price'] * item['quantity'] for item in data['items'])
                memo = f"{config['payment_memo_prefix']}-{order_id}"
                
                conn.execute('''
                    INSERT INTO orders (id, total_amount, payment_address, payment_memo, customer_email, customer_notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    order_id,
                    total,
                    config['payment_address'],
                    memo,
                    data.get('customer_email'),
                    data.get('customer_notes')
                ))
                
                for item in data['items']:
                    subtotal = item['price'] * item['quantity']
                    conn.execute('''
                        INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        order_id,
                        item['id'],
                        item['name'],
                        item['price'],
                        item['quantity'],
                        subtotal
                    ))
                
                conn.commit()
                
                order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
                items = conn.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
                
                result = dict(order)
                result['items'] = [dict(i) for i in items]
                self.send_json_response(result, 201)
            
            elif path == '/api/payments':
                required = ['order_id', 'amount', 'to_address']
                if not all(k in data for k in required):
                    self.send_error_response('Missing required fields')
                    return
                
                conn.execute('''
                    INSERT INTO payments (order_id, txid, amount, from_address, to_address, memo, block_height, confirmations, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['order_id'],
                    data.get('txid'),
                    data['amount'],
                    data.get('from_address'),
                    data['to_address'],
                    data.get('memo'),
                    data.get('block_height'),
                    data.get('confirmations', 0),
                    'confirmed' if data.get('confirmations', 0) >= 1 else 'unconfirmed'
                ))
                
                if data.get('confirmations', 0) >= 1:
                    conn.execute('''
                        UPDATE orders 
                        SET status = 'paid', paid_at = CURRENT_TIMESTAMP 
                        WHERE id = ? AND status = 'pending'
                    ''', (data['order_id'],))
                
                conn.commit()
                self.send_json_response({'success': True})
            
            else:
                self.send_error_response('Not found', 404)
        
        except sqlite3.IntegrityError as e:
            self.send_error_response(f'Database error: {str(e)}', 400)
        finally:
            conn.close()
    
    def handle_api_put(self, path, data):
        """Handle API PUT requests"""
        conn = self.get_db()
        
        try:
            if path.startswith('/api/products/'):
                product_id = path.split('/')[-1]
                
                updates = []
                values = []
                for field in ['emoji', 'name', 'description', 'price', 'active']:
                    if field in data:
                        updates.append(f'{field} = ?')
                        values.append(data[field])
                
                if updates:
                    values.append(product_id)
                    conn.execute(f'''
                        UPDATE products 
                        SET {', '.join(updates)}
                        WHERE id = ?
                    ''', values)
                    conn.commit()
                    self.send_json_response({'success': True})
                else:
                    self.send_error_response('No fields to update')
            
            elif path.startswith('/api/orders/'):
                order_id = path.split('/')[-1]
                
                if 'status' in data:
                    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (data['status'], order_id))
                    
                    if data['status'] == 'confirmed':
                        conn.execute('UPDATE orders SET confirmed_at = CURRENT_TIMESTAMP WHERE id = ?', (order_id,))
                    elif data['status'] == 'fulfilled':
                        conn.execute('UPDATE orders SET fulfilled_at = CURRENT_TIMESTAMP WHERE id = ?', (order_id,))
                    
                    conn.commit()
                    self.send_json_response({'success': True})
                else:
                    self.send_error_response('No status provided')
            
            else:
                self.send_error_response('Not found', 404)
        
        finally:
            conn.close()

def init_database():
    """Initialize database with schema"""
    if not os.path.exists(DB_FILE):
        print(f"Creating database: {DB_FILE}")
        conn = sqlite3.connect(DB_FILE)
        
        with open(SCHEMA_FILE, 'r') as f:
            schema = f.read()
            conn.executescript(schema)
        
        conn.commit()
        conn.close()
        print("Database initialized")
    else:
        print(f"Database exists: {DB_FILE}")

def find_free_port(start=50000, end=60000):
    """Find a free port in the specified range"""
    for _ in range(100):
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError("Could not find a free port in range")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    init_database()
    
    port = find_free_port()
    
    with socketserver.TCPServer(("127.0.0.1", port), ShopAPIHandler) as httpd:
        print(f"NESS Shop API server running at http://127.0.0.1:{port}/shop.html")
        print(f"API endpoint: http://127.0.0.1:{port}/api/")
        print(f"Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    main()
