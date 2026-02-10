-- 01_schema.sql : création des tables brutes + tables de validation

-----------------------
-- Tables *_raw
-----------------------

CREATE TABLE IF NOT EXISTS patients_raw (
    patient_id TEXT,
    name TEXT,
    age FLOAT,
    arrival_date DATE,
    departure_date DATE,
    service TEXT,
    satisfaction FLOAT,
    adresse_postale TEXT,
    code_postal TEXT,
    genre TEXT,
    date_naissance DATE,
    telephone TEXT,
    email TEXT,
    numero_dossier_medical TEXT
);

CREATE TABLE IF NOT EXISTS staff_raw (
    staff_id TEXT,
    staff_name TEXT,
    role TEXT,
    service TEXT,
    adresse_postale TEXT,
    code_postal TEXT,
    genre TEXT,
    date_naissance DATE,
    age FLOAT,
    telephone TEXT,
    email TEXT,
    departement TEXT
);

CREATE TABLE IF NOT EXISTS consultations_raw (
    patientid TEXT,
    staffid TEXT,
    consultationdate DATE,
    consultationtime TIME,
    description TEXT
);

CREATE TABLE IF NOT EXISTS staff_schedule_raw (
    week INTEGER,
    staff_id TEXT,
    staff_name TEXT,
    role TEXT,
    service TEXT,
    present INTEGER
);

CREATE TABLE IF NOT EXISTS services_weekly_raw (
    week INTEGER,
    month INTEGER,
    service TEXT,
    availablebeds INTEGER,
    patientsrequest INTEGER,
    patientsadmitted INTEGER,
    patientsrefused INTEGER,
    patientsatisfaction INTEGER,
    staffmorale INTEGER,
    event TEXT
);

-----------------------
-- Tables de validation
-----------------------

CREATE TABLE IF NOT EXISTS validation_history (
    id                 SERIAL PRIMARY KEY,
    table_name         VARCHAR(100)      NOT NULL,
    column_name        VARCHAR(200)      NOT NULL,
    run_date           TIMESTAMP         NOT NULL,
    pilier             VARCHAR(50)       NOT NULL,
    rule_name          VARCHAR(200)      NOT NULL,
    checks_passed      BIGINT            NOT NULL,
    checks_failed      BIGINT            NOT NULL,
    success_rate       NUMERIC(6,2)      NOT NULL,
    error_type         VARCHAR(200),
    total_expectations BIGINT
);

CREATE TABLE IF NOT EXISTS superset_validation_metrics (
    id         SERIAL PRIMARY KEY,
    table_name VARCHAR(100)     NOT NULL,
    pilier     VARCHAR(50)      NOT NULL,
    regle      VARCHAR(200)     NOT NULL,
    colonne    VARCHAR(200)     NOT NULL,
    date_run   TIMESTAMP        NOT NULL,
    passed     BIGINT           NOT NULL,
    failed     BIGINT           NOT NULL,
    pct_succes NUMERIC(6,2)     NOT NULL,
    erreurs    TEXT
);



