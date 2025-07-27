# Joker's Telegram Bot - Package de Déploiement Render.com

Un bot Telegram sophistiqué pour une communauté de 3K développeurs avec système de prédiction de cartes automatique.

## 🚀 Déploiement sur Render.com

### 1. Configuration sur Render.com
1. Créez un compte sur https://render.com
2. Cliquez sur "New +" → "Web Service"
3. Connectez votre repository GitHub ou uploadez ce ZIP
4. Configurez les paramètres suivants:

**Paramètres de base:**
- **Name:** jokers-telegram-bot
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`

### 2. Variables d'Environnement Requises
Dans les paramètres de votre service Render.com, ajoutez:
```
BOT_TOKEN=votre_token_telegram_bot_ici
```

### 3. Déploiement Automatique
- Le bot se déploiera automatiquement
- Utilisez le Dockerfile inclus pour une configuration optimisée
- Le fichier render.yaml est fourni pour une configuration automatique

### 4. Alternative avec GitHub
1. Uploadez ce projet sur GitHub
2. Connectez le repository à Render.com
3. Le déploiement se fera automatiquement

## 📋 Fonctionnalités

### 🎯 Système de Prédiction Automatique
- Détection automatique des combinaisons de 3 cartes différentes
- Prédictions basées sur l'analyse des messages de jeu
- Vérification automatique des résultats
- Statistiques de précision en temps réel

### 👥 Gestion Communautaire
- Accueil automatique des nouveaux membres
- Commandes d'aide et d'information
- Limitation de débit anti-spam
- Interface en français pour la communauté

### 🛠️ Architecture Technique
- Python 3.11 + asyncio
- Architecture modulaire et événementielle
- Logging complet et gestion d'erreurs
- Optimisé pour déploiement Replit

## 📁 Structure du Projet

```
jokers-telegram-bot/
├── main.py              # Point d'entrée principal
├── bot.py               # Contrôleur du bot
├── handlers.py          # Gestionnaires d'événements
├── card_predictor.py    # Système de prédiction
├── config.py            # Configuration
├── requirements.txt     # Dépendances Python
├── .replit             # Configuration Replit
├── replit.nix          # Environnement Nix
├── run.sh              # Script de démarrage
└── README.md           # Documentation
```

## 🎮 Commandes Disponibles

- `/start` - Message de bienvenue
- `/help` - Aide et documentation
- `/about` - Informations sur le bot
- `/dev` - Informations techniques
- `/stats` - Statistiques des prédictions
- `/deploy` - Générer package de déploiement

## 🃏 Système de Cartes

Le bot reconnaît les symboles de cartes suivants :
- ♠️ Pique
- ♥️ Cœur  
- ♣️ Trèfle
- ♦️ Carreau

## 📊 Prédictions

Le bot analyse automatiquement les messages contenant des numéros de jeu (#N1234) et fait des prédictions quand il détecte :
- 3 cartes différentes dans le premier parenthèses, OU
- 3 cartes différentes dans le deuxième parenthèses

La vérification se fait quand le message édité contient :
- ✅ ou 🔰 (symboles de succès) ET
- 3 cartes ou plus dans le premier parenthèses

## 👨‍💻 Développé par Kouamé

Spécialement conçu pour la communauté des 3K développeurs.

---

**Version :** 2.0  
**Dernière mise à jour :** Juillet 2025  
**Plateforme :** Replit Optimized
