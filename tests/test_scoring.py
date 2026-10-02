"""Scoring bout-en-bout — la chaîne complète sur un lot brut (§10.2)."""

from __future__ import annotations

import pandas as pd
import pytest
from pandera.errors import SchemaError

from churn.cli import main


class TestScoringBoutEnBout:
    def test_absorbe_un_lot_brut_non_nettoye(self, scoreur, lot_brut):
        scores = scoreur.scorer(lot_brut)
        assert len(scores) == len(lot_brut)
        assert scores["probabilite_churn"].between(0, 1).all()

    def test_respecte_la_capacite(self, scoreur, lot_brut, config):
        scores = scoreur.scorer(lot_brut)
        attendu = round(config.capacite_par_cycle * len(lot_brut))
        assert scores["alerte"].sum() == attendu

    def test_aucun_compte_signale_sous_le_plancher(self, scoreur, lot_brut, config):
        scores = scoreur.scorer(lot_brut)
        signales = scores[scores["alerte"]]
        assert (signales["probabilite_churn"] >= config.plancher_risque).all()

    def test_les_signales_sont_ordonnes_par_perte_esperee(self, scoreur, lot_brut):
        signales = scoreur.scorer(lot_brut).query("alerte")
        assert signales["perte_esperee_eur"].is_monotonic_decreasing
        assert signales["priorite"].tolist() == list(range(1, len(signales) + 1))

    def test_chaque_compte_signale_porte_ses_facteurs(self, scoreur, lot_brut):
        signales = scoreur.scorer(lot_brut).query("alerte")
        assert (signales["facteurs_principaux"].str.len() > 0).all()

    def test_reproductible(self, scoreur, lot_brut):
        premier = scoreur.scorer(lot_brut)
        second = scoreur.scorer(lot_brut)
        pd.testing.assert_frame_equal(premier, second)

    def test_la_version_du_modele_accompagne_chaque_score(self, scoreur, lot_brut, config):
        scores = scoreur.scorer(lot_brut)
        assert (scores["modele_version"] == config.version).all()

    def test_capacite_explicite_prioritaire(self, scoreur, lot_brut):
        assert scoreur.scorer(lot_brut, capacite=3)["alerte"].sum() == 3

    def test_plan_inconnu_interrompt_le_scoring(self, scoreur, lot_brut):
        lot = lot_brut.copy()
        lot.loc[0, "plan"] = "PLATINIUM"
        with pytest.raises(SchemaError):
            scoreur.scorer(lot)


class TestLigneDeCommande:
    def test_score_ecrit_un_fichier(self, tmp_path, config):
        sortie = tmp_path / "scores.csv"
        code = main(
            [
                "--artefacts",
                str(config.chemin_manifeste.parent),
                "score",
                "--lot",
                "churn_saas_echantillon.csv",
                "--sortie",
                str(sortie),
            ]
        )
        assert code == 0
        scores = pd.read_csv(sortie)
        assert {"priorite", "client_id", "probabilite_churn", "alerte"} <= set(scores.columns)

    def test_verifier_valide_le_contrat(self):
        assert main(["verifier", "--lot", "churn_saas_echantillon.csv"]) == 0

    def test_verifier_signale_un_lot_non_conforme(self, tmp_path, lot_brut):
        invalide = tmp_path / "invalide.csv"
        lot = lot_brut.copy()
        lot.loc[0, "plan"] = "PLATINIUM"
        lot.to_csv(invalide, index=False)
        assert main(["verifier", "--lot", str(invalide)]) == 2
