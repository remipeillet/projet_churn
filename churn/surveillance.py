"""Instruments de surveillance en production (§13.1).

Trois contrôles, du plus précoce au plus tardif : qualité des entrées, dérive
des distributions, et recherche de fuite avant tout ré-entraînement.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from churn.config import SEUIL_SUSPICION_FUITE

SEUIL_VIGILANCE = 0.10
SEUIL_DERIVE = 0.25


def indice_stabilite(reference, courant, n_classes: int = 10) -> float:
    """Population Stability Index entre une référence et un cycle courant.

    Les bornes sont les déciles de la référence ; l'indice cumule, classe par
    classe, l'écart de proportion pondéré par le logarithme de son rapport.
    Repères usuels : < 0,10 stable · 0,10-0,25 vigilance · > 0,25 dérive avérée.
    """
    reference = pd.Series(reference).dropna()
    courant = pd.Series(courant).dropna()
    if reference.empty or courant.empty:
        return 0.0
    bornes = np.unique(np.quantile(reference, np.linspace(0, 1, n_classes + 1)))
    if len(bornes) < 3:
        return 0.0
    bornes[0], bornes[-1] = -np.inf, np.inf
    part_reference = np.clip(np.histogram(reference, bins=bornes)[0] / len(reference), 1e-4, None)
    part_courante = np.clip(np.histogram(courant, bins=bornes)[0] / len(courant), 1e-4, None)
    return float(((part_courante - part_reference) * np.log(part_courante / part_reference)).sum())


def statut_derive(psi: float) -> str:
    if psi > SEUIL_DERIVE:
        return "DERIVE"
    return "vigilance" if psi > SEUIL_VIGILANCE else "stable"


def controle_derive(
    reference: pd.DataFrame, courant: pd.DataFrame, variables: list[str] | None = None
) -> pd.DataFrame:
    """Tableau de bord de dérive, une ligne par variable surveillée."""
    variables = variables or list(reference.select_dtypes(include="number").columns)
    lignes = [
        {
            "variable": variable,
            "psi": round(indice_stabilite(reference[variable], courant[variable]), 4),
            "statut": statut_derive(indice_stabilite(reference[variable], courant[variable])),
            "manquants_%": round(100 * courant[variable].isna().mean(), 2),
        }
        for variable in variables
        if variable in courant.columns
    ]
    return pd.DataFrame(lignes).sort_values("psi", ascending=False, ignore_index=True)


def controle_antifuite(
    donnees: pd.DataFrame, cible: pd.Series, seuil: float = SEUIL_SUSPICION_FUITE
) -> pd.DataFrame:
    """Rejoue le diagnostic de §6.5 sur les variables d'entrée.

    À exécuter avant chaque ré-entraînement : une variable amont peut devenir
    fuyante sans avertissement — champ recalculé, fenêtre d'extraction qui
    glisse, enrichissement en aval.
    """
    lignes = []
    for variable in donnees.select_dtypes(include="number").columns:
        renseignes = donnees[variable].notna()
        if cible[renseignes].nunique() < 2:
            continue
        auc = roc_auc_score(cible[renseignes], donnees.loc[renseignes, variable])
        auc_orientee = max(auc, 1 - auc)
        lignes.append(
            {
                "variable": variable,
                "auc_univariee": round(auc_orientee, 4),
                "suspecte": bool(auc_orientee > seuil),
            }
        )
    return pd.DataFrame(lignes).sort_values("auc_univariee", ascending=False, ignore_index=True)
