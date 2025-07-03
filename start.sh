#!/bin/bash

echo "🚀 Démarrage du chatbot de déclaration de sinistres..."

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker d'abord."
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose d'abord."
    exit 1
fi

# Arrêter les conteneurs existants s'ils existent
echo "🛑 Arrêt des conteneurs existants..."
docker-compose down

# Construire les images
echo "🔨 Construction des images Docker..."
docker-compose build

# Démarrer les services
echo "▶️ Démarrage des services..."
docker-compose up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier l'état des services
echo "🔍 Vérification de l'état des services..."
docker-compose ps

echo ""
echo "✅ Le chatbot est maintenant disponible !"
echo "🌐 Interface web : http://localhost:8080"
echo "🤖 API Rasa : http://localhost:5005"
echo "⚙️ Actions Rasa : http://localhost:5055"
echo ""
echo "Pour arrêter les services, utilisez : docker-compose down"
echo "Pour voir les logs, utilisez : docker-compose logs -f" 