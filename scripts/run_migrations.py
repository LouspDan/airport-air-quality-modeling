#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de gestion des migrations PostgreSQL - Version Windows Compatible
Projet: Airport Air Quality Modeling
Auteur: Portfolio Project
Date: 2025-08-15
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List
import argparse
import hashlib
import time

# Configuration spéciale pour Windows
if sys.platform == "win32":
    os.system("chcp 65001")  # UTF-8
    
# Configuration du logging SANS emojis pour Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migrations.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MigrationManager:
    """Gestionnaire des migrations PostgreSQL - Version Windows Compatible"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.connection = None
        self.cursor = None
        
        # Chemins des fichiers
        self.project_root = Path(__file__).parent.parent
        self.migrations_dir = self.project_root / "database" / "migrations"
        
        # Créer le dossier logs s'il n'existe pas
        os.makedirs("logs", exist_ok=True)
        
        # Messages sans emojis pour Windows
        self.MSG = {
            'success': '[OK]',
            'error': '[ERROR]',
            'warning': '[WARN]',
            'info': '[INFO]',
            'running': '[RUNNING]'
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
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            
            logger.info(f"{self.MSG['success']} Connexion PostgreSQL etablie")
            return True
            
        except Exception as e:
            logger.error(f"{self.MSG['error']} Erreur connexion PostgreSQL: {e}")
            return False
    
    def create_migration_table(self) -> bool:
        """Création de la table de suivi des migrations"""
        try:
            migration_table_sql = """
            CREATE SCHEMA IF NOT EXISTS _migrations;
            
            CREATE TABLE IF NOT EXISTS _migrations.schema_version (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) NOT NULL UNIQUE,
                description TEXT,
                sql_file VARCHAR(255),
                checksum VARCHAR(64),
                execution_time_ms INTEGER,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                applied_by VARCHAR(100),
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_schema_version_version 
            ON _migrations.schema_version(version);
            
            CREATE INDEX IF NOT EXISTS idx_schema_version_applied_at 
            ON _migrations.schema_version(applied_at);
            """
            
            self.cursor.execute(migration_table_sql)
            logger.info(f"{self.MSG['success']} Table de migration creee/verifiee")
            return True
            
        except Exception as e:
            logger.error(f"{self.MSG['error']} Erreur creation table migration: {e}")
            return False
    
    def get_applied_migrations(self) -> List[str]:
        """Récupération de la liste des migrations déjà appliquées"""
        try:
            self.cursor.execute(
                "SELECT version FROM _migrations.schema_version WHERE success = TRUE ORDER BY version"
            )
            return [row[0] for row in self.cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"{self.MSG['error']} Erreur lecture migrations: {e}")
            return []
    
    def get_pending_migrations(self) -> List[Path]:
        """Identification des migrations en attente"""
        try:
            applied_migrations = self.get_applied_migrations()
            
            # Vérification de l'existence du dossier migrations
            if not self.migrations_dir.exists():
                logger.error(f"{self.MSG['error']} Dossier migrations introuvable: {self.migrations_dir}")
                return []
            
            migration_files = sorted(self.migrations_dir.glob("V*.sql"))
            
            if not migration_files:
                logger.warning(f"{self.MSG['warning']} Aucun fichier de migration trouve dans {self.migrations_dir}")
                return []
            
            pending = []
            for file_path in migration_files:
                # Extraction du numéro de version (ex: V001 depuis V001__create_initial_schema.sql)
                version = file_path.name.split('__')[0]
                
                if version not in applied_migrations:
                    pending.append(file_path)
                    logger.info(f"{self.MSG['info']} Migration en attente: {file_path.name}")
            
            return pending
            
        except Exception as e:
            logger.error(f"{self.MSG['error']} Erreur identification migrations: {e}")
            return []
    
    def calculate_checksum(self, content: str) -> str:
        """Calcul du checksum SHA256 du contenu SQL"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def execute_migration(self, migration_file: Path) -> bool:
        """Exécution d'une migration spécifique"""
        try:
            # Lecture du fichier SQL
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Calcul du checksum pour l'intégrité
            checksum = self.calculate_checksum(sql_content)
            
            # Extraction des métadonnées
            version = migration_file.name.split('__')[0]
            description = migration_file.name.split('__')[1].replace('.sql', '').replace('_', ' ')
            
            logger.info(f"{self.MSG['running']} Execution migration {version}: {description}")
            
            # Mesure du temps d'exécution
            start_time = time.time()
            
            try:
                # Exécution du SQL
                self.cursor.execute(sql_content)
                
                execution_time = int((time.time() - start_time) * 1000)
                
                # Enregistrement du succès
                self.cursor.execute("""
                    INSERT INTO _migrations.schema_version 
                    (version, description, sql_file, checksum, execution_time_ms, success, applied_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    version, description, migration_file.name, 
                    checksum, execution_time, True, os.getenv('USER', os.getenv('USERNAME', 'unknown'))
                ))
                
                logger.info(f"{self.MSG['success']} Migration {version} appliquee avec succes ({execution_time}ms)")
                return True
                
            except Exception as sql_error:
                # Enregistrement de l'échec
                execution_time = int((time.time() - start_time) * 1000)
                
                self.cursor.execute("""
                    INSERT INTO _migrations.schema_version 
                    (version, description, sql_file, checksum, execution_time_ms, success, error_message, applied_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    version, description, migration_file.name, 
                    checksum, execution_time, False, str(sql_error), os.getenv('USER', os.getenv('USERNAME', 'unknown'))
                ))
                
                logger.error(f"{self.MSG['error']} Echec migration {version}: {sql_error}")
                return False
                
        except Exception as e:
            logger.error(f"{self.MSG['error']} Erreur execution migration {migration_file.name}: {e}")
            return False
    
    def run_migrations(self) -> bool:
        """Exécution de toutes les migrations en attente"""
        try:
            pending_migrations = self.get_pending_migrations()
            
            if not pending_migrations:
                logger.info(f"{self.MSG['success']} Aucune migration en attente")
                return True
            
            logger.info(f"{self.MSG['info']} {len(pending_migrations)} migration(s) a appliquer")
            
            success_count = 0
            for migration_file in pending_migrations:
                if self.execute_migration(migration_file):
                    success_count += 1
                else:
                    logger.error(f"{self.MSG['error']} Arret sur echec migration: {migration_file.name}")
                    break
            
            if success_count == len(pending_migrations):
                logger.info(f"{self.MSG['success']} Toutes les migrations appliquees avec succes ({success_count}/{len(pending_migrations)})")
                return True
            else:
                logger.warning(f"{self.MSG['warning']} Migrations partiellement appliquees ({success_count}/{len(pending_migrations)})")
                return False
                
        except Exception as e:
            logger.error(f"{self.MSG['error']} Erreur execution migrations: {e}")
            return False
    
    def get_migration_status(self) -> Dict:
        """Récupération du statut des migrations"""
        try:
            applied_migrations = self.get_applied_migrations()
            pending_migrations = self.get_pending_migrations()
            
            # Détails des migrations appliquées
            self.cursor.execute("""
                SELECT version, description, applied_at, execution_time_ms, success
                FROM _migrations.schema_version 
                ORDER BY applied_at DESC
                LIMIT 10
            """)
            recent_migrations = self.cursor.fetchall()
            
            return {
                'applied_count': len(applied_migrations),
                'pending_count': len(pending_migrations),
                'applied_versions': applied_migrations,
                'pending_files': [f.name for f in pending_migrations],
                'recent_migrations': recent_migrations
            }
            
        except Exception as e:
            logger.error(f"{self.MSG['error']} Erreur lecture statut: {e}")
            return {}
    
    def verify_database_integrity(self) -> bool:
        """Vérification de l'intégrité de la base de données"""
        try:
            logger.info(f"{self.MSG['info']} Verification integrite base de donnees...")
            
            # Vérification des schémas
            self.cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name IN ('airport', 'air_quality', 'analytics')
            """)
            schemas = [row[0] for row in self.cursor.fetchall()]
            
            expected_schemas = ['airport', 'air_quality', 'analytics']
            missing_schemas = set(expected_schemas) - set(schemas)
            
            if missing_schemas:
                logger.error(f"{self.MSG['error']} Schemas manquants: {missing_schemas}")
                return False
            
            # Vérification des tables principales
            self.cursor.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema IN ('airport', 'air_quality', 'analytics')
                ORDER BY table_schema, table_name
            """)
            tables = self.cursor.fetchall()
            
            logger.info(f"{self.MSG['success']} Schemas trouves: {schemas}")
            logger.info(f"{self.MSG['success']} Tables trouvees: {len(tables)}")
            
            # Vérification des extensions
            self.cursor.execute("SELECT extname FROM pg_extension WHERE extname IN ('postgis', 'uuid-ossp')")
            extensions = [row[0] for row in self.cursor.fetchall()]
            
            expected_extensions = ['postgis', 'uuid-ossp']
            missing_extensions = set(expected_extensions) - set(extensions)
            
            if missing_extensions:
                logger.warning(f"{self.MSG['warning']} Extensions manquantes: {missing_extensions}")
            else:
                logger.info(f"{self.MSG['success']} Extensions trouvees: {extensions}")
            
            return True
            
        except Exception as e:
            logger.error(f"{self.MSG['error']} Erreur verification integrite: {e}")
            return False
    
    def close_connection(self):
        """Fermeture de la connexion"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info(f"{self.MSG['info']} Connexion fermee")


def load_config() -> Dict[str, str]:
    """Chargement de la configuration depuis .env"""
    load_dotenv()
    
    return {
        'DB_HOST': os.getenv('DB_HOST', 'localhost'),
        'DB_PORT': os.getenv('DB_PORT', '5433'),
        'DB_NAME': os.getenv('DB_NAME', 'airport_air_quality'),
        'DB_USER': os.getenv('DB_USER', 'airport_user'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', 'airport_password')
    }


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Gestionnaire de migrations PostgreSQL')
    parser.add_argument('--run', action='store_true', help='Executer les migrations en attente')
    parser.add_argument('--status', action='store_true', help='Afficher le statut des migrations')
    parser.add_argument('--verify', action='store_true', help='Verifier l\'integrite de la base')
    parser.add_argument('--init', action='store_true', help='Initialiser le systeme de migrations')
    
    args = parser.parse_args()
    
    # Si aucun argument, afficher l'aide
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Chargement de la configuration
    config = load_config()
    
    # Initialisation du gestionnaire
    migration_manager = MigrationManager(config)
    
    try:
        # Connexion à la base
        if not migration_manager.connect_database():
            sys.exit(1)
        
        # Initialisation du système
        if args.init or args.run:
            if not migration_manager.create_migration_table():
                sys.exit(1)
        
        # Exécution des commandes
        if args.status:
            logger.info("STATUT DES MIGRATIONS:")
            status = migration_manager.get_migration_status()
            
            print(f"\nRESUME:")
            print(f"  - Migrations appliquees: {status.get('applied_count', 0)}")
            print(f"  - Migrations en attente: {status.get('pending_count', 0)}")
            
            if status.get('applied_versions'):
                print(f"\nAPPLIQUEES:")
                for version in status['applied_versions']:
                    print(f"  - {version}")
            
            if status.get('pending_files'):
                print(f"\nEN ATTENTE:")
                for file_name in status['pending_files']:
                    print(f"  - {file_name}")
        
        elif args.verify:
            if migration_manager.verify_database_integrity():
                logger.info("[OK] Integrite de la base verifiee")
            else:
                logger.error("[ERROR] Problemes d'integrite detectes")
                sys.exit(1)
        
        elif args.run:
            if migration_manager.run_migrations():
                logger.info("[OK] Migrations executees avec succes")
            else:
                logger.error("[ERROR] Erreur lors de l'execution des migrations")
                sys.exit(1)
        
        elif args.init:
            logger.info("[OK] Systeme de migrations initialise")
    
    finally:
        migration_manager.close_connection()


if __name__ == "__main__":
    main()