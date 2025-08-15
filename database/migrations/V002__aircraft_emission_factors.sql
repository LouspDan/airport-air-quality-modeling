-- =====================================================
-- Migration V002: Base de données des aéronefs et facteurs d'émission (Version Simplifiée)
-- Description: Tables essentielles pour calculs d'émissions
-- Auteur: Portfolio Project
-- Date: 2025-08-15
-- =====================================================

-- =====================================================
-- 1. TABLE DES MOTEURS
-- =====================================================

CREATE TABLE IF NOT EXISTS airport.moteur_type (
    id_moteur UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    designation VARCHAR(50) NOT NULL UNIQUE,
    constructeur VARCHAR(50) NOT NULL,
    modele VARCHAR(50) NOT NULL,
    type_moteur VARCHAR(20) NOT NULL DEFAULT 'Turbofan',
    
    -- Caractéristiques techniques
    poussee_statique_kn NUMERIC(8,2) NOT NULL,
    consommation_specifique_gknh NUMERIC(8,4),
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT chk_poussee_positive CHECK (poussee_statique_kn > 0)
);

-- =====================================================
-- 2. RELATION AERONEF-MOTEUR
-- =====================================================

CREATE TABLE IF NOT EXISTS airport.aeronef_moteur (
    id_aeronef_moteur UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_type_aeronef UUID NOT NULL REFERENCES airport.aeronef_type(id_type_aeronef) ON DELETE CASCADE,
    id_moteur UUID NOT NULL REFERENCES airport.moteur_type(id_moteur) ON DELETE CASCADE,
    
    -- Configuration
    nombre_moteurs INTEGER NOT NULL DEFAULT 2,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    UNIQUE(id_type_aeronef, id_moteur),
    CONSTRAINT chk_nb_moteurs_valid CHECK (nombre_moteurs BETWEEN 1 AND 8)
);

-- =====================================================
-- 3. FACTEURS D'ÉMISSION ICAO (Simplifié)
-- =====================================================

CREATE TABLE IF NOT EXISTS air_quality.facteur_emission_icao (
    id_facteur UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_moteur UUID NOT NULL REFERENCES airport.moteur_type(id_moteur) ON DELETE CASCADE,
    
    -- Identification
    uid_icao VARCHAR(20) NOT NULL,
    
    -- Régime moteur  
    regime_moteur VARCHAR(20) NOT NULL,
    pourcentage_poussee NUMERIC(5,2) NOT NULL,
    
    -- Facteurs d'émission principaux (g/kg carburant)
    facteur_co2_g_kg NUMERIC(8,2) DEFAULT 3150.0,
    facteur_nox_g_kg NUMERIC(8,4) NOT NULL,
    facteur_co_g_kg NUMERIC(8,4) NOT NULL,
    facteur_hc_g_kg NUMERIC(8,4) NOT NULL,
    
    -- Débit carburant (kg/s)
    debit_carburant_kg_s NUMERIC(8,4) NOT NULL,
    
    -- Validité
    statut_actif BOOLEAN DEFAULT TRUE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT chk_regime_valide CHECK (regime_moteur IN ('Idle', 'Approach', 'Climb-out', 'Take-off')),
    CONSTRAINT chk_pourcentage_valid CHECK (pourcentage_poussee BETWEEN 0 AND 100),
    CONSTRAINT chk_facteurs_valid CHECK (
        facteur_nox_g_kg >= 0 AND facteur_co_g_kg >= 0 AND 
        facteur_hc_g_kg >= 0 AND debit_carburant_kg_s > 0
    ),
    UNIQUE(id_moteur, regime_moteur)
);

-- =====================================================
-- 4. PHASES DE VOL STANDARD
-- =====================================================

CREATE TABLE IF NOT EXISTS airport.phase_vol_standard (
    id_phase_standard UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom_phase VARCHAR(20) NOT NULL UNIQUE,
    ordre_sequence INTEGER NOT NULL UNIQUE,
    regime_moteur_icao VARCHAR(20) NOT NULL,
    duree_typique_minutes NUMERIC(5,2),
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT chk_ordre_valid CHECK (ordre_sequence > 0),
    CONSTRAINT chk_duree_valid CHECK (duree_typique_minutes > 0)
);

-- =====================================================
-- 5. DONNÉES DE RÉFÉRENCE
-- =====================================================

-- Vérifier si les données existent déjà avant insertion
DO $$
BEGIN
    -- Insertion des phases standard seulement si table vide
    IF NOT EXISTS (SELECT 1 FROM airport.phase_vol_standard) THEN
        INSERT INTO airport.phase_vol_standard (
            nom_phase, ordre_sequence, regime_moteur_icao, duree_typique_minutes
        ) VALUES
        ('Taxi-out', 1, 'Idle', 19.0),
        ('Take-off', 2, 'Take-off', 0.7),
        ('Climb-out', 3, 'Climb-out', 2.2),
        ('Approach', 4, 'Approach', 4.0),
        ('Landing', 5, 'Idle', 0.7),
        ('Taxi-in', 6, 'Idle', 7.0);
        
        RAISE NOTICE 'Phases de vol standard inserees';
    END IF;
    
    -- Insertion des moteurs seulement si table vide
    IF NOT EXISTS (SELECT 1 FROM airport.moteur_type) THEN
        INSERT INTO airport.moteur_type (
            designation, constructeur, modele, type_moteur, poussee_statique_kn, consommation_specifique_gknh
        ) VALUES
        ('CFM56-7B27', 'CFM International', 'CFM56-7B', 'Turbofan', 121.4, 549.0),
        ('V2533-A5', 'International Aero Engines', 'V2500', 'Turbofan', 146.8, 545.0),
        ('LEAP-1A26', 'CFM International', 'LEAP-1A', 'Turbofan', 146.8, 470.0);
        
        RAISE NOTICE 'Moteurs de reference inseres';
    END IF;
END $$;

-- =====================================================
-- 6. FACTEURS D'ÉMISSION POUR CFM56-7B27
-- =====================================================

DO $$
DECLARE
    moteur_id UUID;
BEGIN
    -- Récupérer l'ID du moteur CFM56-7B27
    SELECT id_moteur INTO moteur_id 
    FROM airport.moteur_type 
    WHERE designation = 'CFM56-7B27';
    
    -- Insérer les facteurs seulement si le moteur existe et pas déjà de facteurs
    IF moteur_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM air_quality.facteur_emission_icao WHERE id_moteur = moteur_id
    ) THEN
        INSERT INTO air_quality.facteur_emission_icao (
            id_moteur, uid_icao, regime_moteur, pourcentage_poussee,
            facteur_nox_g_kg, facteur_co_g_kg, facteur_hc_g_kg, debit_carburant_kg_s
        ) VALUES
        (moteur_id, 'CFM56-7B27', 'Take-off', 100.0, 14.9, 0.40, 0.02, 1.210),
        (moteur_id, 'CFM56-7B27', 'Climb-out', 85.0, 14.2, 0.60, 0.04, 1.028),
        (moteur_id, 'CFM56-7B27', 'Approach', 30.0, 8.6, 3.20, 0.15, 0.309),
        (moteur_id, 'CFM56-7B27', 'Idle', 7.0, 4.2, 26.80, 0.40, 0.078);
        
        RAISE NOTICE 'Facteurs emission CFM56-7B27 inseres';
    END IF;
END $$;

-- =====================================================
-- 7. VUE SIMPLE POUR CALCULS
-- =====================================================

CREATE OR REPLACE VIEW analytics.v_emission_factors_simple AS
SELECT 
    at.designation_icao,
    mt.designation as moteur,
    phs.nom_phase,
    phs.ordre_sequence,
    fe.regime_moteur,
    fe.facteur_co2_g_kg,
    fe.facteur_nox_g_kg,
    fe.debit_carburant_kg_s,
    phs.duree_typique_minutes,
    -- Calcul simple pour 1 moteur
    ROUND((fe.debit_carburant_kg_s * phs.duree_typique_minutes * 60 * fe.facteur_co2_g_kg / 1000)::NUMERIC, 3) as co2_phase_kg
FROM airport.aeronef_type at
JOIN airport.aeronef_moteur am ON at.id_type_aeronef = am.id_type_aeronef  
JOIN airport.moteur_type mt ON am.id_moteur = mt.id_moteur
JOIN air_quality.facteur_emission_icao fe ON mt.id_moteur = fe.id_moteur
JOIN airport.phase_vol_standard phs ON fe.regime_moteur = phs.regime_moteur_icao
WHERE fe.statut_actif = TRUE;

-- =====================================================
-- 8. FONCTION SIMPLE DE CALCUL
-- =====================================================

CREATE OR REPLACE FUNCTION air_quality.calculate_simple_emissions(
    p_aeronef_icao VARCHAR(10)
) RETURNS TABLE (
    phase VARCHAR(20),
    co2_kg NUMERIC,
    nox_kg NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        phs.nom_phase::VARCHAR(20),
        ROUND((fe.debit_carburant_kg_s * phs.duree_typique_minutes * 60 * am.nombre_moteurs * fe.facteur_co2_g_kg / 1000)::NUMERIC, 2),
        ROUND((fe.debit_carburant_kg_s * phs.duree_typique_minutes * 60 * am.nombre_moteurs * fe.facteur_nox_g_kg / 1000)::NUMERIC, 3)
    FROM airport.aeronef_type at
    JOIN airport.aeronef_moteur am ON at.id_type_aeronef = am.id_type_aeronef
    JOIN airport.moteur_type mt ON am.id_moteur = mt.id_moteur
    JOIN air_quality.facteur_emission_icao fe ON mt.id_moteur = fe.id_moteur
    JOIN airport.phase_vol_standard phs ON fe.regime_moteur = phs.regime_moteur_icao
    WHERE at.designation_icao = p_aeronef_icao 
      AND fe.statut_actif = TRUE
    ORDER BY phs.ordre_sequence;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 9. LIEN AERONEF A320 AVEC MOTEUR V2500
-- =====================================================

DO $$
DECLARE
    aeronef_id UUID;
    moteur_id UUID;
BEGIN
    -- Récupérer les IDs
    SELECT id_type_aeronef INTO aeronef_id FROM airport.aeronef_type WHERE designation_icao = 'A320';
    SELECT id_moteur INTO moteur_id FROM airport.moteur_type WHERE designation = 'V2533-A5';
    
    -- Créer la liaison seulement si elle n'existe pas
    IF aeronef_id IS NOT NULL AND moteur_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM airport.aeronef_moteur WHERE id_type_aeronef = aeronef_id AND id_moteur = moteur_id
    ) THEN
        INSERT INTO airport.aeronef_moteur (id_type_aeronef, id_moteur, nombre_moteurs)
        VALUES (aeronef_id, moteur_id, 2);
        
        RAISE NOTICE 'Liaison A320-V2500 creee';
    END IF;
END $$;

-- =====================================================
-- 10. COMMENTAIRES
-- =====================================================

COMMENT ON TABLE airport.moteur_type IS 'Catalogue des moteurs avec caractéristiques de base';
COMMENT ON TABLE air_quality.facteur_emission_icao IS 'Facteurs émission ICAO par régime moteur';
COMMENT ON FUNCTION air_quality.calculate_simple_emissions IS 'Calcul émissions simplifié par aéronef';

-- =====================================================
-- FIN MIGRATION V002 SIMPLIFIÉE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Migration V002 (simplifiee) appliquee avec succes';
END $$;