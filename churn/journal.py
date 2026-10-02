"""Journal des exécutions — détection de l'échec et de la non-exécution.

Un batch mensuel qui échoue à 3 h du matin ne produit aucun signal : personne ne
s'en aperçoit avant le cycle suivant, et un cycle perdu, ce sont des comptes non
signalés. Chaque exécution laisse donc une trace, et `verifier_fraicheur`
implémente un *dead man's switch* : il détecte l'**absence** d'exécution, pas
seulement l'échec.
"""

from __future__ import annotations

import json
import os
import platform
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from churn.config import ARTEFACTS

CHEMIN_JOURNAL = Path(os.environ.get("CHURN_JOURNAL", ARTEFACTS / "journal_executions.jsonl"))
# Un cycle mensuel : au-delà de 35 jours sans exécution réussie, il en manque une.
FRAICHEUR_MAX_JOURS = int(os.environ.get("CHURN_FRAICHEUR_JOURS", "35"))


@dataclass
class Execution:
    """Trace d'un cycle de scoring."""

    horodatage: str
    statut: str  # "succes" | "echec"
    modele_version: str
    comptes: int = 0
    alertes: int = 0
    plancher_risque: float | None = None
    duree_s: float | None = None
    message: str | None = None
    machine: str = platform.node()


def enregistrer_execution(execution: Execution, chemin: Path | None = None) -> Path:
    """Ajoute une ligne au journal (format JSONL, append-only)."""
    chemin = Path(chemin or CHEMIN_JOURNAL)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("a", encoding="utf-8") as fichier:
        fichier.write(json.dumps(asdict(execution), ensure_ascii=False) + "\n")
    return chemin


def lire_journal(chemin: Path | None = None) -> list[dict]:
    chemin = Path(chemin or CHEMIN_JOURNAL)
    if not chemin.exists():
        return []
    return [
        json.loads(ligne)
        for ligne in chemin.read_text(encoding="utf-8").splitlines()
        if ligne.strip()
    ]


def derniere_execution(statut: str = "succes", chemin: Path | None = None) -> dict | None:
    """Dernière exécution du statut demandé, ou None si le journal est vide."""
    executions = [e for e in lire_journal(chemin) if e.get("statut") == statut]
    return max(executions, key=lambda e: e["horodatage"]) if executions else None


def verifier_fraicheur(
    max_jours: int = FRAICHEUR_MAX_JOURS, chemin: Path | None = None, maintenant=None
) -> tuple[bool, str]:
    """*Dead man's switch* : une exécution réussie a-t-elle eu lieu récemment ?

    Renvoie (conforme, message). Un batch mensuel qui n'a pas tourné depuis plus
    de `max_jours` signale une non-exécution — la panne la plus difficile à
    détecter sur un job planifié.
    """
    maintenant = maintenant or datetime.now(UTC)
    derniere = derniere_execution("succes", chemin)
    if derniere is None:
        return False, "aucune exécution réussie enregistrée"

    horodatage = datetime.fromisoformat(derniere["horodatage"])
    age = maintenant - horodatage
    if age > timedelta(days=max_jours):
        return False, (
            f"dernière exécution réussie il y a {age.days} jours "
            f"({horodatage:%Y-%m-%d}) — au-delà du seuil de {max_jours} jours"
        )
    return True, f"dernière exécution réussie il y a {age.days} jours ({horodatage:%Y-%m-%d})"
