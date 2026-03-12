#!/usr/bin/env python3
import http.server
import socketserver
import socket
import random
import os

def find_free_port(start=50000, end=60000):
    """Find a free port in the specified range."""
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
    
    port = find_free_port()
    
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        print(f"NESS Shop server running at http://127.0.0.1:{port}/shop.html")
        print(f"Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    main()
