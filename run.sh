#!/bin/bash
echo "🚀 Démarrage de Joker's Telegram Bot..."
echo "📁 Répertoire de travail: $(pwd)"
echo "🐍 Version Python: $(python --version)"
echo "📦 Installation des dépendances..."

pip install -r requirements.txt

echo "✅ Dépendances installées"
echo "🤖 Démarrage du bot..."

export PORT=10000
python main.py
