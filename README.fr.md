# Gestion de l'Infrastructure NESS

Outils de gestion de l'infrastructure pour la démo Privateness.network et NESS Shop.

**[English](README.md)** | Français

## Démarrage Rapide

```bash
# Démarrer tous les serveurs
./manage.sh start

# Vérifier le statut
./manage.sh status

# Arrêter tous les serveurs
./manage.sh stop
```

## Script de Gestion

Le script `manage.sh` fournit un contrôle complet sur les serveurs de démo et de boutique.

### Commandes

| Commande | Description | Exemple |
|----------|-------------|---------|
| `start [service]` | Démarrer le(s) serveur(s) | `./manage.sh start demo` |
| `stop [service]` | Arrêter le(s) serveur(s) | `./manage.sh stop shop` |
| `restart [service]` | Redémarrer le(s) serveur(s) | `./manage.sh restart all` |
| `status [service]` | Afficher le statut du serveur | `./manage.sh status` |
| `logs [service]` | Suivre les logs du serveur | `./manage.sh logs demo` |

### Services

- **demo** - Démo Privateness.network × PayRam (`index.html`)
- **shop** - NESS Shop avec paiements XBTSX.NCH (`shop.html`)
- **all** - Tous les serveurs (par défaut)

### Exemples

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

## Détails des Serveurs

### Serveur Démo (`server.py`)
- **Fichier**: `index.html`
- **Port**: Aléatoire (50000-60000)
- **Fichier PID**: `.demo_server.pid`
- **Fichier Log**: `demo_server.log`

### Serveur Shop (`shop_server.py`)
- **Fichier**: `shop.html`
- **Port**: Aléatoire (50000-60000)
- **Fichier PID**: `.shop_server.pid`
- **Fichier Log**: `shop_server.log`

## Fonctionnalités

- ✅ Gestion des processus avec suivi PID
- ✅ Arrêt gracieux avec repli force-kill
- ✅ Détection et affichage des ports
- ✅ Sortie de statut codée par couleur
- ✅ Support de suivi des logs
- ✅ Contrôle individuel ou en masse des serveurs

## Architecture

### Démo Privateness.network
- **Stack**: Skywire (Transport) → EMC (Nommage) → NESS (Exécution) → PayRam (Commerce)
- **Intégration**: Assistant MCP PayRam pour les flux de paiement
- **Fonctionnalités**: Vue d'ensemble de l'architecture, flux de paiement, modèle de déploiement, tableau de bord admin

### NESS Shop
- **Paiement**: XBTSX.NCH (NESS Coin Hours) sur XBTS DEX
- **Fonctionnalités**: Catalogue de produits, panier d'achat, paiement XBTSX.NCH, gestion des commandes
- **Produits**: Accès relais, domaines EMC, bande passante Skywire, calcul NESS, kits d'intégration PayRam
- **Configuration**: Aucun mock ou placeholder - toutes les données proviennent de formulaires utilisateur
- **Stockage**: LocalStorage du navigateur pour la configuration du commerçant

## Dépôt Git

```bash
# Initialiser le dépôt (si ce n'est pas fait)
git init

# Ajouter des fichiers
git add .

# Commit
git commit -m "Commit initial: Infrastructure NESS avec intégration PayRam"
```

## Exigences

- Python 3.x
- Git Bash (Windows) ou Bash (Linux/macOS)
- Plage de ports aléatoires 50000-60000 disponible

## Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier si le port est utilisé
./manage.sh status

# Arrêter tous les serveurs et redémarrer
./manage.sh stop all
./manage.sh start all
```

### Vérifier les logs pour les erreurs

```bash
# Voir les logs de démo
cat demo_server.log

# Voir les logs de boutique
cat shop_server.log

# Ou suivre en temps réel
./manage.sh logs demo
```

### Redémarrage propre

```bash
# Tout arrêter
./manage.sh stop all

# Supprimer les fichiers PID s'ils sont obsolètes
rm -f .demo_server.pid .shop_server.pid

# Démarrer à neuf
./manage.sh start all
```

## Structure du Projet

```
h:\ness.cx\2026-rethink\
├── manage.sh              # Script de gestion de l'infrastructure
├── server.py              # Serveur de démo
├── shop_server.py         # Serveur de boutique
├── index.html             # Démo Privateness.network × PayRam
├── shop.html              # NESS Shop (paiements XBTSX.NCH)
├── ness-pitch.txt         # Document de pitch original
├── ROADMAP.md             # Feuille de route du projet
├── README.md              # Documentation (Anglais)
├── README.fr.md           # Documentation (Français)
├── SHOP-GUIDE.md          # Guide de la boutique (Bilingue)
├── USAGE.md               # Guide d'utilisation
├── .gitignore             # Règles d'ignore Git
├── .demo_server.pid       # PID du serveur de démo (runtime)
├── .shop_server.pid       # PID du serveur de boutique (runtime)
├── demo_server.log        # Logs du serveur de démo
└── shop_server.log        # Logs du serveur de boutique
```

## Guide de la Boutique NESS

Pour des instructions détaillées sur la configuration et l'utilisation de NESS Shop, consultez [SHOP-GUIDE.md](SHOP-GUIDE.md).

### Configuration de la Boutique

1. Démarrer le serveur: `./manage.sh start shop`
2. Ouvrir dans le navigateur
3. Cliquer sur **⚙️ Configure**
4. Entrer:
   - Nom de la boutique
   - Description
   - Adresse de paiement XBTS
   - Produits (nom, prix, emoji)
5. Sauvegarder la configuration

### Aucun Mock ou Placeholder

Toutes les données proviennent de votre configuration:
- ✅ Détails du commerçant (nom, description)
- ✅ Adresse de paiement XBTS réelle
- ✅ Catalogue de produits personnalisé
- ✅ URL webhook optionnelle
- ✅ Stockage LocalStorage du navigateur

### Flux de Paiement Réel

1. Le client ajoute des articles au panier
2. Procède au paiement
3. Reçoit les instructions de paiement XBTS:
   - Compte XBTS destinataire
   - Montant exact en XBTSX.NCH
   - Mémo de référence de commande unique
4. Envoie le paiement via le portefeuille XBTS
5. Le commerçant vérifie sur la blockchain XBTS
6. Exécute la commande

## Conseils

- Les serveurs utilisent des **ports aléatoires 50000-60000** pour la sécurité
- Toujours vérifier `./manage.sh status` pour les URLs actuelles
- Les logs sont écrits dans `demo_server.log` et `shop_server.log`
- Les fichiers PID suivent les processus en cours d'exécution
- Utiliser `Ctrl+C` pour quitter le suivi des logs
- Git ignore automatiquement les fichiers `.pid` et `.log`
- La configuration de la boutique persiste dans le LocalStorage du navigateur

## Licence

Infrastructure souveraine. Aucun gardien.
