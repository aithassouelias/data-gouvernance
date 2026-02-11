import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from ydata_profiling import ProfileReport


# =========================
# Configuration
# =========================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dq_user:dq_pass@postgres:5432/dq_db"
)

OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/exploration/html")

TABLES_TO_PROFILE = [
    "patients_raw",
    "staff_raw",
    "consultations_raw",
    "staff_schedule_raw",
    "services_weekly_raw"
]


# =========================
# Utils
# =========================

def ensure_output_dir(path: str):
    os.makedirs(path, exist_ok=True)


def load_table(engine, table_name: str) -> pd.DataFrame:
    print(f"📥 Chargement de la table : {table_name}")
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)


def generate_profile(df: pd.DataFrame, table_name: str, output_dir: str):
    print(f"📊 Génération du profiling : {table_name}")

    profile = ProfileReport(
        df,
        title=f"{table_name} – Data Profiling Report",
        explorative=True,
        minimal=True
    )

    output_file = os.path.join(output_dir, f"{table_name}.html")
    profile.to_file(output_file)

    print(f"✅ Rapport généré : {output_file}")


# =========================
# Main
# =========================

def main():
    print("🚀 Démarrage du profiling automatique")

    ensure_output_dir(OUTPUT_PATH)

    try:
        engine = create_engine(DATABASE_URL)
    except Exception as e:
        print("❌ Impossible de se connecter à la base de données")
        print(e)
        sys.exit(1)

    for table in TABLES_TO_PROFILE:
        try:
            df = load_table(engine, table)

            if df.empty:
                print(f"⚠️ Table vide : {table} — profiling ignoré")
                continue

            generate_profile(df, table, OUTPUT_PATH)

        except Exception as e:
            print(f"❌ Erreur sur la table {table}")
            print(e)

    print("🎉 Profiling terminé avec succès")


if __name__ == "__main__":
    main()
