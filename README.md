# 🏥 Data Gouvernance – Plateforme Dockerisée

Projet de mise en place d’une **plateforme de data gouvernance** pour un environnement hospitalier (BDD, exploration, dashboards, data catalog, orchestration).  

---

## 🧩 Stack technique

- 🐳 **Docker / Docker Compose** – orchestration de tous les services.
- 🐘 **PostgreSQL** – stockage des données opérationnelles.
- 📊 **Apache Superset** – dashboards et visualisation des indicateurs.
- 📚 **OpenMetadata** – Data catalog, domaines, RGPD, Tiers, niveaux de qualité des données d'une table.
- 🐍 **Python** – Scripts d’exploration/profilage des données -**Validation Qualité Python/Pandas** – pipeline programmatique des 6 piliers
v.

---
## 🏗️ Architecture logique – 5 couches

1. **Couche 1 – Stockage des données (PostgreSQL)**  
   - Base `dq_db` avec les tables métiers (`patients`, `staff`, `consultations`…) et les tables de data quality (`superset_validation_metrics`, etc.).

2. **Couche 2 – Exploration / Profiling**  
   - Conteneur `exploration` (Python) qui se connecte à `dq_db` et génère des rapports HTML de profilage dans `exploration/html`.

3. **Couche 3 – Contrôle qualité avec Great Expectations**  
   - Tableau de règles de qualité automatisées s’appuyant sur Great Expectations pour vérifier la complétude, la cohérence et l’exactitude des principales tables (patients, staff, consultations, indicateurs) et produire des rapports/données exploitables dans le reste de la plateforme.

4. **Couche 4 – Visualisation (Superset)**  
   - Apache Superset pour créer les dashboards sur les données hospitalières et les indicateurs de qualité.

5. **Couche 5 – Data Catalog (OpenMetadata)**  
   - OpenMetadata pour documenter les tables, gérer les domaines (gestion hospitalière vs gestion informatique), les tags RGPD/PII, les Tiers, et les niveaux Bronze/Silver/Gold.
---

## 🗂️ Arborescence du projet
- ⚠️ Le dossier ```data/``` n’est pas dans GitHub : il doit être présent à la racine en local avant de lancer Docker.

- Les rapports de chaque partie sont stockés dans le dossier ```00. Rapports```

---

## 📥 Prérequis

1. Docker Desktop + Docker Compose installés.

2. Git cloné en local :

```
git clone https://github.com/aithassouelias/data-gouvernance.git
```

3. Créer le dossier data à la racine (copie des fichiers de données CSV fournit au format zip) :

``` 
mkdir data 
```

## ▶️ Démarrage des services

``` docker compose -f docker-compose.yml -f docker-compose-openmetadata.yml up -d``` 
Cette commande lance :

- l’instance Postgres (dq_db),
- le conteneur d’exploration,
- Superset,
- OpenMetadata (serveur + DB + ingestion).

- # 1. Démarrer PostgreSQL 
docker compose up -d postgres

# 2. Attendre 15 secondes que PostgreSQL soit prêt

# 3. Exécuter la Couche 2 : Profiling 
docker compose up exploration
# → Rapports générés dans ./exploration/html/*.html

# 4. Exécuter la Couche 3 : Validation Qualité
docker compose up validation
# → Livrables générés :
#    • ./results/validation_history.csv
#    • ./results/superset_validation_metrics.csv
#    • ./data/validation_history.csv 
#    • ./data/superset_validation_metrics.csv 
#    • ./reports/gx_data_docs/rapport_validation_qualite.html

# 5. Démarrer Superset
docker compose up -d superset

# 6.  Démarrer OpenMetadata
docker compose -f docker-compose.yml -f docker-compose-openmetadata.yml up -d openmetadata

## 🌐 Accès aux outils

- PostgreSQL (couche 1)

    - Host : localhost
    - Port : 5433

- Profiling des données (couche 2) : 
    - Les fichiers HTML de profiling automatique sont dans le dossier : ```exploration/html```

- Apache Superset (couche 4)
  - URL : `http://localhost:8088`
  - Identifiants par défaut : `admin / admin`
  - Connexion PostgreSQL (Settings → Databases → + Database → SQLAlchemy URI) :
    - `postgresql://dq_user:dq_pass@postgres:5432/dq_db`
  - Cette connexion permet à Superset d’accéder à la base `dq_db` du conteneur `postgres`.
  - Import du dashboard de data quality :
    - Télécharger `Dashboard-export.zip` depuis le dépôt GitHub
    - Aller dans **Dashboards → Import Dashboard**
    - Cliquer sur **Select file** et choisir `Dashboard-export.zip`
    - Valider pour recréer le tableau de bord
  - Les captures d’écran du dashboard sont disponibles dans le répertoire `Captures_Dashboard` du dépôt.


- OpenMetadata (couche 5) : 

    - URL : http://localhost:9000
    - Login: Ces informations ont été fournies par email au professeur, sinon créer un nouveau compte OpenMetadata.
    - Les métadonnées de la base de données sont exportées dans le fichier ```openmetadata/db_data_catalog.csv```, celles-ci peuvent être importées dans l'outil si besoin

## Contributeurs
- Abdeljebbar ABID
- Yousra BOUHANNA
- Elias AIT HASSOU
