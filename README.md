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

``` 
docker compose -f docker-compose.yml -f docker-compose-openmetadata.yml up -d
``` 
Cette commande lance :

- l’instance Postgres (dq_db),
- le conteneur d’exploration,
- Superset,
- OpenMetadata (serveur + DB + ingestion).

### 1. Démarrer PostgreSQL 
``` 
docker compose up -d postgres
 ```


### 2. Exécuter la Couche 2 : Profiling 
```
docker compose up exploration
```
Rapports générés dans ./exploration/html/*.html

### 3. Exécuter la Couche 3 : Validation Qualité 
``` 
docker compose up validation
```
Livrables générés :
    • /results/validation_history.csv
    • /results/superset_validation_metrics.csv
    • /data/validation_history.csv (dupliqué)
    • /data/superset_validation_metrics.csv (dupliqué)
    • /reports/gx_data_docs/rapport_validation_qualite.html

### 4. Démarrer Superset 
``` 
docker compose up -d superset
```

### 5.  Démarrer OpenMetadata
```
docker compose -f docker-compose.yml -f docker-compose-openmetadata.yml up -d openmetadata
```


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
