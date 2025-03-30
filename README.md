# FastAPI Meter

Une API RESTful pour la gestion des compteurs d'eau, de gaz et d'électricité, avec authentification et contrôle d'accès basé sur les rôles.

## Description du projet

FastAPI Meter permet de gérer un ensemble de compteurs associés à des emplacements physiques et des utilisateurs. L'application permet :

- La gestion des utilisateurs avec différents niveaux d'accès (consommateur, employé, administrateur)
- La gestion des emplacements géographiques
- La gestion des compteurs (eau, gaz, électricité) avec suivi des consommations
- Une API sécurisée avec authentification JWT

## Structure de données

### User (Utilisateur)

- `id`: Identifiant unique
- `name`: Nom de l'utilisateur
- `email`: Email (utilisé pour l'authentification)
- `password`: Mot de passe (hashé)
- `role`: Rôle (consumer, employee, admin)

### Location (Emplacement)

- `id`: Identifiant unique
- `name`: Nom décrivant l'endroit
- `lat`: Latitude
- `lon`: Longitude
- `user_id`: ID de l'utilisateur associé

### Meter (Compteur)

- `ean`: Identifiant unique (visible)
- `status`: État (Open/Close)
- `type`: Type (gas, water, electricity)
- `reading`: Consommation actuelle
- `unit`: Unité correspondante (m³, kWh)
- `location_id`: ID de l'emplacement
- `last_update`: Horodatage de la dernière mise à jour

## Contraintes

- Un compteur se trouve dans un et un seul emplacement
- Un emplacement peut avoir plusieurs compteurs
- Un emplacement est relié à un et un seul utilisateur
- Un utilisateur de type employee ou admin n'a pas d'emplacement
- Un utilisateur de type consumer a au minimum 1 emplacement et peut en avoir plusieurs

## Endpoints API

1. **/** - Racine
   - `GET`: Affiche le nom et la version de l'application

2. **/meter** - Gestion des compteurs
   - `GET`: Liste des compteurs
   - `PUT`: Création d'un compteur

3. **/meter/{ean}** - Opérations sur un compteur spécifique
   - `GET`: Détails du compteur
   - `PATCH`: Mise à jour de la valeur ou du statut
   - `DELETE`: Suppression du compteur

4. **/location** - Gestion des emplacements
   - `GET`: Liste des emplacements
   - `PUT`: Création d'un emplacement

5. **/location/{id}** - Opérations sur un emplacement spécifique
   - `GET`: Détails de l'emplacement et compteurs associés
   - `PATCH`: Mise à jour des informations
   - `DELETE`: Suppression de l'emplacement

6. **/user** - Gestion des utilisateurs
   - `GET`: Liste des utilisateurs
   - `PUT`: Création d'un utilisateur

7. **/user/{id}** - Opérations sur un utilisateur spécifique
   - `GET`: Détails de l'utilisateur
   - `PATCH`: Mise à jour des informations
   - `DELETE`: Suppression de l'utilisateur

8. **/token** - Authentification
   - `POST`: Obtention d'un token JWT

## Autorisations par rôle

### Consumer

- Accès à ses propres données uniquement (compteurs, emplacements)
- Lecture seule sauf pour son profil

### Employee

- Accès en lecture/écriture pour tous les compteurs et emplacements
- Pas de suppression de données
- Accès en lecture pour les utilisateurs consommateurs

### Admin

- Accès complet à toutes les fonctionnalités
- Seul rôle autorisé à supprimer des données

## Technologies utilisées

- **FastAPI**: Framework web haute performance
- **SQLModel**: ORM combinant SQLAlchemy et Pydantic
- **PostgreSQL**: Base de données relationnelle
- **JWT**: Authentification sécurisée
- **Docker**: Conteneurisation de l'application

## Installation et démarrage

### Prérequis

- Docker et Docker Compose

### Installation

1. Cloner le dépôt
2. Copier `.env.example` vers `.env` et personnaliser les variables d'environnement
3. Lancer l'application avec Docker Compose :

   ```bash
   docker-compose up -d
   ```

### Accès

- API: <http://localhost:8000>
- Documentation OpenAPI: <http://localhost:8000/docs>
- Adminer (gestion de base de données): <http://localhost:8080>

## Utilisateur initial

Un utilisateur administrateur est créé automatiquement au premier démarrage avec les identifiants configurés dans le fichier `.env` (par défaut: <admin@example.com> / admin_secure_password).

## Développement

### Structure du projet

```tee
fastapi-meter/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée de l'application
│   ├── config.py               # Configurations et variables d'environnement
│   ├── database.py             # Configuration de la base de données
│   ├── models.py               # Modèles de données SQLModel
│   ├── auth/                   # Authentification et autorisation
│   ├── routers/                # Endpoints API
│   └── core/                   # Fonctionnalités centrales
├── alembic/                    # Migrations de base de données
├── tests/                      # Tests unitaires et d'intégration
├── .env.example                # Exemple de fichier .env
├── requirements.txt            # Dépendances Python
├── Dockerfile                  # Configuration Docker
└── docker-compose.yml          # Configuration Docker Compose
```

### Commandes utiles

- Démarrer les containers: `docker-compose up -d`
- Arrêter les containers: `docker-compose down`
- Voir les logs: `docker-compose logs -f app`
- Accéder au shell du container: `docker-compose exec app /bin/bash`

## Licence

Ce projet est sous licence MIT.
