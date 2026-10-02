"""Règle de priorisation risque × valeur (§9.4)."""

from __future__ import annotations

import numpy as np

from churn.modele import prioriser


class TestPriorisation:
    def test_aucun_compte_sous_le_plancher_n_est_signale(self):
        probabilites = np.array([0.05, 0.25, 0.95, 0.40])
        valeurs = np.array([1e6, 1e6, 1.0, 1e5])  # les plus gros sont les moins risqués
        selection, _ = prioriser(probabilites, valeurs, capacite=4, plancher=0.30)
        assert not selection[[0, 1]].any()
        assert selection[[2, 3]].all()

    def test_la_capacite_est_respectee(self):
        probabilites = np.full(100, 0.9)
        valeurs = np.arange(100, dtype=float)
        selection, _ = prioriser(probabilites, valeurs, capacite=20, plancher=0.30)
        assert selection.sum() == 20

    def test_l_ordre_suit_la_risque_de_perte(self):
        probabilites = np.array([0.60, 0.85])
        valeurs = np.array([30_000.0, 2_000.0])  # l'exemple de §9.4
        selection, rangs = prioriser(probabilites, valeurs, capacite=2, plancher=0.30)
        assert selection.all()
        assert rangs[0] == 1 and rangs[1] == 2  # 18 k€ avant 1,7 k€

    def test_le_tri_par_risque_donnerait_l_ordre_inverse(self):
        probabilites = np.array([0.60, 0.85])
        assert np.argmax(probabilites) == 1  # le risque seul classerait B premier

    def test_rangs_absents_hors_selection(self):
        probabilites = np.array([0.9, 0.9, 0.1])
        valeurs = np.array([10.0, 5.0, 1000.0])
        selection, rangs = prioriser(probabilites, valeurs, capacite=1, plancher=0.30)
        assert selection.sum() == 1
        assert np.isnan(rangs[~selection]).all()

    def test_capacite_nulle_ne_signale_personne(self):
        selection, _ = prioriser(np.array([0.9]), np.array([1.0]), capacite=0, plancher=0.3)
        assert not selection.any()
