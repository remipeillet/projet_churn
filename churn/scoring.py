"""Scoring bout-en-bout d'un lot de comptes bruts (§10.2).

Enchaîne validation du contrat d'entrée, préparation, scoring des deux modèles,
priorisation risque × valeur et production de la table de scores.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from churn.config import Config, charger_config
from churn.contrats import valider_lot, valider_scores
from churn.modele import Artefacts, prioriser
from churn.preparation import charger_catalogue, lire_lot_brut, preparer


class Scoreur:
    """Dispositif de scoring : artefacts chargés une fois, réutilisés."""

    def __init__(self, config: Config | None = None):
        self.config = config or charger_config()
        self.artefacts = Artefacts.charger(self.config)
        self.catalogue = charger_catalogue(self.config.chemin_catalogue)

    def scorer(self, brut: pd.DataFrame, capacite: int | None = None) -> pd.DataFrame:
        """Score un lot brut et renvoie la liste priorisée remise aux CSM."""
        valider_lot(brut)
        prepare = preparer(brut, self.catalogue, self.config.colonnes_attendues)

        probabilites = self.artefacts.churn.predict_proba(prepare)[:, 1]
        valeurs = self.artefacts.valeur.predict(prepare).clip(min=0)
        if capacite is None:
            capacite = round(self.config.capacite_par_cycle * len(brut))

        selection, rangs = prioriser(probabilites, valeurs, capacite, self.config.plancher_risque)

        scores = pd.DataFrame(
            {
                "priorite": rangs,
                "client_id": brut["client_id"].to_numpy(),
                "probabilite_churn": probabilites.round(4),
                "valeur_estimee_eur": valeurs.round(0),
                "perte_esperee_eur": (probabilites * valeurs).round(0),
                "alerte": selection,
                "facteurs_principaux": self.artefacts.facteurs(prepare),
                "modele_version": self.config.version,
                "plancher_risque": self.config.plancher_risque,
            }
        ).sort_values(["alerte", "perte_esperee_eur"], ascending=[False, False], ignore_index=True)
        return valider_scores(scores)


def scorer(
    lot: Path | pd.DataFrame,
    config: Config | None = None,
    capacite: int | None = None,
) -> pd.DataFrame:
    """Raccourci : score un fichier CSV brut ou un DataFrame déjà chargé."""
    brut = lire_lot_brut(Path(lot)) if isinstance(lot, (str, Path)) else lot
    return Scoreur(config).scorer(brut, capacite=capacite)
