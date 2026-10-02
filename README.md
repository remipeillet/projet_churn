# Détection du risque de résiliation client (churn SaaS B2B)

Dispositif d'aide à la décision pour les équipes Customer Success : il estime la
probabilité de résiliation de chaque compte à son échéance, l'assortit d'une
estimation de valeur vie, et restitue une **liste priorisée par risque de perte**
accompagnée des facteurs qui expliquent chaque score.

| | |
|---|---|
| **Référence méthodologique** | [`churn_saas_notebook.ipynb`](churn_saas_notebook.ipynb) — démarche complète, du cadrage à l'amélioration continue |
| **Mise en œuvre** | paquet [`churn/`](churn/) — préparation, scoring, surveillance |
| **Modèle** | régression logistique (L1, C = 0,1) · ROC-AUC 0,883 · PR-AUC 0,762 sur jeu de test |
| **Règle de décision** | plancher de risque 0,30, puis priorisation par `probabilité × valeur vie estimée`, dans la limite de la capacité CSM (20 % du portefeuille) |

## Démarrage

```bash
uv venv && uv pip install -r requirements-dev.txt

python -m churn verifier --lot churn_saas_echantillon.csv          # contrat d'entrée
python -m churn score    --lot churn_saas_echantillon.csv          # liste priorisée
python -m churn derive   --reference ref.csv --courant lot.csv     # dérive (PSI)
python -m churn statut                                             # le cycle a-t-il tourné ?

pytest tests                                                        # 75 tests
```

## Qualité du code

```bash
make qualite          # ruff check + ruff format + gitleaks
make format-ecrit     # applique le formatage
pre-commit install    # mêmes contrôles avant chaque commit
```

`ruff` (analyse statique **et** formatage, 100 colonnes) et `gitleaks`
(recherche de secrets) tournent aussi en intégration continue, **avant** les
tests : une erreur de style ou un identifiant en clair arrête la chaîne.

## Exécution conteneurisée

```bash
docker build -t churn-saas:1.0.0 .
docker run --rm -v "$PWD:/data" churn-saas:1.0.0 score --lot /data/churn_saas_echantillon.csv

docker compose up -d entrepot mlflow grafana    # maquette de l'architecture cible
```

MLflow sur <http://localhost:5000>, Grafana sur <http://localhost:3000>.

## Planification

```cron
# Scoring mensuel, le 1er à 6 h
0 6 1 * * cd /opt/churn && python -m churn score --lot /data/comptes.csv --sortie /data/scores.csv

# Dead man's switch : alerte si aucun cycle réussi depuis 35 jours
0 7 * * * cd /opt/churn && python -m churn statut || notifier "cycle de scoring manquant"
```

Chaque exécution — réussie ou en échec — est consignée dans
`artefacts/journal_executions.jsonl` et dans la table `executions` de l'entrepôt.

## Structure

```
churn/          paquet applicatif — config, contrats, préparation, modèle, scoring, surveillance, CLI
tests/          suite pytest : conversion, contrats, priorisation, scoring bout-en-bout, dérive
artefacts/      modèles sérialisés, manifeste, registre des versions
sql/            schéma de l'entrepôt : scores, actions CSM, indicateurs
grafana/        source de données et tableau de bord provisionnés
figures/        schéma d'architecture et son code de génération
notes_oral/     fiches de préparation (hors livrable)
```

## Paramètres métier

Ils relèvent du commanditaire, pas du modèle, et se modifient sans
ré-entraînement ni redéploiement :

```bash
CHURN_PLANCHER_RISQUE=0.30   # aucun compte moins risqué que la moyenne n'est signalé
CHURN_CAPACITE=0.20          # part du portefeuille traitable par cycle
```
