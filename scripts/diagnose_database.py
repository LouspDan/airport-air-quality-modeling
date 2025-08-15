#!/usr/bin/env python3
"""
Script de diagnostic pour identifier la structure réelle de la base de données
Version corrigée sans dépendances Streamlit
"""

import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text

# Configuration base de données
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'airport_air_quality',
    'user': 'airport_user',
    'password': 'airport_password'
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

def diagnose_database():
    """Diagnostiquer la structure de la base de données"""
    
    print("🔍 DIAGNOSTIC DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # 1. Lister tous les schémas
        print("\n1️⃣ SCHÉMAS DISPONIBLES:")
        query_schemas = """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        ORDER BY schema_name;
        """
        schemas = pd.read_sql_query(query_schemas, engine)
        for schema in schemas['schema_name']:
            print(f"   📁 {schema}")
        
        # 2. Lister toutes les tables par schéma
        print("\n2️⃣ TABLES PAR SCHÉMA:")
        query_tables = """
        SELECT 
            table_schema,
            table_name,
            table_type
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        ORDER BY table_schema, table_name;
        """
        tables = pd.read_sql_query(query_tables, engine)
        
        for schema in schemas['schema_name']:
            schema_tables = tables[tables['table_schema'] == schema]
            if not schema_tables.empty:
                print(f"\n   📁 Schéma: {schema}")
                for _, table in schema_tables.iterrows():
                    print(f"      📋 {table['table_name']} ({table['table_type']})")
        
        # 3. Analyser les tables de données principales
        print("\n3️⃣ ANALYSE DES TABLES PRINCIPALES:")
        
        # Chercher les tables de vols
        flight_tables = tables[tables['table_name'].str.contains('flight|vol', case=False)]
        if not flight_tables.empty:
            print("\n   ✈️ TABLES DE VOLS:")
            for _, table in flight_tables.iterrows():
                table_full_name = f"{table['table_schema']}.{table['table_name']}"
                print(f"      📋 {table_full_name}")
                
                # Analyser la structure de la table
                try:
                    query_columns = f"""
                    SELECT 
                        column_name, 
                        data_type, 
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_schema = '{table['table_schema']}' 
                    AND table_name = '{table['table_name']}'
                    ORDER BY ordinal_position;
                    """
                    columns = pd.read_sql_query(query_columns, engine)
                    print(f"         Colonnes: {', '.join(columns['column_name'].tolist()[:10])}...")
                    
                    # Compter les enregistrements
                    count_query = f"SELECT COUNT(*) as count FROM {table_full_name};"
                    count_result = pd.read_sql_query(count_query, engine)
                    print(f"         Enregistrements: {count_result['count'].iloc[0]}")
                    
                    # Échantillon de données si la table contient des données
                    if count_result['count'].iloc[0] > 0:
                        sample_query = f"SELECT * FROM {table_full_name} LIMIT 3;"
                        sample_data = pd.read_sql_query(sample_query, engine)
                        print(f"         Échantillon disponible: {len(sample_data)} lignes")
                    
                except Exception as e:
                    print(f"         ❌ Erreur d'accès: {e}")
        
        # Chercher les tables d'émissions
        emission_tables = tables[tables['table_name'].str.contains('emission|émission', case=False)]
        if not emission_tables.empty:
            print("\n   🌫️ TABLES D'ÉMISSIONS:")
            for _, table in emission_tables.iterrows():
                table_full_name = f"{table['table_schema']}.{table['table_name']}"
                print(f"      📋 {table_full_name}")
                
                try:
                    # Analyser la structure
                    query_columns = f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = '{table['table_schema']}' 
                    AND table_name = '{table['table_name']}'
                    ORDER BY ordinal_position;
                    """
                    columns = pd.read_sql_query(query_columns, engine)
                    print(f"         Colonnes: {', '.join(columns['column_name'].tolist()[:8])}...")
                    
                    # Compter les enregistrements
                    count_query = f"SELECT COUNT(*) as count FROM {table_full_name};"
                    count_result = pd.read_sql_query(count_query, engine)
                    print(f"         Enregistrements: {count_result['count'].iloc[0]}")
                    
                except Exception as e:
                    print(f"         ❌ Erreur d'accès: {e}")
        
        # Chercher les tables météo
        weather_tables = tables[tables['table_name'].str.contains('weather|meteo|météo', case=False)]
        if not weather_tables.empty:
            print("\n   🌤️ TABLES MÉTÉO:")
            for _, table in weather_tables.iterrows():
                table_full_name = f"{table['table_schema']}.{table['table_name']}"
                print(f"      📋 {table_full_name}")
                
                try:
                    count_query = f"SELECT COUNT(*) as count FROM {table_full_name};"
                    count_result = pd.read_sql_query(count_query, engine)
                    print(f"         Enregistrements: {count_result['count'].iloc[0]}")
                except Exception as e:
                    print(f"         ❌ Erreur d'accès: {e}")
        
        # Chercher les tables de mesures
        measurement_tables = tables[tables['table_name'].str.contains('mesure|measurement|station', case=False)]
        if not measurement_tables.empty:
            print("\n   📡 TABLES DE MESURES:")
            for _, table in measurement_tables.iterrows():
                table_full_name = f"{table['table_schema']}.{table['table_name']}"
                print(f"      📋 {table_full_name}")
                
                try:
                    count_query = f"SELECT COUNT(*) as count FROM {table_full_name};"
                    count_result = pd.read_sql_query(count_query, engine)
                    print(f"         Enregistrements: {count_result['count'].iloc[0]}")
                except Exception as e:
                    print(f"         ❌ Erreur d'accès: {e}")
        
        # 4. Vérifier les extensions PostGIS
        print("\n4️⃣ EXTENSIONS POSTGIS:")
        try:
            query_extensions = """
            SELECT 
                extname as extension_name,
                extversion as version
            FROM pg_extension 
            WHERE extname LIKE '%gis%' OR extname LIKE '%spatial%';
            """
            extensions = pd.read_sql_query(query_extensions, engine)
            if not extensions.empty:
                for _, ext in extensions.iterrows():
                    print(f"   ✅ {ext['extension_name']} v{ext['version']}")
            else:
                print("   ❌ Aucune extension PostGIS trouvée")
        except Exception as e:
            print(f"   ❌ Erreur lors de la vérification des extensions: {e}")
        
        # 5. Suggestions pour le dashboard
        print("\n5️⃣ RECOMMANDATIONS POUR LE DASHBOARD:")
        
        # Vérifier si nous avons des données pour le dashboard
        has_flight_data = not flight_tables.empty
        has_emission_data = not emission_tables.empty
        has_weather_data = not weather_tables.empty
        has_measurement_data = not measurement_tables.empty
        
        if has_flight_data:
            print("   ✅ Données de vols disponibles")
            # Proposer une requête adaptée
            first_flight_table = flight_tables.iloc[0]
            flight_table_name = f"{first_flight_table['table_schema']}.{first_flight_table['table_name']}"
            print(f"   💡 Utiliser: {flight_table_name}")
        else:
            print("   ⚠️ Aucune donnée de vol trouvée - créer des données de test")
            
        if has_emission_data:
            print("   ✅ Données d'émissions disponibles")
        else:
            print("   ⚠️ Aucune donnée d'émission trouvée - calculer depuis les vols")
            
        if has_weather_data:
            print("   ✅ Données météo disponibles")
        else:
            print("   ⚠️ Aucune donnée météo trouvée - générer des données simulées")
            
        if has_measurement_data:
            print("   ✅ Données de mesures disponibles")
        else:
            print("   ⚠️ Aucune station de mesure trouvée - créer des stations fictives")
        
        return {
            'schemas': schemas,
            'tables': tables,
            'flight_tables': flight_tables,
            'emission_tables': emission_tables,
            'weather_tables': weather_tables,
            'measurement_tables': measurement_tables,
            'has_data': {
                'flights': has_flight_data,
                'emissions': has_emission_data,
                'weather': has_weather_data,
                'measurements': has_measurement_data
            }
        }
        
    except Exception as e:
        print(f"❌ ERREUR DE CONNEXION: {e}")
        print("💡 Vérifiez que PostgreSQL est démarré avec docker-compose up -d postgres")
        return None

def generate_sample_queries(diagnostic_result):
    """Générer des requêtes d'exemple basées sur les tables trouvées"""
    
    if not diagnostic_result:
        return
    
    print("\n6️⃣ REQUÊTES D'EXEMPLE GÉNÉRÉES:")
    
    # Requêtes pour les vols
    if not diagnostic_result['flight_tables'].empty:
        flight_table = diagnostic_result['flight_tables'].iloc[0]
        table_name = f"{flight_table['table_schema']}.{flight_table['table_name']}"
        
        print(f"\n   ✈️ Requête vols depuis {table_name}:")
        print(f"""
        -- Compter les vols par type d'aéronef
        SELECT 
            aircraft_type,
            COUNT(*) as flight_count
        FROM {table_name}
        GROUP BY aircraft_type
        ORDER BY flight_count DESC
        LIMIT 10;
        """)
        
        print(f"""
        -- Vols récents (adaptation automatique de colonne date)
        SELECT 
            flight_id, aircraft_type, 
            COALESCE(flight_date, scheduled_departure::date) as date_vol
        FROM {table_name}
        ORDER BY COALESCE(flight_date, scheduled_departure::date) DESC
        LIMIT 5;
        """)
    
    # Requêtes pour les émissions
    if not diagnostic_result['emission_tables'].empty:
        emission_table = diagnostic_result['emission_tables'].iloc[0]
        table_name = f"{emission_table['table_schema']}.{emission_table['table_name']}"
        
        print(f"\n   🌫️ Requête émissions depuis {table_name}:")
        print(f"""
        -- Émissions par type de polluant
        SELECT 
            type_polluant,
            SUM(quantite_emise_kg) as total_kg
        FROM {table_name}
        GROUP BY type_polluant
        ORDER BY total_kg DESC;
        """)

def test_connection():
    """Tester la connexion à la base de données"""
    print("🔗 TEST DE CONNEXION:")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"   ✅ Connexion réussie")
            print(f"   📊 Version PostgreSQL: {version}")
            return True
    except Exception as e:
        print(f"   ❌ Échec de connexion: {e}")
        print(f"   💡 Vérifiez que PostgreSQL est démarré:")
        print(f"      docker-compose up -d postgres")
        print(f"      docker-compose logs postgres")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DU DIAGNOSTIC")
    
    # Test de connexion d'abord
    if test_connection():
        # Exécuter le diagnostic complet
        result = diagnose_database()
        
        if result:
            # Générer des requêtes d'exemple
            generate_sample_queries(result)
            
            print("\n" + "=" * 50)
            print("✅ DIAGNOSTIC TERMINÉ")
            print("💡 Utilisez ces informations pour adapter le dashboard")
            
            # Résumé pour le dashboard
            print(f"\n📋 RÉSUMÉ POUR LE DASHBOARD:")
            if result['has_data']['flights']:
                print(f"   ✅ Mode données réelles possible")
            else:
                print(f"   🎭 Mode données simulées recommandé")
        else:
            print("❌ Échec du diagnostic")
    else:
        print("❌ Impossible de se connecter à la base de données")
        print("🎭 Le dashboard utilisera des données simulées")