"""Configuration du dispositif : chemins, paramètres métier, seuils.

Les paramètres métier (§9.3) relèvent du commanditaire et non du modèle : ils
sont lus depuis le manifeste de l'artefact, et surchargeables par variables
d'environnement sans redéploiement.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(os.environ.get("CHURN_RACINE", Path(__file__).resolve().parent.parent))
ARTEFACTS = Path(os.environ.get("CHURN_ARTEFACTS", RACINE / "artefacts"))
VERSION_MODELE = os.environ.get("CHURN_VERSION", "1.0.0")

# Colonnes du périmètre (§7.6) — l'ordre est imposé par le modèle sérialisé.
COLONNES_CATEGORIELLES = [
    "plan",
    "taille_entreprise",
    "secteur",
    "pays",
    "jour_souscription",
    "couleur_theme_interface",
    "code_datacenter",
    "groupe_experimentation",
]
COLONNES_NUMERIQUES = [
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
    "sante_compte_fin_periode",
    "valeur_vie_client_eur",
]
MODALITE_INCONNUE = "INCONNU"
ORDRE_PLAN = ["STARTER", "PRO", "BUSINESS", "ENTERPRISE"]

# Seuil de suspicion de fuite (§6.5) : une variable d'entrée qui le dépasse
# bloque le ré-entraînement tant que son horodatage n'est pas vérifié.
SEUIL_SUSPICION_FUITE = 0.85


@dataclass(frozen=True)
class Config:
    """Paramètres d'un cycle de scoring."""

    version: str
    chemin_modele: Path
    chemin_valeur: Path
    chemin_manifeste: Path
    chemin_catalogue: Path
    plancher_risque: float
    capacite_par_cycle: float
    colonnes_attendues: list[str] = field(default_factory=list)

    @property
    def manifeste(self) -> dict:
        return json.loads(self.chemin_manifeste.read_text(encoding="utf-8"))


def _flottant_env(nom: str, defaut: float) -> float:
    valeur = os.environ.get(nom)
    return defaut if valeur is None else float(valeur)


def charger_config(
    artefacts: Path | None = None,
    version: str | None = None,
    catalogue: Path | None = None,
) -> Config:
    """Construit la configuration à partir du manifeste de l'artefact.

    Les paramètres métier peuvent être surchargés par `CHURN_PLANCHER_RISQUE`
    et `CHURN_CAPACITE` : réviser la capacité des équipes ne demande ni
    ré-entraînement ni redéploiement (§13.3).
    """
    artefacts = Path(artefacts or ARTEFACTS)
    version = version or VERSION_MODELE
    chemin_manifeste = artefacts / f"modele_churn_v{version}.json"
    if not chemin_manifeste.exists():
        raise FileNotFoundError(
            f"manifeste introuvable : {chemin_manifeste}. "
            "Exécuter §10.1 du notebook pour produire les artefacts."
        )
    manifeste = json.loads(chemin_manifeste.read_text(encoding="utf-8"))
    return Config(
        version=version,
        chemin_modele=artefacts / f"modele_churn_v{version}.joblib",
        chemin_valeur=artefacts
        / manifeste.get("modele_valeur", f"modele_valeur_v{version}.joblib"),
        chemin_manifeste=chemin_manifeste,
        chemin_catalogue=Path(catalogue or RACINE / "catalogue_plans.csv"),
        plancher_risque=_flottant_env("CHURN_PLANCHER_RISQUE", manifeste["plancher_risque"]),
        capacite_par_cycle=_flottant_env("CHURN_CAPACITE", manifeste["capacite_par_cycle"]),
        colonnes_attendues=list(manifeste["colonnes_attendues"]),
    )
