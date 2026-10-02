"""Contrats de données — validation à l'ingestion et en sortie.

Formalise avec `pandera` les contrôles défensifs de §10.2 : un lot de
production ne ressemble pas toujours à un lot d'entraînement, et une extraction
défaillante doit échouer bruyamment plutôt que produire des scores faux.
"""

from __future__ import annotations

import pandas as pd
from pandera.pandas import Check, Column, DataFrameSchema

from churn.config import ORDRE_PLAN

# --- Contrat d'entrée : le lot brut, tel qu'il sort des systèmes sources -----
# Les valeurs sont attendues en TEXTE : la conversion est du ressort de la
# préparation (§7.2), pas de la source.
COLONNES_BRUTES_REQUISES = [
    "client_id",
    "plan",
    "taille_entreprise",
    "secteur",
    "anciennete_mois",
    "sieges_souscrits",
    "utilisateurs_actifs",
    "taux_adoption_pct",
    "connexions_30j",
    "heures_usage_30j",
    "fonctionnalites_total",
    "fonctionnalites_utilisees",
    "nb_integrations",
    "derniere_connexion_jours",
    "tickets_support_90j",
    "delai_reponse_support_h",
    "csat",
    "retards_paiement_12m",
    "revenu_mensuel_recurrent_eur",
]

SCHEMA_LOT_BRUT = DataFrameSchema(
    {
        "client_id": Column(str, nullable=False, unique=True),
        "plan": Column(
            str,
            Check(
                lambda s: s.str.strip().str.upper().isin(ORDRE_PLAN),
                error="plan absent du référentiel catalogue",
            ),
            nullable=False,
        ),
        **{
            colonne: Column(str, nullable=True, required=True)
            for colonne in COLONNES_BRUTES_REQUISES
            if colonne not in ("client_id", "plan")
        },
    },
    strict=False,
    coerce=True,
    name="lot brut de comptes à scorer",
)

# --- Contrat de sortie : la table de scores livrée au CRM (§11.1) -----------
SCHEMA_SCORES = DataFrameSchema(
    {
        "client_id": Column(str, nullable=False, unique=True),
        "probabilite_churn": Column(float, Check.in_range(0.0, 1.0), nullable=False),
        "valeur_estimee_eur": Column(float, Check.ge(0.0), nullable=False),
        "risque_de_perte_eur": Column(float, Check.ge(0.0), nullable=False),
        "priorite": Column(float, nullable=True),
        "alerte": Column(bool, nullable=False),
        "facteurs_principaux": Column(str, nullable=False),
        "modele_version": Column(str, nullable=False),
        "plancher_risque": Column(float, nullable=False),
    },
    strict=False,
    name="table de scores",
)


def valider_lot(brut: pd.DataFrame) -> pd.DataFrame:
    """Valide un lot brut avant préparation. Lève `pa.errors.SchemaError`."""
    return SCHEMA_LOT_BRUT.validate(brut, lazy=False)


def valider_scores(scores: pd.DataFrame) -> pd.DataFrame:
    """Valide la table de scores avant livraison au CRM."""
    return SCHEMA_SCORES.validate(scores, lazy=False)


def rapport_qualite(brut: pd.DataFrame) -> pd.DataFrame:
    """Taux de manquants par colonne — à comparer au taux de référence (§13.1)."""
    return pd.DataFrame(
        {
            "colonne": brut.columns,
            "manquants_%": (100 * brut.isna().mean()).round(2).to_numpy(),
        }
    ).sort_values("manquants_%", ascending=False, ignore_index=True)
