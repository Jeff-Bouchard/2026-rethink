import socket
import sys

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

if __name__ == '__main__':
    port = 8080
    if check_port(port):
        print(f"Port {port} is in use.")
        sys.exit(1)
    else:
        print(f"Port {port} is free.")
        sys.exit(0)
