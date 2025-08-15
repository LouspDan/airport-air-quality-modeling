#!/usr/bin/env python3
"""
Pipeline ETL Simplifié - Sans suppression de tables
Version robuste qui évite les conflits de contraintes
"""

import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine, text
import logging
from datetime import datetime, timedelta
import random
import time

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('etl_simple')

# Configuration base de données (port corrigé)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'airport_air_quality',
    'user': 'airport_user',
    'password': 'airport_password'
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

class SimpleETLPipeline:
    """Pipeline ETL simplifié sans suppressions problématiques"""
    
    def __init__(self):
        self.engine = None
        
        # Données de référence ICAO
        self.aircraft_types = {
            'A320': {'manufacturer': 'Airbus', 'engines': 2, 'mtow_kg': 78000, 'fuel_flow_kgh': 2400},
            'A321': {'manufacturer': 'Airbus', 'engines': 2, 'mtow_kg': 93500, 'fuel_flow_kgh': 2600},
            'A330': {'manufacturer': 'Airbus', 'engines': 2, 'mtow_kg': 242000, 'fuel_flow_kgh': 5800},
            'B737': {'manufacturer': 'Boeing', 'engines': 2, 'mtow_kg': 79000, 'fuel_flow_kgh': 2500},
            'B777': {'manufacturer': 'Boeing', 'engines': 2, 'mtow_kg': 351000, 'fuel_flow_kgh': 7200},
            'B787': {'manufacturer': 'Boeing', 'engines': 2, 'mtow_kg': 254000, 'fuel_flow_kgh': 5400}
        }
        
        # Facteurs d'émission ICAO
        self.emission_factors = {
            'CO2': 3.157, 'NOx': 0.013, 'PM10': 0.0002, 'PM25': 0.0001, 'SOx': 0.0008
        }
        
        # Phases de vol
        self.flight_phases = {
            'taxi_out': {'duration_min': 15, 'power_setting': 0.07},
            'takeoff': {'duration_min': 0.7, 'power_setting': 1.00},
            'climb': {'duration_min': 8, 'power_setting': 0.85},
            'cruise': {'duration_min': 120, 'power_setting': 0.75},
            'descent': {'duration_min': 6, 'power_setting': 0.40},
            'approach': {'duration_min': 4, 'power_setting': 0.30},
            'taxi_in': {'duration_min': 10, 'power_setting': 0.07}
        }
    
    def connect_database(self):
        """Connexion base de données"""
        try:
            self.engine = create_engine(DATABASE_URL)
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 'ETL Simple Connected' as status"))
                logger.info(f"✅ {result.fetchone()[0]}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False
    
    def create_tables_if_not_exists(self):
        """Créer les tables seulement si elles n'existent pas"""
        logger.info("🗄️ CRÉATION - Tables ETL (si nécessaire)")
        
        # Vérifier d'abord si les tables existent
        check_sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'etl' 
        AND table_name IN ('flights_staging', 'emissions_staging', 'weather_staging', 'pipeline_runs')
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(check_sql))
                existing_tables = [row[0] for row in result.fetchall()]
                
                if len(existing_tables) == 4:
                    logger.info("✅ Tables ETL existent déjà - pas de création nécessaire")
                    return True
                
                # Créer les tables manquantes
                schema_sql = """
                CREATE SCHEMA IF NOT EXISTS etl;
                
                CREATE TABLE IF NOT EXISTS etl.flights_staging (
                    flight_id VARCHAR(50) PRIMARY KEY,
                    aircraft_type VARCHAR(10) NOT NULL,
                    departure_airport VARCHAR(4) NOT NULL,
                    arrival_airport VARCHAR(4) NOT NULL,
                    departure_time TIMESTAMP NOT NULL,
                    arrival_time TIMESTAMP NOT NULL,
                    flight_duration_minutes INTEGER,
                    passengers INTEGER,
                    cargo_kg DECIMAL(8,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS etl.emissions_staging (
                    emission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    flight_id VARCHAR(50) NOT NULL,
                    flight_phase VARCHAR(20) NOT NULL,
                    pollutant_type VARCHAR(10) NOT NULL,
                    fuel_consumed_kg DECIMAL(10,4),
                    emission_quantity_kg DECIMAL(12,6),
                    calculation_method VARCHAR(20) DEFAULT 'ICAO',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS etl.weather_staging (
                    weather_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    airport_code VARCHAR(4) NOT NULL,
                    observation_time TIMESTAMP NOT NULL,
                    temperature_c DECIMAL(5,2),
                    humidity_percent INTEGER,
                    wind_speed_ms DECIMAL(5,2),
                    wind_direction_deg INTEGER,
                    pressure_hpa DECIMAL(7,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS etl.pipeline_runs (
                    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    pipeline_step VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    records_processed INTEGER DEFAULT 0,
                    execution_time_seconds DECIMAL(8,3),
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                
                conn.execute(text(schema_sql))
                conn.commit()
                
                logger.info("✅ Tables ETL créées")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur création tables: {e}")
            return False
    
    def clear_staging_data(self):
        """Vider les données de staging pour nouvelle exécution"""
        logger.info("🧹 NETTOYAGE - Données staging")
        
        try:
            with self.engine.connect() as conn:
                # Vider dans l'ordre inverse des dépendances
                conn.execute(text("TRUNCATE TABLE etl.emissions_staging"))
                conn.execute(text("TRUNCATE TABLE etl.flights_staging"))
                conn.execute(text("TRUNCATE TABLE etl.weather_staging"))
                conn.commit()
                
                logger.info("✅ Données staging nettoyées")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage: {e}")
            return False
    
    def generate_flights(self, num_flights=1000):
        """Générer données de vol"""
        logger.info(f"✈️ GÉNÉRATION - {num_flights} vols")
        
        airports = ['CDG', 'ORY', 'LHR', 'AMS', 'FRA', 'BCN', 'FCO', 'MAD', 'ZUR', 'VIE']
        airlines = ['AF', 'BA', 'LH', 'KL', 'IB', 'AZ', 'LX', 'OS']
        
        flights_data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(num_flights):
            aircraft_type = random.choice(list(self.aircraft_types.keys()))
            departure_airport = 'CDG'
            arrival_airport = random.choice([apt for apt in airports if apt != departure_airport])
            
            departure_time = base_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(6, 22),
                minutes=random.randint(0, 59)
            )
            
            flight_duration = random.randint(60, 240)
            arrival_time = departure_time + timedelta(minutes=flight_duration)
            
            if aircraft_type in ['A320', 'B737']:
                passengers = random.randint(120, 180)
            elif aircraft_type in ['A321']:
                passengers = random.randint(150, 220)
            else:
                passengers = random.randint(200, 400)
            
            flights_data.append({
                'flight_id': f"{random.choice(airlines)}{random.randint(1000, 9999)}_{departure_time.strftime('%Y%m%d')}",
                'aircraft_type': aircraft_type,
                'departure_airport': departure_airport,
                'arrival_airport': arrival_airport,
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'flight_duration_minutes': flight_duration,
                'passengers': passengers,
                'cargo_kg': random.randint(5000, 15000)
            })
        
        try:
            df_flights = pd.DataFrame(flights_data)
            df_flights.to_sql('flights_staging', self.engine, schema='etl', 
                            if_exists='append', index=False, method='multi', chunksize=100)
            
            logger.info(f"✅ {len(flights_data)} vols insérés")
            return df_flights
            
        except Exception as e:
            logger.error(f"❌ Erreur insertion vols: {e}")
            return None
    
    def calculate_emissions(self, flights_df):
        """Calculer émissions"""
        logger.info("🧮 CALCUL - Émissions ICAO")
        
        emissions_data = []
        
        for _, flight in flights_df.iterrows():
            aircraft_type = flight['aircraft_type']
            flight_id = flight['flight_id']
            flight_duration = flight['flight_duration_minutes']
            
            if aircraft_type not in self.aircraft_types:
                continue
            
            aircraft_info = self.aircraft_types[aircraft_type]
            base_fuel_flow = aircraft_info['fuel_flow_kgh']
            
            for phase, phase_info in self.flight_phases.items():
                if phase == 'cruise':
                    other_phases_duration = sum([p['duration_min'] for p in self.flight_phases.values() if p != phase_info])
                    phase_duration = max(flight_duration - other_phases_duration, 10)
                else:
                    phase_duration = phase_info['duration_min']
                
                power_setting = phase_info['power_setting']
                fuel_consumed_kg = (base_fuel_flow * power_setting * phase_duration) / 60
                
                for pollutant, emission_factor in self.emission_factors.items():
                    emission_quantity = fuel_consumed_kg * emission_factor
                    
                    emissions_data.append({
                        'flight_id': flight_id,
                        'flight_phase': phase,
                        'pollutant_type': pollutant,
                        'fuel_consumed_kg': fuel_consumed_kg,
                        'emission_quantity_kg': emission_quantity,
                        'calculation_method': 'ICAO'
                    })
        
        try:
            df_emissions = pd.DataFrame(emissions_data)
            df_emissions.to_sql('emissions_staging', self.engine, schema='etl', 
                              if_exists='append', index=False, method='multi', chunksize=500)
            
            logger.info(f"✅ {len(emissions_data)} calculs d'émissions effectués")
            return df_emissions
            
        except Exception as e:
            logger.error(f"❌ Erreur insertion émissions: {e}")
            return None
    
    def generate_weather(self, num_observations=720):
        """Générer données météo"""
        logger.info(f"🌤️ GÉNÉRATION - {num_observations} observations météo")
        
        airports = ['CDG', 'ORY']
        weather_data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(num_observations):
            for airport in airports:
                observation_time = base_date + timedelta(hours=i)
                
                weather_data.append({
                    'airport_code': airport,
                    'observation_time': observation_time,
                    'temperature_c': random.uniform(5, 25),
                    'humidity_percent': random.randint(40, 90),
                    'wind_speed_ms': random.uniform(2, 15),
                    'wind_direction_deg': random.randint(0, 359),
                    'pressure_hpa': random.uniform(995, 1025)
                })
        
        try:
            df_weather = pd.DataFrame(weather_data)
            df_weather.to_sql('weather_staging', self.engine, schema='etl', 
                            if_exists='append', index=False, method='multi', chunksize=200)
            
            logger.info(f"✅ {len(weather_data)} observations météo générées")
            return df_weather
            
        except Exception as e:
            logger.error(f"❌ Erreur insertion météo: {e}")
            return None
    
    def validate_results(self):
        """Validation finale"""
        logger.info("✅ VALIDATION - Résultats")
        
        try:
            with self.engine.connect() as conn:
                # Compter les données
                result = conn.execute(text("SELECT COUNT(*) FROM etl.flights_staging"))
                flights_count = result.fetchone()[0]
                
                result = conn.execute(text("SELECT COUNT(*) FROM etl.emissions_staging"))
                emissions_count = result.fetchone()[0]
                
                result = conn.execute(text("SELECT COUNT(*) FROM etl.weather_staging"))
                weather_count = result.fetchone()[0]
                
                result = conn.execute(text("SELECT SUM(emission_quantity_kg) FROM etl.emissions_staging WHERE pollutant_type = 'CO2'"))
                total_co2 = result.fetchone()[0] or 0
                
                return {
                    'flights': flights_count,
                    'emissions': emissions_count,
                    'weather': weather_count,
                    'total_co2_kg': float(total_co2)
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur validation: {e}")
            return None
    
    def run_pipeline(self):
        """Exécuter le pipeline complet"""
        
        print("""
🚀 PIPELINE ETL SIMPLIFIÉ - AIRPORT AIR QUALITY
==============================================

Pipeline robuste évitant les conflits de contraintes
        """)
        
        start_time = time.time()
        
        try:
            # 1. Connexion
            if not self.connect_database():
                return False
            
            # 2. Création tables
            if not self.create_tables_if_not_exists():
                return False
            
            # 3. Nettoyage données
            if not self.clear_staging_data():
                return False
            
            # 4. Génération vols
            flights_df = self.generate_flights(1000)
            if flights_df is None:
                return False
            
            # 5. Calcul émissions
            emissions_df = self.calculate_emissions(flights_df)
            if emissions_df is None:
                return False
            
            # 6. Génération météo
            weather_df = self.generate_weather(720)
            if weather_df is None:
                return False
            
            # 7. Validation
            results = self.validate_results()
            if results is None:
                return False
            
            # 8. Rapport final
            duration = time.time() - start_time
            
            print(f"""
🎉 PIPELINE ETL TERMINÉ AVEC SUCCÈS!
===================================

⏱️ Durée: {duration:.1f} secondes

📊 DONNÉES GÉNÉRÉES:
------------------
✈️ Vols: {results['flights']:,}
🏭 Émissions: {results['emissions']:,} calculs
🌤️ Météo: {results['weather']:,} observations
💨 CO2 total: {results['total_co2_kg']:,.2f} kg

🗄️ TABLES ETL REMPLIES:
----------------------
✅ etl.flights_staging
✅ etl.emissions_staging  
✅ etl.weather_staging

🎯 PROJET 100% OPÉRATIONNEL!
===========================

Votre base de données contient maintenant:
- Calculs d'émissions conformes ICAO
- Données réalistes d'aéroport
- Pipeline ETL documenté et fonctionnel

🏆 PRÊT POUR L'ENTRETIEN ADP!
            """)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur pipeline: {e}")
            return False

def main():
    print("🚀 Démarrage pipeline ETL simplifié...")
    
    pipeline = SimpleETLPipeline()
    success = pipeline.run_pipeline()
    
    if success:
        print("\n🎉 PIPELINE RÉUSSI - Projet prêt pour démonstration!")
        return True
    else:
        print("\n❌ PIPELINE ÉCHOUÉ - Consultez les logs")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)