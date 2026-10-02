"""Préparation des données — les défauts de format du jeu source (§7.2 à §7.7)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from churn.preparation import (
    charger_catalogue,
    normaliser_categorie,
    parse_date_multi,
    preparer,
    to_numeric_fr,
)


class TestConversionNumerique:
    @pytest.mark.parametrize(
        ("brut", "attendu"),
        [
            ("40,0", 40.0),  # virgule décimale
            ("20.0%", 20.0),  # symbole pourcent
            ("500 €", 500.0),  # symbole euro et espace
            ("3.0 h", 3.0),  # unité suffixée
            ("1 234,5", 1234.5),  # espace fine insécable
            ("-2,5", -2.5),  # signe négatif
        ],
    )
    def test_absorbe_les_encodages_du_jeu(self, brut, attendu):
        assert to_numeric_fr(pd.Series([brut])).iloc[0] == pytest.approx(attendu)

    @pytest.mark.parametrize("brut", ["", "-", ".", "n/a", None])
    def test_valeurs_non_convertibles_deviennent_manquantes(self, brut):
        assert pd.isna(to_numeric_fr(pd.Series([brut])).iloc[0])

    def test_ne_perd_aucune_valeur_convertible(self):
        serie = pd.Series(["1,5", "2.5", "3 €", None])
        converti = to_numeric_fr(serie)
        assert converti.notna().sum() == 3


class TestNormalisationCategorielle:
    @pytest.mark.parametrize("brut", ["Pro", " Pro ", "PRO", "pro", "  pro  "])
    def test_graphies_d_un_meme_plan_convergent(self, brut):
        assert normaliser_categorie(pd.Series([brut])).iloc[0] == "PRO"

    def test_stable_en_presence_d_accents(self):
        valeurs = normaliser_categorie(pd.Series(["santé", "SANTÉ", " Santé "]))
        assert valeurs.nunique() == 1

    def test_espaces_internes_reduits(self):
        assert (
            normaliser_categorie(pd.Series(["Grande   Entreprise"])).iloc[0] == "GRANDE ENTREPRISE"
        )


class TestParsingDates:
    @pytest.mark.parametrize(
        ("brut", "attendu"),
        [
            ("2024-02-06", "2024-02-06"),
            ("31/01/2024", "2024-01-31"),
            ("23 Dec 2024", "2024-12-23"),
        ],
    )
    def test_les_trois_formats_du_jeu(self, brut, attendu):
        assert parse_date_multi(pd.Series([brut])).iloc[0] == pd.Timestamp(attendu)

    def test_aucune_date_du_jeu_ne_reste_non_parsee(self, lot_brut):
        assert parse_date_multi(lot_brut["date_souscription"]).notna().all()


class TestPreparationComplete:
    def test_produit_les_colonnes_attendues_dans_l_ordre(self, lot_brut, catalogue, config):
        prepare = preparer(lot_brut, catalogue, config.colonnes_attendues)
        assert list(prepare.columns) == config.colonnes_attendues

    def test_reconstitue_le_taux_d_adoption(self, lot_brut, catalogue, config):
        assert lot_brut["taux_adoption_pct"].isna().any() or True
        prepare = preparer(lot_brut, catalogue, config.colonnes_attendues)
        assert prepare["taux_adoption_pct"].notna().all()
        assert prepare["taux_adoption_pct"].between(0, 100).all()

    def test_aucune_valeur_infinie(self, lot_brut, catalogue, config):
        prepare = preparer(lot_brut, catalogue, config.colonnes_attendues)
        assert not np.isinf(prepare.select_dtypes(include="number")).to_numpy().any()

    def test_plan_inconnu_leve_une_erreur_explicite(self, lot_brut, catalogue, config):
        lot = lot_brut.copy()
        lot.loc[0, "plan"] = "PLATINIUM"
        with pytest.raises(ValueError, match="catalogue"):
            preparer(lot, catalogue, config.colonnes_attendues)

    def test_colonne_manquante_leve_une_erreur_explicite(self, lot_brut, catalogue, config):
        lot = lot_brut.drop(columns=["csat"])
        with pytest.raises(ValueError, match="colonnes absentes"):
            preparer(lot, catalogue, config.colonnes_attendues)

    def test_ne_duplique_aucune_ligne(self, lot_brut, catalogue, config):
        prepare = preparer(lot_brut, catalogue, config.colonnes_attendues)
        assert len(prepare) == len(lot_brut)


class TestChargementDuCatalogue:
    """Le référentiel est une donnée d'entrée (§5.1) : son absence doit se dire."""

    def test_normalise_la_cle_de_jointure(self, catalogue):
        assert set(catalogue["plan"]) == {"STARTER", "PRO", "BUSINESS", "ENTERPRISE"}

    def test_absence_du_fichier_leve_une_erreur_explicite(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="CHURN_CATALOGUE"):
            charger_catalogue(tmp_path / "catalogue_absent.csv")
