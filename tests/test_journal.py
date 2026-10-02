"""Journal des exécutions et détection de non-exécution (§11.4)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from churn.cli import main
from churn.journal import (
    Execution,
    derniere_execution,
    enregistrer_execution,
    lire_journal,
    verifier_fraicheur,
)


def _execution(jours_avant: int, statut: str = "succes") -> Execution:
    horodatage = datetime.now(UTC) - timedelta(days=jours_avant)
    return Execution(
        horodatage=horodatage.isoformat(timespec="seconds"),
        statut=statut,
        modele_version="1.0.0",
        comptes=50,
        alertes=10,
    )


class TestJournal:
    def test_journal_absent_est_vide(self, tmp_path):
        assert lire_journal(tmp_path / "absent.jsonl") == []

    def test_les_executions_s_ajoutent_sans_ecraser(self, tmp_path):
        journal = tmp_path / "j.jsonl"
        enregistrer_execution(_execution(2), journal)
        enregistrer_execution(_execution(1), journal)
        assert len(lire_journal(journal)) == 2

    def test_derniere_execution_ignore_les_echecs(self, tmp_path):
        journal = tmp_path / "j.jsonl"
        enregistrer_execution(_execution(10, "succes"), journal)
        enregistrer_execution(_execution(1, "echec"), journal)
        derniere = derniere_execution("succes", journal)
        assert derniere["statut"] == "succes"


class TestDeadManSwitch:
    def test_journal_vide_signale_une_absence(self, tmp_path):
        conforme, message = verifier_fraicheur(chemin=tmp_path / "absent.jsonl")
        assert not conforme and "aucune" in message

    def test_cycle_recent_conforme(self, tmp_path):
        journal = tmp_path / "j.jsonl"
        enregistrer_execution(_execution(3), journal)
        assert verifier_fraicheur(max_jours=35, chemin=journal)[0]

    def test_cycle_manquant_detecte(self, tmp_path):
        journal = tmp_path / "j.jsonl"
        enregistrer_execution(_execution(60), journal)
        conforme, message = verifier_fraicheur(max_jours=35, chemin=journal)
        assert not conforme and "60 jours" in message

    def test_un_echec_recent_ne_masque_pas_l_absence_de_succes(self, tmp_path):
        journal = tmp_path / "j.jsonl"
        enregistrer_execution(_execution(60, "succes"), journal)
        enregistrer_execution(_execution(1, "echec"), journal)
        assert not verifier_fraicheur(max_jours=35, chemin=journal)[0]


class TestIntegrationLigneDeCommande:
    def test_le_scoring_consigne_son_execution(self, tmp_path, config):
        journal = tmp_path / "j.jsonl"
        code = main(
            [
                "--artefacts",
                str(config.chemin_manifeste.parent),
                "score",
                "--lot",
                "churn_saas_echantillon.csv",
                "--sortie",
                str(tmp_path / "scores.csv"),
                "--journal",
                str(journal),
            ]
        )
        assert code == 0
        trace = lire_journal(journal)[-1]
        assert trace["statut"] == "succes"
        assert trace["comptes"] == 50 and trace["alertes"] == 10
        assert trace["duree_s"] > 0

    def test_un_echec_est_consigne_puis_remonte(self, tmp_path, config, lot_brut):
        journal = tmp_path / "j.jsonl"
        invalide = tmp_path / "invalide.csv"
        lot = lot_brut.copy()
        lot.loc[0, "plan"] = "PLATINIUM"
        lot.to_csv(invalide, index=False)

        code = main(
            [
                "--artefacts",
                str(config.chemin_manifeste.parent),
                "score",
                "--lot",
                str(invalide),
                "--journal",
                str(journal),
            ]
        )
        assert code == 3
        trace = lire_journal(journal)[-1]
        assert trace["statut"] == "echec" and "PLATINIUM" in trace["message"]

    def test_commande_statut(self, tmp_path):
        journal = tmp_path / "j.jsonl"
        enregistrer_execution(_execution(1), journal)
        assert main(["statut", "--journal", str(journal)]) == 0
        enregistrer_execution(_execution(0, "echec"), journal)
        assert main(["statut", "--journal", str(journal), "--max-jours", "0"]) == 1
