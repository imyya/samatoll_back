# 🌧️ Samatoll Backend - Système de Prédiction d'Humidité

API backend pour la prédiction d'humidité au Sénégal avec alertes automatiques par SMS. Ce service utilise un modèle de machine learning pour prédire l'humidité basé sur les données météorologiques et envoie des notifications automatiques lorsque le niveau d'humidité dépasse un seuil critique.

## 📋 Table des Matières

- [À propos](#-à-propos)
- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [API Documentation](#-api-documentation)
- [Déploiement](#-déploiement)
- [Structure du Projet](#-structure-du-projet)
- [Contribution](#-contribution)

## 🎯 À propos

Samatoll Backend est une API REST développée avec FastAPI qui fournit des prédictions d'humidité en temps réel pour différentes régions du Sénégal. Le système surveille automatiquement les conditions météorologiques et envoie des alertes par SMS lorsque l'humidité atteint des niveaux critiques pouvant causer des problèmes de moisissure ou de sécheresse.

### 🤖 Modèle de Machine Learning

**Le modèle de prédiction d'humidité utilisé dans ce projet a été développé par l'équipe Data Science et Data Engineer.** Le modèle utilise XGBoost et a été entraîné sur des données météorologiques historiques du Sénégal. Les fichiers du modèle sont stockés dans `app/ml/models/` et incluent :

- `best_humidity_model.pkl` : Modèle XGBoost optimisé
- `scaler.pkl` : Scaler pour la normalisation des données
- `encoders.pkl` : Encoders pour les variables catégorielles
- `feature_columns.pkl` : Liste des colonnes de features
- `model_metadata.pkl` : Métadonnées du modèle

## ✨ Fonctionnalités

- 🔮 **Prédiction d'humidité** : Prédiction de l'humidité basée sur les données météorologiques (région, département, température, vitesse du vent, conditions météo)
- 📱 **Alertes automatiques** : Envoi automatique de SMS via Twilio lorsque l'humidité dépasse 80%
- ⏰ **Surveillance continue** : Scheduler qui vérifie les conditions météorologiques toutes les 1 heure
- 📊 **Historique des notifications** : Stockage de toutes les notifications envoyées dans une base de données
- 🌍 **Intégration OpenWeatherMap** : Récupération automatique des données météorologiques en temps réel
- 🔍 **API REST complète** : Endpoints pour la prédiction, l'envoi de notifications et la consultation de l'historique

## 🛠️ Technologies

- **Framework** : FastAPI 0.121.0
- **Langage** : Python 3.12
- **Base de données** : PostgreSQL (via SQLAlchemy)
- **Machine Learning** : XGBoost, scikit-learn, pandas, numpy
- **Scheduling** : APScheduler
- **SMS** : Twilio
- **Météo** : OpenWeatherMap API
- **Déploiement** : Docker, Jenkins CI/CD

## 📦 Prérequis

- Python 3.12+
- PostgreSQL (ou SQLite pour le développement)
- Compte Twilio (pour l'envoi de SMS)
- Clé API OpenWeatherMap (pour les données météorologiques)
- Docker (optionnel, pour le déploiement)

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone <repository-url>
cd samatoll_back
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/samatoll_db
# Ou pour SQLite: DATABASE_URL=sqlite:///./samatoll.db

# Twilio (SMS)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=+1234567890

# OpenWeatherMap
OPENWEATHER_API_KEY=your_openweather_api_key

# Numéro de téléphone pour les alertes
ALERT_PHONE=+221771234567
```

### 5. Initialiser la base de données

La base de données est créée automatiquement au démarrage de l'application. Les tables sont créées via SQLAlchemy.

## ⚙️ Configuration

### Variables d'environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `DATABASE_URL` | URL de connexion à la base de données | Oui |
| `TWILIO_ACCOUNT_SID` | Identifiant de compte Twilio | Oui (pour SMS) |
| `TWILIO_AUTH_TOKEN` | Token d'authentification Twilio | Oui (pour SMS) |
| `TWILIO_FROM_NUMBER` | Numéro Twilio pour l'envoi | Oui (pour SMS) |
| `OPENWEATHER_API_KEY` | Clé API OpenWeatherMap | Oui |
| `ALERT_PHONE` | Numéro de téléphone pour les alertes | Oui |

### Configuration du Scheduler

Le scheduler est configuré dans `main.py` pour vérifier l'humidité toutes les 5 minutes. Pour modifier l'intervalle, éditez :

```python
scheduler.add_job(
    func=check_humidity_periodically,
    trigger="interval",
    minutes=5,  # Modifier ici
)
```

## 🎮 Utilisation

### Démarrer l'application

```bash
uvicorn main:app --reload
```

L'API sera accessible sur `http://localhost:8000`

### Documentation interactive

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

### Test de santé

```bash
curl http://localhost:8000/health
```

## 📚 API Documentation

### Endpoints principaux

#### 1. Health Check

```http
GET /health
```

**Réponse :**
```json
{
  "status": "ok working girl"
}
```

#### 2. Prédiction d'humidité

```http
POST /humidity/predict
Content-Type: application/json

{
  "region": "Dakar",
  "departement": "Dakar",
  "weather": "clear sky",
  "temperature": 28.5,
  "wind_speed": 5.2,
  "date": "2025-01-15 14:00:00"
}
```

**Réponse :**
```json
{
  "humidity": 75.3,
  "alert": "Attention : Humidité élevée",
  "level": "warning"
}
```

#### 3. Vérification manuelle pour Dakar

```http
POST /humidity/check-dakar-now
```

**Réponse :**
```json
{
  "status": "Check lancé – vérifie les logs"
}
```

#### 4. Envoyer un SMS

```http
POST /notifications/send_sms/
Content-Type: application/x-www-form-urlencoded

message=Hello World&to=+221771234567
```

**Réponse :**
```json
{
  "sid": "SM1234567890",
  "notification_id": 1,
  "status": "sent"
}
```

#### 5. Lister les notifications

```http
GET /notifications/?skip=0&limit=100&status=sent
```

**Réponse :**
```json
{
  "total": 10,
  "notifications": [
    {
      "id": 1,
      "message": "🚨 ALERTE HUMIDITÉ DAKAR: 75.3% !",
      "recipient": "+221771234567",
      "notification_type": "sms",
      "status": "sent",
      "twilio_sid": "SM1234567890",
      "created_at": "2025-01-15T14:00:00",
      "sent_at": "2025-01-15T14:00:01"
    }
  ]
}
```

#### 6. Obtenir une notification spécifique

```http
GET /notifications/{notification_id}
```

## 🐳 Déploiement

### Docker

#### Construire l'image

```bash
docker build -t samatoll_back:latest .
```

#### Lancer le conteneur

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/db \
  -e TWILIO_ACCOUNT_SID=your_sid \
  -e TWILIO_AUTH_TOKEN=your_token \
  -e TWILIO_FROM_NUMBER=+1234567890 \
  -e OPENWEATHER_API_KEY=your_key \
  -e ALERT_PHONE=+221771234567 \
  --name samatoll_back \
  samatoll_back:latest
```

### Docker Compose (exemple)

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/samatoll
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - TWILIO_FROM_NUMBER=${TWILIO_FROM_NUMBER}
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - ALERT_PHONE=${ALERT_PHONE}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=samatoll
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### CI/CD avec Jenkins

Le projet inclut un `Jenkinsfile` pour l'intégration continue. Le pipeline :

1. Checkout du code
2. Build de l'image Docker
3. Tests de smoke (vérification de santé)

## 📁 Structure du Projet

```
samatoll_back/
├── app/
│   ├── core/                 # Scheduler et tâches périodiques
│   │   └── scheduler.py
│   ├── db/                   # Configuration base de données
│   │   ├── database.py
│   │   └── migrations/       # Scripts de migration SQL
│   ├── ml/                   # Modèle de machine learning
│   │   ├── models/           # Modèles pré-entraînés
│   │   │   ├── best_humidity_model.pkl
│   │   │   ├── scaler.pkl
│   │   │   ├── encoders.pkl
│   │   │   └── ...
│   │   └── predictor.py      # Fonctions de prédiction
│   ├── models/               # Modèles SQLAlchemy
│   │   ├── notifications.py
│   │   └── user.py
│   ├── routers/              # Routes API
│   │   ├── humidity.py       # Routes prédiction humidité
│   │   └── notifications.py  # Routes notifications
│   └── schemas/              # Schémas Pydantic
├── main.py                   # Point d'entrée de l'application
├── requirements.txt          # Dépendances Python
├── Dockerfile                # Configuration Docker
├── Jenkinsfile               # Pipeline CI/CD
└── README.md                 # Ce fichier
```

## 🧪 Tests

### Test manuel de prédiction

```bash
curl -X POST "http://localhost:8000/humidity/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "Dakar",
    "departement": "Dakar",
    "weather": "clear sky",
    "temperature": 28.5,
    "wind_speed": 5.2,
    "date": "2025-01-15 14:00:00"
  }'
```

### Test de vérification Dakar

```bash
curl -X POST "http://localhost:8000/humidity/check-dakar-now"
```

## 🔧 Dépannage

### Problèmes courants

1. **Erreur de connexion à la base de données**
   - Vérifiez que PostgreSQL est en cours d'exécution
   - Vérifiez la variable `DATABASE_URL` dans le fichier `.env`

2. **Erreur Twilio**
   - Vérifiez que les credentials Twilio sont corrects
   - Vérifiez que le numéro `TWILIO_FROM_NUMBER` est valide

3. **Erreur OpenWeatherMap**
   - Vérifiez que la clé API est valide
   - Vérifiez votre quota d'appels API

4. **Le scheduler ne fonctionne pas**
   - Vérifiez les logs de l'application
   - Vérifiez que les variables d'environnement sont définies

## 📝 Notes importantes

- **Modèle ML** : Le modèle de prédiction a été développé par l'équipe Data Science et Data Engineer. Ne modifiez pas les fichiers du modèle sans consultation.
- **Scheduler** : Le scheduler vérifie l'humidité toutes les 1 heure . Ajustez selon vos besoins.
- **Base de données** : Les tables sont créées automatiquement au démarrage. Pour une migration manuelle, utilisez les scripts SQL dans `app/db/migrations/`.

## 🤝 Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request


## 👥 Équipe

- **Backend Development** : moi
- **Data Science & Data Engineer** : Modèle de prédiction d'humidité
- **DevOps** : Configuration Docker et CI/CD

## 📧 Contact

Pour toute question ou suggestion, contactez mamya.samane@gmail.com ou ouvrez une issue sur le dépôt.

---

**Développé avec ❤️ pour le Sénégal**

