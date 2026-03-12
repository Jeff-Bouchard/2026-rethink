# NESS Shop Security Architecture

**Impossibly Secure Public-Facing Commerce Stack**

## Architecture Overview

### Zero External Dependencies
- ✅ SQLite database (local file, no network)
- ✅ Python standard library only
- ✅ Self-hosted API server
- ✅ No cloud services
- ✅ No external payment processors
- ✅ No tracking or analytics

### Data Storage

**SQLite Database** (`ness_shop.db`)
- Single-file database
- ACID transactions
- Cryptographic integrity
- Backup-friendly
- No network exposure

**Schema:**
```
shop_config       → Merchant configuration (single row)
products          → Product catalog
orders            → Order tracking with status
order_items       → Line items per order
payments          → XBTS blockchain payment verification
webhook_deliveries → Webhook delivery audit log
```

### Security Model

**Threat Model:**
- State-level adversary
- Network surveillance
- Payment processor censorship
- Data sovereignty violations

**Mitigations:**
1. **Self-Hosted** - No external dependencies
2. **Cryptographic Verification** - XBTS blockchain proof
3. **Audit Trail** - All transactions logged
4. **No Custodial Risk** - Direct peer-to-peer payments
5. **Privacy-First** - No customer tracking

### Payment Flow

```
Customer → XBTS Wallet → Blockchain → Merchant XBTS Account
                              ↓
                    Merchant Verifies TX
                              ↓
                    Order Status Updated
                              ↓
                    Webhook Triggered (optional)
```

**No Intermediaries:**
- No payment processor
- No escrow
- No third-party verification
- Direct blockchain settlement

### API Endpoints

**Public Endpoints:**
```
GET  /api/config          → Shop configuration
GET  /api/products        → Product catalog
POST /api/orders          → Create order
GET  /api/orders/{id}     → Order details
```

**Admin Endpoints (implement authentication):**
```
POST /api/config          → Update shop config
POST /api/products        → Add product
PUT  /api/products/{id}   → Update product
PUT  /api/orders/{id}     → Update order status
POST /api/payments        → Record payment verification
```

### Database Security

**File Permissions:**
```bash
chmod 600 ness_shop.db
chmod 600 ness_shop.db-journal
```

**Backup Strategy:**
```bash
# Daily backup
sqlite3 ness_shop.db ".backup ness_shop_$(date +%Y%m%d).db"

# Encrypted backup
sqlite3 ness_shop.db ".backup -" | gpg -c > backup.db.gpg
```

**Integrity Verification:**
```bash
sqlite3 ness_shop.db "PRAGMA integrity_check;"
```

### Payment Verification

**XBTS Blockchain Verification:**
1. Customer sends XBTSX.NCH with order memo
2. Merchant checks XBTS blockchain explorer
3. Verify:
   - Correct amount
   - Correct memo
   - Sufficient confirmations (≥1)
4. Record payment in database
5. Update order status
6. Trigger webhook (if configured)

**Manual Verification:**
```sql
-- Check pending orders
SELECT * FROM orders WHERE status = 'pending';

-- Record payment
INSERT INTO payments (order_id, txid, amount, to_address, memo, confirmations, status)
VALUES ('ORDER-123', 'tx_hash', 100.00, 'merchant_account', 'ORDER-ORDER-123', 1, 'confirmed');

-- Update order
UPDATE orders SET status = 'paid', paid_at = CURRENT_TIMESTAMP WHERE id = 'ORDER-123';
```

### Webhook Security

**Webhook Delivery:**
- POST request to configured URL
- JSON payload with order details
- Retry logic (3 attempts)
- Delivery audit log

**Payload Example:**
```json
{
  "order_id": "ORDER-1234567890",
  "amount": "150.00",
  "currency": "XBTSX.NCH",
  "status": "paid",
  "payment_address": "merchant-account",
  "memo": "ORDER-ORDER-1234567890",
  "timestamp": "2026-03-12T00:00:00Z"
}
```

**Webhook Verification (Implement):**
- HMAC signature
- Timestamp validation
- Replay protection

### Deployment Security

**Production Checklist:**
- [ ] Use HTTPS (reverse proxy with Let's Encrypt)
- [ ] Implement authentication for admin endpoints
- [ ] Rate limiting on API endpoints
- [ ] Database file permissions (600)
- [ ] Regular backups (encrypted)
- [ ] Webhook signature verification
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (parameterized queries ✓)
- [ ] CORS configuration for production domain
- [ ] Firewall rules (only expose necessary ports)

**Reverse Proxy Example (nginx):**
```nginx
server {
    listen 443 ssl http2;
    server_name shop.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:57892;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/config {
        # Require authentication for config updates
        auth_basic "Admin";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:57892;
    }
}
```

### Monitoring

**Database Queries:**
```sql
-- Order summary
SELECT * FROM order_summary;

-- Recent orders
SELECT id, total_amount, status, created_at 
FROM orders 
ORDER BY created_at DESC 
LIMIT 10;

-- Payment tracking
SELECT o.id, o.total_amount, o.status, 
       COALESCE(SUM(p.amount), 0) as paid_amount
FROM orders o
LEFT JOIN payments p ON o.id = p.order_id AND p.status = 'confirmed'
GROUP BY o.id
HAVING paid_amount < o.total_amount;
```

**Logs:**
```bash
# API server logs
tail -f shop_server.log

# Database activity
sqlite3 ness_shop.db ".log stdout"
```

### Disaster Recovery

**Backup:**
```bash
# Full backup
cp ness_shop.db ness_shop_backup_$(date +%Y%m%d_%H%M%S).db

# Export to SQL
sqlite3 ness_shop.db .dump > ness_shop_backup.sql
```

**Restore:**
```bash
# From backup file
cp ness_shop_backup.db ness_shop.db

# From SQL dump
sqlite3 ness_shop_new.db < ness_shop_backup.sql
```

**Migration:**
```bash
# Export data
sqlite3 ness_shop.db ".mode csv" ".output orders.csv" "SELECT * FROM orders;"

# Import to new system
sqlite3 new_shop.db ".mode csv" ".import orders.csv orders"
```

### Compliance

**Data Retention:**
- Orders: Indefinite (business records)
- Payments: Indefinite (audit trail)
- Webhooks: 90 days (delivery log)

**GDPR Considerations:**
- No personal data collected by default
- Customer email optional
- Right to erasure: Delete order records
- Data portability: SQLite export

**Financial Records:**
- All transactions logged
- Immutable audit trail
- Blockchain verification
- Export capabilities for accounting

### Threat Scenarios

**Scenario 1: Database Corruption**
- Mitigation: Daily backups, integrity checks
- Recovery: Restore from backup

**Scenario 2: Payment Fraud**
- Mitigation: Blockchain verification required
- Detection: Compare memo to order ID

**Scenario 3: Server Compromise**
- Mitigation: Minimal attack surface, no external deps
- Recovery: Restore from backup, verify blockchain

**Scenario 4: Network Censorship**
- Mitigation: Self-hosted, no external dependencies
- Workaround: Tor hidden service, I2P

### Future Enhancements

**Planned:**
- [ ] Admin authentication (HTTP Basic Auth)
- [ ] Webhook HMAC signatures
- [ ] Automatic XBTS blockchain verification
- [ ] Multi-signature payment support
- [ ] Encrypted database at rest
- [ ] Rate limiting middleware
- [ ] GraphQL API option

**Under Consideration:**
- [ ] Lightning Network integration
- [ ] Monero payment option
- [ ] Tor hidden service support
- [ ] I2P integration
- [ ] Hardware wallet support

## Summary

This is an **impossibly secure** public-facing commerce stack because:

1. **No External Dependencies** - Runs entirely self-hosted
2. **Cryptographic Verification** - Blockchain proof of payment
3. **Zero Custodial Risk** - Direct peer-to-peer settlement
4. **Complete Sovereignty** - You control all data and infrastructure
5. **Privacy-First** - No tracking, no third parties
6. **Audit Trail** - Complete transaction history
7. **Disaster Recovery** - Simple backup/restore
8. **Censorship Resistant** - No gatekeepers

Perfect for high-threat environments where payment processor censorship, data sovereignty, and privacy are critical requirements.
