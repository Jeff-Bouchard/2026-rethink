import http.server
import socketserver
import socket
import sys
import random

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def find_free_port(start=50001, end=59999, attempts=200):
    for _ in range(attempts):
        candidate = random.randint(start, end)
        if not is_port_in_use(candidate):
            return candidate
    raise RuntimeError("Could not find a free port in range 50001-59999")


PORT = find_free_port()

if is_port_in_use(PORT):
    print(f"[FATAL] Port {PORT} is currently bound by another process. Cannot initialize listener.")
    print(f"Execute 'ss -tlnp' or 'netstat -ano | findstr :{PORT}' to identify the PID, and kill it before retrying.")
    sys.exit(1)

Handler = http.server.SimpleHTTPRequestHandler

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[INFO] HTTP daemon initialized. Listening on TCP 0.0.0.0:{PORT}")
        print(f"[INFO] Access the Privateness.network demonstration at http://127.0.0.1:{PORT}")
        httpd.serve_forever()
except Exception as e:
    print(f"[ERROR] Socket binding failed: {e}")
    sys.exit(1)
