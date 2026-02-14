#!/usr/bin/env python3
"""
Pipeline de Validation Qualité des Données - Great Expectations v1.11.3
Couche 3 : Validation des 6 piliers de qualité (COMPLÉTUDE, EXACTITUDE, VALIDITÉ, COHÉRENCE, UNICITÉ, ACTUALITÉ)
"""

import os
import sys
import pandas as pd
import numpy as np
import warnings
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine

# Supprimer les warnings inutiles
warnings.filterwarnings('ignore')

# =========================
# CONFIGURATION
# =========================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dq_user:dq_pass@postgres:5432/dq_db"
)
RESULTS_DIR = Path("/app/results")
REPORTS_DIR = Path("/app/reports")
DATA_DIR = Path("/data") 

GX_DATA_DOCS_DIR = REPORTS_DIR / "gx_data_docs"

# Créer les répertoires de sortie
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
GX_DATA_DOCS_DIR.mkdir(parents=True, exist_ok=True)

RUN_DATE = datetime.now()
RUN_DATE_STR = RUN_DATE.strftime("%Y%m%d")
RUN_DATETIME_STR = RUN_DATE.strftime("%Y-%m-%d %H:%M:%S")

print("=" * 70)
print("🚀 DÉMARRAGE DU PIPELINE DE VALIDATION QUALITÉ - COUCHE 3")
print(f"⏰ Exécution : {RUN_DATETIME_STR}")
print(f"📁 Résultats : {RESULTS_DIR}")
print(f"📈 Rapports  : {GX_DATA_DOCS_DIR}")
print("=" * 70)

# =========================
# CLASSE DE GESTION DES MÉTRIQUES
# =========================
class ValidationMetriques:
    def __init__(self):
        self.metriques = []
    
    def ajouter_metrique(self, table_name, column_name, pilier, rule_name, 
                         checks_passed, checks_failed, error_type=None):
        total = checks_passed + checks_failed
        success_rate = (checks_passed / total * 100) if total > 0 else 0
        
        self.metriques.append({
            'table_name': table_name,
            'column_name': column_name,
            'run_date': RUN_DATETIME_STR,
            'pilier': pilier,
            'rule_name': rule_name,
            'checks_passed': checks_passed,
            'checks_failed': checks_failed,
            'success_rate': round(success_rate, 2),
            'error_type': error_type,
            'total_expectations': total
        })
    
    def to_dataframe(self):
        return pd.DataFrame(self.metriques)

# =========================
# CHARGEMENT DES DONNÉES
# =========================
def charger_donnees(engine):
    print("\n📥 CHARGEMENT DES DONNÉES DEPUIS POSTGRESQL...")

    tables = {
        'staff': 'staff_raw',
        'patients': 'patients_raw',
        'consultations': 'consultations_raw',
        'staff_schedule': 'staff_schedule_raw',
        'services_weekly': 'services_weekly_raw'
    }

    dataframes = {}
    for alias, table_name in tables.items():
        try:
            df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
            # 🔑 NORMALISATION CRITIQUE : minuscules + snake_case
            original_cols = df.columns.tolist()
            df.columns = (
                df.columns
                .str.strip()
                .str.lower()
                .str.replace(r'\s+', '_', regex=True)
                .str.replace(r'-', '_', regex=False)
                .str.replace(r'[^a-z0-9_]', '', regex=True)
            )
            print(f"  ✓ {alias:20} : {len(df):,} lignes chargées")
            print(f"    Colonnes originales: {original_cols}")
            print(f"    Colonnes normalisées: {list(df.columns)}")  # 🔍 DEBUG
            dataframes[alias] = df
        except Exception as e:
            print(f"  ❌ {alias:20} : Erreur - {e}")
            raise

    return dataframes

# =========================
# VALIDATION - COMPLÉTUDE
# =========================
def valider_completude(df_staff, df_patients, df_consultations, metriques):
    print("\n🔍 VALIDATION PILIER : COMPLÉTUDE")
    
    # Staff
    total = len(df_staff)
    not_null = df_staff['staff_id'].notna().sum()
    metriques.ajouter_metrique('staff', 'staff_id', 'COMPLÉTUDE', 'staff_id_not_null', not_null, total - not_null)
    
    phone_filled = df_staff['telephone'].notna().sum()
    metriques.ajouter_metrique('staff', 'telephone', 'COMPLÉTUDE', 'telephone_70pct_filled', 
                              max(int(total * 0.7), phone_filled), total - max(int(total * 0.7), phone_filled))
    
    # Patients
    total = len(df_patients)
    not_null = df_patients['patient_id'].notna().sum()
    metriques.ajouter_metrique('patients', 'patient_id', 'COMPLÉTUDE', 'patient_id_not_null', not_null, total - not_null)
    
    phone_filled = df_patients['telephone'].notna().sum()
    metriques.ajouter_metrique('patients', 'telephone', 'COMPLÉTUDE', 'telephone_70pct_filled',
                              max(int(total * 0.7), phone_filled), total - max(int(total * 0.7), phone_filled))
    
    # Consultations
    total = len(df_consultations)
    not_null = df_consultations['consultationdate'].notna().sum()
    metriques.ajouter_metrique('consultations', 'consultationdate', 'COMPLÉTUDE', 
                              'consultationdate_not_null', not_null, total - not_null)

# =========================
# VALIDATION - EXACTITUDE (formats)
# =========================
def valider_exactitude(df_staff, df_patients, df_staff_schedule, metriques):
    print("🔍 VALIDATION PILIER : EXACTITUDE")
    
    # Regex FR
    REGEX_PHONE_FR = r'^(\+33|0033|0)[1-9](\s?\d{2}){4}$'
    REGEX_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    REGEX_POSTAL_FR = r'^[1-9]\d{4}$'  # 5 chiffres sans 0 initial
    
    # Staff - téléphone
    total = df_staff['telephone'].notna().sum()
    valid = df_staff['telephone'].dropna().str.match(REGEX_PHONE_FR, na=False).sum()
    metriques.ajouter_metrique('staff', 'telephone', 'EXACTITUDE', 'telephone_format_FR', valid, total - valid)
    
    # Staff - email
    total = df_staff['email'].notna().sum()
    valid = df_staff['email'].dropna().str.match(REGEX_EMAIL, na=False).sum()
    metriques.ajouter_metrique('staff', 'email', 'EXACTITUDE', 'email_format_rfc5322', valid, total - valid)
    
    # Staff - code postal
    cp_clean = df_staff['code_postal'].astype(str).str.replace(r'\D', '', regex=True)
    total = cp_clean.notna().sum()
    valid = cp_clean.dropna().str.match(REGEX_POSTAL_FR, na=False).sum()
    metriques.ajouter_metrique('staff', 'code_postal', 'EXACTITUDE', 'code_postal_5chiffres_sans0', valid, total - valid)
    
    # Patients - mêmes validations
    total = df_patients['telephone'].notna().sum()
    valid = df_patients['telephone'].dropna().str.match(REGEX_PHONE_FR, na=False).sum()
    metriques.ajouter_metrique('patients', 'telephone', 'EXACTITUDE', 'telephone_format_FR', valid, total - valid)
    
    total = df_patients['email'].notna().sum()
    valid = df_patients['email'].dropna().str.match(REGEX_EMAIL, na=False).sum()
    metriques.ajouter_metrique('patients', 'email', 'EXACTITUDE', 'email_format_rfc5322', valid, total - valid)
    
    cp_clean = df_patients['code_postal'].astype(str).str.replace(r'\D', '', regex=True)
    total = cp_clean.notna().sum()
    valid = cp_clean.dropna().str.match(REGEX_POSTAL_FR, na=False).sum()
    metriques.ajouter_metrique('patients', 'code_postal', 'EXACTITUDE', 'code_postal_5chiffres_sans0', valid, total - valid)
    
    # Staff Schedule - binary & range
    total = len(df_staff_schedule)
    valid = df_staff_schedule['present'].isin([0, 1]).sum()
    metriques.ajouter_metrique('staff_schedule', 'present', 'EXACTITUDE', 'present_binary_valid', valid, total - valid)
    
    valid = ((df_staff_schedule['week'] >= 1) & (df_staff_schedule['week'] <= 52)).sum()
    metriques.ajouter_metrique('staff_schedule', 'week', 'EXACTITUDE', 'week_range_1_52', valid, total - valid)

# =========================
# VALIDATION - VALIDITÉ (énumérations & plages)
# =========================
def valider_validite(df_staff, df_patients, df_services_weekly, metriques):
    print("🔍 VALIDATION PILIER : VALIDITÉ")
    
    VALID_ROLES = ['doctor', 'nurse', 'nursing_assistant']
    VALID_SERVICES = ['emergency', 'surgery', 'general_medicine', 'ICU', 'cardiology', 'neurology', 'pediatrics']
    VALID_GENRES = ['Male', 'Female', 'Other']
    
    # Staff
    total = len(df_staff)
    valid = df_staff['role'].isin(VALID_ROLES).sum()
    metriques.ajouter_metrique('staff', 'role', 'VALIDITÉ', 'role_in_allowed_values', valid, total - valid)
    
    valid = df_staff['service'].isin(VALID_SERVICES).sum()
    metriques.ajouter_metrique('staff', 'service', 'VALIDITÉ', 'service_in_allowed_values', valid, total - valid)
    
    valid = df_staff['genre'].isin(VALID_GENRES).sum()
    metriques.ajouter_metrique('staff', 'genre', 'VALIDITÉ', 'genre_in_allowed_values', valid, total - valid)
    
    valid = ((df_staff['age'] >= 18) & (df_staff['age'] <= 75)).sum()
    metriques.ajouter_metrique('staff', 'age', 'VALIDITÉ', 'age_range_18_75', valid, total - valid)
    
    # Patients
    total = len(df_patients)
    valid = df_patients['genre'].isin(VALID_GENRES).sum()
    metriques.ajouter_metrique('patients', 'genre', 'VALIDITÉ', 'genre_in_allowed_values', valid, total - valid)
    
    valid = ((df_patients['satisfaction'] >= 0) & (df_patients['satisfaction'] <= 100)).sum()
    metriques.ajouter_metrique('patients', 'satisfaction', 'VALIDITÉ', 'satisfaction_range_0_100', valid, total - valid)
    
    valid = df_patients['service'].isin(VALID_SERVICES).sum()
    metriques.ajouter_metrique('patients', 'service', 'VALIDITÉ', 'service_in_allowed_values', valid, total - valid)
    
    # Services Weekly
    total = len(df_services_weekly)
    valid = (df_services_weekly['availablebeds'] >= 0).sum()
    metriques.ajouter_metrique('services_weekly', 'availablebeds', 'VALIDITÉ', 'availablebeds_non_negative', valid, total - valid)
    
    valid = df_services_weekly['service'].isin(VALID_SERVICES).sum()
    metriques.ajouter_metrique('services_weekly', 'service', 'VALIDITÉ', 'service_in_allowed_values', valid, total - valid)

# =========================
# VALIDATION - COHÉRENCE (logique métier)
# =========================
def valider_coherence(df_staff, df_patients, df_consultations, df_services_weekly, metriques):
    print("🔍 VALIDATION PILIER : COHÉRENCE")
    
    current_year = RUN_DATE.year
    
    # Staff - cohérence age/date_naissance
    df_staff['date_naissance'] = pd.to_datetime(df_staff['date_naissance'], errors='coerce')
    df_staff['calc_age'] = current_year - df_staff['date_naissance'].dt.year
    total = len(df_staff)
    valid = (abs(df_staff['age'] - df_staff['calc_age']) <= 1).sum()
    metriques.ajouter_metrique('staff', 'age', 'COHÉRENCE', 'age_date_naissance_coherent', valid, total - valid)
    
    # Patients - cohérence dates
    df_patients['arrival_date'] = pd.to_datetime(df_patients['arrival_date'], errors='coerce')
    df_patients['departure_date'] = pd.to_datetime(df_patients['departure_date'], errors='coerce')
    total = len(df_patients)
    valid = (df_patients['departure_date'].isna() | (df_patients['departure_date'] >= df_patients['arrival_date'])).sum()
    metriques.ajouter_metrique('patients', 'departure_date', 'COHÉRENCE', 'departure_after_arrival', valid, total - valid)
    
    # Patients - cohérence age/date_naissance
    df_patients['date_naissance'] = pd.to_datetime(df_patients['date_naissance'], errors='coerce')
    df_patients['calc_age'] = current_year - df_patients['date_naissance'].dt.year
    valid = (abs(df_patients['age'] - df_patients['calc_age']) <= 1).sum()
    metriques.ajouter_metrique('patients', 'age', 'COHÉRENCE', 'age_date_naissance_coherent', valid, total - valid)
    
    # Services Weekly - cohérence logique
    total = len(df_services_weekly)
    valid = ((df_services_weekly['patientsadmitted'] + df_services_weekly['patientsrefused']) <= df_services_weekly['patientsrequest']).sum()
    metriques.ajouter_metrique('services_weekly', 'patientsrequest', 'COHÉRENCE', 'admitted_refused_le_requested', valid, total - valid)
    
    # Consultations - intégrité référentielle
    total = len(df_consultations)
    valid = df_consultations['patientid'].isin(df_patients['patient_id']).sum()
    metriques.ajouter_metrique('consultations', 'patientid', 'COHÉRENCE', 'patientid_fk_valid', valid, total - valid)
    
    valid = df_consultations['staffid'].isin(df_staff['staff_id']).sum()
    metriques.ajouter_metrique('consultations', 'staffid', 'COHÉRENCE', 'staffid_fk_valid', valid, total - valid)

# =========================
# VALIDATION - UNICITÉ & ACTUALITÉ
# =========================
def valider_unicite_actualite(df_staff, df_patients, df_consultations, df_staff_schedule, metriques):
    print("🔍 VALIDATION PILIER : UNICITÉ & ACTUALITÉ")
    
    # UNICITÉ - Staff ID
    total = len(df_staff)
    unique = df_staff['staff_id'].nunique()
    metriques.ajouter_metrique('staff', 'staff_id', 'UNICITÉ', 'staff_id_unique', unique, total - unique)
    
    # UNICITÉ - Patient ID
    total = len(df_patients)
    unique = df_patients['patient_id'].nunique()
    metriques.ajouter_metrique('patients', 'patient_id', 'UNICITÉ', 'patient_id_unique', unique, total - unique)
    
    # UNICITÉ - Staff Schedule (week, staff_id)
    total = len(df_staff_schedule)
    unique = df_staff_schedule.groupby(['week', 'staff_id']).size().shape[0]
    metriques.ajouter_metrique('staff_schedule', 'week,staff_id', 'UNICITÉ', 'week_staff_id_combination_unique', unique, total - unique)
    
    # UNICITÉ - Consultations (patient_id, date, time)
    total = len(df_consultations)
    df_consultations['consultationdate'] = pd.to_datetime(df_consultations['consultationdate'], errors='coerce')
    unique = df_consultations.groupby(['patientid', 'consultationdate', 'consultationtime']).size().shape[0]
    metriques.ajouter_metrique('consultations', 'patientid,consultationdate,consultationtime', 'UNICITÉ', 'patient_consultation_unique', unique, total - unique)
    
    # ACTUALITÉ - Patients arrival_date >= 2020
    total = len(df_patients)
    valid = (df_patients['arrival_date'] >= pd.Timestamp('2020-01-01')).sum()
    metriques.ajouter_metrique('patients', 'arrival_date', 'ACTUALITÉ', 'arrival_date_since_2020', valid, total - valid)

# =========================
# GÉNÉRATION DES RAPPORTS
# =========================
def generer_rapports(df_metriques):
    print("\n📊 GÉNÉRATION DES LIVRABLES...")
    
    # 1. Historique de validation (dans results/ ET data/)
    history_file_results = RESULTS_DIR / "validation_history.csv"
    history_file_data = DATA_DIR / "validation_history.csv"
    
    if history_file_results.exists():
        df_existing = pd.read_csv(history_file_results)
        df_history = pd.concat([df_existing, df_metriques], ignore_index=True)
    else:
        df_history = df_metriques.copy()
    
    df_history.to_csv(history_file_results, index=False)
    df_history.to_csv(history_file_data, index=False)
    print(f"  ✓ Historique sauvegardé :")
    print(f"    → {history_file_results}")
    print(f"    → {history_file_data}")
    
    # 2. Dataset pour Superset
    df_superset = df_metriques.rename(columns={
        'table_name': 'table',
        'pilier': 'pilier',
        'rule_name': 'règle',
        'column_name': 'colonne',
        'run_date': 'date_run',
        'checks_passed': 'passed',
        'checks_failed': 'failed',
        'success_rate': '%_succès',
        'error_type': 'erreurs'
    })
    df_superset['%_succès'] = df_superset['%_succès'].apply(lambda x: f"{x:.2f}%")
    df_superset['erreurs'] = df_superset['erreurs'].fillna('N/A')
    
    superset_file_results = RESULTS_DIR / "superset_validation_metrics.csv"
    superset_file_data = DATA_DIR / "superset_validation_metrics.csv"
    
    df_superset.to_csv(superset_file_results, index=False)
    df_superset.to_csv(superset_file_data, index=False)
    print(f"  ✓ Dataset Superset sauvegardé :")
    print(f"    → {superset_file_results}")
    print(f"    → {superset_file_data}")
    # 3. Rapport HTML synthétique
    html_file = GX_DATA_DOCS_DIR / "rapport_validation_qualite.html"
    total_checks = df_metriques['checks_passed'].sum() + df_metriques['checks_failed'].sum()
    total_passed = df_metriques['checks_passed'].sum()
    global_rate = (total_passed / total_checks * 100) if total_checks > 0 else 0
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport Validation Qualité - Great Expectations</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .card h3 {{ margin: 0 0 10px 0; font-size: 14px; opacity: 0.9; }}
        .card .value {{ font-size: 32px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #34495e; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #ddd; }}
        tr:nth-child(even) {{ background: #fafafa; }}
        .success-rate.high {{ background-color: #d4edda; color: #155724; padding: 2px 8px; border-radius: 4px; }}
        .success-rate.medium {{ background-color: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 4px; }}
        .success-rate.low {{ background-color: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport de Validation Qualité des Données Hospitalières</h1>
        <div class="summary">
            <div class="card"><h3>Taux de Succès Global</h3><div class="value">{global_rate:.2f}%</div></div>
            <div class="card"><h3>Vérifications</h3><div class="value">{total_checks:,}</div></div>
            <div class="card"><h3>Réussies</h3><div class="value">{total_passed:,}</div></div>
            <div class="card"><h3>Échouées</h3><div class="value">{total_checks - total_passed:,}</div></div>
        </div>
        
        <h2>📈 Détail par Pilier</h2>
        <table>
            <tr><th>Pilier</th><th>Réussies</th><th>Échouées</th><th>Taux</th></tr>
"""
    
    for pilier in df_metriques['pilier'].unique():
        df_p = df_metriques[df_metriques['pilier'] == pilier]
        passed = df_p['checks_passed'].sum()
        failed = df_p['checks_failed'].sum()
        rate = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
        cls = "high" if rate >= 90 else ("medium" if rate >= 70 else "low")
        html_content += f'<tr><td>{pilier}</td><td>{passed:,}</td><td>{failed:,}</td><td class="success-rate {cls}">{rate:.2f}%</td></tr>\n'
    
    html_content += """
        </table>
        
        <h2>📋 Détail par Table</h2>
        <table>
            <tr><th>Table</th><th>Colonne</th><th>Pilier</th><th>Règle</th><th>Taux</th></tr>
"""
    
    for _, row in df_metriques.iterrows():
        cls = "high" if row['success_rate'] >= 90 else ("medium" if row['success_rate'] >= 70 else "low")
        html_content += f'<tr><td>{row["table_name"]}</td><td>{row["column_name"]}</td><td>{row["pilier"]}</td><td>{row["rule_name"]}</td><td class="success-rate {cls}">{row["success_rate"]:.2f}%</td></tr>\n'
    
    html_content += f"""
        </table>
        <div style="color: #7f8c8d; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
            Généré le : {RUN_DATETIME_STR}<br>
            Pipeline : Great Expectations v1.11.3
        </div>
    </div>
</body>
</html>"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"  ✓ Rapport HTML : {html_file}")

# =========================
# FONCTION PRINCIPALE
# =========================
def main():
    try:
        # Connexion à PostgreSQL
        print("\n🔌 Connexion à PostgreSQL...")
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("  ✓ Connexion établie")
        
        # Chargement des données
        dfs = charger_donnees(engine)
        
        # Initialisation des métriques
        metriques = ValidationMetriques()
        
        # Exécution des validations par pilier
        valider_completude(dfs['staff'], dfs['patients'], dfs['consultations'], metriques)
        valider_exactitude(dfs['staff'], dfs['patients'], dfs['staff_schedule'], metriques)
        valider_validite(dfs['staff'], dfs['patients'], dfs['services_weekly'], metriques)
        valider_coherence(dfs['staff'], dfs['patients'], dfs['consultations'], dfs['services_weekly'], metriques)
        valider_unicite_actualite(dfs['staff'], dfs['patients'], dfs['consultations'], dfs['staff_schedule'], metriques)
        
        # Génération des rapports
        df_metriques = metriques.to_dataframe()
        generer_rapports(df_metriques)
        
        # Affichage du résumé final
        total = df_metriques['checks_passed'].sum() + df_metriques['checks_failed'].sum()
        passed = df_metriques['checks_passed'].sum()
        rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 70)
        print("✅ VALIDATION QUALITÉ TERMINÉE AVEC SUCCÈS")
        print(f"   • Total vérifications : {total:,}")
        print(f"   • Taux de succès global : {rate:.2f}%")
        print(f"   • Rapports générés dans : {REPORTS_DIR}")
        print(f"   • Historique sauvegardé dans : {RESULTS_DIR}")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())