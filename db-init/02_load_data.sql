-- 02_load_data.sql : chargement des CSV dans les 7 tables

-------------------------
-- 1) tables *_raw
-------------------------

TRUNCATE TABLE patients_raw;

COPY patients_raw (
    patient_id,
    name,
    age,
    arrival_date,
    departure_date,
    service,
    satisfaction,
    adresse_postale,
    code_postal,
    genre,
    date_naissance,
    telephone,
    email,
    numero_dossier_medical
)
FROM '/data/patients.csv'
DELIMITER ','
CSV HEADER;


TRUNCATE TABLE staff_raw;

COPY staff_raw (
    staff_id,
    staff_name,
    role,
    service,
    adresse_postale,
    code_postal,
    genre,
    date_naissance,
    age,
    telephone,
    email,
    departement
)
FROM '/data/enriched_staff.csv'
DELIMITER ','
CSV HEADER;


TRUNCATE TABLE consultations_raw;

COPY consultations_raw (
    patientid,
    staffid,
    consultationdate,
    consultationtime,
    description
)
FROM '/data/consultations.csv'
DELIMITER ','
CSV HEADER;


TRUNCATE TABLE staff_schedule_raw;

COPY staff_schedule_raw (
    week,
    staff_id,
    staff_name,
    role,
    service,
    present
)
FROM '/data/staff_schedule.csv'
DELIMITER ','
CSV HEADER;


TRUNCATE TABLE services_weekly_raw;

COPY services_weekly_raw (
    week,
    month,
    service,
    availablebeds,
    patientsrequest,
    patientsadmitted,
    patientsrefused,
    patientsatisfaction,
    staffmorale,
    event
)
FROM '/data/services_weekly.csv'
DELIMITER ','
CSV HEADER;


-------------------------
-- 2) validation_history
-------------------------

TRUNCATE TABLE validation_history;

COPY validation_history (
    table_name,
    column_name,
    run_date,
    pilier,
    rule_name,
    checks_passed,
    checks_failed,
    success_rate,
    error_type,
    total_expectations
)
FROM '/data/validation_history.csv'
DELIMITER ','
CSV HEADER;


-----------------------------------
-- 3) superset_validation_metrics
-----------------------------------

-- Problème de départ :
--   - Le CSV superset_validation_metrics.csv contient une colonne "%_succès"
--     avec des valeurs texte comme "100.00%".
--   - Dans la table finale superset_validation_metrics, on veut une colonne
--     numérique pct_succes NUMERIC(6,2) (par ex. 100.00).
--   - PostgreSQL ne peut pas copier directement "100.00%" dans un NUMERIC :
--     il faut d'abord enlever le symbole % et convertir en nombre.
--
-- Solution :
--   1) On crée une table RAW (superset_validation_metrics_raw) qui a
--      exactement les mêmes noms de colonnes que le CSV, y compris
--      "règle" et "%_succès", et on stocke "%_succès" en TEXT.
--   2) On fait un COPY du CSV vers cette table RAW sans transformation.
--   3) On insère ensuite dans la table finale superset_validation_metrics
--      en :
--          - renommant les colonnes (table -> table_name, "règle" -> regle),
--          - nettoyant "%_succès" avec REPLACE(..., '%', '')::NUMERIC
--            pour remplir pct_succes.

DROP TABLE IF EXISTS superset_validation_metrics_raw;
DROP TABLE IF EXISTS superset_validation_metrics_raw;

CREATE TABLE superset_validation_metrics_raw (
    table_name      TEXT,
    pilier          TEXT,
    regle_raw       TEXT,
    colonne         TEXT,
    date_run_raw    TEXT,
    passed_raw      TEXT,
    failed_raw      TEXT,
    pct_succes_raw  TEXT,
    erreurs         TEXT
);

TRUNCATE TABLE superset_validation_metrics;

COPY superset_validation_metrics_raw
FROM '/data/superset_validation_metrics.csv'
DELIMITER ','
CSV HEADER;

INSERT INTO superset_validation_metrics (
    table_name,
    pilier,
    regle,
    colonne,
    date_run,
    passed,
    failed,
    pct_succes,
    erreurs
)
SELECT
    table_name,
    pilier,
    regle_raw,
    colonne,
    date_run_raw::timestamp,
    passed_raw::bigint,
    failed_raw::bigint,
    REPLACE(pct_succes_raw, '%', '')::NUMERIC,
    erreurs
FROM superset_validation_metrics_raw;