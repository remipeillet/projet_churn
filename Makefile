# Raccourcis d'exploitation. `make aide` liste les cibles.

VENV ?= .venv/bin
LOT  ?= churn_saas_echantillon.csv

.PHONY: aide qualite lint format secrets tests score verifier derive statut image compose-up compose-down

aide:  ## Liste les cibles disponibles
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

qualite: lint format secrets  ## Lance tous les contrôles de qualité

lint:  ## Analyse statique (ruff)
	$(VENV)/ruff check churn tests

format:  ## Vérifie le formatage — `make format-ecrit` pour corriger
	$(VENV)/ruff format --check --diff churn tests

format-ecrit:  ## Applique le formatage et les corrections automatiques
	$(VENV)/ruff format churn tests
	$(VENV)/ruff check --fix churn tests

secrets:  ## Recherche de secrets dans le dépôt (gitleaks, via Docker)
	docker run --rm -v "$(PWD):/repo" -w /repo zricethezav/gitleaks:latest \
		detect --source=/repo --config=/repo/.gitleaks.toml --no-git --redact

tests:  ## Exécute la suite de tests
	$(VENV)/python -m pytest tests

score:  ## Score un lot (make score LOT=fichier.csv)
	$(VENV)/python -m churn score --lot $(LOT)

verifier:  ## Valide le contrat d'entrée d'un lot
	$(VENV)/python -m churn verifier --lot $(LOT)

derive:  ## Compare deux lots (make derive REF=a.csv COURANT=b.csv)
	$(VENV)/python -m churn derive --reference $(REF) --courant $(COURANT)

statut:  ## Vérifie qu'un cycle a tourné récemment (dead man's switch)
	$(VENV)/python -m churn statut

image:  ## Construit l'image Docker de scoring
	docker build -t churn-saas:1.0.0 .

compose-up:  ## Monte la maquette d'architecture (entrepôt, MLflow, Grafana)
	docker compose up -d entrepot mlflow grafana

compose-down:  ## Arrête la maquette
	docker compose down
