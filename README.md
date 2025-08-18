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

### 🔊 Simulation du Bruit Aérien (nouveau 🚀)
- **Méthodologie** : Doc 29 simplifiée  
- **Indicateurs** : Lden (day-evening-night), **Lnight**  
- **Génération d’isophones** (contours bruit)  
- **Export en **PNG / GeoJSON**  
- **Exemple** :  
  ![Carte isophones fictifs](outputs/noise/noise_map_example.png)

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

### 📁 Structure du Repository
```

├── 📁 dashboards/
│   └── 📁 streamlit/
│       ├── 🐍 app.py
│       ├── 🐍 dashboard_environmental.py
│       ├── 🐍 dashboard_executive.py
│       └── 🐍 dashboard_operational.py
├── 📁 data/
│   ├── 📁 processed/
│   │   └── 📄 etl_simple_report_20250815_132436.json
│   └── 📁 raw/
│       ├── 📄 aircraft_catalog_icao_2025.csv
│       ├── 📄 emission_factors_icao_2025.csv
│       ├── 📄 flights_data_2025_08_01_to_30days.csv
│       └── 📄 weather_data_sample_3days.csv
├── 📁 database/
│   ├── 📁 migrations/
│   │   ├── 📄 .gitkeep
│   │   ├── 🗄️ V001__create_initial_schema.sql
│   │   ├── 🗄️ V002__aircraft_emission_factors.sql
│   │   └── 🗄️ V003__create_staging_schema.sql
│   └── 📁 seed-data/
│       ├── 📄 .gitkeep
│       └── 🗄️ test_connection.sql
├── 📁 deployment/
│   ├── 📄 pgadmin_servers.json
│   └── ⚙️ redis.conf
├── 📁 docs/
├── 📁 logs/
│   ├── 📋 etl_pipeline.log 🚫 (auto-hidden)
│   ├── 📋 etl_simple.log 🚫 (auto-hidden)
│   └── 📋 migrations.log 🚫 (auto-hidden)
├── 📁 notebooks/
│   ├── 📁 .ipynb_checkpoints/
│   │   ├── 📓 03_noise_doc29_simplified-checkpoint.ipynb
│   │   ├── 📓 03_noise_minimal-checkpoint.ipynb
│   │   └── 📓 03_noise_simplified-checkpoint.ipynb
│   ├── 📁 otebooks/
│   ├── 📁 outputs/
│   │   ├── 📁 air/
│   │   └── 📁 noise/
│   │       ├── 📄 grid_points.geojson
│   │       ├── 📄 lden_contours.geojson
│   │       ├── 📄 lnight_contours.geojson
│   │       ├── 🌐 map_lden.html
│   │       ├── 🌐 map_lnight.html
│   │       ├── 🖼️ noise_map_example.png
│   │       └── 📄 statistics.csv
│   ├── 📓 03_noise_minimal.ipynb
│   └── 📓 03_noise_simplified.ipynb
├── 📁 screenshots/
├── 📁 scripts/
│   ├── 📁 logs/
│   │   └── 📋 migrations.log 🚫 (auto-hidden)
│   ├── 🐚 check_setup.sh
│   ├── 🐍 diagnose_database.py
│   ├── 🐍 etl_pipeline.py
│   ├── 🐍 generate_csv_data.py
│   ├── 🐍 generate_flights_simple.py
│   └── 🐍 run_migrations.py
├── 📁 src/
│   └── 🐍 __init__.py
├── 📁 tests/
│   ├── 🐍 __init__.py
│   └── 🐍 conftest.py
├── 📜 LICENSE
├── 📖 README.md
├── 🐍 db_config_working.py
├── ⚙️ docker-compose.yml
└── 📄 requirements.txt
```
---

## 🚀 **Démarrage Rapide**

### **Prérequis**
- Docker & Docker Compose
- Python 3.11+
- Git

### **Installation**


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

### 📖 **Références méthodologiques**

- ICAO Engine Emissions Databank – facteurs d’émission (cycle LTO)
- DEFRA / EPA – équations d’émissions complémentaires
- ECAC Doc 29 – méthodologie de calcul des isophones bruit
- ANP (Aircraft Noise & Performance) – paramètres acoustiques avion
- AEDT – implémentation industrielle Doc29 (référence US)

### 🚧 Travaux en cours

- Ajout d’un module de simulation bruit avancée avec données ANP
- Développement de la page Streamlit Impacts combinés Air & Bruit
- Intégration de tests automatiques (pytest) pour validation qualité des données