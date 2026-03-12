# Quick Start Guide

## Infrastructure Management

### Start Everything
```bash
./manage.sh start
```

### Check Status
```bash
./manage.sh status
```

Output:
```
=== NESS Infrastructure Status ===

[OK] Demo server: RUNNING (PID: 3394, Port: 51237)
[INFO] URL: http://127.0.0.1:51237

[OK] Shop server: RUNNING (PID: 3401, Port: 56724)
[INFO] URL: http://127.0.0.1:56724/shop.html
```

### Stop Everything
```bash
./manage.sh stop
```

### Restart Everything
```bash
./manage.sh restart
```

## Individual Server Control

### Demo Server (Privateness.network × PayRam)
```bash
./manage.sh start demo    # Start
./manage.sh stop demo     # Stop
./manage.sh restart demo  # Restart
./manage.sh status demo   # Status
./manage.sh logs demo     # View logs
```

### Shop Server (XBTSX.NCH Payments)
```bash
./manage.sh start shop    # Start
./manage.sh stop shop     # Stop
./manage.sh restart shop  # Restart
./manage.sh status shop   # Status
./manage.sh logs shop     # View logs
```

## Common Workflows

### Development Workflow
```bash
# Start servers
./manage.sh start

# Make changes to index.html or shop.html
# (no restart needed - just refresh browser)

# Check logs if something breaks
./manage.sh logs demo

# Stop when done
./manage.sh stop
```

### Deployment Workflow
```bash
# Stop existing servers
./manage.sh stop all

# Pull latest changes
git pull

# Start fresh
./manage.sh start all

# Verify everything is running
./manage.sh status
```

### Troubleshooting Workflow
```bash
# Check what's running
./manage.sh status

# View logs for errors
./manage.sh logs demo    # or shop

# Force restart if needed
./manage.sh restart all
```

## Git Workflow

### Initial Setup
```bash
git init
git add .
git commit -m "Initial commit: NESS infrastructure"
```

### Regular Commits
```bash
git add .
git commit -m "Update: [describe changes]"
```

### Branch for Features
```bash
git checkout -b feature/payment-integration
# Make changes
git add .
git commit -m "Add: XBTSX.NCH payment flow"
git checkout main
git merge feature/payment-integration
```

## Accessing the Applications

### Demo (Privateness.network × PayRam)
- **URL**: Check `./manage.sh status` for current port
- **Features**: Architecture, payment flow, roadmap, admin dashboard
- **Tech**: Skywire + EMC + NESS + PayRam integration model

### Shop (XBTSX.NCH Payments)
- **URL**: Check `./manage.sh status` for current port + `/shop.html`
- **Features**: Product catalog, shopping cart, XBTSX.NCH checkout
- **Payment**: NESS Coin Hours on XBTS DEX

## File Structure

```
.
├── manage.sh              # Infrastructure management script
├── server.py              # Demo server
├── shop_server.py         # Shop server
├── index.html             # Privateness.network demo
├── shop.html              # NESS Shop
├── README.md              # Full documentation
├── USAGE.md               # This file
├── .gitignore             # Git ignore rules
├── .demo_server.pid       # Demo PID (runtime)
├── .shop_server.pid       # Shop PID (runtime)
├── demo_server.log        # Demo logs
└── shop_server.log        # Shop logs
```

## Tips

- Servers use **random ports 50000-60000** for security
- Always check `./manage.sh status` for current URLs
- Logs are written to `demo_server.log` and `shop_server.log`
- PID files track running processes
- Use `Ctrl+C` to exit log tailing
- Git ignores `.pid` and `.log` files automatically
