FROM python:3.11-slim

WORKDIR /app

# Copier les requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Créer les répertoires nécessaires
RUN mkdir -p /app/data /app/results /app/logs /app/src

# Ajouter /app/src au PYTHONPATH pour que Python trouve les modules
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Pas de CMD par défaut pour plus de flexibilité