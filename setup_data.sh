#!/bin/bash

# Script pour initialiser les données dans l'API fastapi-meter
# Usage: ./setup_data.sh [BASE_URL] [--debug]

set -e  # Arrêter le script en cas d'erreur

# URL de base de l'API (par défaut: http://localhost:8000)
BASE_URL=${1:-http://localhost:8000}

# Mode debug
DEBUG=0
if [ "$2" == "--debug" ]; then
    DEBUG=1
fi

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

echo -e "${BLUE}Initialisation des données pour l'API à ${BASE_URL}${NC}"

# Fonction pour vérifier les erreurs dans les réponses curl
check_error() {
    if echo "$1" | grep -q "error\|Error\|ERROR\|404\|401\|403\|500"; then
        echo -e "${RED}Erreur: $1${NC}"
        exit 1
    fi
}

# 1. Authentifier l'administrateur et récupérer le token JWT
echo -e "${YELLOW}1. Authentification de l'administrateur...${NC}"

# Variables pour l'authentification
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="admin_secure_password"

echo -e "${BLUE}Tentative d'authentification avec email: ${ADMIN_EMAIL}, password: ${ADMIN_PASSWORD}${NC}"

# En mode debug, afficher la commande curl complète
if [ $DEBUG -eq 1 ]; then
    echo -e "${YELLOW}curl -v -X POST \"${BASE_URL}/token\" -H \"Content-Type: application/x-www-form-urlencoded\" -d \"username=${ADMIN_EMAIL}&password=${ADMIN_PASSWORD}\"${NC}"
    AUTH_RESPONSE=$(curl -v -X POST "${BASE_URL}/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=${ADMIN_EMAIL}&password=${ADMIN_PASSWORD}" 2>&1)
else
    AUTH_RESPONSE=$(curl -s -X POST "${BASE_URL}/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=${ADMIN_EMAIL}&password=${ADMIN_PASSWORD}")
fi

# Afficher la réponse complète en mode debug
if [ $DEBUG -eq 1 ]; then
    echo -e "${YELLOW}Réponse d'authentification:${NC}"
    echo "$AUTH_RESPONSE"
fi

# Vérifier les erreurs
if echo "$AUTH_RESPONSE" | grep -q "error\|Error\|ERROR\|404\|401\|403\|500"; then
    echo -e "${RED}Erreur d'authentification: $AUTH_RESPONSE${NC}"
    exit 1
fi

# Extraire le token JWT
JWT_TOKEN=$(echo $AUTH_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$JWT_TOKEN" ]; then
    echo -e "${RED}Erreur: Impossible de récupérer le token JWT${NC}"
    exit 1
fi

echo -e "${GREEN}Token JWT récupéré avec succès!${NC}"

# Suite du script identique...
# ... (continuer avec les étapes 2, 3, etc.)

# 2. Créer un utilisateur de type "consumer"
echo -e "${YELLOW}2. Création de l'utilisateur consumer 'dd'...${NC}"
USER_RESPONSE=$(curl -s -X PUT "${BASE_URL}/user" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${JWT_TOKEN}" \
    -d '{
        "name": "dd",
        "email": "dd@tuut.toot",
        "password": "toto",
        "role": "consumer"
    }')

check_error "$USER_RESPONSE"

# Extraire l'ID de l'utilisateur
USER_ID=$(echo $USER_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$USER_ID" ]; then
    echo -e "${RED}Erreur: Impossible de récupérer l'ID de l'utilisateur${NC}"
    exit 1
fi

echo -e "${GREEN}Utilisateur créé avec succès! ID: ${USER_ID}${NC}"

# 3. Créer une location "maison" à Bruxelles
echo -e "${YELLOW}3. Création de la location 'maison' à Bruxelles...${NC}"

# Coordonnées de Bruxelles
BRUSSELS_LAT=50.8503
BRUSSELS_LON=4.3517

LOCATION_RESPONSE=$(curl -s -X PUT "${BASE_URL}/location" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${JWT_TOKEN}" \
    -d "{
        \"name\": \"maison\",
        \"lat\": ${BRUSSELS_LAT},
        \"lon\": ${BRUSSELS_LON},
        \"user_id\": ${USER_ID}
    }")

check_error "$LOCATION_RESPONSE"

# Extraire l'ID de la location
LOCATION_ID=$(echo $LOCATION_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$LOCATION_ID" ]; then
    echo -e "${RED}Erreur: Impossible de récupérer l'ID de la location${NC}"
    exit 1
fi

echo -e "${GREEN}Location créée avec succès! ID: ${LOCATION_ID}${NC}"

# 4. Créer un compteur d'eau associé à la maison
echo -e "${YELLOW}4. Création d'un compteur d'eau...${NC}"

# Générer un EAN aléatoire
# Format: Préfixe 54 (Belgique eau) + 11 chiffres aléatoires
EAN="54$(openssl rand -hex 6 | tr -dc '0-9' | head -c 11)"

METER_RESPONSE=$(curl -s -X PUT "${BASE_URL}/meter" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${JWT_TOKEN}" \
    -d "{
        \"ean\": \"${EAN}\",
        \"type\": \"water\",
        \"reading\": 0,
        \"status\": \"open\",
        \"location_id\": ${LOCATION_ID}
    }")

check_error "$METER_RESPONSE"

echo -e "${GREEN}Compteur d'eau créé avec succès! EAN: ${EAN}${NC}"

# 5. Lire tous les utilisateurs
echo -e "${YELLOW}5. Lecture de tous les utilisateurs...${NC}"
USERS_RESPONSE=$(curl -s -X GET "${BASE_URL}/user" \
    -H "Authorization: Bearer ${JWT_TOKEN}")

check_error "$USERS_RESPONSE"

echo -e "${GREEN}Liste des utilisateurs récupérée avec succès!${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${BLUE}           Utilisateurs                 ${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo $USERS_RESPONSE | jq -r '.' 2>/dev/null || echo $USERS_RESPONSE
echo -e "${BLUE}----------------------------------------${NC}"

# 6. Lire toutes les locations
echo -e "${YELLOW}6. Lecture de toutes les locations...${NC}"
LOCATIONS_RESPONSE=$(curl -s -X GET "${BASE_URL}/location" \
    -H "Authorization: Bearer ${JWT_TOKEN}")

check_error "$LOCATIONS_RESPONSE"

echo -e "${GREEN}Liste des locations récupérée avec succès!${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${BLUE}           Locations                    ${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo $LOCATIONS_RESPONSE | jq -r '.' 2>/dev/null || echo $LOCATIONS_RESPONSE
echo -e "${BLUE}----------------------------------------${NC}"

# 7. Lire tous les compteurs
echo -e "${YELLOW}7. Lecture de tous les compteurs...${NC}"
METERS_RESPONSE=$(curl -s -X GET "${BASE_URL}/meter" \
    -H "Authorization: Bearer ${JWT_TOKEN}")

check_error "$METERS_RESPONSE"

echo -e "${GREEN}Liste des compteurs récupérée avec succès!${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${BLUE}           Compteurs                    ${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo $METERS_RESPONSE | jq -r '.' 2>/dev/null || echo $METERS_RESPONSE
echo -e "${BLUE}----------------------------------------${NC}"

# Résumé
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${BLUE}           Résumé des opérations        ${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${GREEN}Utilisateur '${USER_ID}' créé avec l'email dd@tuut.toot${NC}"
echo -e "${GREEN}Location '${LOCATION_ID}' (maison) créée à Bruxelles${NC}"
echo -e "${GREEN}Compteur d'eau créé avec l'EAN ${EAN}${NC}"
echo -e "${BLUE}----------------------------------------${NC}"

echo -e "${GREEN}Initialisation des données terminée avec succès!${NC}"
