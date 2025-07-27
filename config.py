"""
Configuration settings for Joker's Telegram Bot - Deployment Version
"""
import os

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Validate bot token
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set. Please provide a valid Telegram bot token.")

# Port configuration for deployment
PORT = int(os.getenv('PORT', 10000))

# Bot messages
GREETING_MESSAGE = """
🎭 Salut tout le monde ! 👋

Je suis le bot unique de Joker pour les 3k développeurs ! 🚀
Développé par Kouamé 👨‍💻

Je suis là pour vous accompagner dans vos projets de développement.
Tapez /help pour voir mes commandes disponibles.

Heureux de rejoindre ce canal ! 🎉
"""

WELCOME_MESSAGE = """
👋 Bienvenue dans la communauté des développeurs !

Je suis Joker, votre bot assistant pour ce groupe de 3K développeurs.

Commandes disponibles :
• /help - Afficher l'aide
• /about - À propos du bot
• /dev - Informations pour développeurs
• /stats - Statistiques des prédictions
• /deploy - Package de déploiement

🎯 **Système de prédiction de cartes automatique :**
Le bot analyse automatiquement vos messages de jeu et fait des prédictions quand il détecte 3 cartes différentes !
"""

HELP_MESSAGE = """
🎭 Aide - Bot de Joker

Commandes disponibles :
• /start - Démarrer l'interaction avec le bot
• /help - Afficher ce message d'aide
• /about - En savoir plus sur le bot
• /dev - Informations sur le développeur
• /stats - Afficher les statistiques de prédiction
• /deploy - Créer un package de déploiement

Fonctionnalités :
✅ Salue automatiquement dans les canaux
🎯 Prédit les jeux avec 3 cartes différentes
📊 Vérifie les prédictions automatiquement
⚡ Détecte les messages modifiés

Développé par Kouamé pour les 3k développeurs 🚀
"""

ABOUT_MESSAGE = """
🎭 À propos du Bot de Joker

🤖 Nom : Bot de Joker
👨‍💻 Développeur : Kouamé
🎯 Public : 3k développeurs
🌟 Version : 2.0

Fonctionnalités :
✅ Salutation automatique dans les canaux
✅ Commandes interactives
✅ Support pour les développeurs
✅ Interface en français
✅ Système de prédiction de cartes automatique

Merci d'utiliser mon bot ! 💙
"""

DEV_MESSAGE = """
👨‍💻 Informations Développeur

Créé par : Kouamé
Spécialement conçu pour : 3k développeurs

🛠️ Stack technique :
• Python 3.11+
• python-telegram-bot v20.7
• Asyncio
• Logging avancé

📧 Contact : Via ce bot ou les canaux officiels
🚀 Mission : Faciliter le travail des développeurs

Merci pour votre confiance ! 🎭
"""

# Rate limiting
MAX_MESSAGES_PER_MINUTE = 20
RATE_LIMIT_WINDOW = 60  # seconds

# Card prediction rules
VALID_CARD_COMBINATIONS = [
    "♥️♠️♦️", "♥️♦️♠️", "♥️♣️♠️", "♥️♠️♣️",
    "♦️♥️♠️", "♦️♣️♥️", "♦️♣️♠️", "♠️♦️♥️",
    "♠️♣️♥️", "♠️♦️♣️", "♣️♦️♠️", "♣️♠️♦️",
    "♣️♦️♥️", "♣️♥️♦️", "♣️♠️♥️",
    "♥️♦️♣️", "♣️♥️♦️"
]

# Card symbols for detection
CARD_SYMBOLS = ["♥️", "♠️", "♦️", "♣️"]

# Prediction message template
PREDICTION_MESSAGE = "🔵{numero} 🔵3K: statut :⏳"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
