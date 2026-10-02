"""Instruments de surveillance : dérive et contrôle anti-fuite (§13.1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from churn.surveillance import (
    controle_antifuite,
    controle_derive,
    indice_stabilite,
    statut_derive,
)

ALEA = np.random.default_rng(42)


class TestIndiceStabilite:
    def test_nul_sur_deux_distributions_identiques(self):
        valeurs = ALEA.normal(size=2000)
        assert indice_stabilite(valeurs, valeurs) == pytest.approx(0.0, abs=1e-9)

    def test_faible_sur_deux_tirages_de_la_meme_loi(self):
        assert indice_stabilite(ALEA.normal(size=5000), ALEA.normal(size=5000)) < 0.10

    def test_detecte_un_decalage_franc(self):
        assert indice_stabilite(ALEA.normal(size=5000), ALEA.normal(loc=2, size=5000)) > 0.25

    def test_symetrique_en_ordre_de_grandeur(self):
        a, b = ALEA.normal(size=3000), ALEA.normal(loc=1, size=3000)
        assert indice_stabilite(a, b) == pytest.approx(indice_stabilite(b, a), rel=0.5)

    def test_serie_vide_sans_erreur(self):
        assert indice_stabilite(pd.Series(dtype=float), pd.Series([1.0, 2.0])) == 0.0

    @pytest.mark.parametrize(
        ("psi", "attendu"), [(0.02, "stable"), (0.15, "vigilance"), (0.40, "DERIVE")]
    )
    def test_statuts(self, psi, attendu):
        assert statut_derive(psi) == attendu


class TestControleDerive:
    def test_tableau_complet_et_trie(self):
        reference = pd.DataFrame({"a": ALEA.normal(size=1000), "b": ALEA.normal(size=1000)})
        courant = pd.DataFrame({"a": ALEA.normal(size=1000), "b": ALEA.normal(loc=3, size=1000)})
        tableau = controle_derive(reference, courant)
        assert list(tableau.columns) == ["variable", "psi", "statut", "manquants_%"]
        assert tableau["psi"].is_monotonic_decreasing
        assert tableau.iloc[0]["variable"] == "b"
        assert tableau.iloc[0]["statut"] == "DERIVE"


class TestControleAntifuite:
    def test_detecte_une_variable_fuyante(self):
        cible = pd.Series(ALEA.integers(0, 2, size=1000))
        donnees = pd.DataFrame(
            {
                "bruit": ALEA.normal(size=1000),
                "copie_de_la_cible": cible + ALEA.normal(scale=0.01, size=1000),
            }
        )
        resultat = controle_antifuite(donnees, cible)
        suspectes = set(resultat.query("suspecte")["variable"])
        assert suspectes == {"copie_de_la_cible"}

    def test_ne_signale_rien_sur_des_variables_saines(self):
        cible = pd.Series(ALEA.integers(0, 2, size=1000))
        donnees = pd.DataFrame({"bruit": ALEA.normal(size=1000)})
        assert not controle_antifuite(donnees, cible)["suspecte"].any()
