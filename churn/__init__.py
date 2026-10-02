"""Détection du risque de résiliation client (churn) — dispositif de scoring.

Ce paquet extrait du notebook `churn_saas_notebook.ipynb` les fonctions
nécessaires à l'exploitation : préparation des données brutes, chargement des
artefacts, scoring priorisé et surveillance de dérive.

Le notebook reste la référence méthodologique (§7 à §13) ; ce paquet en est la
mise en œuvre opérable, testée et exécutable hors Jupyter.
"""

from churn.config import Config, charger_config
from churn.preparation import normaliser_categorie, preparer, to_numeric_fr
from churn.scoring import Scoreur, scorer

__all__ = [
    "Config",
    "Scoreur",
    "charger_config",
    "normaliser_categorie",
    "preparer",
    "scorer",
    "to_numeric_fr",
]
__version__ = "1.0.0"
