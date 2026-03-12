#!/bin/bash
# NESS Infrastructure Management Script
# Manages demo and shop servers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DEMO_SERVER="server.py"
SHOP_SERVER="shop_api.py"
DEMO_PID_FILE=".demo_server.pid"
SHOP_PID_FILE=".shop_server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

http_get() {
    local url=$1
    python - "$url" <<'PY'
import sys
from urllib.request import urlopen

url = sys.argv[1]
with urlopen(url, timeout=10) as response:
    data = response.read().decode("utf-8", errors="replace")
    sys.stdout.buffer.write(data.encode("utf-8", errors="replace"))
PY
}

http_get_json() {
    local url=$1
    python - "$url" <<'PY'
import json
import sys
from urllib.request import urlopen

url = sys.argv[1]
with urlopen(url, timeout=10) as response:
    data = json.loads(response.read().decode("utf-8"))
    print(json.dumps(data))
PY
}

# Extract port from log file
extract_port_from_log() {
    local log_file=$1
    if [ ! -f "$log_file" ]; then
        return 0
    fi

    local port
    port=$(grep -Eo 'http://(127\.0\.0\.1|localhost):[0-9]+' "$log_file" 2>/dev/null | head -1 | sed 's/.*://')

    if [ -z "$port" ]; then
        port=$(grep -Eo '0\.0\.0\.0:[0-9]+' "$log_file" 2>/dev/null | head -1 | sed 's/.*://')
    fi

    echo "$port"
}

# Get PID from file
get_pid() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        cat "$pid_file"
    fi
}

# Check if process is running
is_running() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi
    ps -p "$pid" > /dev/null 2>&1
}

# Start demo server
start_demo() {
    local pid=$(get_pid "$DEMO_PID_FILE")
    
    if is_running "$pid"; then
        log_warn "Demo server already running (PID: $pid)"
        return 0
    fi
    
    log_info "Starting demo server..."
    python -u "$DEMO_SERVER" > demo_server.log 2>&1 &
    local new_pid=$!
    echo $new_pid > "$DEMO_PID_FILE"
    
    sleep 2
    
    if is_running "$new_pid"; then
        local port=$(extract_port_from_log demo_server.log)
        log_success "Demo server started (PID: $new_pid, Port: ${port:-detecting...})"
        if [ -n "$port" ]; then
            log_info "Access at: http://127.0.0.1:$port"
        fi
    else
        log_error "Failed to start demo server"
        rm -f "$DEMO_PID_FILE"
        return 1
    fi
}

# Start shop server
start_shop() {
    local pid=$(get_pid "$SHOP_PID_FILE")
    
    if is_running "$pid"; then
        log_warn "Shop server already running (PID: $pid)"
        return 0
    fi
    
    log_info "Starting shop server..."
    python -u "$SHOP_SERVER" > shop_server.log 2>&1 &
    local new_pid=$!
    echo $new_pid > "$SHOP_PID_FILE"
    
    sleep 2
    
    if is_running "$new_pid"; then
        local port=$(extract_port_from_log shop_server.log)
        log_success "Shop server started (PID: $new_pid, Port: ${port:-detecting...})"
        if [ -n "$port" ]; then
            log_info "Access at: http://127.0.0.1:$port/shop.html"
        fi
    else
        log_error "Failed to start shop server"
        rm -f "$SHOP_PID_FILE"
        return 1
    fi
}

# Stop demo server
stop_demo() {
    local pid=$(get_pid "$DEMO_PID_FILE")
    
    if ! is_running "$pid"; then
        log_warn "Demo server not running"
        rm -f "$DEMO_PID_FILE"
        return 0
    fi
    
    log_info "Stopping demo server (PID: $pid)..."
    kill "$pid" 2>/dev/null || true
    
    # Wait up to 5 seconds for graceful shutdown
    for i in {1..5}; do
        if ! is_running "$pid"; then
            break
        fi
        sleep 1
    done
    
    # Force kill if still running
    if is_running "$pid"; then
        log_warn "Force killing demo server..."
        kill -9 "$pid" 2>/dev/null || true
    fi
    
    rm -f "$DEMO_PID_FILE"
    log_success "Demo server stopped"
}

# Stop shop server
stop_shop() {
    local pid=$(get_pid "$SHOP_PID_FILE")
    
    if ! is_running "$pid"; then
        log_warn "Shop server not running"
        rm -f "$SHOP_PID_FILE"
        return 0
    fi
    
    log_info "Stopping shop server (PID: $pid)..."
    kill "$pid" 2>/dev/null || true
    
    # Wait up to 5 seconds for graceful shutdown
    for i in {1..5}; do
        if ! is_running "$pid"; then
            break
        fi
        sleep 1
    done
    
    # Force kill if still running
    if is_running "$pid"; then
        log_warn "Force killing shop server..."
        kill -9 "$pid" 2>/dev/null || true
    fi
    
    rm -f "$SHOP_PID_FILE"
    log_success "Shop server stopped"
}

# Status of demo server
status_demo() {
    local pid=$(get_pid "$DEMO_PID_FILE")
    
    if is_running "$pid"; then
        local port=$(extract_port_from_log demo_server.log)
        log_success "Demo server: RUNNING (PID: $pid, Port: ${port:-unknown})"
        if [ -n "$port" ]; then
            log_info "URL: http://127.0.0.1:$port"
        fi
        return 0
    else
        log_warn "Demo server: STOPPED"
        rm -f "$DEMO_PID_FILE"
        return 1
    fi
}

# Status of shop server
status_shop() {
    local pid=$(get_pid "$SHOP_PID_FILE")
    
    if is_running "$pid"; then
        local port=$(extract_port_from_log shop_server.log)
        log_success "Shop server: RUNNING (PID: $pid, Port: ${port:-unknown})"
        if [ -n "$port" ]; then
            log_info "URL: http://127.0.0.1:$port/shop.html"
        fi
        return 0
    else
        log_warn "Shop server: STOPPED"
        rm -f "$SHOP_PID_FILE"
        return 1
    fi
}

# Restart demo server
restart_demo() {
    log_info "Restarting demo server..."
    stop_demo
    sleep 1
    start_demo
}

# Restart shop server
restart_shop() {
    log_info "Restarting shop server..."
    stop_shop
    sleep 1
    start_shop
}

# Show status of all servers
status_all() {
    echo ""
    echo "=== NESS Infrastructure Status ==="
    echo ""
    status_demo
    echo ""
    status_shop
    echo ""
}

# Start all servers
start_all() {
    log_info "Starting all servers..."
    echo ""
    start_demo
    echo ""
    start_shop
    echo ""
    log_success "All servers started"
}

# Stop all servers
stop_all() {
    log_info "Stopping all servers..."
    echo ""
    stop_demo
    echo ""
    stop_shop
    echo ""
    log_success "All servers stopped"
}

# Restart all servers
restart_all() {
    log_info "Restarting all servers..."
    echo ""
    stop_all
    sleep 1
    start_all
}

# Show logs
logs_demo() {
    if [ -f "demo_server.log" ]; then
        tail -f "demo_server.log"
    else
        log_error "Demo server log not found"
    fi
}

logs_shop() {
    if [ -f "shop_server.log" ]; then
        tail -f "shop_server.log"
    else
        log_error "Shop server log not found"
    fi
}

test_demo() {
    local pid=$(get_pid "$DEMO_PID_FILE")
    local port=$(extract_port_from_log demo_server.log)

    if ! is_running "$pid"; then
        log_error "Demo E2E failed: server is not running"
        return 1
    fi

    if [ -z "$port" ]; then
        log_error "Demo E2E failed: could not determine demo port"
        return 1
    fi

    log_info "E2E demo check on http://127.0.0.1:$port"

    local body
    if ! body=$(http_get "http://127.0.0.1:$port/"); then
        log_error "Demo E2E failed: HTTP request to demo root failed"
        return 1
    fi

    if ! printf '%s' "$body" | grep -q 'Privateness.network'; then
        log_error "Demo E2E failed: response does not contain expected Privateness.network marker"
        return 1
    fi

    log_success "Demo E2E passed"
    return 0
}

test_shop() {
    local pid=$(get_pid "$SHOP_PID_FILE")
    local port=$(extract_port_from_log shop_server.log)

    if ! is_running "$pid"; then
        log_error "Shop E2E failed: server is not running"
        return 1
    fi

    if [ -z "$port" ]; then
        log_error "Shop E2E failed: could not determine shop port"
        return 1
    fi

    if [ ! -f "ness_shop.db" ]; then
        log_error "Shop E2E failed: database file ness_shop.db not found"
        return 1
    fi

    log_info "E2E shop check on http://127.0.0.1:$port/shop.html"

    local shop_html
    if ! shop_html=$(http_get "http://127.0.0.1:$port/shop.html"); then
        log_error "Shop E2E failed: HTTP request to shop frontend failed"
        return 1
    fi

    if ! printf '%s' "$shop_html" | grep -q 'NESS Shop'; then
        log_error "Shop E2E failed: shop frontend missing expected NESS Shop marker"
        return 1
    fi

    local config_json
    if ! config_json=$(http_get_json "http://127.0.0.1:$port/api/config"); then
        log_error "Shop E2E failed: /api/config did not return valid JSON"
        return 1
    fi

    local products_json
    if ! products_json=$(http_get_json "http://127.0.0.1:$port/api/products"); then
        log_error "Shop E2E failed: /api/products did not return valid JSON"
        return 1
    fi

    log_info "Config payload: $config_json"
    log_info "Products payload: $products_json"
    log_success "Shop E2E passed"
    return 0
}

test_all() {
    log_info "Running full E2E suite..."
    echo ""
    test_demo
    echo ""
    test_shop
    echo ""
    log_success "All E2E tests passed"
}

# Show usage
usage() {
    cat << EOF
NESS Infrastructure Management Script

Usage: $0 <command> [service]

Commands:
  start [service]    Start server(s)
  stop [service]     Stop server(s)
  restart [service]  Restart server(s)
  status [service]   Show server status
  test [service]     Run end-to-end checks
  logs [service]     Tail server logs (Ctrl+C to exit)

Services:
  demo              Privateness.network demo (index.html)
  shop              NESS Shop (shop.html)
  all               All servers (default)

Examples:
  $0 start          Start all servers
  $0 start demo     Start demo server only
  $0 stop shop      Stop shop server only
  $0 restart all    Restart all servers
  $0 status         Show status of all servers
  $0 test all       Run full E2E suite
  $0 logs demo      Tail demo server logs

EOF
}

# Main command dispatcher
main() {
    local command=$1
    local service=${2:-all}
    
    case "$command" in
        start)
            case "$service" in
                demo) start_demo ;;
                shop) start_shop ;;
                all) start_all ;;
                *) log_error "Unknown service: $service"; usage; exit 1 ;;
            esac
            ;;
        stop)
            case "$service" in
                demo) stop_demo ;;
                shop) stop_shop ;;
                all) stop_all ;;
                *) log_error "Unknown service: $service"; usage; exit 1 ;;
            esac
            ;;
        restart)
            case "$service" in
                demo) restart_demo ;;
                shop) restart_shop ;;
                all) restart_all ;;
                *) log_error "Unknown service: $service"; usage; exit 1 ;;
            esac
            ;;
        status)
            case "$service" in
                demo) status_demo ;;
                shop) status_shop ;;
                all) status_all ;;
                *) log_error "Unknown service: $service"; usage; exit 1 ;;
            esac
            ;;
        test)
            case "$service" in
                demo) test_demo ;;
                shop) test_shop ;;
                all) test_all ;;
                *) log_error "Unknown service: $service"; usage; exit 1 ;;
            esac
            ;;
        logs)
            case "$service" in
                demo) logs_demo ;;
                shop) logs_shop ;;
                *) log_error "Unknown service: $service"; usage; exit 1 ;;
            esac
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Run main if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    if [ $# -eq 0 ]; then
        usage
        exit 1
    fi
    main "$@"
fi
