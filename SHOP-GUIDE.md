# NESS Shop - Complete Guide / Guide Complet

**English** | [Français](#guide-en-français)

---

## English Guide

### Overview

NESS Shop is a **self-hosted sovereign commerce application** with SQLite backend that accepts XBTSX.NCH (NESS Coin Hours) payments on the XBTS decentralized exchange.

**Key Features:**

- ✅ **SQLite Backend** - All data stored in local database file
- ✅ **RESTful API** - JSON API for all operations
- ✅ **Zero External Dependencies** - Completely self-hosted
- ✅ **Real XBTS Payments** - Actual XBTSX.NCH transactions on XBTS DEX
- ✅ **Payment Verification** - Blockchain-based proof of payment
- ✅ **Webhook Support** - Optional payment notifications
- ✅ **Complete Data Sovereignty** - You own all data
- ✅ **Audit Trail** - All transactions logged
- ✅ **Backup-Friendly** - Single SQLite file

### Architecture

```
Frontend (shop.html)
    ↓ HTTP/JSON
Backend API (shop_api.py)
    ↓ SQL
SQLite Database (ness_shop.db)
    ↓ Verification
XBTS Blockchain
```

**No Mocks or Placeholders:**
- All merchant data from database
- All products from database
- All orders persisted to database
- Real XBTS payment addresses
- Real blockchain verification

### Getting Started

#### 1. Start the Shop Server

```bash
./manage.sh start shop
```

Check the port:
```bash
./manage.sh status shop
```

Output example:
```
[OK] Shop server: RUNNING (PID: 3537, Port: 57892)
[INFO] URL: http://127.0.0.1:57892/shop.html
```

Access at: `http://127.0.0.1:[PORT]/shop.html`

#### 2. Configure Your Shop

Click the **⚙️ Configure** button in the header.

**Required Fields:**

- **Shop Name** - Your store's display name (e.g., "NESS Services")
- **Shop Description** - Brief description of your services
- **XBTS Payment Address** - Your XBTS account name (where payments are sent)
- **Products** - At least one product with name, price, and emoji

**Optional Fields:**

- **Payment Memo Prefix** - Customize order reference prefix (default: ORDER)
- **Webhook URL** - URL to receive payment notifications (must be publicly accessible)

**Data Storage:**
All configuration is saved to SQLite database (`ness_shop.db`), not browser LocalStorage.

#### 3. Add Products

Click **+ Add Product** to add items to your catalog.

For each product:
- **Emoji** - Visual icon (e.g., 🎁, 💻, 🌐)
- **Name** - Product name (required)
- **Description** - Brief description (optional)
- **Price** - Price in NCH (XBTSX.NCH) (required, must be > 0)

**Example Products:**
- 🌐 NESS Relay Access - 30-day premium relay node access - 100 NCH
- 🔐 EMC Domain Registration - 1-year .emc domain via NVS - 250 NCH
- ⚡ Skywire Bandwidth Pack - 100GB encrypted mesh transit - 75 NCH

#### 4. Save Configuration

Click **Save Configuration**. Your shop is now live!

**Verification:**
```bash
# Check configuration was saved
python db.py config

# Check products were created
python db.py products
```

### Making a Sale

#### Customer Flow

1. Customer browses products on your shop
2. Adds items to cart
3. Clicks "Proceed to Checkout"
4. Order is created in database
5. Receives payment instructions:
   - XBTS account to send to
   - Exact NCH amount
   - Unique order reference memo

**Example Payment Instructions:**
```
Send To (XBTS Account): your-xbts-account
Amount: 150.00 XBTSX.NCH
Memo / Reference: ORDER-ORDER-1710208800000
```

#### Merchant Verification

**Manual Verification (Recommended):**

1. Customer sends payment via XBTS wallet
2. You check XBTS blockchain explorer
3. Verify:
   - Correct amount
   - Correct memo matches order ID
   - At least 1 confirmation
4. Record payment in database
5. Update order status
6. Fulfill order

**Recording Payment:**

```bash
python db.py shell
```

```sql
-- Record the payment
INSERT INTO payments (order_id, txid, amount, from_address, to_address, memo, confirmations, status)
VALUES (
  'ORDER-1710208800000',
  'xbts_transaction_hash',
  150.00,
  'customer_xbts_account',
  'your_xbts_account',
  'ORDER-ORDER-1710208800000',
  1,
  'confirmed'
);

-- Update order status
UPDATE orders 
SET status = 'paid', paid_at = CURRENT_TIMESTAMP 
WHERE id = 'ORDER-1710208800000';

-- Mark as fulfilled after delivery
UPDATE orders 
SET status = 'fulfilled', fulfilled_at = CURRENT_TIMESTAMP 
WHERE id = 'ORDER-1710208800000';
```

**Webhook Automation (Optional):**

If you configure a webhook URL, you can receive automated payment notifications. See `SECURITY.md` for webhook implementation details.

### Database Management

#### Viewing Data

```bash
# List all tables
python db.py tables

# View shop configuration
python db.py config

# View all products
python db.py products

# View recent orders
python db.py orders
python db.py orders 20          # Last 20 orders

# View specific order details
python db.py order ORDER-1710208800000
```

**Example Output:**
```
Order Details: ORDER-1710208800000
--------------------------------------------------------------------------------
Status: paid
Total: 150.0 XBTSX.NCH
Payment Address: your-xbts-account
Payment Memo: ORDER-ORDER-1710208800000
Created: 2024-03-12 00:00:00

Items (2):
  - NESS Relay Access x1 @ 100.0 = 100.0
  - Skywire Bandwidth Pack x1 @ 75.0 = 75.0

Payments (1):
  - 150.0 XBTSX.NCH (confirmed)
    TX: xbts_transaction_hash
```

#### Database Operations

```bash
# Backup database
python db.py backup
python db.py backup ness_shop_$(date +%Y%m%d).db

# Export orders to JSON
python db.py export orders

# Check database integrity
python db.py integrity

# Vacuum database (reclaim space)
python db.py vacuum

# Interactive SQL shell
python db.py shell
```

#### Common Queries

```bash
# Pending orders
python db.py query "SELECT * FROM orders WHERE status='pending'"

# Orders with payments
python db.py query "SELECT * FROM order_summary"

# Total revenue
python db.py query "SELECT SUM(total_amount) as revenue FROM orders WHERE status IN ('paid', 'fulfilled')"

# Recent payments
python db.py query "SELECT * FROM payments ORDER BY created_at DESC LIMIT 10"
```

### Payment Verification Workflow

#### Step-by-Step Process

1. **Customer Checkout**
   - Order created in database
   - Status: `pending`
   - Unique order ID generated
   - Payment instructions displayed

2. **Customer Payment**
   - Customer sends XBTSX.NCH via XBTS wallet
   - Includes order memo in transaction
   - Transaction broadcast to XBTS blockchain

3. **Merchant Verification**
   - Check XBTS blockchain explorer
   - Find transaction by memo or address
   - Verify amount matches order total
   - Verify memo matches order ID
   - Wait for confirmations (≥1)

4. **Record Payment**
   - Insert payment record in database
   - Include transaction hash (txid)
   - Update order status to `paid`
   - Record payment timestamp

5. **Fulfill Order**
   - Deliver product/service
   - Update order status to `fulfilled`
   - Record fulfillment timestamp

6. **Customer Notification** (Optional)
   - Send confirmation email
   - Trigger webhook if configured
   - Provide receipt/invoice

### Security Best Practices

#### Payment Verification

1. **Always Verify on Blockchain** - Never trust customer claims
2. **Check Memo Exactly** - Must match order ID precisely
3. **Require Confirmations** - Wait for at least 1 blockchain confirmation
4. **Verify Amount** - Must match order total exactly
5. **Record Transaction Hash** - Store txid for audit trail

#### Database Security

```bash
# Set proper file permissions
chmod 600 ness_shop.db
chmod 600 ness_shop.db-journal

# Regular backups
python db.py backup

# Encrypted backups
python db.py backup - | gpg -c > backup_$(date +%Y%m%d).db.gpg
```

#### API Security

For production deployment:
- Use HTTPS (reverse proxy with Let's Encrypt)
- Implement authentication for admin endpoints
- Rate limiting on API endpoints
- CORS configuration for production domain
- Firewall rules (only expose necessary ports)

See `SECURITY.md` for complete security architecture.

### Troubleshooting

#### Shop won't load

```bash
# Check server is running
./manage.sh status shop

# Check logs
./manage.sh logs shop

# Restart server
./manage.sh restart shop
```

#### Configuration not saving

```bash
# Check database exists
ls -lh ness_shop.db

# Check database integrity
python db.py integrity

# Check API logs
tail -f shop_server.log
```

#### Orders not appearing

```bash
# Check database directly
python db.py orders

# Check for errors in logs
./manage.sh logs shop

# Verify API is responding
curl http://127.0.0.1:[PORT]/api/orders
```

#### Payment not confirming

- Verify XBTS account name is correct in configuration
- Check memo format matches exactly: `PREFIX-ORDER-ID`
- Confirm payment on XBTS blockchain explorer
- Verify transaction has confirmations
- Check database for payment record: `python db.py query "SELECT * FROM payments"`

### Export/Import Configuration

#### Export Database

```bash
# Full database backup
python db.py backup production_backup.db

# Export specific tables to JSON
python db.py export shop_config
python db.py export products
python db.py export orders
```

#### Import/Restore

```bash
# Restore from backup
cp production_backup.db ness_shop.db
./manage.sh restart shop

# Import from SQL dump
python db.py shell < backup.sql
```

### API Reference

#### Public Endpoints

```
GET  /api/config          - Get shop configuration
GET  /api/products        - Get product catalog
POST /api/orders          - Create new order
GET  /api/orders/{id}     - Get order details
```

#### Admin Endpoints

```
POST /api/config          - Update shop configuration
POST /api/products        - Add new product
PUT  /api/products/{id}   - Update product
PUT  /api/orders/{id}     - Update order status
POST /api/payments        - Record payment
```

**Example: Create Order**

```bash
curl -X POST http://127.0.0.1:57892/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "product-001", "name": "NESS Relay", "price": 100, "quantity": 1}
    ]
  }'
```

**Response:**
```json
{
  "id": "ORDER-1710208800000",
  "total_amount": 100.0,
  "currency": "XBTSX.NCH",
  "payment_address": "your-xbts-account",
  "payment_memo": "ORDER-ORDER-1710208800000",
  "status": "pending",
  "items": [...]
}
```

---

## Guide en Français

### Aperçu

NESS Shop est une **application de commerce souverain auto-hébergée** avec backend SQLite qui accepte les paiements XBTSX.NCH (NESS Coin Hours) sur la bourse décentralisée XBTS.

**Fonctionnalités Principales:**

- ✅ **Backend SQLite** - Toutes les données stockées dans un fichier de base de données local
- ✅ **API RESTful** - API JSON pour toutes les opérations
- ✅ **Zéro Dépendance Externe** - Complètement auto-hébergé
- ✅ **Paiements XBTS Réels** - Transactions XBTSX.NCH réelles sur XBTS DEX
- ✅ **Vérification des Paiements** - Preuve de paiement basée sur la blockchain
- ✅ **Support Webhook** - Notifications de paiement optionnelles
- ✅ **Souveraineté Complète des Données** - Vous possédez toutes les données
- ✅ **Piste d'Audit** - Toutes les transactions enregistrées
- ✅ **Compatible Sauvegarde** - Fichier SQLite unique

### Architecture

```
Frontend (shop.html)
    ↓ HTTP/JSON
Backend API (shop_api.py)
    ↓ SQL
Base de Données SQLite (ness_shop.db)
    ↓ Vérification
Blockchain XBTS
```

**Aucun Mock ou Placeholder:**
- Toutes les données du commerçant depuis la base de données
- Tous les produits depuis la base de données
- Toutes les commandes persistées dans la base de données
- Adresses de paiement XBTS réelles
- Vérification blockchain réelle

### Démarrage

#### 1. Démarrer le Serveur Shop

```bash
./manage.sh start shop
```

Vérifier le port:
```bash
./manage.sh status shop
```

Exemple de sortie:
```
[OK] Shop server: RUNNING (PID: 3537, Port: 57892)
[INFO] URL: http://127.0.0.1:57892/shop.html
```

Accéder à: `http://127.0.0.1:[PORT]/shop.html`

#### 2. Configurer Votre Boutique

Cliquer sur le bouton **⚙️ Configure** dans l'en-tête.

**Champs Obligatoires:**

- **Nom de la Boutique** - Le nom d'affichage de votre magasin (ex: "NESS Services")
- **Description** - Brève description de vos services
- **Adresse de Paiement XBTS** - Votre nom de compte XBTS (où les paiements sont envoyés)
- **Produits** - Au moins un produit avec nom, prix et emoji

**Champs Optionnels:**

- **Préfixe Mémo** - Personnaliser le préfixe de référence de commande (défaut: ORDER)
- **URL Webhook** - URL pour recevoir les notifications de paiement (doit être accessible publiquement)

**Stockage des Données:**
Toute la configuration est sauvegardée dans la base de données SQLite (`ness_shop.db`), pas dans le LocalStorage du navigateur.

#### 3. Ajouter des Produits

Cliquer sur **+ Add Product** pour ajouter des articles à votre catalogue.

Pour chaque produit:
- **Emoji** - Icône visuelle (ex: 🎁, 💻, 🌐)
- **Nom** - Nom du produit (obligatoire)
- **Description** - Brève description (optionnel)
- **Prix** - Prix en NCH (XBTSX.NCH) (obligatoire, doit être > 0)

**Exemples de Produits:**
- 🌐 Accès Relais NESS - Accès nœud relais premium 30 jours - 100 NCH
- 🔐 Enregistrement Domaine EMC - Domaine .emc 1 an via NVS - 250 NCH
- ⚡ Pack Bande Passante Skywire - Transit mesh chiffré 100GB - 75 NCH

#### 4. Sauvegarder la Configuration

Cliquer sur **Save Configuration**. Votre boutique est maintenant en ligne!

**Vérification:**
```bash
# Vérifier que la configuration a été sauvegardée
python db.py config

# Vérifier que les produits ont été créés
python db.py products
```

### Réaliser une Vente

#### Flux Client

1. Le client parcourt les produits sur votre boutique
2. Ajoute des articles au panier
3. Clique sur "Proceed to Checkout"
4. La commande est créée dans la base de données
5. Reçoit les instructions de paiement:
   - Compte XBTS destinataire
   - Montant exact en NCH
   - Mémo de référence de commande unique

**Exemple d'Instructions de Paiement:**
```
Envoyer À (Compte XBTS): votre-compte-xbts
Montant: 150.00 XBTSX.NCH
Mémo / Référence: ORDER-ORDER-1710208800000
```

#### Vérification Commerçant

**Vérification Manuelle (Recommandé):**

1. Le client envoie le paiement via le portefeuille XBTS
2. Vous vérifiez l'explorateur de blockchain XBTS
3. Vérifier:
   - Montant correct
   - Mémo correct correspond à l'ID de commande
   - Au moins 1 confirmation
4. Enregistrer le paiement dans la base de données
5. Mettre à jour le statut de la commande
6. Exécuter la commande

**Enregistrement du Paiement:**

```bash
python db.py shell
```

```sql
-- Enregistrer le paiement
INSERT INTO payments (order_id, txid, amount, from_address, to_address, memo, confirmations, status)
VALUES (
  'ORDER-1710208800000',
  'hash_transaction_xbts',
  150.00,
  'compte_xbts_client',
  'votre_compte_xbts',
  'ORDER-ORDER-1710208800000',
  1,
  'confirmed'
);

-- Mettre à jour le statut de la commande
UPDATE orders 
SET status = 'paid', paid_at = CURRENT_TIMESTAMP 
WHERE id = 'ORDER-1710208800000';

-- Marquer comme exécutée après livraison
UPDATE orders 
SET status = 'fulfilled', fulfilled_at = CURRENT_TIMESTAMP 
WHERE id = 'ORDER-1710208800000';
```

**Automatisation Webhook (Optionnel):**

Si vous configurez une URL webhook, vous pouvez recevoir des notifications de paiement automatisées. Voir `SECURITY.md` pour les détails d'implémentation webhook.

### Gestion de la Base de Données

#### Visualiser les Données

```bash
# Lister toutes les tables
python db.py tables

# Voir la configuration de la boutique
python db.py config

# Voir tous les produits
python db.py products

# Voir les commandes récentes
python db.py orders
python db.py orders 20          # 20 dernières commandes

# Voir les détails d'une commande spécifique
python db.py order ORDER-1710208800000
```

**Exemple de Sortie:**
```
Détails de la Commande: ORDER-1710208800000
--------------------------------------------------------------------------------
Statut: paid
Total: 150.0 XBTSX.NCH
Adresse de Paiement: votre-compte-xbts
Mémo de Paiement: ORDER-ORDER-1710208800000
Créé: 2024-03-12 00:00:00

Articles (2):
  - Accès Relais NESS x1 @ 100.0 = 100.0
  - Pack Bande Passante Skywire x1 @ 75.0 = 75.0

Paiements (1):
  - 150.0 XBTSX.NCH (confirmé)
    TX: hash_transaction_xbts
```

#### Opérations de Base de Données

```bash
# Sauvegarder la base de données
python db.py backup
python db.py backup ness_shop_$(date +%Y%m%d).db

# Exporter les commandes vers JSON
python db.py export orders

# Vérifier l'intégrité de la base de données
python db.py integrity

# Vacuum de la base de données (récupérer l'espace)
python db.py vacuum

# Shell SQL interactif
python db.py shell
```

#### Requêtes Courantes

```bash
# Commandes en attente
python db.py query "SELECT * FROM orders WHERE status='pending'"

# Commandes avec paiements
python db.py query "SELECT * FROM order_summary"

# Revenu total
python db.py query "SELECT SUM(total_amount) as revenue FROM orders WHERE status IN ('paid', 'fulfilled')"

# Paiements récents
python db.py query "SELECT * FROM payments ORDER BY created_at DESC LIMIT 10"
```

### Flux de Vérification des Paiements

#### Processus Étape par Étape

1. **Paiement Client**
   - Commande créée dans la base de données
   - Statut: `pending`
   - ID de commande unique généré
   - Instructions de paiement affichées

2. **Paiement Client**
   - Le client envoie XBTSX.NCH via le portefeuille XBTS
   - Inclut le mémo de commande dans la transaction
   - Transaction diffusée sur la blockchain XBTS

3. **Vérification Commerçant**
   - Vérifier l'explorateur de blockchain XBTS
   - Trouver la transaction par mémo ou adresse
   - Vérifier que le montant correspond au total de la commande
   - Vérifier que le mémo correspond à l'ID de commande
   - Attendre les confirmations (≥1)

4. **Enregistrer le Paiement**
   - Insérer l'enregistrement de paiement dans la base de données
   - Inclure le hash de transaction (txid)
   - Mettre à jour le statut de la commande à `paid`
   - Enregistrer l'horodatage du paiement

5. **Exécuter la Commande**
   - Livrer le produit/service
   - Mettre à jour le statut de la commande à `fulfilled`
   - Enregistrer l'horodatage d'exécution

6. **Notification Client** (Optionnel)
   - Envoyer un email de confirmation
   - Déclencher le webhook si configuré
   - Fournir un reçu/facture

### Bonnes Pratiques de Sécurité

#### Vérification des Paiements

1. **Toujours Vérifier sur la Blockchain** - Ne jamais faire confiance aux affirmations du client
2. **Vérifier le Mémo Exactement** - Doit correspondre précisément à l'ID de commande
3. **Exiger des Confirmations** - Attendre au moins 1 confirmation blockchain
4. **Vérifier le Montant** - Doit correspondre exactement au total de la commande
5. **Enregistrer le Hash de Transaction** - Stocker le txid pour la piste d'audit

#### Sécurité de la Base de Données

```bash
# Définir les permissions de fichier appropriées
chmod 600 ness_shop.db
chmod 600 ness_shop.db-journal

# Sauvegardes régulières
python db.py backup

# Sauvegardes chiffrées
python db.py backup - | gpg -c > backup_$(date +%Y%m%d).db.gpg
```

#### Sécurité API

Pour le déploiement en production:
- Utiliser HTTPS (reverse proxy avec Let's Encrypt)
- Implémenter l'authentification pour les endpoints admin
- Limitation de débit sur les endpoints API
- Configuration CORS pour le domaine de production
- Règles de pare-feu (exposer uniquement les ports nécessaires)

Voir `SECURITY.md` pour l'architecture de sécurité complète.

### Dépannage

#### La boutique ne charge pas

```bash
# Vérifier que le serveur fonctionne
./manage.sh status shop

# Vérifier les logs
./manage.sh logs shop

# Redémarrer le serveur
./manage.sh restart shop
```

#### La configuration ne sauvegarde pas

```bash
# Vérifier que la base de données existe
ls -lh ness_shop.db

# Vérifier l'intégrité de la base de données
python db.py integrity

# Vérifier les logs de l'API
tail -f shop_server.log
```

#### Les commandes n'apparaissent pas

```bash
# Vérifier la base de données directement
python db.py orders

# Vérifier les erreurs dans les logs
./manage.sh logs shop

# Vérifier que l'API répond
curl http://127.0.0.1:[PORT]/api/orders
```

#### Le paiement ne se confirme pas

- Vérifier que le nom du compte XBTS est correct dans la configuration
- Vérifier que le format du mémo correspond exactement: `PREFIXE-ORDER-ID`
- Confirmer le paiement sur l'explorateur de blockchain XBTS
- Vérifier que la transaction a des confirmations
- Vérifier la base de données pour l'enregistrement de paiement: `python db.py query "SELECT * FROM payments"`

### Exporter/Importer la Configuration

#### Exporter la Base de Données

```bash
# Sauvegarde complète de la base de données
python db.py backup production_backup.db

# Exporter des tables spécifiques vers JSON
python db.py export shop_config
python db.py export products
python db.py export orders
```

#### Importer/Restaurer

```bash
# Restaurer depuis la sauvegarde
cp production_backup.db ness_shop.db
./manage.sh restart shop

# Importer depuis un dump SQL
python db.py shell < backup.sql
```

### Référence API

#### Points de Terminaison Publics

```
GET  /api/config          - Obtenir la configuration de la boutique
GET  /api/products        - Obtenir le catalogue de produits
POST /api/orders          - Créer une nouvelle commande
GET  /api/orders/{id}     - Obtenir les détails de la commande
```

#### Points de Terminaison Admin

```
POST /api/config          - Mettre à jour la configuration de la boutique
POST /api/products        - Ajouter un nouveau produit
PUT  /api/products/{id}   - Mettre à jour un produit
PUT  /api/orders/{id}     - Mettre à jour le statut de la commande
POST /api/payments        - Enregistrer un paiement
```

**Exemple: Créer une Commande**

```bash
curl -X POST http://127.0.0.1:57892/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "product-001", "name": "Relais NESS", "price": 100, "quantity": 1}
    ]
  }'
```

**Réponse:**
```json
{
  "id": "ORDER-1710208800000",
  "total_amount": 100.0,
  "currency": "XBTSX.NCH",
  "payment_address": "votre-compte-xbts",
  "payment_memo": "ORDER-ORDER-1710208800000",
  "status": "pending",
  "items": [...]
}
```

---

## Support / Assistance

For technical support or questions / Pour le support technique ou questions:
- GitHub: https://github.com/privateness-network
- Documentation: See README.md, SECURITY.md, and schema.sql
- Documentation: Voir README.md, SECURITY.md et schema.sql
