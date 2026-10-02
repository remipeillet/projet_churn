"""Fixtures partagées par la suite de tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

RACINE = Path(__file__).resolve().parent.parent
ECHANTILLON = RACINE / "churn_saas_echantillon.csv"
CATALOGUE = RACINE / "catalogue_plans.csv"
ARTEFACTS = RACINE / "artefacts"


@pytest.fixture(scope="session")
def catalogue() -> pd.DataFrame:
    from churn.preparation import charger_catalogue

    return charger_catalogue(CATALOGUE)


@pytest.fixture(scope="session")
def lot_brut() -> pd.DataFrame:
    from churn.preparation import lire_lot_brut

    return lire_lot_brut(ECHANTILLON)


@pytest.fixture(scope="session")
def config():
    """Configuration réelle — les tests d'intégration sont ignorés sans artefacts."""
    from churn.config import charger_config

    if not (ARTEFACTS / "modele_churn_v1.0.0.json").exists():
        pytest.skip("artefacts absents : exécuter §10.1 du notebook")
    return charger_config(artefacts=ARTEFACTS, catalogue=CATALOGUE)


@pytest.fixture(scope="session")
def scoreur(config):
    from churn.scoring import Scoreur

    return Scoreur(config)
