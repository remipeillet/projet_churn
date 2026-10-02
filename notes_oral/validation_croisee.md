# Plis et validation croisée (§8, §9) — fiche de préparation orale

Ce qu'est un **pli**, pourquoi la validation croisée, et ce qu'elle protège. Vocabulaire mobilisé dès
§8.1 (baseline) et central en §9 (comparaison et réglage).

Fiches liées : [lecture_distributions.md](lecture_distributions.md) (§6.2) ·
[detection_leurres.md](detection_leurres.md) (§6.4) · [auc_univariee.md](auc_univariee.md) (§6.5) ·
[log_odds.md](log_odds.md) · [derive_psi.md](derive_psi.md) (dérive, PSI) · [metriques_regression.md](metriques_regression.md) (R², MAE, RMSE) · [metriques_classification.md](metriques_classification.md) (précision, rappel, F1).

---

## 1. Définition

Un **pli** (*fold*) est un des morceaux en lesquels on découpe le jeu d'entraînement pour la validation
croisée.

`StratifiedKFold(n_splits=5)` découpe les **4 000 comptes du train en 5 paquets de 800**, puis entraîne
et évalue **cinq fois** :

| Tour | Entraînement | Évaluation |
|---|---|---|
| 1 | plis 2, 3, 4, 5 (3 200 comptes) | pli 1 (800 comptes) |
| 2 | plis 1, 3, 4, 5 | pli 2 |
| 3 | plis 1, 2, 4, 5 | pli 3 |
| 4 | plis 1, 2, 3, 5 | pli 4 |
| 5 | plis 1, 2, 3, 4 | pli 5 |

Chaque compte sert donc **une fois à évaluer** et **quatre fois à entraîner**. On obtient cinq scores,
dont on rapporte la **moyenne** et l'**écart-type** — exactement ce qu'affiche le tableau de §8.1
(`roc_auc` 0,8907 ; `roc_auc_ecart` 0,0085).

> **Vocabulaire.** On parle de **validation croisée à k plis** (*k-fold cross-validation*), ici k = 5.
> Le choix de 5 ou 10 est conventionnel : 5 suffit sur 4 000 lignes et coûte deux fois moins cher en
> calcul.

---

## 2. Pourquoi cinq fois plutôt qu'une

**Pour ne pas gaspiller de données.** Réserver un jeu de validation fixe consommerait 800 comptes qui
ne serviraient jamais à entraîner. En tournant, chaque compte sert aux deux usages.

**Pour mesurer la stabilité.** Un score unique ne dit pas s'il est reproductible ; l'écart-type entre
plis, si.

> **L'exemple à citer.** En §6.5, `commentaire_csm` fait passer l'AUC de 0,8900 à 0,8884. Conclure à
> une dégradation serait une erreur : l'écart de 0,0016 est **inférieur à l'écart-type entre plis**
> (± 0,011). C'est le dispositif des plis qui autorise à dire « c'est du bruit » — sans lui, la
> variation aurait pu passer pour un résultat.

**Pour choisir sans toucher au jeu de test.** Le jeu de test de §7.8 est **scellé jusqu'à §12** : toute
la comparaison de modèles (§8.2) et le réglage des hyperparamètres (§9.2) se font par les plis, **sur
le train seul**.

---

## 3. Le rôle de « stratifié »

`StratifiedKFold` garantit que chaque pli conserve la prévalence de **28 %** de churners.

Avec un découpage purement aléatoire, un pli pourrait tomber à 24 % et un autre à 32 %. Deux
conséquences : les **PR-AUC des plis ne seraient plus comparables** entre eux — cette métrique se lit
contre la prévalence —, et l'écart-type mesurerait le hasard du découpage autant que l'instabilité du
modèle.

---

## 4. Ce que le pli protège — l'argument anti-fuite

Dans le notebook, le `Pipeline` fait que l'**imputation** et la **standardisation** sont ajustées
*à l'intérieur* de chaque tour, sur les 3 200 comptes d'entraînement de ce tour uniquement.

Si l'imputation avait été faite avant la validation croisée, la médiane aurait été calculée sur les
4 000 comptes — **y compris les 800 sur lesquels on s'apprête à évaluer**. C'est une fuite discrète :
elle gonfle le score de quelques millièmes et **aucune erreur ne la signale**.

C'est précisément la raison pour laquelle §7.2 a renvoyé l'imputation au pipeline plutôt que de
l'appliquer dans la préparation.

---

## 5. Trois niveaux de protection à ne pas confondre

| Dispositif | Ce qu'il protège | Section |
|---|---|---|
| **Séparation train / test** | L'évaluation finale, contre les choix du praticien | §7.8, §12 |
| **Plis de validation croisée** | La sélection de modèle, contre la chance d'un découpage unique | §8, §9 |
| **`Pipeline`** | Chaque pli, contre la fuite des statistiques de préparation | §7.2, §8.1 |

---

## 6. Questions probables du jury — réponses courtes

**« Qu'appelez-vous un pli ? »**
Un des cinq paquets en lesquels le jeu d'entraînement est découpé. Le modèle est entraîné sur quatre
d'entre eux et évalué sur le cinquième, et l'opération tourne cinq fois : chaque compte sert une fois à
évaluer et quatre fois à entraîner.

**« Pourquoi ne pas simplement garder un jeu de validation fixe ? »**
Il consommerait 800 comptes qui ne serviraient jamais à entraîner, et il ne donnerait qu'un score
unique — sans indication de stabilité. La validation croisée fournit une moyenne **et** un écart-type.

**« Pourquoi stratifier ? »**
Pour que chaque pli conserve la prévalence de 28 %. Sinon les PR-AUC des plis ne sont plus comparables
et l'écart-type mesure le hasard du découpage autant que le modèle.

**« Pourquoi k = 5 et pas 10 ? »**
Convention ; 5 suffit sur 4 000 lignes de train et divise par deux le coût de calcul. Au-delà, le gain
sur la précision de l'estimation est marginal.

**« La validation croisée remplace-t-elle le jeu de test ? »**
Non. Elle sert à **choisir** — modèle, hyperparamètres. Le jeu de test sert à **mesurer** une fois, à la
fin. Un jeu de test interrogé pour choisir cesse d'être un jeu de test.
