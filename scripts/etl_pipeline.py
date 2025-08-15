#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline ETL simplifié sans pandas - Fonctionne avec Python standard
Projet: Airport Air Quality Modeling
Auteur: Portfolio Project
Date: 2025-08-15
"""

import os
import sys
import csv
import json
import logging
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl_simple.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Chargement manual de .env (sans python-dotenv)
def load_env_manual():
    """Chargement manuel du fichier .env"""
    config = {}
    env_file = Path('.env')
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    # Valeurs par défaut
    return {
        'DB_HOST': config.get('DB_HOST', 'localhost'),
        'DB_PORT': config.get('DB_PORT', '5433'),
        'DB_NAME': config.get('DB_NAME', 'airport_air_quality'),
        'DB_USER': config.get('DB_USER', 'airport_user'),
        'DB_PASSWORD': config.get('DB_PASSWORD', 'airport_password')
    }

class SimpleETLPipeline:
    """Pipeline ETL simplifié avec CSV standard"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.connection = None
        
        # Créer dossiers nécessaires
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)
        
        # Statistiques
        self.stats = {
            'files_processed': 0,
            'total_rows_read': 0,
            'total_rows_inserted': 0,
            'errors': []
        }
    
    def connect_database(self) -> bool:
        """Connexion à la base de données"""
        try:
            self.connection = psycopg2.connect(
                host=self.config['DB_HOST'],
                port=self.config['DB_PORT'],
                user=self.config['DB_USER'],
                password=self.config['DB_PASSWORD'],
                database=self.config['DB_NAME']
            )
            self.connection.autocommit = False
            logger.info("[OK] Connexion base de données établie")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Connexion échouée: {e}")
            return False
    
    def read_csv_file(self, file_path: str) -> Tuple[List[Dict], str]:
        """Lecture d'un fichier CSV avec détection du type"""
        try:
            logger.info(f"[EXTRACT] Lecture fichier: {file_path}")
            
            data = []
            with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
                # Détection automatique du dialecte
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                
                reader = csv.DictReader(csvfile, dialect=dialect)
                
                for row in reader:
                    # Nettoyer les données
                    cleaned_row = {}
                    for key, value in row.items():
                        if key and value:
                            cleaned_row[key.strip()] = str(value).strip()
                    
                    if cleaned_row:  # Ignorer les lignes vides
                        data.append(cleaned_row)
            
            # Détection du type de fichier
            filename = os.path.basename(file_path).lower()
            if 'flights_data' in filename:
                table_type = 'flights'
            elif 'aircraft_catalog' in filename:
                table_type = 'aircraft'
            elif 'emission_factors' in filename:
                table_type = 'emissions'
            elif 'weather' in filename:
                table_type = 'weather'
            else:
                table_type = 'unknown'
            
            logger.info(f"[EXTRACT] {len(data)} lignes lues, type: {table_type}")
            return data, table_type
            
        except Exception as e:
            logger.error(f"[ERROR] Lecture fichier échouée: {e}")
            return [], "error"
    
    def validate_flight_data(self, data: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Validation des données de vol"""
        valid_data = []
        errors = []
        
        for i, row in enumerate(data):
            is_valid = True
            row_errors = []
            
            # Vérifications de base
            if not row.get('flight_number'):
                row_errors.append(f"Ligne {i+2}: Numéro de vol manquant")
                is_valid = False
            
            if not row.get('aircraft_type'):
                row_errors.append(f"Ligne {i+2}: Type d'aéronef manquant")
                is_valid = False
            
            # Validation des passagers
            try:
                passengers = int(row.get('passengers', 0))
                if passengers < 0 or passengers > 500:
                    row_errors.append(f"Ligne {i+2}: Nombre de passagers invalide ({passengers})")
                    is_valid = False
            except ValueError:
                row_errors.append(f"Ligne {i+2}: Nombre de passagers non numérique")
                is_valid = False
            
            # Validation du carburant
            try:
                fuel = float(row.get('fuel_kg', 0))
                if fuel < 0 or fuel > 200000:
                    row_errors.append(f"Ligne {i+2}: Quantité carburant invalide ({fuel})")
                    is_valid = False
            except ValueError:
                row_errors.append(f"Ligne {i+2}: Quantité carburant non numérique")
                is_valid = False
            
            if is_valid:
                valid_data.append(row)
            else:
                errors.extend(row_errors)
        
        if errors:
            logger.warning(f"[VALIDATE] {len(errors)} erreur(s) de validation détectée(s)")
        
        return valid_data, errors
    
    def transform_flight_data(self, data: List[Dict]) -> List[Tuple]:
        """Transformation des données de vol pour insertion"""
        logger.info("[TRANSFORM] Transformation données de vol")
        
        transformed = []
        for row in data:
            try:
                # Conversion et nettoyage
                numero_vol = row.get('flight_number', '').upper()
                date_vol = row.get('flight_date', '2025-08-01')
                heure_depart = row.get('scheduled_departure', '12:00')
                heure_arrivee = row.get('scheduled_arrival', '14:00')
                
                # Conversion des types numériques
                try:
                    distance_km = int(row.get('distance_km', 0))
                except ValueError:
                    distance_km = 0
                
                try:
                    nb_passagers = int(row.get('passengers', 0))
                except ValueError:
                    nb_passagers = 0
                
                try:
                    fuel_kg = float(row.get('fuel_kg', 0))
                except ValueError:
                    fuel_kg = 0.0
                
                # Codes aéroport et compagnie
                airline_iata = row.get('airline_iata', 'XX')
                aircraft_type = row.get('aircraft_type', 'A320')
                destination = row.get('destination_airport', 'XXX')
                flight_type = row.get('flight_type', 'european')
                
                # Tuple pour insertion
                transformed_row = (
                    numero_vol, date_vol, heure_depart, heure_arrivee,
                    distance_km, nb_passagers, fuel_kg, airline_iata,
                    aircraft_type, destination, flight_type, 'CSV_IMPORT'
                )
                
                transformed.append(transformed_row)
                
            except Exception as e:
                logger.warning(f"[TRANSFORM] Erreur transformation ligne: {e}")
                continue
        
        logger.info(f"[TRANSFORM] {len(transformed)} lignes transformées")
        return transformed
    
    def load_flights_to_db(self, data: List[Tuple]) -> int:
        """Chargement des données de vol en base"""
        if not data:
            logger.warning("[LOAD] Aucune donnée à charger")
            return 0
        
        try:
            with self.connection.cursor() as cursor:
                # Création table temporaire si nécessaire
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS temp_flights_etl (
                        numero_vol VARCHAR(10),
                        date_vol DATE,
                        heure_depart TIME,
                        heure_arrivee TIME,
                        distance_km INTEGER,
                        nb_passagers INTEGER,
                        fuel_kg NUMERIC,
                        airline_iata VARCHAR(3),
                        aircraft_type VARCHAR(10),
                        destination VARCHAR(3),
                        flight_type VARCHAR(20),
                        data_source VARCHAR(50),
                        imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insertion en lot
                insert_query = """
                    INSERT INTO temp_flights_etl 
                    (numero_vol, date_vol, heure_depart, heure_arrivee, distance_km, 
                     nb_passagers, fuel_kg, airline_iata, aircraft_type, destination, 
                     flight_type, data_source) 
                    VALUES %s
                """
                
                execute_values(cursor, insert_query, data, template=None, page_size=1000)
                self.connection.commit()
                
                logger.info(f"[LOAD] {len(data)} vols insérés dans temp_flights_etl")
                return len(data)
                
        except Exception as e:
            logger.error(f"[ERROR] Chargement échoué: {e}")
            self.connection.rollback()
            return 0
    
    def process_other_files(self, data: List[Dict], table_type: str) -> int:
        """Traitement simplifié des autres types de fichiers"""
        if not data:
            return 0
        
        try:
            with self.connection.cursor() as cursor:
                if table_type == 'aircraft':
                    # Table catalogue aéronefs
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS temp_aircraft_etl (
                            icao_code VARCHAR(10),
                            manufacturer VARCHAR(50),
                            model VARCHAR(50),
                            seating INTEGER,
                            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    values = []
                    for row in data:
                        values.append((
                            row.get('icao_designation', ''),
                            row.get('manufacturer', ''),
                            row.get('model', ''),
                            int(row.get('max_seating', 0)) if row.get('max_seating', '').isdigit() else 0
                        ))
                    
                    execute_values(cursor, 
                        "INSERT INTO temp_aircraft_etl (icao_code, manufacturer, model, seating) VALUES %s",
                        values, page_size=100)
                
                elif table_type == 'emissions':
                    # Table facteurs d'émission
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS temp_emissions_etl (
                            engine_designation VARCHAR(50),
                            manufacturer VARCHAR(50),
                            nox_takeoff NUMERIC,
                            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    values = []
                    for row in data:
                        try:
                            nox = float(row.get('nox_takeoff_gkg', 0))
                        except ValueError:
                            nox = 0.0
                        
                        values.append((
                            row.get('engine_designation', ''),
                            row.get('manufacturer', ''),
                            nox
                        ))
                    
                    execute_values(cursor,
                        "INSERT INTO temp_emissions_etl (engine_designation, manufacturer, nox_takeoff) VALUES %s",
                        values, page_size=100)
                
                elif table_type == 'weather':
                    # Table données météo
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS temp_weather_etl (
                            station_id VARCHAR(20),
                            measurement_time TIMESTAMP,
                            temperature NUMERIC,
                            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    values = []
                    for row in data:
                        try:
                            temp = float(row.get('temperature_c', 0))
                        except ValueError:
                            temp = 0.0
                        
                        measurement_time = row.get('measurement_time', '2025-08-01 12:00:00')
                        
                        values.append((
                            row.get('station_id', ''),
                            measurement_time,
                            temp
                        ))
                    
                    execute_values(cursor,
                        "INSERT INTO temp_weather_etl (station_id, measurement_time, temperature) VALUES %s",
                        values, page_size=100)
                
                self.connection.commit()
                logger.info(f"[LOAD] {len(data)} lignes insérées pour {table_type}")
                return len(data)
                
        except Exception as e:
            logger.error(f"[ERROR] Chargement {table_type} échoué: {e}")
            self.connection.rollback()
            return 0
    
    def process_file(self, file_path: str):
        """Traitement complet d'un fichier"""
        logger.info(f"[PIPELINE] === Traitement {os.path.basename(file_path)} ===")
        
        # Extract
        data, table_type = self.read_csv_file(file_path)
        if not data:
            logger.warning(f"[PIPELINE] Aucune donnée extraite de {file_path}")
            return
        
        self.stats['total_rows_read'] += len(data)
        
        # Transform & Load
        if table_type == 'flights':
            # Validation spécifique pour les vols
            valid_data, errors = self.validate_flight_data(data)
            self.stats['errors'].extend(errors)
            
            # Transformation
            transformed_data = self.transform_flight_data(valid_data)
            
            # Chargement
            inserted = self.load_flights_to_db(transformed_data)
            self.stats['total_rows_inserted'] += inserted
            
        else:
            # Traitement simplifié pour les autres types
            inserted = self.process_other_files(data, table_type)
            self.stats['total_rows_inserted'] += inserted
        
        self.stats['files_processed'] += 1
        logger.info(f"[PIPELINE] {os.path.basename(file_path)}: {len(data)} lues, {inserted} insérées")
    
    def run_pipeline(self, source_dir: str = "data/raw"):
        """Exécution complète du pipeline"""
        logger.info(f"[PIPELINE] Démarrage ETL depuis {source_dir}")
        
        if not self.connect_database():
            return False
        
        # Recherche des fichiers CSV
        source_path = Path(source_dir)
        csv_files = list(source_path.glob("*.csv"))
        
        if not csv_files:
            logger.warning(f"Aucun fichier CSV trouvé dans {source_dir}")
            return False
        
        logger.info(f"[PIPELINE] {len(csv_files)} fichier(s) à traiter")
        
        # Traitement de chaque fichier
        for csv_file in sorted(csv_files):
            try:
                self.process_file(str(csv_file))
            except Exception as e:
                logger.error(f"[ERROR] Échec traitement {csv_file.name}: {e}")
                self.stats['errors'].append(f"Erreur {csv_file.name}: {str(e)}")
        
        # Génération du rapport final
        self.generate_report()
        
        # Fermeture connexion
        if self.connection:
            self.connection.close()
            logger.info("[PIPELINE] Connexion fermée")
        
        return True
    
    def generate_report(self):
        """Génération du rapport final"""
        report = {
            "execution_timestamp": datetime.now().isoformat(),
            "summary": self.stats,
            "success_rate": round((self.stats['total_rows_inserted'] / max(self.stats['total_rows_read'], 1)) * 100, 1)
        }
        
        # Sauvegarde JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"data/processed/etl_simple_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Affichage du résumé
        print("\n" + "="*60)
        print("📊 RAPPORT ETL SIMPLIFIÉ")
        print("="*60)
        print(f"📁 Fichiers traités: {self.stats['files_processed']}")
        print(f"📈 Lignes lues: {self.stats['total_rows_read']:,}")
        print(f"💾 Lignes insérées: {self.stats['total_rows_inserted']:,}")
        print(f"✅ Taux de succès: {report['success_rate']:.1f}%")
        
        if self.stats['errors']:
            print(f"⚠️ Erreurs détectées: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Afficher les 5 premières
                print(f"  - {error}")
        
        print(f"📋 Rapport sauvegardé: {report_file}")
        print("="*60)


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Pipeline ETL simplifié')
    parser.add_argument('--source-dir', type=str, default='data/raw',
                       help='Dossier source des fichiers CSV')
    
    args = parser.parse_args()
    
    print("🚀 PIPELINE ETL SIMPLIFIÉ")
    print("="*40)
    print(f"📁 Source: {args.source_dir}")
    
    # Chargement de la configuration
    config = load_env_manual()
    
    # Initialisation du pipeline
    pipeline = SimpleETLPipeline(config)
    
    try:
        success = pipeline.run_pipeline(args.source_dir)
        
        if success:
            print("\n✅ Pipeline ETL terminé avec succès")
        else:
            print("\n❌ Échec du pipeline ETL")
            return 1
    
    except Exception as e:
        logger.error(f"Erreur pipeline: {e}")
        print(f"\n❌ ERREUR: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())