# 🏥 Data Gouvernance – Plateforme Dockerisée

> Projet de mise en place d’une **plateforme de data gouvernance** pour un environnement hospitalier (BDD, exploration, dashboards, data catalog, orchestration).  

---

## 🧩 Stack technique

- 🐳 **Docker / Docker Compose** – orchestration de tous les services.
- 🐘 **PostgreSQL** – stockage des données opérationnelles.
- 📊 **Apache Superset** – dashboards et visualisation des indicateurs.
- 📚 **OpenMetadata** – Data catalog, domaines, RGPD, Tiers, niveaux de qualité des données d'une table.
- 🐍 **Python** – Scripts d’exploration/profilage des données.

---

## 🗂️ Structure du projet
⚠️ Le dossier ```data/``` n’est pas dans GitHub : il doit être présent à la racine en local avant de lancer Docker.

---

## 📥 Prérequis

1. Docker Desktop + Docker Compose installés.

2. Git cloné en local :

```
git clone https://github.com/aithassouelias/data-gouvernance.git
```

3. Créer le dossier data à la racine (copie des fichiers de données CSV) :

``` 
mkdir data 
```

## 🌐 Accès aux outils

- PostgreSQL (couche 1)

    - Host : localhost
    - Port : 5433

- Profiling des données (couche 2) : 
    - Les fichiers HTML de profiling automatique sont dans le dossier : ```exploration/html```

- Apache Superset (couche 3)

    - URL : http://localhost:8088
    - Login par défaut : admin / admin
    - URL de connexion SQLAlchemy à utiliser dans Superset (cohérente avec docker-compose.yml) : ```postgresql://dq_user:dq_pass@postgres:5432/dq_db```
    Ceci permet à Superset d’accéder à la base dq_db du conteneur postgres.


- OpenMetadata (couche 5) : 

    - URL : http://localhost:9000
    - Login: Ces informations ont été fournies par email au professeur, sinon créer un nouveau compte OpenMetadata.
