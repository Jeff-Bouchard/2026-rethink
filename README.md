# NESS Infrastructure Management

**[English](#english-documentation)** | **[Français](#documentation-française)**

Privateness.network demo and NESS Shop infrastructure with SQLite-backed sovereign commerce.

---

## English Documentation

### Overview

Complete self-hosted infrastructure for sovereign commerce:
- **Demo Server** - Privateness.network × PayRam architecture demonstration
- **Shop Server** - XBTSX.NCH payment processing with SQLite backend
- **Database Management** - Python-based SQLite administration tools
- **Zero External Dependencies** - Complete data sovereignty

### Quick Start

```bash
# Start all servers
./manage.sh start

# Check status
./manage.sh status

# Access shop
# URL will be shown in status output (random port 50000-60000)

# Manage database
python db.py tables
python db.py config
python db.py products
```

## Infrastructure Management

### Management Script (`manage.sh`)

Complete control over demo and shop servers.

**Commands:**

| Command | Description | Example |
|---------|-------------|---------|
| `start [service]` | Start server(s) | `./manage.sh start demo` |
| `stop [service]` | Stop server(s) | `./manage.sh stop shop` |
| `restart [service]` | Restart server(s) | `./manage.sh restart all` |
| `status [service]` | Show server status | `./manage.sh status` |
| `logs [service]` | Tail server logs | `./manage.sh logs demo` |

**Services:**

- **demo** - Privateness.network × PayRam demo (`index.html`)
- **shop** - NESS Shop API with SQLite (`shop_api.py`)
- **all** - All servers (default)

**Examples:**

```bash
# Start only the demo server
./manage.sh start demo

# Stop only the shop server
./manage.sh stop shop

# Restart all servers
./manage.sh restart all

# Check status of all servers
./manage.sh status

# View demo server logs (Ctrl+C to exit)
./manage.sh logs demo

# View shop server logs
./manage.sh logs shop
```

## Database Management

### Database Tool (`db.py`)

Python-based SQLite management (no `sqlite3` command required on Windows).

**View Data:**

```bash
# List all tables
python db.py tables

# Show table schemas
python db.py schema
python db.py schema orders

# View shop configuration
python db.py config

# View products
python db.py products

# View recent orders
python db.py orders
python db.py orders 20          # Last 20 orders

# View specific order details
python db.py order ORDER-1234567890
```

**Database Operations:**

```bash
# Backup database
python db.py backup
python db.py backup my_backup.db

# Export table to JSON
python db.py export orders
python db.py export products orders_export.json

# Check database integrity
python db.py integrity

# Vacuum database (reclaim space)
python db.py vacuum

# Interactive SQL shell
python db.py shell

# Execute SQL query
python db.py query "SELECT * FROM orders WHERE status='pending'"
```

**Interactive Shell:**

```bash
python db.py shell
```

```sql
sqlite> SELECT * FROM shop_config;
sqlite> SELECT COUNT(*) FROM orders;
sqlite> SELECT * FROM order_summary;
sqlite> exit
```

## Server Details

### Demo Server (`server.py`)

- **File**: `index.html`
- **Port**: Random (50000-60000)
- **PID File**: `.demo_server.pid`
- **Log File**: `demo_server.log`
- **Content**: Privateness.network × PayRam architecture demo

### Shop Server (`shop_api.py`)

- **File**: `shop.html` (frontend)
- **Backend**: RESTful JSON API with SQLite
- **Port**: Random (50000-60000)
- **PID File**: `.shop_server.pid`
- **Log File**: `shop_server.log`
- **Database**: `ness_shop.db` (SQLite)

**API Endpoints:**

```
GET  /api/config          - Shop configuration
GET  /api/products        - Product catalog
POST /api/orders          - Create order
GET  /api/orders/{id}     - Order details
POST /api/config          - Update configuration
POST /api/products        - Add product
PUT  /api/products/{id}   - Update product
PUT  /api/orders/{id}     - Update order status
POST /api/payments        - Record payment
```

## Database Schema

**Tables:**

- `shop_config` - Merchant configuration (single row)
- `products` - Product catalog with pricing
- `orders` - Order tracking with status workflow
- `order_items` - Line items per order
- `payments` - XBTS blockchain payment verification
- `webhook_deliveries` - Webhook delivery audit log

**Views:**

- `order_summary` - Aggregated order data with payment status

**See**: `schema.sql` for complete schema definition

## Architecture

### Privateness.network Demo

**Stack**: Skywire (Transport) → EMC (Naming) → NESS (Execution) → PayRam (Commerce)

**Features:**
- Architecture overview
- Payment flow diagrams
- Deployment model
- Admin dashboard
- Roadmap visualization

### NESS Shop

**Payment**: XBTSX.NCH (NESS Coin Hours) on XBTS DEX

**Features:**
- SQLite backend (complete data sovereignty)
- RESTful JSON API
- Product catalog management
- Shopping cart
- XBTSX.NCH checkout flow
- Order tracking
- Payment verification
- Webhook support (optional)

**Security:**
- No external dependencies
- Self-hosted database
- Cryptographic payment verification
- Audit trail
- No custodial risk

## Configuration

### Shop Configuration

1. Start shop server: `./manage.sh start shop`
2. Open in browser (check status for URL)
3. Click **⚙️ Configure**
4. Enter required fields:
   - Shop name
   - Shop description
   - XBTS payment address
   - Products (name, price, emoji)
5. Save configuration

**Data Storage:**
- All configuration stored in SQLite database
- No browser LocalStorage
- Server-side persistence
- Backup-friendly

### Adding Products

Through web UI:
1. Click Configure
2. Click "Add Product"
3. Enter: emoji, name, description, price (NCH)
4. Save

Through database:
```bash
python db.py shell
```
```sql
INSERT INTO products (id, emoji, name, description, price)
VALUES ('product-001', '🎁', 'Premium Service', 'Description', 99.99);
```

## Payment Flow

### Customer Checkout

1. Customer adds items to cart
2. Proceeds to checkout
3. Order created in database
4. Payment instructions displayed:
   - XBTS account address
   - Exact NCH amount
   - Unique order memo

### Merchant Verification

**Manual Verification:**
1. Customer sends payment via XBTS wallet
2. Merchant checks XBTS blockchain
3. Verify amount, memo, confirmations
4. Record payment in database:

```bash
python db.py shell
```
```sql
INSERT INTO payments (order_id, txid, amount, to_address, memo, confirmations, status)
VALUES ('ORDER-123', 'tx_hash', 100.00, 'merchant_account', 'ORDER-ORDER-123', 1, 'confirmed');

UPDATE orders SET status = 'paid', paid_at = CURRENT_TIMESTAMP WHERE id = 'ORDER-123';
```

**Webhook Automation (Optional):**
- Configure webhook URL in shop settings
- Automatic payment notifications
- See `SECURITY.md` for webhook implementation

## Backup & Recovery

### Database Backup

```bash
# Quick backup
python db.py backup

# Named backup
python db.py backup ness_shop_$(date +%Y%m%d).db

# Encrypted backup
python db.py backup - | gpg -c > backup.db.gpg
```

### Export Data

```bash
# Export orders to JSON
python db.py export orders

# Export all tables
python db.py export shop_config
python db.py export products
python db.py export orders
python db.py export payments
```

### Restore

```bash
# From backup file
cp ness_shop_backup.db ness_shop.db
./manage.sh restart shop
```

## Security

### Threat Model

- State-level adversary
- Network surveillance
- Payment processor censorship
- Data sovereignty violations

### Mitigations

1. **Self-Hosted** - No external dependencies
2. **SQLite** - Local file database, no network exposure
3. **Cryptographic Verification** - XBTS blockchain proof
4. **Audit Trail** - All transactions logged
5. **No Custodial Risk** - Direct peer-to-peer payments

**See**: `SECURITY.md` for complete security architecture

## Monitoring

### Server Status

```bash
./manage.sh status
```

### Database Queries

```bash
# Recent orders
python db.py orders

# Pending orders
python db.py query "SELECT * FROM orders WHERE status='pending'"

# Order summary
python db.py query "SELECT * FROM order_summary"

# Payment tracking
python db.py query "
SELECT o.id, o.total_amount, o.status, 
       COALESCE(SUM(p.amount), 0) as paid_amount
FROM orders o
LEFT JOIN payments p ON o.id = p.order_id AND p.status = 'confirmed'
GROUP BY o.id
"
```

### Logs

```bash
# API server logs
./manage.sh logs shop

# Or directly
tail -f shop_server.log
```

## Troubleshooting

### Server won't start

```bash
# Check if port is in use
./manage.sh status

# Stop all servers and restart
./manage.sh stop all
./manage.sh start all
```

### Database issues

```bash
# Check integrity
python db.py integrity

# Vacuum database
python db.py vacuum

# Restore from backup
cp ness_shop_backup.db ness_shop.db
```

### Configuration not saving

- Check shop server is running: `./manage.sh status shop`
- Check logs: `./manage.sh logs shop`
- Verify database exists: `ls -lh ness_shop.db`
- Check database integrity: `python db.py integrity`

## File Structure

```
h:\ness.cx\2026-rethink\
├── manage.sh              # Infrastructure management script
├── db.py                  # Database management tool
├── server.py              # Demo server
├── shop_api.py            # Shop API server with SQLite
├── index.html             # Privateness.network × PayRam demo
├── shop.html              # NESS Shop frontend
├── schema.sql             # Database schema
├── ness_shop.db           # SQLite database (runtime)
├── ness-pitch.txt         # Original pitch document
├── ROADMAP.md             # Project roadmap
├── README.md              # This file (English)
├── README.fr.md           # Documentation (Français)
├── SHOP-GUIDE.md          # Shop user guide (bilingual)
├── SECURITY.md            # Security architecture
├── USAGE.md               # Quick usage guide
├── .gitignore             # Git ignore rules
├── .demo_server.pid       # Demo server PID (runtime)
├── .shop_server.pid       # Shop server PID (runtime)
├── demo_server.log        # Demo server logs
└── shop_server.log        # Shop server logs
```

## Requirements

- Python 3.x (with sqlite3 module - included in standard library)
- Git Bash (Windows) or Bash (Linux/macOS)
- Random port range 50000-60000 available

## Documentation

- **README.md** - Infrastructure management (this file)
- **README.fr.md** - Documentation en français
- **SHOP-GUIDE.md** - Shop configuration and usage (bilingual)
- **SECURITY.md** - Security architecture and best practices
- **USAGE.md** - Quick start guide
- **schema.sql** - Database schema with comments

## Tips

- Servers use **random ports 50000-60000** for security
- Always check `./manage.sh status` for current URLs
- Database operations via `python db.py` (no sqlite3 command needed)
- Backup database before major changes: `python db.py backup`
- Use `python db.py shell` for interactive SQL
- Git ignores `.pid`, `.log`, and `.db` files automatically

## License

Sovereign infrastructure. No gatekeepers.

---

## Documentation Française

### Vue d'ensemble

Infrastructure complète auto-hébergée pour le commerce souverain:
- **Serveur Démo** - Démonstration de l'architecture Privateness.network × PayRam
- **Serveur Boutique** - Traitement des paiements XBTSX.NCH avec backend SQLite
- **Gestion de Base de Données** - Outils d'administration SQLite basés sur Python
- **Zéro Dépendance Externe** - Souveraineté complète des données

### Démarrage Rapide

```bash
# Démarrer tous les serveurs
./manage.sh start

# Vérifier le statut
./manage.sh status

# Accéder à la boutique
# L'URL sera affichée dans la sortie du statut (port aléatoire 50000-60000)

# Gérer la base de données
python db.py tables
python db.py config
python db.py products
```

## Gestion de l'Infrastructure

### Script de Gestion (`manage.sh`)

Contrôle complet sur les serveurs de démo et de boutique.

**Commandes:**

| Commande | Description | Exemple |
|----------|-------------|---------|
| `start [service]` | Démarrer le(s) serveur(s) | `./manage.sh start demo` |
| `stop [service]` | Arrêter le(s) serveur(s) | `./manage.sh stop shop` |
| `restart [service]` | Redémarrer le(s) serveur(s) | `./manage.sh restart all` |
| `status [service]` | Afficher le statut du serveur | `./manage.sh status` |
| `logs [service]` | Suivre les logs du serveur | `./manage.sh logs demo` |

**Services:**

- **demo** - Démo Privateness.network × PayRam (`index.html`)
- **shop** - API NESS Shop avec SQLite (`shop_api.py`)
- **all** - Tous les serveurs (par défaut)

**Exemples:**

```bash
# Démarrer uniquement le serveur de démo
./manage.sh start demo

# Arrêter uniquement le serveur de boutique
./manage.sh stop shop

# Redémarrer tous les serveurs
./manage.sh restart all

# Vérifier le statut de tous les serveurs
./manage.sh status

# Voir les logs du serveur de démo (Ctrl+C pour quitter)
./manage.sh logs demo

# Voir les logs du serveur de boutique
./manage.sh logs shop
```

## Gestion de la Base de Données

### Outil de Base de Données (`db.py`)

Gestion SQLite basée sur Python (pas besoin de commande `sqlite3` sur Windows).

**Visualiser les Données:**

```bash
# Lister toutes les tables
python db.py tables

# Afficher les schémas de table
python db.py schema
python db.py schema orders

# Voir la configuration de la boutique
python db.py config

# Voir les produits
python db.py products

# Voir les commandes récentes
python db.py orders
python db.py orders 20          # 20 dernières commandes

# Voir les détails d'une commande spécifique
python db.py order ORDER-1234567890
```

**Opérations de Base de Données:**

```bash
# Sauvegarder la base de données
python db.py backup
python db.py backup ma_sauvegarde.db

# Exporter une table vers JSON
python db.py export orders
python db.py export products export_commandes.json

# Vérifier l'intégrité de la base de données
python db.py integrity

# Vacuum de la base de données (récupérer l'espace)
python db.py vacuum

# Shell SQL interactif
python db.py shell

# Exécuter une requête SQL
python db.py query "SELECT * FROM orders WHERE status='pending'"
```

**Shell Interactif:**

```bash
python db.py shell
```

```sql
sqlite> SELECT * FROM shop_config;
sqlite> SELECT COUNT(*) FROM orders;
sqlite> SELECT * FROM order_summary;
sqlite> exit
```

## Détails des Serveurs

### Serveur Démo (`server.py`)

- **Fichier**: `index.html`
- **Port**: Aléatoire (50000-60000)
- **Fichier PID**: `.demo_server.pid`
- **Fichier Log**: `demo_server.log`
- **Contenu**: Démo de l'architecture Privateness.network × PayRam

### Serveur Boutique (`shop_api.py`)

- **Fichier**: `shop.html` (frontend)
- **Backend**: API JSON RESTful avec SQLite
- **Port**: Aléatoire (50000-60000)
- **Fichier PID**: `.shop_server.pid`
- **Fichier Log**: `shop_server.log`
- **Base de Données**: `ness_shop.db` (SQLite)

**Points de Terminaison API:**

```
GET  /api/config          - Configuration de la boutique
GET  /api/products        - Catalogue de produits
POST /api/orders          - Créer une commande
GET  /api/orders/{id}     - Détails de la commande
POST /api/config          - Mettre à jour la configuration
POST /api/products        - Ajouter un produit
PUT  /api/products/{id}   - Mettre à jour un produit
PUT  /api/orders/{id}     - Mettre à jour le statut de la commande
POST /api/payments        - Enregistrer un paiement
```

## Schéma de Base de Données

**Tables:**

- `shop_config` - Configuration du commerçant (ligne unique)
- `products` - Catalogue de produits avec prix
- `orders` - Suivi des commandes avec workflow de statut
- `order_items` - Articles par commande
- `payments` - Vérification des paiements blockchain XBTS
- `webhook_deliveries` - Journal d'audit de livraison webhook

**Vues:**

- `order_summary` - Données de commande agrégées avec statut de paiement

**Voir**: `schema.sql` pour la définition complète du schéma

## Architecture

### Démo Privateness.network

**Stack**: Skywire (Transport) → EMC (Nommage) → NESS (Exécution) → PayRam (Commerce)

**Fonctionnalités:**
- Vue d'ensemble de l'architecture
- Diagrammes de flux de paiement
- Modèle de déploiement
- Tableau de bord admin
- Visualisation de la feuille de route

### NESS Shop

**Paiement**: XBTSX.NCH (NESS Coin Hours) sur XBTS DEX

**Fonctionnalités:**
- Backend SQLite (souveraineté complète des données)
- API JSON RESTful
- Gestion du catalogue de produits
- Panier d'achat
- Flux de paiement XBTSX.NCH
- Suivi des commandes
- Vérification des paiements
- Support webhook (optionnel)

**Sécurité:**
- Aucune dépendance externe
- Base de données auto-hébergée
- Vérification cryptographique des paiements
- Piste d'audit
- Aucun risque de garde

## Configuration

### Configuration de la Boutique

1. Démarrer le serveur de boutique: `./manage.sh start shop`
2. Ouvrir dans le navigateur (vérifier le statut pour l'URL)
3. Cliquer sur **⚙️ Configure**
4. Entrer les champs requis:
   - Nom de la boutique
   - Description de la boutique
   - Adresse de paiement XBTS
   - Produits (nom, prix, emoji)
5. Sauvegarder la configuration

**Stockage des Données:**
- Toute la configuration stockée dans la base de données SQLite
- Pas de LocalStorage du navigateur
- Persistance côté serveur
- Compatible avec les sauvegardes

### Ajout de Produits

Via l'interface web:
1. Cliquer sur Configure
2. Cliquer sur "Add Product"
3. Entrer: emoji, nom, description, prix (NCH)
4. Sauvegarder

Via la base de données:
```bash
python db.py shell
```
```sql
INSERT INTO products (id, emoji, name, description, price)
VALUES ('product-001', '🎁', 'Service Premium', 'Description', 99.99);
```

## Flux de Paiement

### Paiement Client

1. Le client ajoute des articles au panier
2. Procède au paiement
3. Commande créée dans la base de données
4. Instructions de paiement affichées:
   - Adresse du compte XBTS
   - Montant exact en NCH
   - Mémo de commande unique

### Vérification Commerçant

**Vérification Manuelle:**
1. Le client envoie le paiement via le portefeuille XBTS
2. Le commerçant vérifie la blockchain XBTS
3. Vérifier le montant, le mémo, les confirmations
4. Enregistrer le paiement dans la base de données:

```bash
python db.py shell
```
```sql
INSERT INTO payments (order_id, txid, amount, to_address, memo, confirmations, status)
VALUES ('ORDER-123', 'tx_hash', 100.00, 'compte_marchand', 'ORDER-ORDER-123', 1, 'confirmed');

UPDATE orders SET status = 'paid', paid_at = CURRENT_TIMESTAMP WHERE id = 'ORDER-123';
```

**Automatisation Webhook (Optionnel):**
- Configurer l'URL webhook dans les paramètres de la boutique
- Notifications de paiement automatiques
- Voir `SECURITY.md` pour l'implémentation webhook

## Sauvegarde et Récupération

### Sauvegarde de Base de Données

```bash
# Sauvegarde rapide
python db.py backup

# Sauvegarde nommée
python db.py backup ness_shop_$(date +%Y%m%d).db

# Sauvegarde chiffrée
python db.py backup - | gpg -c > backup.db.gpg
```

### Exporter les Données

```bash
# Exporter les commandes vers JSON
python db.py export orders

# Exporter toutes les tables
python db.py export shop_config
python db.py export products
python db.py export orders
python db.py export payments
```

### Restaurer

```bash
# Depuis un fichier de sauvegarde
cp ness_shop_backup.db ness_shop.db
./manage.sh restart shop
```

## Sécurité

### Modèle de Menace

- Adversaire au niveau de l'État
- Surveillance réseau
- Censure des processeurs de paiement
- Violations de la souveraineté des données

### Atténuations

1. **Auto-Hébergé** - Aucune dépendance externe
2. **SQLite** - Base de données fichier local, pas d'exposition réseau
3. **Vérification Cryptographique** - Preuve blockchain XBTS
4. **Piste d'Audit** - Toutes les transactions enregistrées
5. **Aucun Risque de Garde** - Paiements directs peer-to-peer

**Voir**: `SECURITY.md` pour l'architecture de sécurité complète

## Surveillance

### Statut du Serveur

```bash
./manage.sh status
```

### Requêtes de Base de Données

```bash
# Commandes récentes
python db.py orders

# Commandes en attente
python db.py query "SELECT * FROM orders WHERE status='pending'"

# Résumé des commandes
python db.py query "SELECT * FROM order_summary"

# Suivi des paiements
python db.py query "
SELECT o.id, o.total_amount, o.status, 
       COALESCE(SUM(p.amount), 0) as paid_amount
FROM orders o
LEFT JOIN payments p ON o.id = p.order_id AND p.status = 'confirmed'
GROUP BY o.id
"
```

### Logs

```bash
# Logs du serveur API
./manage.sh logs shop

# Ou directement
tail -f shop_server.log
```

## Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier si le port est utilisé
./manage.sh status

# Arrêter tous les serveurs et redémarrer
./manage.sh stop all
./manage.sh start all
```

### Problèmes de base de données

```bash
# Vérifier l'intégrité
python db.py integrity

# Vacuum de la base de données
python db.py vacuum

# Restaurer depuis la sauvegarde
cp ness_shop_backup.db ness_shop.db
```

### La configuration ne sauvegarde pas

- Vérifier que le serveur de boutique fonctionne: `./manage.sh status shop`
- Vérifier les logs: `./manage.sh logs shop`
- Vérifier que la base de données existe: `ls -lh ness_shop.db`
- Vérifier l'intégrité de la base de données: `python db.py integrity`

## Exigences

- Python 3.x (avec module sqlite3 - inclus dans la bibliothèque standard)
- Git Bash (Windows) ou Bash (Linux/macOS)
- Plage de ports aléatoires 50000-60000 disponible

## Documentation

- **README.md** - Gestion de l'infrastructure (ce fichier)
- **README.fr.md** - Documentation française complète
- **SHOP-GUIDE.md** - Configuration et utilisation de la boutique (bilingue)
- **SECURITY.md** - Architecture de sécurité et meilleures pratiques
- **USAGE.md** - Guide de démarrage rapide
- **schema.sql** - Schéma de base de données avec commentaires

## Conseils

- Les serveurs utilisent des **ports aléatoires 50000-60000** pour la sécurité
- Toujours vérifier `./manage.sh status` pour les URLs actuelles
- Opérations de base de données via `python db.py` (pas besoin de commande sqlite3)
- Sauvegarder la base de données avant les changements majeurs: `python db.py backup`
- Utiliser `python db.py shell` pour SQL interactif
- Git ignore automatiquement les fichiers `.pid`, `.log` et `.db`

## Licence

Infrastructure souveraine. Aucun gardien.
