FROM python:3.11-slim

WORKDIR /app

# Installer dépendances système pour psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script de validation
COPY validation.py .

# Créer les répertoires de sortie
RUN mkdir -p /app/results /app/reports/gx_data_docs

# Exécuter la validation
CMD ["python", "validation.py"]