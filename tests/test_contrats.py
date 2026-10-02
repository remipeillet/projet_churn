"""Contrats de données à l'ingestion et en sortie (§10.2)."""

from __future__ import annotations

import pandas as pd
import pytest
from pandera.errors import SchemaError

from churn.contrats import rapport_qualite, valider_lot


class TestContratEntree:
    def test_le_jeu_de_reference_respecte_le_contrat(self, lot_brut):
        assert len(valider_lot(lot_brut)) == len(lot_brut)

    def test_identifiant_duplique_rejete(self, lot_brut):
        lot = pd.concat([lot_brut, lot_brut.head(1)], ignore_index=True)
        with pytest.raises(SchemaError):
            valider_lot(lot)

    def test_plan_hors_referentiel_rejete(self, lot_brut):
        lot = lot_brut.copy()
        lot.loc[0, "plan"] = "PLATINIUM"
        with pytest.raises(SchemaError):
            valider_lot(lot)

    def test_colonne_requise_absente_rejetee(self, lot_brut):
        with pytest.raises(SchemaError):
            valider_lot(lot_brut.drop(columns=["csat"]))

    def test_identifiant_manquant_rejete(self, lot_brut):
        lot = lot_brut.copy()
        lot.loc[0, "client_id"] = None
        with pytest.raises(SchemaError):
            valider_lot(lot)

    def test_casse_du_plan_toleree(self, lot_brut):
        lot = lot_brut.copy()
        lot.loc[0, "plan"] = " pro "
        assert len(valider_lot(lot)) == len(lot)


class TestRapportQualite:
    def test_denombre_les_manquants(self, lot_brut):
        rapport = rapport_qualite(lot_brut)
        assert set(rapport.columns) == {"colonne", "manquants_%"}
        assert rapport["manquants_%"].between(0, 100).all()
