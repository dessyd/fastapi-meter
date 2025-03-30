# Makefile pour le projet fastapi-meter
# Utilisation:
#   make build - Reconstruit les images Docker sans cache
#   make up    - Démarre les conteneurs en mode détaché
#   make logs  - Affiche les logs en mode suivi
#   make down  - Arrête les conteneurs
#   make clean - Arrête les conteneurs et supprime les volumes

.PHONY: build up logs down clean

# Variables
DOCKER_COMPOSE = docker compose

# Reconstruit le conteneur à partir du Dockerfile avec --no-cache
build:
	$(DOCKER_COMPOSE) build --no-cache

# Démarre les conteneurs en mode détaché
up:
	$(DOCKER_COMPOSE) up -d

# Affiche les logs en mode suivi
logs:
	$(DOCKER_COMPOSE) logs -f

# Arrête les conteneurs
down:
	$(DOCKER_COMPOSE) down

# Arrête les conteneurs et supprime les volumes
clean:
	$(DOCKER_COMPOSE) down -v

# Aide
help:
	@echo "Commandes disponibles:"
	@echo "  make build - Reconstruit les images Docker sans cache"
	@echo "  make up    - Démarre les conteneurs en mode détaché"
	@echo "  make logs  - Affiche les logs en mode suivi"
	@echo "  make down  - Arrête les conteneurs"
	@echo "  make clean - Arrête les conteneurs et supprime les volumes"
	@echo "  make help  - Affiche ce message d'aide"
