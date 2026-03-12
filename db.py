#!/usr/bin/env python3
"""
NESS Shop Database Management Tool
SQLite3 command-line interface for Windows (no sqlite3.exe required)
"""

import sqlite3
import sys
import os
import json
from datetime import datetime

DB_FILE = 'ness_shop.db'

def connect_db():
    """Connect to database"""
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found")
        sys.exit(1)
    return sqlite3.connect(DB_FILE)

def execute_query(query, params=None):
    """Execute a query and return results"""
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return results
        else:
            conn.commit()
            return cursor.rowcount
    finally:
        conn.close()

def show_tables():
    """Show all tables in database"""
    results = execute_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    print("\nTables:")
    for row in results:
        print(f"  - {row['name']}")

def show_schema(table=None):
    """Show table schema"""
    if table:
        results = execute_query(f"PRAGMA table_info({table})")
        print(f"\nSchema for table '{table}':")
        print(f"{'Column':<20} {'Type':<15} {'NotNull':<8} {'Default':<15} {'PK':<5}")
        print("-" * 70)
        for row in results:
            print(f"{row['name']:<20} {row['type']:<15} {row['notnull']:<8} {str(row['dflt_value']):<15} {row['pk']:<5}")
    else:
        results = execute_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        for row in results:
            show_schema(row['name'])
            print()

def show_config():
    """Show shop configuration"""
    results = execute_query("SELECT * FROM shop_config WHERE id = 1")
    if results:
        config = dict(results[0])
        print("\nShop Configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print("\nNo shop configuration found")

def show_products():
    """Show all products"""
    results = execute_query("SELECT * FROM products WHERE active = 1 ORDER BY created_at")
    print(f"\nProducts ({len(results)} active):")
    print(f"{'ID':<25} {'Emoji':<8} {'Name':<30} {'Price':<10} {'Description':<40}")
    print("-" * 120)
    for row in results:
        print(f"{row['id']:<25} {row['emoji']:<8} {row['name']:<30} {row['price']:<10.2f} {row['description'] or '':<40}")

def show_orders(limit=10):
    """Show recent orders"""
    results = execute_query(f"SELECT * FROM order_summary ORDER BY created_at DESC LIMIT {limit}")
    print(f"\nRecent Orders (last {limit}):")
    print(f"{'Order ID':<20} {'Amount':<10} {'Status':<12} {'Items':<8} {'Paid':<10} {'Created':<20}")
    print("-" * 90)
    for row in results:
        print(f"{row['id']:<20} {row['total_amount']:<10.2f} {row['status']:<12} {row['item_count']:<8} {row['paid_amount']:<10.2f} {row['created_at']:<20}")

def show_order_details(order_id):
    """Show detailed order information"""
    order = execute_query("SELECT * FROM orders WHERE id = ?", (order_id,))
    if not order:
        print(f"Order '{order_id}' not found")
        return
    
    order = dict(order[0])
    items = execute_query("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
    payments = execute_query("SELECT * FROM payments WHERE order_id = ?", (order_id,))
    
    print(f"\nOrder Details: {order_id}")
    print("-" * 80)
    print(f"Status: {order['status']}")
    print(f"Total: {order['total_amount']} {order['currency']}")
    print(f"Payment Address: {order['payment_address']}")
    print(f"Payment Memo: {order['payment_memo']}")
    print(f"Created: {order['created_at']}")
    
    print(f"\nItems ({len(items)}):")
    for item in items:
        print(f"  - {item['product_name']} x{item['quantity']} @ {item['product_price']} = {item['subtotal']}")
    
    print(f"\nPayments ({len(payments)}):")
    if payments:
        for payment in payments:
            print(f"  - {payment['amount']} {payment['currency']} ({payment['status']})")
            if payment['txid']:
                print(f"    TX: {payment['txid']}")
    else:
        print("  No payments recorded")

def backup_database(backup_file=None):
    """Backup database to file"""
    if not backup_file:
        backup_file = f"ness_shop_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    conn = connect_db()
    backup_conn = sqlite3.connect(backup_file)
    
    with backup_conn:
        conn.backup(backup_conn)
    
    backup_conn.close()
    conn.close()
    
    print(f"Database backed up to: {backup_file}")
    print(f"Size: {os.path.getsize(backup_file)} bytes")

def export_json(table, output_file=None):
    """Export table to JSON"""
    if not output_file:
        output_file = f"{table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    results = execute_query(f"SELECT * FROM {table}")
    data = [dict(row) for row in results]
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"Exported {len(data)} rows from '{table}' to: {output_file}")

def integrity_check():
    """Check database integrity"""
    results = execute_query("PRAGMA integrity_check")
    print("\nDatabase Integrity Check:")
    for row in results:
        print(f"  {row[0]}")

def vacuum():
    """Vacuum database to reclaim space"""
    conn = connect_db()
    size_before = os.path.getsize(DB_FILE)
    conn.execute("VACUUM")
    conn.close()
    size_after = os.path.getsize(DB_FILE)
    
    print(f"Database vacuumed")
    print(f"Size before: {size_before} bytes")
    print(f"Size after: {size_after} bytes")
    print(f"Reclaimed: {size_before - size_after} bytes")

def interactive_shell():
    """Interactive SQL shell"""
    print("SQLite Interactive Shell (type 'exit' or 'quit' to exit)")
    print(f"Connected to: {DB_FILE}\n")
    
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    
    while True:
        try:
            query = input("sqlite> ").strip()
            
            if query.lower() in ['exit', 'quit', '.quit', '.exit']:
                break
            
            if not query:
                continue
            
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.upper().startswith('SELECT'):
                results = cursor.fetchall()
                if results:
                    # Print column headers
                    headers = results[0].keys()
                    print(" | ".join(headers))
                    print("-" * (len(" | ".join(headers))))
                    
                    # Print rows
                    for row in results:
                        print(" | ".join(str(row[col]) for col in headers))
                    
                    print(f"\n{len(results)} rows")
                else:
                    print("No results")
            else:
                conn.commit()
                print(f"Query executed ({cursor.rowcount} rows affected)")
        
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'quit' to exit")
        except Exception as e:
            print(f"Error: {e}")
    
    conn.close()
    print("Goodbye!")

def print_usage():
    """Print usage information"""
    print("""
NESS Shop Database Management Tool

Usage: python db.py <command> [options]

Commands:
  tables              List all tables
  schema [table]      Show table schema (all tables if not specified)
  config              Show shop configuration
  products            Show all products
  orders [limit]      Show recent orders (default: 10)
  order <id>          Show detailed order information
  backup [file]       Backup database to file
  export <table>      Export table to JSON
  integrity           Check database integrity
  vacuum              Vacuum database to reclaim space
  shell               Interactive SQL shell
  query <sql>         Execute SQL query

Examples:
  python db.py tables
  python db.py schema orders
  python db.py products
  python db.py orders 20
  python db.py order ORDER-1234567890
  python db.py backup
  python db.py export orders
  python db.py query "SELECT * FROM orders WHERE status='pending'"
  python db.py shell
""")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == 'tables':
            show_tables()
        
        elif command == 'schema':
            table = sys.argv[2] if len(sys.argv) > 2 else None
            show_schema(table)
        
        elif command == 'config':
            show_config()
        
        elif command == 'products':
            show_products()
        
        elif command == 'orders':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            show_orders(limit)
        
        elif command == 'order':
            if len(sys.argv) < 3:
                print("Error: Order ID required")
                sys.exit(1)
            show_order_details(sys.argv[2])
        
        elif command == 'backup':
            backup_file = sys.argv[2] if len(sys.argv) > 2 else None
            backup_database(backup_file)
        
        elif command == 'export':
            if len(sys.argv) < 3:
                print("Error: Table name required")
                sys.exit(1)
            table = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            export_json(table, output_file)
        
        elif command == 'integrity':
            integrity_check()
        
        elif command == 'vacuum':
            vacuum()
        
        elif command == 'shell':
            interactive_shell()
        
        elif command == 'query':
            if len(sys.argv) < 3:
                print("Error: SQL query required")
                sys.exit(1)
            query = ' '.join(sys.argv[2:])
            results = execute_query(query)
            
            if isinstance(results, list):
                for row in results:
                    print(dict(row))
            else:
                print(f"{results} rows affected")
        
        else:
            print(f"Unknown command: {command}")
            print_usage()
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
