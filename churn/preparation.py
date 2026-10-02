"""Préparation des données brutes — mise en œuvre de §7 du notebook.

Toute transformation appliquée en production passe par ce module : le notebook
et le service de scoring partagent le même code, ce qui exclut la divergence
entre entraînement et exploitation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from churn.config import (
    COLONNES_CATEGORIELLES,
    COLONNES_NUMERIQUES,
    MODALITE_INCONNUE,
)

FORMATS_DATE = ("%Y-%m-%d", "%d/%m/%Y", "%d %b %Y")


def to_numeric_fr(serie: pd.Series) -> pd.Series:
    """Convertit une série texte en numérique (§6.2).

    Stratégie de liste blanche : on ne retire pas une liste de symboles connus
    — on en oublierait — mais on ne conserve que ce qui compose un nombre.
    Absorbe la virgule décimale, les symboles `%`, `€`, les unités suffixées et
    les espaces (ordinaires, insécables, fines).
    """
    nettoye = (
        serie.astype(str)
        .str.replace(r"[^\d,.\-]", "", regex=True)
        .str.replace(",", ".", regex=False)
        .replace({"": None, ".": None, "-": None})
    )
    return pd.to_numeric(nettoye, errors="coerce")


def normaliser_categorie(serie: pd.Series) -> pd.Series:
    """Ramène une catégorielle à sa forme canonique (§6.3).

    Sans espaces de bord, espaces internes réduits, en majuscules : la casse
    haute est stable en présence d'accents et sert de clé de jointure avec le
    catalogue des plans.
    """
    return (
        serie.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
        .replace({"": None, "NAN": None, "NONE": None})
    )


def parse_date_multi(serie: pd.Series, formats: tuple[str, ...] = FORMATS_DATE) -> pd.Series:
    """Parse des dates mêlant plusieurs formats (§7.3).

    Les formats sont essayés tour à tour sur les valeurs encore non résolues ;
    les mois littéraux sont interprétés en anglais, conformément aux données.
    """
    valeurs = serie.astype(str).str.strip()
    resultat = pd.Series(pd.NaT, index=serie.index, dtype="datetime64[ns]")
    for format_date in formats:
        a_resoudre = resultat.isna() & valeurs.notna()
        if not a_resoudre.any():
            break
        resultat.loc[a_resoudre] = pd.to_datetime(
            valeurs[a_resoudre], format=format_date, errors="coerce"
        )
    return resultat


def charger_catalogue(chemin: Path) -> pd.DataFrame:
    """Charge le référentiel des plans et normalise sa clé de jointure (§7.5)."""
    catalogue = pd.read_csv(chemin, encoding="utf-8-sig")
    catalogue["plan"] = normaliser_categorie(catalogue["plan"])
    catalogue["support_dedie"] = (catalogue["support_dedie"] == "Oui").astype(int)
    return catalogue


def lire_lot_brut(chemin: Path) -> pd.DataFrame:
    """Lecture brute d'un lot : tout en texte, aucune inférence de type (§5)."""
    return pd.read_csv(
        chemin, dtype=str, keep_default_na=False, na_values=[""], encoding="utf-8-sig"
    )


def preparer(
    brut: pd.DataFrame, catalogue: pd.DataFrame, colonnes_attendues: list[str]
) -> pd.DataFrame:
    """Rejoue la préparation de §7 sur un lot de comptes bruts.

    Étapes : normalisation des catégorielles (§7.4), conversion des numériques
    stockés en texte (§7.2), reconstitution arithmétique du taux d'adoption,
    jointure du catalogue (§7.5), ratios métier (§7.7), puis restriction au
    périmètre explicatif dans l'ordre attendu par le modèle (§7.6).

    Lève `ValueError` sur un plan inconnu ou une colonne manquante : un échec
    explicite vaut mieux qu'un score silencieusement faux.
    """
    lot = brut.copy()

    for colonne in COLONNES_CATEGORIELLES:
        if colonne in lot.columns:
            lot[colonne] = normaliser_categorie(lot[colonne])
            lot[colonne] = lot[colonne].fillna(MODALITE_INCONNUE)

    for colonne in COLONNES_NUMERIQUES:
        if colonne in lot.columns:
            lot[colonne] = to_numeric_fr(lot[colonne])

    a_reconstituer = lot["taux_adoption_pct"].isna()
    if a_reconstituer.any():
        lot.loc[a_reconstituer, "taux_adoption_pct"] = (
            100 * lot["utilisateurs_actifs"] / lot["sieges_souscrits"]
        )[a_reconstituer].round(1)

    plans_inconnus = set(lot["plan"].unique()) - set(catalogue["plan"])
    if plans_inconnus:
        raise ValueError(f"plan(s) absent(s) du catalogue : {sorted(plans_inconnus)}")
    lot = lot.merge(catalogue, on="plan", how="left", validate="many_to_one")

    lot["taux_fonctionnalites"] = (
        lot["fonctionnalites_utilisees"] / lot["fonctionnalites_total"]
    ).round(4)
    lot["heures_par_siege"] = (lot["heures_usage_30j"] / lot["sieges_souscrits"]).round(4)
    lot["tickets_par_siege"] = (lot["tickets_support_90j"] / lot["sieges_souscrits"]).round(4)
    lot["respect_sla"] = (lot["delai_reponse_support_h"] / lot["sla_reponse_h"]).round(4)
    lot["ratio_prix_catalogue"] = (
        lot["revenu_mensuel_recurrent_eur"]
        / (lot["sieges_souscrits"] * lot["prix_mensuel_par_siege_eur"])
    ).round(4)

    manquantes = set(colonnes_attendues) - set(lot.columns)
    if manquantes:
        raise ValueError(f"colonnes absentes du lot : {sorted(manquantes)}")

    prepare = lot[list(colonnes_attendues)]
    if np.isinf(prepare.select_dtypes(include="number")).to_numpy().any():
        raise ValueError("une division a produit une valeur infinie")
    return prepare
