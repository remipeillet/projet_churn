"""Chargement des artefacts et règle de priorisation (§9.4, §10.1)."""

from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np

from churn.config import Config


def prioriser(
    probabilites: np.ndarray, valeurs: np.ndarray, capacite: int, plancher: float
) -> tuple[np.ndarray, np.ndarray]:
    """Applique la règle de §9.4 et renvoie (sélection, rangs).

    Étape 1 — éligibilité : probabilité >= plancher de risque. Un compte moins
    risqué que la moyenne du portefeuille n'est jamais signalé au seul motif de
    sa taille.
    Étape 2 — priorisation : risque de perte décroissant, dans la limite de la
    capacité de traitement.
    """
    probabilites = np.asarray(probabilites, dtype=float)
    risque_de_perte = probabilites * np.asarray(valeurs, dtype=float)
    eligibles = np.where(probabilites >= plancher)[0]
    retenus = eligibles[np.argsort(-risque_de_perte[eligibles])][: max(capacite, 0)]

    selection = np.zeros(len(probabilites), dtype=bool)
    selection[retenus] = True
    rangs = np.full(len(probabilites), np.nan)
    rangs[retenus] = np.arange(1, len(retenus) + 1)
    return selection, rangs


@dataclass
class Artefacts:
    """Les deux modèles du dispositif, chargés depuis le disque."""

    churn: object
    valeur: object
    config: Config

    @classmethod
    def charger(cls, config: Config) -> Artefacts:
        return cls(
            churn=joblib.load(config.chemin_modele),
            valeur=joblib.load(config.chemin_valeur),
            config=config,
        )

    def facteurs(self, prepare, k: int = 3) -> list[str]:
        """Facteurs explicatifs par compte : contribution `coefficient x valeur`.

        Propre aux modèles linéaires — c'est l'un des motifs du choix de §9.1.
        """
        preparation = self.churn.named_steps["preparation"]
        colonnes = preparation.get_feature_names_out()
        contributions = preparation.transform(prepare) * self.churn.named_steps["modele"].coef_[0]

        libelles = []
        for ligne in contributions:
            ordre = np.argsort(-ligne)
            retenus = [colonnes[j] for j in ordre[:k] if ligne[j] > 0]
            libelles.append(" · ".join(retenus) if retenus else "aucun facteur aggravant")
        return libelles
