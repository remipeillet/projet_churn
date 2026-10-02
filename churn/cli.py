"""Point d'entrée en ligne de commande — ce que le planificateur appelle.

python -m churn score --lot comptes.csv --sortie scores.csv
python -m churn verifier --lot comptes.csv
python -m churn derive --reference ref.csv --courant lot.csv
python -m churn statut                      # le cycle a-t-il bien tourné ?
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from churn.config import charger_config
from churn.contrats import rapport_qualite, valider_lot
from churn.journal import Execution, enregistrer_execution, verifier_fraicheur
from churn.preparation import lire_lot_brut
from churn.scoring import Scoreur
from churn.surveillance import controle_derive


def _commande_score(arguments: argparse.Namespace) -> int:
    """Score un lot, puis consigne l'exécution — succès comme échec."""
    config = charger_config(artefacts=arguments.artefacts, version=arguments.version)
    depart = time.perf_counter()

    def _tracer(statut: str, comptes: int = 0, alertes: int = 0, message: str | None = None):
        if arguments.sans_journal:
            return
        enregistrer_execution(
            Execution(
                horodatage=datetime.now(UTC).isoformat(timespec="seconds"),
                statut=statut,
                modele_version=config.version,
                comptes=comptes,
                alertes=alertes,
                plancher_risque=config.plancher_risque,
                duree_s=round(time.perf_counter() - depart, 3),
                message=message,
            ),
            chemin=arguments.journal,
        )

    try:
        brut = lire_lot_brut(arguments.lot)
        scores = Scoreur(config).scorer(brut, capacite=arguments.capacite)
    except Exception as erreur:
        # Un échec silencieux est la panne la plus coûteuse sur un batch mensuel :
        # il est consigné avant d'être remonté.
        _tracer("echec", message=f"{type(erreur).__name__}: {erreur}")
        print(f"ÉCHEC DU CYCLE : {erreur}", file=sys.stderr)
        return 3

    alertes = int(scores["alerte"].sum())
    print(f"Lot scoré           : {len(scores)} comptes")
    print(f"Comptes signalés    : {alertes} ({alertes / len(scores):.1%})")
    print(f"Plancher de risque  : {config.plancher_risque}")
    print(f"Version du modèle   : {config.version}")

    if arguments.sortie:
        Path(arguments.sortie).parent.mkdir(parents=True, exist_ok=True)
        scores.to_csv(arguments.sortie, index=False, encoding="utf-8")
        print(f"Écrit dans          : {arguments.sortie}")
    else:
        colonnes = ["priorite", "client_id", "probabilite_churn", "risque_de_perte_eur"]
        print("\n" + scores.head(10)[colonnes].to_string(index=False))

    _tracer("succes", comptes=len(scores), alertes=alertes)
    return 0


def _commande_statut(arguments: argparse.Namespace) -> int:
    """Dead man's switch : vérifie qu'un cycle a bien tourné récemment."""
    conforme, message = verifier_fraicheur(max_jours=arguments.max_jours, chemin=arguments.journal)
    if not conforme:
        print(f"CYCLE MANQUANT : {message}", file=sys.stderr)
        return 1
    print(f"Cycle à jour : {message}")
    return 0


def _commande_verifier(arguments: argparse.Namespace) -> int:
    brut = lire_lot_brut(arguments.lot)
    try:
        valider_lot(brut)
    except Exception as erreur:  # pandera.errors.SchemaError
        print(f"CONTRAT NON RESPECTÉ : {erreur}", file=sys.stderr)
        return 2
    print(f"Contrat d'entrée respecté : {len(brut)} comptes, {brut.shape[1]} colonnes")
    print("\nTaux de manquants par colonne :")
    qualite = rapport_qualite(brut)
    print(qualite[qualite["manquants_%"] > 0].to_string(index=False))
    return 0


def _commande_derive(arguments: argparse.Namespace) -> int:
    config = charger_config(artefacts=arguments.artefacts, version=arguments.version)
    scoreur = Scoreur(config)
    from churn.preparation import preparer

    reference = preparer(
        lire_lot_brut(arguments.reference), scoreur.catalogue, config.colonnes_attendues
    )
    courant = preparer(
        lire_lot_brut(arguments.courant), scoreur.catalogue, config.colonnes_attendues
    )
    tableau = controle_derive(reference, courant)
    print(tableau.to_string(index=False))

    en_derive = tableau[tableau["statut"] == "DERIVE"]
    if not en_derive.empty:
        print(f"\nDÉRIVE DÉTECTÉE sur {len(en_derive)} variable(s)", file=sys.stderr)
        return 1
    print("\nAucune dérive : toutes les variables sous le seuil de vigilance (0,10).")
    return 0


def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        prog="churn", description="Dispositif de scoring du risque de résiliation"
    )
    parseur.add_argument("--artefacts", type=Path, default=None, help="dossier des artefacts")
    parseur.add_argument("--version", default=None, help="version du modèle à charger")
    sous = parseur.add_subparsers(dest="commande", required=True)

    score = sous.add_parser("score", help="scorer un lot de comptes bruts")
    score.add_argument("--lot", type=Path, required=True)
    score.add_argument("--sortie", type=Path, default=None)
    score.add_argument("--capacite", type=int, default=None, help="nombre de comptes à signaler")
    score.add_argument("--journal", type=Path, default=None, help="journal des exécutions")
    score.add_argument("--sans-journal", action="store_true", help="ne rien consigner")
    score.set_defaults(fonction=_commande_score)

    verifier = sous.add_parser("verifier", help="valider le contrat d'entrée d'un lot")
    verifier.add_argument("--lot", type=Path, required=True)
    verifier.set_defaults(fonction=_commande_verifier)

    derive = sous.add_parser("derive", help="comparer deux lots et mesurer la dérive")
    derive.add_argument("--reference", type=Path, required=True)
    derive.add_argument("--courant", type=Path, required=True)
    derive.set_defaults(fonction=_commande_derive)

    statut = sous.add_parser("statut", help="vérifier qu'un cycle a tourné récemment")
    statut.add_argument("--max-jours", type=int, default=35, dest="max_jours")
    statut.add_argument("--journal", type=Path, default=None)
    statut.set_defaults(fonction=_commande_statut)
    return parseur


def main(argv: list[str] | None = None) -> int:
    arguments = construire_parseur().parse_args(argv)
    return arguments.fonction(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
