-- =====================================================
-- Migration V003: Système de modélisation acoustique
-- Description: Tables et fonctions pour calculs de bruit aéronautique
-- Auteur: Portfolio Project - Module Acoustique
-- Date: 2025-08-15
-- =====================================================

-- =====================================================
-- 1. EXTENSION DU SCHÉMA POUR L'ACOUSTIQUE
-- =====================================================

-- Nouveau schéma dédié à l'acoustique
CREATE SCHEMA IF NOT EXISTS acoustique;

-- =====================================================
-- 2. CARACTÉRISTIQUES ACOUSTIQUES DES AÉRONEFS
-- =====================================================

-- Table des profils acoustiques par type d'aéronef
CREATE TABLE acoustique.profil_acoustique_aeronef (
    id_profil_acoustique UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_type_aeronef UUID NOT NULL REFERENCES airport.aeronef_type(id_type_aeronef) ON DELETE CASCADE,
    
    -- Certification acoustique
    chapitre_bruit VARCHAR(20) NOT NULL, -- Chapter 3, 4, 14 (OACI Annexe 16)
    niveau_certification_epndb NUMERIC(5,2), -- Niveau certifié en EPNdB
    marge_cumulative_epndb NUMERIC(5,2), -- Marge par rapport aux limites
    
    -- Niveaux de bruit par phase (dB(A) à distance de référence)
    -- Distance de référence : 1000m, conditions standards
    bruit_taxi_dba NUMERIC(5,2) DEFAULT 65.0,
    bruit_decollage_dba NUMERIC(5,2) NOT NULL,
    bruit_montee_dba NUMERIC(5,2) NOT NULL,
    bruit_approche_dba NUMERIC(5,2) NOT NULL,
    bruit_atterrissage_dba NUMERIC(5,2) NOT NULL,
    
    -- Caractéristiques fréquentielles (pour modélisation avancée)
    frequence_dominante_hz INTEGER DEFAULT 1000,
    largeur_bande_hz INTEGER DEFAULT 500,
    
    -- Paramètres de propagation
    coefficient_attenuation NUMERIC(6,4) DEFAULT 0.0050, -- dB/100m
    facteur_directivite NUMERIC(4,2) DEFAULT 1.0,
    
    -- Métadonnées certification
    organisme_certification VARCHAR(50) DEFAULT 'EASA',
    date_certification DATE,
    norme_mesure VARCHAR(50) DEFAULT 'OACI Annexe 16 Volume I',
    
    -- Validité et traçabilité
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_actif BOOLEAN DEFAULT TRUE,
    commentaires TEXT,
    
    -- Contraintes métier
    CONSTRAINT chk_chapitre_bruit CHECK (chapitre_bruit IN ('Chapter 2', 'Chapter 3', 'Chapter 4', 'Chapter 14')),
    CONSTRAINT chk_niveaux_realistes CHECK (
        bruit_decollage_dba BETWEEN 70 AND 120 AND
        bruit_montee_dba BETWEEN 65 AND 115 AND
        bruit_approche_dba BETWEEN 60 AND 110 AND
        bruit_atterrissage_dba BETWEEN 60 AND 105
    ),
    CONSTRAINT chk_frequence_valide CHECK (frequence_dominante_hz BETWEEN 50 AND 10000)
);

-- Index pour recherches fréquentes
CREATE INDEX idx_profil_acoustique_aeronef ON acoustique.profil_acoustique_aeronef(id_type_aeronef);
CREATE INDEX idx_profil_chapitre ON acoustique.profil_acoustique_aeronef(chapitre_bruit);

-- =====================================================
-- 3. STATIONS DE MESURE ACOUSTIQUE
-- =====================================================

CREATE TABLE acoustique.station_mesure_bruit (
    id_station_bruit UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_aeroport UUID NOT NULL REFERENCES airport.aeroport(id_aeroport) ON DELETE CASCADE,
    
    -- Identification
    code_station VARCHAR(20) NOT NULL,
    nom_station VARCHAR(100) NOT NULL,
    adresse_complete TEXT,
    
    -- Localisation précise
    coordonnees_gps GEOMETRY(POINT, 4326) NOT NULL,
    altitude_m INTEGER NOT NULL,
    hauteur_microphone_m NUMERIC(4,2) DEFAULT 4.0,
    
    -- Type de station et environnement
    type_station VARCHAR(30) DEFAULT 'Automatique',
    environnement_sonore VARCHAR(50), -- Résidentiel, Commercial, Industriel, Rural
    zone_reglementaire VARCHAR(10), -- A, B, C (PEB), ou Hors zone
    
    -- Équipement technique
    modele_sonometre VARCHAR(100),
    classe_precision INTEGER DEFAULT 1, -- Classe 1 ou 2 selon IEC 61672
    frequence_echantillonnage_hz INTEGER DEFAULT 48000,
    
    -- Paramètres de mesure
    seuil_declenchement_dba NUMERIC(4,1) DEFAULT 55.0,
    duree_integration_s INTEGER DEFAULT 1,
    filtre_frequentiel VARCHAR(20) DEFAULT 'A', -- A, C, Z (linéaire)
    
    -- Calibration et maintenance
    date_installation DATE DEFAULT CURRENT_DATE,
    date_derniere_calibration TIMESTAMP,
    periodicite_calibration_jours INTEGER DEFAULT 30,
    
    -- Population et enjeux
    nb_habitants_zone INTEGER DEFAULT 0,
    etablissements_sensibles TEXT[], -- École, Hôpital, Maison retraite
    
    -- Statut opérationnel
    statut_operationnel BOOLEAN DEFAULT TRUE,
    date_debut_service DATE DEFAULT CURRENT_DATE,
    date_fin_service DATE,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT chk_classe_precision CHECK (classe_precision IN (1, 2)),
    CONSTRAINT chk_filtre_freq CHECK (filtre_frequentiel IN ('A', 'C', 'Z')),
    CONSTRAINT chk_seuil_realiste CHECK (seuil_declenchement_dba BETWEEN 30 AND 80),
    UNIQUE(id_aeroport, code_station)
);

-- Index géospatial et opérationnels
CREATE INDEX idx_station_bruit_geom ON acoustique.station_mesure_bruit USING GIST (coordonnees_gps);
CREATE INDEX idx_station_bruit_aeroport ON acoustique.station_mesure_bruit(id_aeroport);
CREATE INDEX idx_station_zone_regl ON acoustique.station_mesure_bruit(zone_reglementaire);

-- =====================================================
-- 4. MESURES ACOUSTIQUES EN CONTINU
-- =====================================================

CREATE TABLE acoustique.mesure_bruit (
    id_mesure_bruit UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_station_bruit UUID NOT NULL REFERENCES acoustique.station_mesure_bruit(id_station_bruit) ON DELETE CASCADE,
    
    -- Temporalité
    timestamp_mesure TIMESTAMP NOT NULL,
    duree_evenement_s NUMERIC(6,2), -- Durée de l'événement sonore détecté
    
    -- Indicateurs acoustiques principaux
    lamax_dba NUMERIC(5,2) NOT NULL, -- Niveau maximum de l'événement
    laeq_dba NUMERIC(5,2), -- Niveau équivalent sur la durée
    la10_dba NUMERIC(5,2), -- Niveau dépassé 10% du temps
    la90_dba NUMERIC(5,2), -- Niveau de bruit de fond
    
    -- Indicateurs pondérés temporellement (pour calculs réglementaires)
    lden_contribution_dba NUMERIC(5,2), -- Contribution à l'indicateur Lden
    ln_contribution_dba NUMERIC(5,2), -- Contribution à l'indicateur Lnight
    
    -- Analyse fréquentielle (optionnelle)
    niveau_63hz_db NUMERIC(5,2), -- Bandes d'octave pour signature spectrale
    niveau_125hz_db NUMERIC(5,2),
    niveau_250hz_db NUMERIC(5,2),
    niveau_500hz_db NUMERIC(5,2),
    niveau_1000hz_db NUMERIC(5,2),
    niveau_2000hz_db NUMERIC(5,2),
    niveau_4000hz_db NUMERIC(5,2),
    niveau_8000hz_db NUMERIC(5,2),
    
    -- Corrélation avec trafic aérien
    id_vol_correlé UUID REFERENCES airport.vol(id_vol), -- Vol potentiellement responsable
    correlation_certitude NUMERIC(3,2), -- Niveau de certitude de la corrélation (0-1)
    azimut_source_deg INTEGER, -- Direction estimée de la source sonore
    distance_estimee_m INTEGER, -- Distance estimée de la source
    
    -- Conditions météorologiques
    vitesse_vent_ms NUMERIC(4,2),
    direction_vent_deg INTEGER,
    temperature_c NUMERIC(4,2),
    humidite_percent INTEGER,
    pression_hpa NUMERIC(6,2),
    
    -- Qualité de la mesure
    validite_mesure VARCHAR(20) DEFAULT 'Valide',
    code_qualite INTEGER DEFAULT 1, -- 1=Excellent, 2=Bon, 3=Moyen, 9=Invalide
    masquage_bruit_fond BOOLEAN DEFAULT FALSE, -- Événement masqué par bruit de fond
    
    -- Classification automatique
    type_evenement VARCHAR(30), -- Aéronef, Route, Train, Autres, Indéterminé
    confiance_classification NUMERIC(3,2), -- Niveau de confiance classification auto
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_donnees VARCHAR(50) DEFAULT 'STATION_AUTO',
    
    -- Contraintes de cohérence
    CONSTRAINT chk_niveaux_coherents CHECK (
        lamax_dba >= laeq_dba AND 
        la10_dba >= la90_dba AND
        lamax_dba >= la10_dba
    ),
    CONSTRAINT chk_validite_mesure CHECK (validite_mesure IN ('Valide', 'Douteux', 'Invalide', 'En_cours')),
    CONSTRAINT chk_correlation_valide CHECK (correlation_certitude BETWEEN 0 AND 1),
    CONSTRAINT chk_azimut_valide CHECK (azimut_source_deg BETWEEN 0 AND 360)
);

-- Index pour performances (partitioning par mois recommandé en production)
CREATE INDEX idx_mesure_bruit_station_time ON acoustique.mesure_bruit(id_station_bruit, timestamp_mesure);
CREATE INDEX idx_mesure_bruit_lamax ON acoustique.mesure_bruit(lamax_dba);
CREATE INDEX idx_mesure_bruit_vol ON acoustique.mesure_bruit(id_vol_correlé) WHERE id_vol_correlé IS NOT NULL;
CREATE INDEX idx_mesure_bruit_type ON acoustique.mesure_bruit(type_evenement);

-- =====================================================
-- 5. ZONES RÉGLEMENTAIRES ET CARTOGRAPHIE
-- =====================================================

-- Zones du Plan d'Exposition au Bruit (PEB)
CREATE TABLE acoustique.zone_exposition_bruit (
    id_zone UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_aeroport UUID NOT NULL REFERENCES airport.aeroport(id_aeroport) ON DELETE CASCADE,
    
    -- Classification réglementaire
    zone_peb VARCHAR(10) NOT NULL, -- A, B, C (selon arrêté préfectoral)
    niveau_exposition_lden_db NUMERIC(4,1) NOT NULL, -- Seuil de la zone (55, 60, 65 dB)
    niveau_exposition_ln_db NUMERIC(4,1), -- Seuil nuit si différent
    
    -- Géométrie de la zone
    geometrie_zone GEOMETRY(POLYGON, 4326) NOT NULL,
    surface_hectares NUMERIC(10,2),
    
    -- Données socio-économiques
    population_estimee INTEGER DEFAULT 0,
    nb_logements INTEGER DEFAULT 0,
    nb_etablissements_sensibles INTEGER DEFAULT 0, -- Écoles, hôpitaux, etc.
    
    -- Réglementation applicable
    arrete_prefectoral_reference VARCHAR(100),
    date_creation_peb DATE,
    date_derniere_revision DATE,
    
    -- Restrictions d'urbanisme
    constructibilite_autorisee BOOLEAN DEFAULT FALSE,
    conditions_constructibilite TEXT,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_actif BOOLEAN DEFAULT TRUE,
    
    -- Contraintes
    CONSTRAINT chk_zone_peb CHECK (zone_peb IN ('A', 'B', 'C', 'D')),
    CONSTRAINT chk_niveau_realiste CHECK (niveau_exposition_lden_db BETWEEN 45 AND 80),
    UNIQUE(id_aeroport, zone_peb)
);

-- Index géospatiaux pour cartographie
CREATE INDEX idx_zone_exposition_geom ON acoustique.zone_exposition_bruit USING GIST (geometrie_zone);
CREATE INDEX idx_zone_exposition_aeroport ON acoustique.zone_exposition_bruit(id_aeroport);
CREATE INDEX idx_zone_niveau ON acoustique.zone_exposition_bruit(niveau_exposition_lden_db);

-- =====================================================
-- 6. CALCULS D'EMPREINTE ACOUSTIQUE
-- =====================================================

CREATE TABLE acoustique.empreinte_acoustique_calculee (
    id_empreinte UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Référence au vol source
    id_vol UUID NOT NULL REFERENCES airport.vol(id_vol) ON DELETE CASCADE,
    id_phase_vol UUID REFERENCES airport.phase_vol(id_phase) ON DELETE CASCADE,
    
    -- Point de calcul
    point_calcul GEOMETRY(POINT, 4326) NOT NULL,
    distance_source_m NUMERIC(8,2) NOT NULL,
    azimut_deg NUMERIC(5,2),
    
    -- Résultats de modélisation
    niveau_bruit_dba NUMERIC(5,2) NOT NULL,
    niveau_bruit_dbc NUMERIC(5,2), -- Pondération C pour basses fréquences
    sel_db NUMERIC(5,2), -- Sound Exposure Level
    
    -- Paramètres de calcul
    modele_propagation VARCHAR(50) DEFAULT 'ECAC_DOC29',
    version_modele VARCHAR(20) DEFAULT '4.0',
    
    -- Conditions de calcul
    temperature_calcul_c NUMERIC(4,2) DEFAULT 15.0,
    humidite_calcul_percent INTEGER DEFAULT 70,
    absorption_atmospherique_db NUMERIC(4,2) DEFAULT 0.0,
    
    -- Corrections appliquées
    correction_vent_db NUMERIC(4,2) DEFAULT 0.0,
    correction_sol_db NUMERIC(4,2) DEFAULT 0.0,
    correction_obstacles_db NUMERIC(4,2) DEFAULT 0.0,
    correction_directivite_db NUMERIC(4,2) DEFAULT 0.0,
    
    -- Métadonnées de calcul
    timestamp_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    methode_calcul VARCHAR(50) DEFAULT 'ECAC_DOC29_4ED',
    precision_estimee_db NUMERIC(3,1) DEFAULT 2.0,
    
    -- Contraintes
    CONSTRAINT chk_distance_positive CHECK (distance_source_m > 0),
    CONSTRAINT chk_niveau_realiste CHECK (niveau_bruit_dba BETWEEN 20 AND 140),
    CONSTRAINT chk_azimut_valide CHECK (azimut_deg BETWEEN 0 AND 360)
);

-- Index pour requêtes spatiales et temporelles
CREATE INDEX idx_empreinte_vol ON acoustique.empreinte_acoustique_calculee(id_vol);
CREATE INDEX idx_empreinte_geom ON acoustique.empreinte_acoustique_calculee USING GIST (point_calcul);
CREATE INDEX idx_empreinte_niveau ON acoustique.empreinte_acoustique_calculee(niveau_bruit_dba);

-- =====================================================
-- 7. FONCTIONS DE CALCUL ACOUSTIQUE
-- =====================================================

-- Fonction de calcul de l'atténuation par la distance
CREATE OR REPLACE FUNCTION acoustique.calculer_attenuation_distance(
    niveau_source_db NUMERIC,
    distance_m NUMERIC,
    distance_reference_m NUMERIC DEFAULT 1000
) RETURNS NUMERIC AS $$
BEGIN
    -- Loi de l'inverse du carré de la distance (champ libre)
    -- Atténuation = 20 * log10(distance / distance_référence)
    IF distance_m <= 0 OR distance_reference_m <= 0 THEN
        RETURN NULL;
    END IF;
    
    RETURN niveau_source_db - 20 * LOG10(distance_m / distance_reference_m);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Fonction de calcul de l'absorption atmosphérique
CREATE OR REPLACE FUNCTION acoustique.calculer_absorption_atmospherique(
    distance_m NUMERIC,
    frequence_hz INTEGER DEFAULT 1000,
    temperature_c NUMERIC DEFAULT 15.0,
    humidite_percent INTEGER DEFAULT 70
) RETURNS NUMERIC AS $$
DECLARE
    coefficient_absorption NUMERIC;
BEGIN
    -- Calcul simplifié basé sur ISO 9613-1
    -- Coefficient d'absorption en dB/km selon fréquence et conditions
    CASE 
        WHEN frequence_hz <= 250 THEN coefficient_absorption := 0.1;
        WHEN frequence_hz <= 500 THEN coefficient_absorption := 0.2;
        WHEN frequence_hz <= 1000 THEN coefficient_absorption := 0.5;
        WHEN frequence_hz <= 2000 THEN coefficient_absorption := 1.0;
        WHEN frequence_hz <= 4000 THEN coefficient_absorption := 2.0;
        ELSE coefficient_absorption := 4.0;
    END CASE;
    
    -- Correction température et humidité (simplifiée)
    coefficient_absorption := coefficient_absorption * 
        (1 + (temperature_c - 15) * 0.01) * 
        (1 + ABS(humidite_percent - 70) * 0.002);
    
    RETURN coefficient_absorption * distance_m / 1000;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Fonction principale de calcul d'empreinte acoustique
CREATE OR REPLACE FUNCTION acoustique.calculer_empreinte_vol(
    p_id_vol UUID,
    p_point_calcul GEOMETRY,
    p_conditions_meteo JSONB DEFAULT '{"temperature": 15, "humidite": 70, "vent": 0}'::JSONB
) RETURNS TABLE (
    phase_vol VARCHAR(20),
    niveau_bruit_dba NUMERIC,
    distance_m NUMERIC,
    sel_db NUMERIC
) AS $$
DECLARE
    vol_record RECORD;
    aeronef_record RECORD;
    phase_record RECORD;
    profil_acoustique RECORD;
    distance_calculee NUMERIC;
    niveau_source NUMERIC;
    niveau_final NUMERIC;
    attenuation_distance NUMERIC;
    absorption_atmo NUMERIC;
BEGIN
    -- Récupération des informations du vol
    SELECT INTO vol_record *
    FROM airport.vol v
    JOIN airport.aeronef_type at ON v.id_type_aeronef = at.id_type_aeronef
    WHERE v.id_vol = p_id_vol;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Vol non trouvé: %', p_id_vol;
    END IF;
    
    -- Récupération du profil acoustique de l'aéronef
    SELECT INTO profil_acoustique *
    FROM acoustique.profil_acoustique_aeronef
    WHERE id_type_aeronef = vol_record.id_type_aeronef
    AND statut_actif = TRUE;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Profil acoustique non trouvé pour aéronef: %', vol_record.designation_icao;
    END IF;
    
    -- Calcul pour chaque phase du vol
    FOR phase_record IN 
        SELECT * FROM airport.phase_vol 
        WHERE id_vol = p_id_vol 
        ORDER BY 
            CASE type_phase
                WHEN 'Taxi-out' THEN 1
                WHEN 'Take-off' THEN 2
                WHEN 'Climb-out' THEN 3
                WHEN 'Approach' THEN 4
                WHEN 'Landing' THEN 5
                WHEN 'Taxi-in' THEN 6
                ELSE 7
            END
    LOOP
        -- Distance entre position phase et point de calcul
        IF phase_record.position_gps IS NOT NULL THEN
            distance_calculee := ST_Distance(
                ST_Transform(phase_record.position_gps, 3857), -- Web Mercator pour calcul métrique
                ST_Transform(p_point_calcul, 3857)
            );
        ELSE
            -- Position par défaut : centre aéroport
            SELECT ST_Distance(
                ST_Transform(coordonnees_gps, 3857),
                ST_Transform(p_point_calcul, 3857)
            ) INTO distance_calculee
            FROM airport.aeroport a
            JOIN airport.vol v ON a.id_aeroport IN (v.id_aeroport_origine, v.id_aeroport_destination)
            WHERE v.id_vol = p_id_vol
            LIMIT 1;
        END IF;
        
        -- Niveau source selon la phase
        CASE phase_record.type_phase
            WHEN 'Taxi-out', 'Taxi-in' THEN 
                niveau_source := profil_acoustique.bruit_taxi_dba;
            WHEN 'Take-off' THEN 
                niveau_source := profil_acoustique.bruit_decollage_dba;
            WHEN 'Climb-out' THEN 
                niveau_source := profil_acoustique.bruit_montee_dba;
            WHEN 'Approach' THEN 
                niveau_source := profil_acoustique.bruit_approche_dba;
            WHEN 'Landing' THEN 
                niveau_source := profil_acoustique.bruit_atterrissage_dba;
            ELSE 
                niveau_source := profil_acoustique.bruit_taxi_dba;
        END CASE;
        
        -- Calculs d'atténuation
        attenuation_distance := acoustique.calculer_attenuation_distance(
            niveau_source, distance_calculee, 1000
        );
        
        absorption_atmo := acoustique.calculer_absorption_atmospherique(
            distance_calculee,
            profil_acoustique.frequence_dominante_hz,
            (p_conditions_meteo->>'temperature')::NUMERIC,
            (p_conditions_meteo->>'humidite')::INTEGER
        );
        
        niveau_final := niveau_source - (attenuation_distance + absorption_atmo);
        
        -- Calcul SEL (Sound Exposure Level)
        -- SEL = LAmax + 10*log10(durée_événement/1s)
        
        RETURN QUERY SELECT 
            phase_record.type_phase,
            ROUND(niveau_final, 1),
            ROUND(distance_calculee, 1),
            ROUND(niveau_final + 10 * LOG10(GREATEST(phase_record.duree_minutes * 60, 1)), 1);
            
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. VUES POUR L'ANALYSE ACOUSTIQUE
-- =====================================================

-- Vue des événements acoustiques corrélés au trafic aérien
CREATE OR REPLACE VIEW acoustique.v_evenements_aeronautiques AS
SELECT 
    mb.timestamp_mesure,
    mb.lamax_dba,
    mb.laeq_dba,
    mb.duree_evenement_s,
    smb.nom_station,
    smb.zone_reglementaire,
    smb.environnement_sonore,
    v.numero_vol,
    c.nom_compagnie,
    at.designation_icao,
    pv.type_phase,
    mb.correlation_certitude,
    mb.distance_estimee_m,
    -- Calcul contribution journalière Lden
    CASE 
        WHEN EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 6 AND 18 THEN mb.laeq_dba -- Jour
        WHEN EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 18 AND 22 THEN mb.laeq_dba + 5 -- Soirée
        ELSE mb.laeq_dba + 10 -- Nuit
    END as contribution_lden_dba,
    -- Classification période réglementaire
    CASE 
        WHEN EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 6 AND 18 THEN 'Jour'
        WHEN EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 18 AND 22 THEN 'Soirée'
        ELSE 'Nuit'
    END as periode_reglementaire
FROM acoustique.mesure_bruit mb
JOIN acoustique.station_mesure_bruit smb ON mb.id_station_bruit = smb.id_station_bruit
LEFT JOIN airport.vol v ON mb.id_vol_correlé = v.id_vol
LEFT JOIN airport.compagnie c ON v.id_compagnie = c.id_compagnie
LEFT JOIN airport.aeronef_type at ON v.id_type_aeronef = at.id_type_aeronef
LEFT JOIN airport.phase_vol pv ON v.id_vol = pv.id_vol
WHERE mb.type_evenement = 'Aéronef'
  AND mb.validite_mesure = 'Valide';

-- Vue des indicateurs réglementaires par station
CREATE OR REPLACE VIEW acoustique.v_indicateurs_reglementaires_station AS
SELECT 
    smb.code_station,
    smb.nom_station,
    smb.zone_reglementaire,
    smb.environnement_sonore,
    DATE(mb.timestamp_mesure) as date_mesure,
    
    -- Calcul Lden (indicateur jour-soirée-nuit)
    ROUND(10 * LOG10(
        (12 * POWER(10, AVG(CASE WHEN EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 6 AND 18 
                                 THEN mb.laeq_dba ELSE NULL END) / 10)) +
        (4 * POWER(10, (AVG(CASE WHEN EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 18 AND 22 
                             THEN mb.laeq_dba ELSE NULL END) + 5) / 10)) +
        (8 * POWER(10, (AVG(CASE WHEN EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 22 AND 24 
                             OR EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 0 AND 6
                             THEN mb.laeq_dba ELSE NULL END) + 10) / 10))
    ) / 24), 1) as lden_dba,
    
    -- Calcul Lnight (indicateur nuit 22h-6h)
    ROUND(AVG(CASE WHEN EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 22 AND 24 
                   OR EXTRACT(hour FROM mb.timestamp_mesure) BETWEEN 0 AND 6
                   THEN mb.laeq_dba ELSE NULL END), 1) as lnight_dba,
    
    -- Statistiques complémentaires
    COUNT(*) as nb_evenements,
    COUNT(CASE WHEN mb.type_evenement = 'Aéronef' THEN 1 END) as nb_evenements_aeriens,
    MAX(mb.lamax_dba) as lamax_max_dba,
    
    -- Évaluation conformité (seuils indicatifs)
    CASE 
        WHEN smb.zone_reglementaire = 'A' THEN 'Zone forte exposition (>65 dB Lden)'
        WHEN smb.zone_reglementaire = 'B' THEN 'Zone exposition modérée (60-65 dB Lden)'
        WHEN smb.zone_reglementaire = 'C' THEN 'Zone exposition faible (55-60 dB Lden)'
        ELSE 'Hors zone réglementaire'
    END as classification_exposition
    
FROM acoustique.mesure_bruit mb
JOIN acoustique.station_mesure_bruit smb ON mb.id_station_bruit = smb.id_station_bruit
WHERE mb.validite_mesure = 'Valide'
GROUP BY smb.code_station, smb.nom_station, smb.zone_reglementaire, 
         smb.environnement_sonore, DATE(mb.timestamp_mesure);

-- =====================================================
-- 9. TRIGGERS ET FONCTIONS UTILITAIRES
-- =====================================================

-- Trigger pour mise à jour automatique des timestamps
CREATE TRIGGER trg_profil_acoustique_modified
    BEFORE UPDATE ON acoustique.profil_acoustique_aeronef
    FOR EACH ROW EXECUTE FUNCTION update_modified_timestamp();

CREATE TRIGGER trg_station_bruit_modified
    BEFORE UPDATE ON acoustique.station_mesure_bruit
    FOR EACH ROW EXECUTE FUNCTION update_modified_timestamp();

CREATE TRIGGER trg_zone_exposition_modified
    BEFORE UPDATE ON acoustique.zone_exposition_bruit
    FOR EACH ROW EXECUTE FUNCTION update_modified_timestamp();

-- =====================================================
-- 10. DONNÉES D'EXEMPLE POUR LES PROFILS ACOUSTIQUES
-- =====================================================

-- Insertion des profils acoustiques pour les aéronefs existants
DO $$
DECLARE
    aeronef_record RECORD;
BEGIN
    -- Profils pour les aéronefs déjà présents
    FOR aeronef_record IN SELECT * FROM airport.aeronef_type LOOP
        
        -- Profil A320 (Chapter 4, moderne)
        IF aeronef_record.designation_icao = 'A320' THEN
            INSERT INTO acoustique.profil_acoustique_aeronef (
                id_type_aeronef, chapitre_bruit, niveau_certification_epndb, marge_cumulative_epndb,
                bruit_decollage_dba, bruit_montee_dba, bruit_approche_dba, bruit_atterrissage_dba,
                frequence_dominante_hz, organisme_certification, date_certification
            ) VALUES (
                aeronef_record.id_type_aeronef, 'Chapter 4', 89.2, 11.8,
                85.3, 78.9, 76.4, 73.2,
                1000, 'EASA', '2010-03-15'
            );
            
        -- Profil B737-800 (Chapter 4)
        ELSIF aeronef_record.designation_icao = 'B738' THEN
            INSERT INTO acoustique.profil_acoustique_aeronef (
                id_type_aeronef, chapitre_bruit, niveau_certification_epndb, marge_cumulative_epndb,
                bruit_decollage_dba, bruit_montee_dba, bruit_approche_dba, bruit_atterrissage_dba,
                frequence_dominante_hz, organisme_certification, date_certification
            ) VALUES (
                aeronef_record.id_type_aeronef, 'Chapter 4', 88.7, 12.3,
                86.1, 79.5, 77.0, 74.1,
                1100, 'FAA', '2008-11-22'
            );
            
        -- Profil A330 (Chapter 4, plus gros)
        ELSIF aeronef_record.designation_icao = 'A333' THEN
            INSERT INTO acoustique.profil_acoustique_aeronef (
                id_type_aeronef, chapitre_bruit, niveau_certification_epndb, marge_cumulative_epndb,
                bruit_decollage_dba, bruit_montee_dba, bruit_approche_dba, bruit_atterrissage_dba,
                frequence_dominante_hz, organisme_certification, date_certification
            ) VALUES (
                aeronef_record.id_type_aeronef, 'Chapter 4', 92.8, 8.2,
                89.7, 82.3, 79.8, 76.5,
                900, 'EASA', '2005-06-10'
            );
            
        END IF;
    END LOOP;
    
    RAISE NOTICE 'Profils acoustiques initialisés pour les aéronefs existants';
END $$;

-- =====================================================
-- 11. COMMENTAIRES ET DOCUMENTATION
-- =====================================================

COMMENT ON SCHEMA acoustique IS 'Schéma dédié à la modélisation et surveillance acoustique aéronautique';

COMMENT ON TABLE acoustique.profil_acoustique_aeronef IS 'Caractéristiques acoustiques certifiées par type d''aéronef selon OACI Annexe 16';
COMMENT ON TABLE acoustique.station_mesure_bruit IS 'Réseau de stations de mesure acoustique automatique autour de l''aéroport';
COMMENT ON TABLE acoustique.mesure_bruit IS 'Mesures acoustiques en continu avec corrélation trafic aérien';
COMMENT ON TABLE acoustique.zone_exposition_bruit IS 'Zones du Plan d''Exposition au Bruit (PEB) selon réglementation française';
COMMENT ON TABLE acoustique.empreinte_acoustique_calculee IS 'Résultats de modélisation d''empreinte acoustique par vol';

COMMENT ON FUNCTION acoustique.calculer_empreinte_vol IS 'Calcul de l''empreinte acoustique complète d''un vol selon méthode ECAC Doc 29';
COMMENT ON VIEW acoustique.v_evenements_aeronautiques IS 'Événements acoustiques corrélés au trafic aérien avec indicateurs réglementaires';
COMMENT ON VIEW acoustique.v_indicateurs_reglementaires_station IS 'Indicateurs Lden et Lnight par station selon réglementation européenne';

-- =====================================================
-- FIN MIGRATION V003 - SYSTÈME ACOUSTIQUE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Migration V003 appliquée avec succès - Système de modélisation acoustique créé';
    RAISE NOTICE 'Tables créées: profil_acoustique_aeronef, station_mesure_bruit, mesure_bruit, zone_exposition_bruit, empreinte_acoustique_calculee';
    RAISE NOTICE 'Fonctions créées: calculer_attenuation_distance, calculer_absorption_atmospherique, calculer_empreinte_vol';
    RAISE NOTICE 'Vues créées: v_evenements_aeronautiques, v_indicateurs_reglementaires_station';
    RAISE NOTICE 'Profils acoustiques initialisés pour A320, B738, A333';
END $$;