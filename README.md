# 🌍 Airport Air Quality Modeling System

> **Système de modélisation et surveillance de la qualité de l'air aéroportuaire**  
> *Projet portfolio - Démonstration techniques Data Engineering & Analytics*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-green.svg)](https://postgresql.org)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.3+-orange.svg)](https://postgis.net)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 **Objectif du Projet**

Développement d'un système complet de **modélisation des émissions** et **surveillance de la qualité de l'air** pour un aéroport fictif. Ce projet démontre des compétences en :

- **Modélisation de données environnementales**
- **Calculs d'émissions selon méthodologies ICAO/DEFRA** 
- **Analyse géospatiale avec PostGIS**
- **Visualisation de données avec Power BI**
- **Architecture microservices avec Docker**

## 🏗️ **Architecture du Système**

### **Composants Principaux**

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Base de Données** | PostgreSQL + PostGIS | Stockage données géospatiales et temporelles |
| **Calculs Émissions** | Python + SQLAlchemy | Algorithmes ICAO pour émissions CO2, NOx, PM |
| **API REST** | FastAPI + Pydantic | Interface d'interrogation des données |
| **Visualisation** | Power BI + Streamlit | Dashboards et cartographies interactives |
| **Cache** | Redis | Optimisation des performances |

## 🌟 **Fonctionnalités Clés**

### ✈️ **Modélisation du Trafic Aérien**
- Suivi détaillé des vols (phases taxi, décollage, croisière, atterrissage)
- Base de données des aéronefs avec facteurs d'émission certifiés
- Calculs de consommation carburant par phase de vol

### 🧪 **Calculs d'Émissions Atmosphériques**
- **Méthodologies standards** : ICAO, DEFRA, EPA
- **Polluants calculés** : CO2, NOx, PM10, PM2.5, SOx
- **Facteurs d'émission** actualisés par type d'aéronef
- **Validation** avec données de stations de mesure

### 🗺️ **Analyse Géospatiale**
- **Cartographie des émissions** par zone aéroportuaire
- **Modélisation de dispersion** atmosphérique simple
- **Zones d'influence** et rayons d'impact
- **Superposition** avec données météorologiques

### 📊 **Surveillance Qualité de l'Air**
- **Stations de mesure** fixes et mobiles
- **Monitoring temps réel** des concentrations
- **Alertes automatiques** en cas de dépassement de seuils
- **Corrélations** trafic aérien / qualité de l'air

## 🚀 **Démarrage Rapide**

### **Prérequis**
- Docker & Docker Compose
- Python 3.11+
- Git

### **Installation**

```bash
# 1. Clonage du repository
git clone https://github.com/LouspDan/airport-air-quality-modeling.git
cd airport-air-quality-modeling

# 2. Configuration environnement
cp .env.example .env
# Éditer .env si nécessaire

# 3. Démarrage des services
docker-compose up -d postgres pgadmin
docker-compose logs -f postgres

# 4. Installation dépendances Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 5. Initialisation base de données
python scripts/setup_database.py --init
python scripts/generate_sample_data.py