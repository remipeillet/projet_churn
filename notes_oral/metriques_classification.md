# Métriques de classification (§8.3, §12.1) — fiche de préparation orale

Les métriques du modèle de churn : lesquelles sont retenues, laquelle est écartée, et pourquoi. La
distinction structurante est entre **métriques de rang** — qui évaluent le classement, tous seuils
confondus — et **métriques de décision**, qui supposent un seuil déjà fixé.

Fiches liées : [auc_univariee.md](auc_univariee.md) (§6.5) ·
[metriques_regression.md](metriques_regression.md) (R², MAE, RMSE) ·
[validation_croisee.md](validation_croisee.md) · [log_odds.md](log_odds.md) ·
[derive_psi.md](derive_psi.md).

---

## 0. La matrice de confusion, socle de tout

Au seuil retenu, chaque compte tombe dans une case. Sur le jeu de test (1 000 comptes, 280
résiliations) :

| | Prédit : conservé | Prédit : à risque |
|---|---|---|
| **Réel : conservé** | 651 vrais négatifs | **69 faux positifs** — sollicitations inutiles |
| **Réel : résilié** | **149 faux négatifs** — comptes perdus | 131 vrais positifs |

Toutes les métriques qui suivent ne sont que des façons de résumer ces quatre nombres.

---

## 1. Les deux mesures de base

$$\text{précision} = \frac{VP}{VP + FP} \qquad \text{rappel} = \frac{VP}{VP + FN}$$

| Mesure | Question | Valeur ici |
|---|---|---|
| **Précision** | Parmi les comptes que je signale, combien partaient vraiment ? | **0,655** |
| **Rappel** | Parmi les comptes qui partent, combien ai-je signalés ? | **0,468** |

Elles varient **en sens inverse** quand le seuil bouge : abaisser le seuil augmente le rappel et
dégrade la précision. Aucune des deux ne se lit seule.

> **L'exactitude (*accuracy*) est disqualifiée d'emblée.** Avec 28 % de churn, un modèle qui prédirait
> « aucune résiliation » pour tout le monde atteindrait **72 %** d'exactitude sans rien détecter
> (§6.1). Elle n'apparaît nulle part dans le document.

---

## 2. Les métriques retenues : ROC-AUC et PR-AUC

Ce sont des **métriques de rang** : elles évaluent l'ordre dans lequel le modèle classe les comptes,
**indépendamment de tout seuil**. C'est exactement ce que demande le cas d'usage — hiérarchiser un
portefeuille, pas rendre un verdict (§2.2).

| Métrique | Ce qu'elle mesure | Référence | Valeur (test) |
|---|---|---|---|
| **ROC-AUC** | Probabilité qu'un churner tiré au hasard ait un score plus élevé qu'un non-churner | 0,5 = hasard | **0,883** |
| **PR-AUC** | Qualité du compromis précision/rappel sur la classe minoritaire | la prévalence = 0,280 | **0,762** |

**Pourquoi les deux.** La ROC-AUC est insensible au déséquilibre — elle se calcule par paires, un
positif contre un négatif — ce qui la rend stable mais aveugle au **volume** de faux positifs. La
PR-AUC, elle, reste sensible à ce volume, c'est-à-dire au temps CSM dépensé pour rien (§4.2). Elle est
aussi la plus instable des deux, ce qui en fait le **capteur précoce** du suivi en production (§13.1).

---

## 3. Le F1 : définition, et pourquoi il est écarté

$$F_1 = 2 \times \frac{\text{précision} \times \text{rappel}}{\text{précision} + \text{rappel}}$$

C'est la **moyenne harmonique** de la précision et du rappel. Ce choix sanctionne le déséquilibre
entre les deux : un modèle à 100 % de précision et 1 % de rappel obtient un F1 de **0,02**, là où une
moyenne arithmétique donnerait 0,50. Le F1 ne récompense donc que les modèles bons **sur les deux
tableaux à la fois**.

> **Sa valeur ici : 0,546.** Il apparaît dans le `classification_report` de §12.1, colonne
> `f1-score`, ligne `resilie`. Il n'est utilisé nulle part pour décider.

**Cinq raisons de ne pas s'en servir :**

| Raison | Détail |
|---|---|
| **1. Il suppose un seuil** | Le F1 se calcule sur une décision binaire. Or §8.3 compare les modèles **avant** tout choix de seuil : l'utiliser aurait figé un seuil arbitraire dans la comparaison, et aurait pu en inverser le classement pour une raison étrangère à la qualité des modèles |
| **2. Il pose que les deux erreurs se valent** | C'est le cas β = 1 de la famille F<sub>β</sub>. §4.2 établit l'inverse : un faux négatif coûte le MRR et la valeur vie résiduelle, un faux positif une heure de CSM. Un F2, qui pondère le rappel deux fois plus, serait déjà plus défendable |
| **3. Il ignore la contrainte réelle** | Le seuil de ce projet vient de la **capacité de traitement** — 200 comptes par cycle. Maximiser le F1 donnerait un seuil sans rapport avec ce que les équipes absorbent (§9.3) |
| **4. Il n'a pas de référence** | La ROC-AUC se lit contre 0,5, la PR-AUC contre la prévalence. Le F1 n'a aucun point d'ancrage, et n'est pas comparable d'un portefeuille à l'autre puisqu'il dépend de la prévalence |
| **5. La règle livrée n'est pas un seuil** | Depuis §9.4, la sélection est un **top-N par risque de perte** sous plancher de risque. Un F1 y existe, mais il ne décrit qu'un point du dispositif et ne dit rien de la valeur protégée |

**Quand le F1 serait le bon outil :** une décision binaire unique à produire, deux types d'erreur de
coût comparable, aucune contrainte de capacité, et le besoin d'un seul nombre pour classer des
systèmes entre eux. Aucune de ces quatre conditions n'est remplie ici.

---

## 4. Ce qui remplace le F1 dans ce projet

Le rôle qu'on lui aurait confié — résumer la qualité d'une décision en un chiffre — est tenu par des
grandeurs métier, pas par une métrique statistique :

| Besoin | Ce qui est utilisé |
|---|---|
| Comparer des modèles | ROC-AUC et PR-AUC, sans seuil (§8.3) |
| Choisir un seuil | La capacité de traitement des équipes (§9.3) |
| Juger la décision livrée | La valeur vie protégée, comparée à la pratique actuelle (§12.3) |
| Suivre en production | PR-AUC sur le groupe témoin, et la calibration (§13.1) |

---

## 5. Questions probables du jury — réponses courtes

**« Pourquoi pas de F1 ? »**
Parce qu'il suppose un seuil et suppose que les deux erreurs se valent. Or mon seuil vient de la
capacité des équipes, et mes deux erreurs n'ont pas le même coût.

**« Pourquoi pas l'exactitude ? »**
À 28 % de prévalence, prédire « personne ne part » donne déjà 72 % d'exactitude sans rien détecter.

**« Pourquoi deux métriques de rang plutôt qu'une ? »**
La ROC-AUC est stable mais insensible au volume de faux positifs ; la PR-AUC y est sensible et se lit
contre la prévalence. Elles répondent à deux questions différentes.

**« Votre rappel n'est que de 0,47 : n'est-ce pas faible ? »**
C'est une conséquence arithmétique de la capacité : à 20 % du portefeuille alerté, couvrir 28 % de
churners est impossible. Le levier est la capacité de traitement, pas le modèle — et §9.3 chiffre ce
que rapporterait un CSM supplémentaire.
