# Image d'exécution du scoring : un job planifié, pas un service permanent (§11.2).
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Les dépendances d'abord : cette couche ne change qu'avec requirements.txt.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Puis le code et les artefacts du modèle.
COPY pyproject.toml ./
COPY churn/ ./churn/
COPY artefacts/modele_churn_v1.0.0.joblib artefacts/modele_valeur_v1.0.0.joblib \
     artefacts/modele_churn_v1.0.0.json ./artefacts/
COPY catalogue_plans.csv ./

# Exécution sans privilèges.
RUN useradd --create-home --uid 10001 scoring && chown -R scoring:scoring /app
USER scoring

# Les paramètres métier sont surchargeables sans reconstruire l'image (§13.3).
ENV CHURN_ARTEFACTS=/app/artefacts \
    CHURN_VERSION=1.0.0

ENTRYPOINT ["python", "-m", "churn"]
CMD ["--help"]
