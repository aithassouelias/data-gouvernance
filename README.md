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
⚠️ Le dossier data/ n’est pas dans GitHub : il doit être présent à la racine en local avant de lancer Docker.

---

## 📥 Prérequis

1. Docker Desktop + Docker Compose installés.

2. Git cloné en local :

bash
git clone
cd data-gouvernance

3. Créer le dossier data à la racine (copie des fichiers CSV/SQL de test) :

bash
mkdir data
