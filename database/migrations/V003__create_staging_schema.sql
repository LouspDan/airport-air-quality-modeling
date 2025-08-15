-- =====================================================
-- Migration V003: Schéma staging pour pipeline ETL
-- Description: Zone de staging avec contrôles qualité
-- Auteur: Portfolio Project
-- Date: 2025-08-15
-- =====================================================

-- =====================================================
-- 1. CRÉATION SCHÉMAS ETL
-- =====================================================

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS _etl;

-- =====================================================
-- 2. TABLES DE CONTRÔLE ETL
-- =====================================================

-- Table de gestion des lots de traitement
CREATE TABLE _etl.batch_control (
    batch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_name VARCHAR(100) NOT NULL,
    source_file VARCHAR(255),
    file_size_bytes BIGINT,
    total_records INTEGER,
    
    -- États du traitement
    status VARCHAR(20) DEFAULT 'STARTED',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Métriques qualité
    valid_records INTEGER DEFAULT 0,
    warning_records INTEGER DEFAULT 0,
    error_records INTEGER DEFAULT 0,
    quality_score NUMERIC(5,2),
    
    -- Métadonnées
    processed_by VARCHAR(100),
    etl_version VARCHAR(20) DEFAULT '1.0',
    config_used JSONB,
    error_summary TEXT,
    
    -- Contraintes
    CONSTRAINT chk_status_valid CHECK (status IN ('STARTED', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    CONSTRAINT chk_quality_score CHECK (quality_score BETWEEN 0 AND 100)
);

CREATE INDEX idx_batch_control_status ON _etl.batch_control(status);
CREATE INDEX idx_batch_control_start_time ON _etl.batch_control(start_time);

-- Table de suivi des erreurs
CREATE TABLE _etl.error_tracking (
    error_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES _etl.batch_control(batch_id),
    
    -- Identification erreur
    error_type VARCHAR(20) NOT NULL, -- CRITICAL, WARNING, INFO
    error_code VARCHAR(50),
    error_message TEXT,
    
    -- Localisation
    source_table VARCHAR(100),
    source_row_id VARCHAR(100),
    field_name VARCHAR(100),
    field_value TEXT,
    
    -- Contexte
    rule_violated VARCHAR(200),
    suggested_action TEXT,
    
    -- Métadonnées
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_action TEXT,
    
    -- Contraintes
    CONSTRAINT chk_error_type_valid CHECK (error_type IN ('CRITICAL', 'WARNING', 'INFO'))
);

CREATE INDEX idx_error_batch ON _etl.error_tracking(batch_id);
CREATE INDEX idx_error_type ON _etl.error_tracking(error_type);

-- =====================================================
-- 3. TABLES STAGING - RÉCEPTION BRUTE
-- =====================================================

-- Staging flights (réception brute CSV)
CREATE TABLE staging.raw_flights (
    staging_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES _etl.batch_control(batch_id),
    source_row_number INTEGER,
    
    -- Données brutes (texte pour éviter erreurs de type)
    flight_id TEXT,
    flight_number TEXT,
    airline_iata TEXT,
    airline_icao TEXT,
    aircraft_type TEXT,
    flight_date TEXT,
    scheduled_departure TEXT,
    scheduled_arrival TEXT,
    origin_airport TEXT,
    destination_airport TEXT,
    destination_city TEXT,
    destination_country TEXT,
    distance_km TEXT,
    passengers TEXT,
    fuel_kg TEXT,
    flight_type TEXT,
    taxi_out_minutes TEXT,
    taxi_in_minutes TEXT,
    flight_time_hours TEXT,
    load_factor TEXT,
    aircraft_age_years TEXT,
    crew_count TEXT,
    data_source TEXT,
    created_timestamp TEXT,
    
    -- Métadonnées staging
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'RAW',
    quality_flags TEXT[],
    
    CONSTRAINT chk_processing_status CHECK (processing_status IN ('RAW', 'VALIDATED', 'REJECTED', 'PROCESSED'))
);

CREATE INDEX idx_raw_flights_batch ON staging.raw_flights(batch_id);
CREATE INDEX idx_raw_flights_status ON staging.raw_flights(processing_status);

-- Staging weather (réception brute)
CREATE TABLE staging.raw_weather (
    staging_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES _etl.batch_control(batch_id),
    source_row_number INTEGER,
    
    -- Données brutes
    station_id TEXT,
    measurement_time TEXT,
    temperature_c TEXT,
    humidity_percent TEXT,
    pressure_hpa TEXT,
    wind_speed_ms TEXT,
    wind_direction_deg TEXT,
    visibility_m TEXT,
    precipitation_mm TEXT,
    cloud_cover_percent TEXT,
    weather_conditions TEXT,
    data_quality TEXT,
    source_system TEXT,
    
    -- Métadonnées staging
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'RAW',
    quality_flags TEXT[]
);

-- Staging aircraft catalog
CREATE TABLE staging.raw_aircraft (
    staging_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES _etl.batch_control(batch_id),
    source_row_number INTEGER,
    
    -- Données brutes
    icao_designation TEXT,
    manufacturer TEXT,
    model TEXT,
    variant TEXT,
    engine_type TEXT,
    number_of_engines TEXT,
    typical_seating TEXT,
    max_seating TEXT,
    cargo_capacity_m3 TEXT,
    max_takeoff_weight_kg TEXT,
    empty_weight_kg TEXT,
    fuel_capacity_l TEXT,
    cruise_speed_kmh TEXT,
    max_range_km TEXT,
    service_ceiling_m TEXT,
    wingspan_m TEXT,
    length_m TEXT,
    height_m TEXT,
    first_flight_year TEXT,
    certification_date TEXT,
    production_status TEXT,
    noise_chapter TEXT,
    co2_efficiency_g_pkm TEXT,
    data_source TEXT,
    last_updated TEXT,
    
    -- Métadonnées staging
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'RAW',
    quality_flags TEXT[]
);

-- Staging emission factors
CREATE TABLE staging.raw_emissions (
    staging_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES _etl.batch_control(batch_id),
    source_row_number INTEGER,
    
    -- Données brutes
    engine_uid TEXT,
    engine_designation TEXT,
    manufacturer TEXT,
    aircraft_types TEXT,
    certification_date TEXT,
    thrust_rating_kn TEXT,
    bypass_ratio TEXT,
    fuel_flow_idle_kgs TEXT,
    fuel_flow_approach_kgs TEXT,
    fuel_flow_climbout_kgs TEXT,
    fuel_flow_takeoff_kgs TEXT,
    nox_idle_gkg TEXT,
    nox_approach_gkg TEXT,
    nox_climbout_gkg TEXT,
    nox_takeoff_gkg TEXT,
    co_idle_gkg TEXT,
    co_approach_gkg TEXT,
    co_climbout_gkg TEXT,
    co_takeoff_gkg TEXT,
    hc_idle_gkg TEXT,
    hc_approach_gkg TEXT,
    hc_climbout_gkg TEXT,
    hc_takeoff_gkg TEXT,
    smoke_number TEXT,
    nvpm_number_mg TEXT,
    nvpm_mass_mg TEXT,
    certification_standard TEXT,
    data_source TEXT,
    last_updated TEXT,
    
    -- Métadonnées staging
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'RAW',
    quality_flags TEXT[]
);

-- =====================================================
-- 4. TABLES STAGING - DONNÉES VALIDÉES
-- =====================================================

-- Flights validés (après transformation)
CREATE TABLE staging.validated_flights (
    validated_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES _etl.batch_control(batch_id),
    source_staging_id UUID REFERENCES staging.raw_flights(staging_id),
    
    -- Données nettoyées et typées
    flight_id VARCHAR(50) NOT NULL,
    flight_number VARCHAR(10) NOT NULL,
    airline_iata VARCHAR(2),
    airline_icao VARCHAR(3),
    aircraft_type VARCHAR(10) NOT NULL,
    flight_date DATE NOT NULL,
    scheduled_departure TIME,
    scheduled_arrival TIME,
    origin_airport VARCHAR(3) NOT NULL,
    destination_airport VARCHAR(3) NOT NULL,
    destination_city VARCHAR(100),
    destination_country VARCHAR(3),
    distance_km INTEGER,
    passengers INTEGER,
    fuel_kg NUMERIC(8,2),
    flight_type VARCHAR(20),
    taxi_out_minutes NUMERIC(5,2),
    taxi_in_minutes NUMERIC(5,2),
    flight_time_hours NUMERIC(5,2),
    load_factor NUMERIC(4,3),
    aircraft_age_years INTEGER,
    crew_count INTEGER,
    data_source VARCHAR(100),
    
    -- Enrichissement
    season VARCHAR(10), -- Calculé depuis flight_date
    day_of_week INTEGER, -- 1=Lundi, 7=Dimanche
    is_weekend BOOLEAN,
    hour_category VARCHAR(20), -- 'peak', 'off_peak', 'night'
    
    -- Qualité et statut
    validation_status VARCHAR(20) DEFAULT 'VALID',
    quality_score INTEGER, -- 0-100
    warnings TEXT[],
    validation_rules_passed TEXT[],
    
    -- Métadonnées
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_by VARCHAR(100),
    
    -- Contraintes
    CONSTRAINT chk_validation_status CHECK (validation_status IN ('VALID', 'WARNING', 'REJECTED')),
    CONSTRAINT chk_quality_score_range CHECK (quality_score BETWEEN 0 AND 100),
    CONSTRAINT chk_passengers_positive CHECK (passengers >= 0),
    CONSTRAINT chk_distance_positive CHECK (distance_km > 0)
);

CREATE INDEX idx_validated_flights_batch ON staging.validated_flights(batch_id);
CREATE INDEX idx_validated_flights_status ON staging.validated_flights(validation_status);
CREATE INDEX idx_validated_flights_date ON staging.validated_flights(flight_date);

-- =====================================================
-- 5. TABLES DE QUALITÉ ET RAPPORTS
-- =====================================================

-- Enregistrements rejetés avec raisons
CREATE TABLE staging.rejected_records (
    rejected_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES _etl.batch_control(batch_id),
    source_table VARCHAR(100) NOT NULL,
    source_staging_id UUID,
    
    -- Raisons du rejet
    rejection_category VARCHAR(50) NOT NULL,
    rejection_reason TEXT NOT NULL,
    failed_validations TEXT[],
    
    -- Données originales (pour debug)
    original_data JSONB,
    
    -- Actions suggérées
    suggested_fix TEXT,
    can_be_corrected BOOLEAN DEFAULT FALSE,
    correction_priority VARCHAR(10) DEFAULT 'MEDIUM',
    
    -- Métadonnées
    rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by VARCHAR(100),
    review_notes TEXT,
    
    CONSTRAINT chk_correction_priority CHECK (correction_priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE INDEX idx_rejected_batch ON staging.rejected_records(batch_id);
CREATE INDEX idx_rejected_category ON staging.rejected_records(rejection_category);

-- Métriques qualité par lot
CREATE TABLE staging.quality_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES _etl.batch_control(batch_id),
    
    -- Métriques par table
    table_name VARCHAR(100) NOT NULL,
    total_records INTEGER NOT NULL,
    valid_records INTEGER DEFAULT 0,
    warning_records INTEGER DEFAULT 0,
    rejected_records INTEGER DEFAULT 0,
    
    -- Pourcentages
    validation_rate NUMERIC(5,2), -- % validés
    rejection_rate NUMERIC(5,2),  -- % rejetés
    warning_rate NUMERIC(5,2),    -- % avec warnings
    
    -- Métriques détaillées
    completeness_score NUMERIC(5,2), -- % champs remplis
    accuracy_score NUMERIC(5,2),     -- % valeurs cohérentes
    consistency_score NUMERIC(5,2),  -- % cohérence référentielle
    
    -- Performance
    processing_start TIMESTAMP,
    processing_end TIMESTAMP,
    processing_duration_seconds INTEGER,
    throughput_records_per_second NUMERIC(8,2),
    
    -- Détails erreurs
    most_common_errors JSONB,
    error_distribution JSONB,
    
    -- Métadonnées
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quality_metrics_batch ON staging.quality_metrics(batch_id);
CREATE INDEX idx_quality_metrics_table ON staging.quality_metrics(table_name);

-- =====================================================
-- 6. VUES DE MONITORING
-- =====================================================

-- Vue résumé qualité par lot
CREATE OR REPLACE VIEW staging.v_batch_quality_summary AS
SELECT 
    bc.batch_id,
    bc.batch_name,
    bc.source_file,
    bc.status,
    bc.start_time,
    bc.duration_seconds,
    bc.total_records,
    bc.valid_records,
    bc.warning_records,
    bc.error_records,
    bc.quality_score,
    
    -- Calculs de pourcentages
    CASE 
        WHEN bc.total_records > 0 THEN 
            ROUND((bc.valid_records::NUMERIC / bc.total_records * 100), 2)
        ELSE 0 
    END AS success_rate_percent,
    
    CASE 
        WHEN bc.total_records > 0 THEN 
            ROUND((bc.error_records::NUMERIC / bc.total_records * 100), 2)
        ELSE 0 
    END AS error_rate_percent,
    
    -- Throughput
    CASE 
        WHEN bc.duration_seconds > 0 THEN 
            ROUND((bc.total_records::NUMERIC / bc.duration_seconds), 2)
        ELSE 0 
    END AS records_per_second,
    
    -- Alertes
    CASE 
        WHEN bc.error_records::NUMERIC / NULLIF(bc.total_records, 0) > 0.1 THEN 'HIGH_ERROR_RATE'
        WHEN bc.duration_seconds > 3600 THEN 'SLOW_PROCESSING'
        WHEN bc.quality_score < 80 THEN 'LOW_QUALITY'
        ELSE 'OK'
    END AS alert_status

FROM _etl.batch_control bc
ORDER BY bc.start_time DESC;

-- Vue erreurs par catégorie
CREATE OR REPLACE VIEW staging.v_error_analysis AS
SELECT 
    et.error_type,
    et.error_code,
    COUNT(*) as error_count,
    COUNT(DISTINCT et.batch_id) as affected_batches,
    ARRAY_AGG(DISTINCT et.source_table) as affected_tables,
    
    -- Exemples d'erreurs
    STRING_AGG(DISTINCT SUBSTRING(et.error_message, 1, 100), ' | ') as sample_messages,
    
    -- Timing
    MIN(et.detected_at) as first_occurrence,
    MAX(et.detected_at) as last_occurrence,
    
    -- Résolution
    COUNT(CASE WHEN et.resolved_at IS NOT NULL THEN 1 END) as resolved_count,
    ROUND(
        COUNT(CASE WHEN et.resolved_at IS NOT NULL THEN 1 END)::NUMERIC 
        / COUNT(*) * 100, 2
    ) as resolution_rate_percent

FROM _etl.error_tracking et
WHERE et.detected_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY et.error_type, et.error_code
ORDER BY error_count DESC;

-- =====================================================
-- 7. FONCTIONS UTILITAIRES
-- =====================================================

-- Fonction de nettoyage des anciennes données staging
CREATE OR REPLACE FUNCTION staging.cleanup_old_batches(retention_days INTEGER DEFAULT 7)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    cutoff_date TIMESTAMP;
BEGIN
    cutoff_date := CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    
    -- Supprimer les données staging anciennes
    WITH deleted_batches AS (
        DELETE FROM _etl.batch_control 
        WHERE start_time < cutoff_date 
        AND status IN ('COMPLETED', 'FAILED')
        RETURNING batch_id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted_batches;
    
    -- Log de l'opération
    INSERT INTO _etl.error_tracking (
        error_type, error_code, error_message, detected_at
    ) VALUES (
        'INFO', 'CLEANUP_COMPLETED', 
        'Nettoyage automatique: ' || deleted_count || ' lots supprimés (>' || retention_days || ' jours)',
        CURRENT_TIMESTAMP
    );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Fonction de calcul du score qualité
CREATE OR REPLACE FUNCTION staging.calculate_quality_score(
    p_total INTEGER,
    p_valid INTEGER, 
    p_warning INTEGER,
    p_error INTEGER
) RETURNS NUMERIC AS $$
BEGIN
    IF p_total = 0 THEN RETURN 0; END IF;
    
    RETURN ROUND(
        (p_valid * 1.0 + p_warning * 0.7 + p_error * 0.0) / p_total * 100,
        2
    );
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. TRIGGERS ET AUTOMATISATIONS
-- =====================================================

-- Trigger pour calcul automatique du score qualité
CREATE OR REPLACE FUNCTION _etl.update_quality_score()
RETURNS TRIGGER AS $$
BEGIN
    NEW.quality_score := staging.calculate_quality_score(
        NEW.total_records,
        NEW.valid_records,
        NEW.warning_records, 
        NEW.error_records
    );
    
    NEW.duration_seconds := EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time));
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_batch_quality_score
    BEFORE UPDATE ON _etl.batch_control
    FOR EACH ROW EXECUTE FUNCTION _etl.update_quality_score();

-- =====================================================
-- 9. PERMISSIONS ET SÉCURITÉ
-- =====================================================

-- Rôle ETL avec permissions spécifiques
CREATE ROLE etl_processor;

-- Permissions lecture/écriture sur staging
GRANT USAGE ON SCHEMA staging TO etl_processor;
GRANT ALL ON ALL TABLES IN SCHEMA staging TO etl_processor;
GRANT ALL ON ALL SEQUENCES IN SCHEMA staging TO etl_processor;

-- Permissions sur contrôle ETL
GRANT USAGE ON SCHEMA _etl TO etl_processor;
GRANT ALL ON ALL TABLES IN SCHEMA _etl TO etl_processor;
GRANT ALL ON ALL SEQUENCES IN SCHEMA _etl TO etl_processor;

-- Permissions lecture sur production (pour validation référentielle)
GRANT SELECT ON ALL TABLES IN SCHEMA airport TO etl_processor;
GRANT SELECT ON ALL TABLES IN SCHEMA air_quality TO etl_processor;

-- =====================================================
-- 10. DONNÉES DE TEST
-- =====================================================

-- Insertion d'un lot de test
INSERT INTO _etl.batch_control (
    batch_name, source_file, status, total_records, processed_by
) VALUES (
    'TEST_BATCH_INIT', 'migration_v003_test.sql', 'COMPLETED', 0, 'MIGRATION_V003'
);

-- =====================================================
-- COMMENTAIRES ET DOCUMENTATION
-- =====================================================

COMMENT ON SCHEMA staging IS 'Zone de staging pour pipeline ETL avec validation qualité';
COMMENT ON SCHEMA _etl IS 'Tables de contrôle et monitoring du processus ETL';

COMMENT ON TABLE _etl.batch_control IS 'Gestion des lots de traitement ETL avec métriques';
COMMENT ON TABLE _etl.error_tracking IS 'Suivi détaillé des erreurs avec classification';
COMMENT ON TABLE staging.raw_flights IS 'Réception brute des données de vol avant validation';
COMMENT ON TABLE staging.validated_flights IS 'Données de vol validées et enrichies';
COMMENT ON TABLE staging.rejected_records IS 'Enregistrements rejetés avec diagnostic';

COMMENT ON VIEW staging.v_batch_quality_summary IS 'Vue de supervision de la qualité par lot';
COMMENT ON VIEW staging.v_error_analysis IS 'Analyse des erreurs par type et fréquence';

COMMENT ON FUNCTION staging.cleanup_old_batches IS 'Nettoyage automatique des données anciennes';
COMMENT ON FUNCTION staging.calculate_quality_score IS 'Calcul du score qualité pondéré';

-- =====================================================
-- FIN MIGRATION V003
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Migration V003 appliquée avec succès - Schéma staging ETL créé avec contrôles qualité';
END $$;