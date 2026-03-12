-- NESS Shop Database Schema
-- Sovereign commerce with XBTSX.NCH payment tracking
-- No external dependencies, cryptographically verifiable

-- Shop configuration (single merchant instance)
CREATE TABLE IF NOT EXISTS shop_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    shop_name TEXT NOT NULL,
    shop_description TEXT NOT NULL,
    payment_address TEXT NOT NULL,
    payment_memo_prefix TEXT DEFAULT 'ORDER',
    webhook_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products catalog
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    emoji TEXT NOT NULL DEFAULT '📦',
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL CHECK (price > 0),
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    total_amount REAL NOT NULL CHECK (total_amount > 0),
    currency TEXT DEFAULT 'XBTSX.NCH',
    payment_address TEXT NOT NULL,
    payment_memo TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'confirmed', 'fulfilled', 'cancelled')),
    customer_email TEXT,
    customer_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,
    confirmed_at TIMESTAMP,
    fulfilled_at TIMESTAMP
);

-- Order items (line items)
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    product_price REAL NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    subtotal REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Payment tracking (XBTS blockchain verification)
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    txid TEXT UNIQUE,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'XBTSX.NCH',
    from_address TEXT,
    to_address TEXT NOT NULL,
    memo TEXT,
    block_height INTEGER,
    confirmations INTEGER DEFAULT 0,
    status TEXT DEFAULT 'unconfirmed' CHECK (status IN ('unconfirmed', 'confirmed', 'invalid')),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- Webhook delivery log
CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    webhook_url TEXT NOT NULL,
    payload TEXT NOT NULL,
    http_status INTEGER,
    response_body TEXT,
    attempt INTEGER DEFAULT 1,
    delivered INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_txid ON payments(txid);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(active);

-- Triggers for updated_at timestamps
CREATE TRIGGER IF NOT EXISTS update_shop_config_timestamp 
AFTER UPDATE ON shop_config
BEGIN
    UPDATE shop_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_products_timestamp 
AFTER UPDATE ON products
BEGIN
    UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_orders_timestamp 
AFTER UPDATE ON orders
BEGIN
    UPDATE orders SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Initial data validation view
CREATE VIEW IF NOT EXISTS order_summary AS
SELECT 
    o.id,
    o.total_amount,
    o.status,
    o.created_at,
    COUNT(oi.id) as item_count,
    COALESCE(SUM(p.amount), 0) as paid_amount,
    CASE 
        WHEN COALESCE(SUM(p.amount), 0) >= o.total_amount THEN 1 
        ELSE 0 
    END as fully_paid
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
LEFT JOIN payments p ON o.id = p.order_id AND p.status = 'confirmed'
GROUP BY o.id;
