-- =====================================================
-- Migration V001: Création du schéma initial
-- Description: Tables principales pour la qualité de l'air aéroportuaire
-- Auteur: Portfolio Project
-- Date: 2025-08-15
-- =====================================================

-- Extensions PostgreSQL nécessaires
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Schémas applicatifs
CREATE SCHEMA IF NOT EXISTS airport;
CREATE SCHEMA IF NOT EXISTS air_quality;
CREATE SCHEMA IF NOT EXISTS analytics;

-- =====================================================
-- 1. TABLES DE RÉFÉRENCE
-- =====================================================

-- Table des aéroports
CREATE TABLE airport.aeroport (
    id_aeroport UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code_iata VARCHAR(3) NOT NULL UNIQUE,
    code_icao VARCHAR(4) NOT NULL UNIQUE,
    nom_aeroport VARCHAR(255) NOT NULL,
    ville VARCHAR(100) NOT NULL,
    pays VARCHAR(3) NOT NULL, -- Code ISO 3166-1 alpha-3
    coordonnees_gps GEOMETRY(POINT, 4326) NOT NULL,
    altitude_m INTEGER NOT NULL,
    fuseau_horaire VARCHAR(50) NOT NULL,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_operationnel BOOLEAN DEFAULT TRUE,
    
    -- Contraintes
    CONSTRAINT chk_code_iata_format CHECK (code_iata ~ '^[A-Z]{3}$'),
    CONSTRAINT chk_code_icao_format CHECK (code_icao ~ '^[A-Z]{4}$'),
    CONSTRAINT chk_altitude_valide CHECK (altitude_m BETWEEN -500 AND 5000)
);

-- Index géospatial
CREATE INDEX idx_aeroport_geom ON airport.aeroport USING GIST (coordonnees_gps);

-- Commentaires
COMMENT ON TABLE airport.aeroport IS 'Table de référence des aéroports';
COMMENT ON COLUMN airport.aeroport.coordonnees_gps IS 'Coordonnées GPS en WGS84 (EPSG:4326)';

-- Table des terminaux
CREATE TABLE airport.terminal (
    id_terminal UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_aeroport UUID NOT NULL REFERENCES airport.aeroport(id_aeroport) ON DELETE CASCADE,
    nom_terminal VARCHAR(10) NOT NULL,
    capacite_passagers_annuelle INTEGER,
    surface_m2 NUMERIC(10,2),
    coordonnees_gps GEOMETRY(POINT, 4326),
    statut_operationnel BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    UNIQUE(id_aeroport, nom_terminal),
    CONSTRAINT chk_capacite_positive CHECK (capacite_passagers_annuelle > 0),
    CONSTRAINT chk_surface_positive CHECK (surface_m2 > 0)
);

CREATE INDEX idx_terminal_aeroport ON airport.terminal(id_aeroport);
CREATE INDEX idx_terminal_geom ON airport.terminal USING GIST (coordonnees_gps);

-- Table des pistes
CREATE TABLE airport.piste (
    id_piste UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_aeroport UUID NOT NULL REFERENCES airport.aeroport(id_aeroport) ON DELETE CASCADE,
    designation VARCHAR(10) NOT NULL, -- Ex: 07L/25R
    longueur_m INTEGER NOT NULL,
    largeur_m INTEGER NOT NULL,
    orientation_degres NUMERIC(5,2),
    coordonnees_debut GEOMETRY(POINT, 4326),
    coordonnees_fin GEOMETRY(POINT, 4326),
    type_surface VARCHAR(20) DEFAULT 'Bitume',
    statut_operationnel BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    UNIQUE(id_aeroport, designation),
    CONSTRAINT chk_longueur_valide CHECK (longueur_m BETWEEN 500 AND 6000),
    CONSTRAINT chk_largeur_valide CHECK (largeur_m BETWEEN 15 AND 100),
    CONSTRAINT chk_orientation_valide CHECK (orientation_degres BETWEEN 0 AND 360)
);

-- Table des types d'aéronefs
CREATE TABLE airport.aeronef_type (
    id_type_aeronef UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    constructeur VARCHAR(50) NOT NULL,
    modele VARCHAR(50) NOT NULL,
    designation_icao VARCHAR(10) NOT NULL UNIQUE,
    nb_moteurs INTEGER NOT NULL,
    type_moteur VARCHAR(20) NOT NULL, -- Turbofan, Turbojet, etc.
    poids_max_decollage_kg INTEGER NOT NULL,
    capacite_passagers_max INTEGER,
    
    -- Facteurs d'émission de base (seront détaillés dans une table séparée)
    facteur_emission_co2_kg_km NUMERIC(8,4),
    facteur_emission_nox_g_km NUMERIC(8,4),
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    UNIQUE(constructeur, modele),
    CONSTRAINT chk_nb_moteurs_valide CHECK (nb_moteurs BETWEEN 1 AND 8),
    CONSTRAINT chk_poids_positif CHECK (poids_max_decollage_kg > 0),
    CONSTRAINT chk_capacite_valide CHECK (capacite_passagers_max >= 0)
);

CREATE INDEX idx_aeronef_designation ON airport.aeronef_type(designation_icao);

-- Table des compagnies aériennes
CREATE TABLE airport.compagnie (
    id_compagnie UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code_iata VARCHAR(2) UNIQUE,
    code_icao VARCHAR(3) NOT NULL UNIQUE,
    nom_compagnie VARCHAR(255) NOT NULL,
    pays_origine VARCHAR(3) NOT NULL,
    statut_actif BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT chk_code_iata_compagnie CHECK (code_iata ~ '^[A-Z0-9]{2}$'),
    CONSTRAINT chk_code_icao_compagnie CHECK (code_icao ~ '^[A-Z]{3}$')
);

-- =====================================================
-- 2. TABLES OPÉRATIONNELLES
-- =====================================================

-- Table des vols
CREATE TABLE airport.vol (
    id_vol UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_vol VARCHAR(10) NOT NULL,
    id_compagnie UUID NOT NULL REFERENCES airport.compagnie(id_compagnie),
    id_type_aeronef UUID NOT NULL REFERENCES airport.aeronef_type(id_type_aeronef),
    
    -- Aéroports
    id_aeroport_origine UUID REFERENCES airport.aeroport(id_aeroport),
    id_aeroport_destination UUID REFERENCES airport.aeroport(id_aeroport),
    
    -- Terminaux et pistes
    id_terminal_depart UUID REFERENCES airport.terminal(id_terminal),
    id_terminal_arrivee UUID REFERENCES airport.terminal(id_terminal),
    id_piste_utilisee UUID REFERENCES airport.piste(id_piste),
    
    -- Planification
    date_vol DATE NOT NULL,
    heure_decollage_prevue TIME,
    heure_atterrissage_prevue TIME,
    
    -- Réalisation
    heure_decollage_reelle TIME,
    heure_atterrissage_reelle TIME,
    
    -- Caractéristiques vol
    distance_km INTEGER,
    nb_passagers INTEGER DEFAULT 0,
    poids_carburant_kg NUMERIC(8,2),
    
    -- Statut
    statut_vol VARCHAR(20) DEFAULT 'Programmé',
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT chk_statut_vol CHECK (statut_vol IN ('Programmé', 'En cours', 'Terminé', 'Annulé', 'Retardé')),
    CONSTRAINT chk_nb_passagers_positif CHECK (nb_passagers >= 0),
    CONSTRAINT chk_distance_positive CHECK (distance_km > 0),
    CONSTRAINT chk_carburant_positif CHECK (poids_carburant_kg >= 0),
    CONSTRAINT chk_heures_coherentes CHECK (
        (heure_atterrissage_reelle IS NULL AND heure_decollage_reelle IS NULL) OR
        (heure_atterrissage_reelle IS NULL) OR
        (heure_decollage_reelle IS NULL) OR
        (heure_atterrissage_reelle >= heure_decollage_reelle)
    )
);

-- Index pour les requêtes fréquentes
CREATE INDEX idx_vol_date ON airport.vol(date_vol);
CREATE INDEX idx_vol_compagnie ON airport.vol(id_compagnie);
CREATE INDEX idx_vol_aeronef ON airport.vol(id_type_aeronef);
CREATE INDEX idx_vol_numero_date ON airport.vol(numero_vol, date_vol);

-- Table des phases de vol
CREATE TABLE airport.phase_vol (
    id_phase UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_vol UUID NOT NULL REFERENCES airport.vol(id_vol) ON DELETE CASCADE,
    
    type_phase VARCHAR(20) NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME,
    duree_minutes INTEGER,
    
    -- Localisation
    position_gps GEOMETRY(POINT, 4326),
    altitude_m INTEGER,
    distance_parcourue_m NUMERIC(8,2),
    
    -- Consommation
    consommation_carburant_kg NUMERIC(8,4),
    puissance_moteur_pourcent NUMERIC(5,2) DEFAULT 0,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT chk_type_phase CHECK (type_phase IN (
        'Taxi-out', 'Décollage', 'Montée', 'Croisière', 
        'Descente', 'Approche', 'Atterrissage', 'Taxi-in'
    )),
    CONSTRAINT chk_duree_positive CHECK (duree_minutes >= 0),
    CONSTRAINT chk_puissance_valide CHECK (puissance_moteur_pourcent BETWEEN 0 AND 100),
    CONSTRAINT chk_heures_phase_coherentes CHECK (
        heure_fin IS NULL OR heure_fin >= heure_debut
    )
);

CREATE INDEX idx_phase_vol ON airport.phase_vol(id_vol);
CREATE INDEX idx_phase_type ON airport.phase_vol(type_phase);
CREATE INDEX idx_phase_geom ON airport.phase_vol USING GIST (position_gps);

-- =====================================================
-- 3. TABLES QUALITÉ DE L'AIR
-- =====================================================

-- Table des stations de mesure
CREATE TABLE air_quality.station_mesure (
    id_station UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_aeroport UUID NOT NULL REFERENCES airport.aeroport(id_aeroport),
    
    nom_station VARCHAR(100) NOT NULL,
    type_station VARCHAR(20) DEFAULT 'Fixe',
    coordonnees_gps GEOMETRY(POINT, 4326) NOT NULL,
    altitude_m INTEGER,
    
    -- Zone de surveillance
    zone_surveillance VARCHAR(100),
    rayon_surveillance_m INTEGER DEFAULT 1000,
    
    -- Polluants mesurés (array)
    polluants_mesures TEXT[] DEFAULT ARRAY['CO2', 'NOx', 'PM10', 'PM2.5'],
    
    -- Dates
    date_installation DATE DEFAULT CURRENT_DATE,
    date_derniere_calibration DATE,
    
    -- Statut
    statut_operationnel BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT chk_type_station CHECK (type_station IN ('Fixe', 'Mobile', 'Temporaire')),
    CONSTRAINT chk_rayon_positif CHECK (rayon_surveillance_m > 0),
    UNIQUE(id_aeroport, nom_station)
);

CREATE INDEX idx_station_aeroport ON air_quality.station_mesure(id_aeroport);
CREATE INDEX idx_station_geom ON air_quality.station_mesure USING GIST (coordonnees_gps);

-- Table des mesures de qualité de l'air
CREATE TABLE air_quality.mesure_qualite_air (
    id_mesure UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_station UUID NOT NULL REFERENCES air_quality.station_mesure(id_station),
    
    timestamp_mesure TIMESTAMP NOT NULL,
    polluant VARCHAR(10) NOT NULL,
    valeur_mesure NUMERIC(12,6) NOT NULL,
    unite_mesure VARCHAR(20) NOT NULL,
    
    -- Qualité de la mesure
    methode_mesure VARCHAR(50),
    qualite_donnee VARCHAR(20) DEFAULT 'En cours',
    code_qualite INTEGER DEFAULT 1,
    
    -- Conditions météo au moment de la mesure
    temperature_c NUMERIC(5,2),
    humidite_pourcent NUMERIC(5,2),
    vitesse_vent_ms NUMERIC(5,2),
    direction_vent_degres INTEGER,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT chk_polluant_valide CHECK (polluant IN ('CO2', 'NOx', 'NO2', 'PM10', 'PM2.5', 'SO2', 'O3')),
    CONSTRAINT chk_qualite_donnee CHECK (qualite_donnee IN ('Validé', 'En cours', 'Douteux', 'Invalide')),
    CONSTRAINT chk_valeur_positive CHECK (valeur_mesure >= 0),
    CONSTRAINT chk_code_qualite CHECK (code_qualite BETWEEN 0 AND 9),
    UNIQUE(id_station, timestamp_mesure, polluant)
);

-- Index pour les performances
CREATE INDEX idx_mesure_station_time ON air_quality.mesure_qualite_air(id_station, timestamp_mesure);
CREATE INDEX idx_mesure_polluant_time ON air_quality.mesure_qualite_air(polluant, timestamp_mesure);

-- =====================================================
-- 4. FONCTIONS ET TRIGGERS
-- =====================================================

-- Fonction de mise à jour automatique des timestamps
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_modification = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers pour les tables principales
CREATE TRIGGER trg_aeroport_modified
    BEFORE UPDATE ON airport.aeroport
    FOR EACH ROW EXECUTE FUNCTION update_modified_timestamp();

CREATE TRIGGER trg_terminal_modified
    BEFORE UPDATE ON airport.terminal
    FOR EACH ROW EXECUTE FUNCTION update_modified_timestamp();

CREATE TRIGGER trg_aeronef_modified
    BEFORE UPDATE ON airport.aeronef_type
    FOR EACH ROW EXECUTE FUNCTION update_modified_timestamp();

CREATE TRIGGER trg_vol_modified
    BEFORE UPDATE ON airport.vol
    FOR EACH ROW EXECUTE FUNCTION update_modified_timestamp();

-- Fonction de calcul automatique de la durée des phases
CREATE OR REPLACE FUNCTION calculate_phase_duration()
RETURNS TRIGGER AS $$
BEGIN
    -- Calcul de la durée en minutes
    IF NEW.heure_debut IS NOT NULL AND NEW.heure_fin IS NOT NULL THEN
        NEW.duree_minutes = EXTRACT(EPOCH FROM (NEW.heure_fin - NEW.heure_debut)) / 60;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_phase_duration
    BEFORE INSERT OR UPDATE ON airport.phase_vol
    FOR EACH ROW EXECUTE FUNCTION calculate_phase_duration();

-- =====================================================
-- 5. VUES MÉTIER DE BASE
-- =====================================================

-- Vue pour les émissions par vol (sera enrichie plus tard)
CREATE VIEW analytics.v_vols_summary AS
SELECT 
    v.numero_vol,
    v.date_vol,
    c.nom_compagnie,
    at.constructeur || ' ' || at.modele AS type_avion,
    aorg.code_iata AS origine,
    adest.code_iata AS destination,
    v.nb_passagers,
    v.statut_vol,
    COUNT(pv.id_phase) AS nb_phases
FROM airport.vol v
LEFT JOIN airport.compagnie c ON v.id_compagnie = c.id_compagnie
LEFT JOIN airport.aeronef_type at ON v.id_type_aeronef = at.id_type_aeronef
LEFT JOIN airport.aeroport aorg ON v.id_aeroport_origine = aorg.id_aeroport
LEFT JOIN airport.aeroport adest ON v.id_aeroport_destination = adest.id_aeroport
LEFT JOIN airport.phase_vol pv ON v.id_vol = pv.id_vol
GROUP BY 
    v.id_vol, v.numero_vol, v.date_vol, c.nom_compagnie, 
    at.constructeur, at.modele, aorg.code_iata, adest.code_iata, 
    v.nb_passagers, v.statut_vol;

-- =====================================================
-- 6. DONNÉES INITIALES DE TEST
-- =====================================================

-- Insertion d'un aéroport fictif "Paris-Val d'Europe"
INSERT INTO airport.aeroport (
    code_iata, code_icao, nom_aeroport, ville, pays, 
    coordonnees_gps, altitude_m, fuseau_horaire
) VALUES (
    'PVE', 'LPVE', 'Paris-Val d''Europe Airport', 
    'Marne-la-Vallée', 'FRA',
    ST_GeomFromText('POINT(2.786 48.881)', 4326),
    104, 'Europe/Paris'
);

-- Récupération de l'ID de l'aéroport pour les relations
-- Cette partie sera développée dans les prochaines migrations

-- =====================================================
-- FIN MIGRATION V001
-- =====================================================

-- Log de la migration
DO $$
BEGIN
    RAISE NOTICE 'Migration V001 appliquée avec succès - Schéma initial créé';
END $$;