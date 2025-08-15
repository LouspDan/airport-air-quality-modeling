# Configuration PostgreSQL corrigée
# Port fonctionnel détecté: 5433

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'airport_air_quality',
    'user': 'airport_user',
    'password': 'airport_password'
}

DATABASE_URL = "postgresql://airport_user:airport_password@localhost:5433/airport_air_quality"
