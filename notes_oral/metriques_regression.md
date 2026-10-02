# R², MAE, RMSE (§12.4) — fiche de préparation orale

Les trois métriques de la régression sur la valeur vie client : ce qu'elles mesurent, pourquoi elles
divergent autant sur ce projet, et laquelle citer selon la question posée.

Fiches liées : [lecture_distributions.md](lecture_distributions.md) (§6.2) ·
[auc_univariee.md](auc_univariee.md) (§6.5) · [validation_croisee.md](validation_croisee.md) ·
[log_odds.md](log_odds.md) · [derive_psi.md](derive_psi.md) · [metriques_classification.md](metriques_classification.md) (précision, rappel, F1).

---

## 0. Le point commun : toutes mesurent un écart

Pour chaque compte, il y a une valeur **réelle** $y_i$ et une valeur **prédite** $\hat{y}_i$.
L'erreur est $e_i = y_i - \hat{y}_i$. Les trois métriques ne diffèrent que par **la façon d'agréger
ces erreurs** — et ce choix d'agrégation change tout quand la distribution a une queue lourde,
comme ici.

---

## 1. MAE — l'erreur absolue moyenne

$$\text{MAE} = \frac{1}{n}\sum_{i=1}^{n} \lvert y_i - \hat{y}_i \rvert$$

**Ce qu'elle dit :** de combien on se trompe en moyenne, dans l'unité de la cible — ici des euros.

**Sa propriété :** chaque erreur pèse **proportionnellement à sa taille**. Se tromper de 100 000 € sur
un compte pèse mille fois plus que se tromper de 100 € sur un autre.

> **Sur ce projet : 42 028 €.** Un chiffre qui décrit mal le compte typique, parce qu'il reste une
> **moyenne** : quelques comptes à plusieurs centaines de milliers d'euros la tirent vers le haut.

---

## 2. RMSE — la racine de l'erreur quadratique moyenne

$$\text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$

**Ce qu'elle dit :** la même chose que la MAE, mais après avoir **élevé les erreurs au carré**.

**Sa propriété :** une erreur deux fois plus grande compte **quatre fois** plus. Le RMSE est donc
dominé par les plus gros écarts, et il est **toujours supérieur ou égal à la MAE**.

> **Sur ce projet : 139 360 €**, soit 3,3 fois la MAE.

**Le rapport RMSE / MAE est lui-même un diagnostic.** Sur une distribution sans valeurs extrêmes, il
vaut environ 1,25. Ici il vaut **3,3** : la mesure est gouvernée par une poignée de comptes, ce qui
confirme la queue lourde relevée en §6.2.

| Métrique | Question à laquelle elle répond | Sensibilité aux extrêmes |
|---|---|---|
| **MAE** | De combien je me trompe en moyenne ? | Moyenne |
| **RMSE** | Quelle est l'ampleur de mes plus grosses erreurs ? | Très forte |
| **Erreur médiane** | De combien je me trompe sur le compte **typique** ? | Nulle |

---

## 3. R² — la part de variance expliquée

$$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

Le numérateur est l'erreur du **modèle**, le dénominateur celle d'un modèle trivial qui prédirait la
**moyenne** pour tout le monde. Le R² est donc un **rapport de performance**, pas une erreur.

| R² | Lecture |
|---|---|
| **1** | Prédiction parfaite |
| **0** | Aussi bon que prédire la moyenne — le modèle n'apporte rien |
| **< 0** | **Pire** que prédire la moyenne |

> **Sur ce projet : 0,641 en euros.** Pour référence, prédire la médiane à tout le monde donne un R²
> de **−0,102** : littéralement pire que ne rien modéliser.

**Trois propriétés à connaître :**

1. **Le R² est sans unité**, donc comparable entre modèles — mais **sur le même jeu de données
   uniquement**. Comparer le R² de deux études portant sur des populations différentes n'a aucun sens :
   une population plus hétérogène gonfle le dénominateur, donc le R².
2. **Il est fondé sur des carrés**, comme le RMSE : il hérite de la même sensibilité aux valeurs
   extrêmes.
3. **Il dépend de l'échelle sur laquelle on le calcule** — et c'est le point décisif ici.

---

## 4. Pourquoi 0,64 en euros et 0,90 en logarithme

Ce sont **deux mesures du même modèle**, sur deux échelles :

| Échelle | R² | Ce que la mesure valorise |
|---|---|---|
| Euros | **0,641** | Bien prédire les comptes à forte valeur, qui dominent la somme des carrés |
| Logarithme | **0,895** | Bien prédire l'**ordre de grandeur** de chaque compte, quelle que soit sa taille |

L'écart entre les deux n'est pas une contradiction : il **décrit la distribution**. Le modèle situe
correctement chaque compte à un facteur près, mais un facteur 1,4 sur un compte à 200 000 € fait
80 000 € d'erreur en euros — pénalisant en échelle linéaire, anodin en échelle logarithmique.

> **Formulation pour la soutenance.** « Le R² vaut 0,64 en euros et 0,90 en échelle logarithmique.
> L'écart dit que le modèle place correctement chaque compte dans son ordre de grandeur, et que les
> erreurs en euros sont concentrées sur une poignée de très gros comptes. »

---

## 5. Les deux métriques ajoutées, et pourquoi

Le RMSE et la MAE décrivent mal ce jeu de données. Deux mesures complémentaires ont donc été
rapportées en §12.4 :

| Mesure | Valeur | Ce qu'elle apporte |
|---|---|---|
| **Erreur médiane** (MedAE) | **4 249 €** | L'erreur du compte typique — dix fois plus faible que la MAE |
| **Erreur relative médiane** | **41,8 %** | La seule lisible à toutes les échelles de valeur |

**Le rapport de 1 à 10 entre MAE et erreur médiane est le fait marquant.** Présenter la seule MAE
suggérerait une erreur typique de 42 000 €, alors que la moitié des comptes sont prédits à moins de
4 200 € près.

L'erreur relative est en outre **stable autour de 40 % du premier au dernier quintile** de valeur :
le modèle n'est pas « bon sur les gros comptes et mauvais sur les petits », il commet partout la même
erreur **en proportion**.

---

## 6. Quelle métrique citer, selon la question

| Question posée | Métrique à donner |
|---|---|
| « Votre modèle est-il meilleur que rien ? » | **R²** — 0,64, contre −0,10 pour la médiane |
| « De combien vous trompez-vous sur un compte ? » | **Erreur médiane** — 4 200 €, et 42 % en relatif |
| « Et sur les gros comptes ? » | **RMSE** — 139 000 €, dominé par eux, d'où la cible logarithmique |
| « Est-ce assez précis pour votre usage ? » | Ni l'une ni l'autre : **97,4 % du potentiel capté** au classement |

La dernière ligne est la plus importante. Aucune de ces trois métriques ne répond à la question de
l'**usage** : elles mesurent une erreur, pas son effet sur la décision. C'est pourquoi §12.4 compare
directement la sélection fondée sur la valeur **estimée** à celle fondée sur la valeur **réelle** —
et montre qu'elle en capte 97,4 %.

---

## 7. Questions probables du jury — réponses courtes

**« Qu'est-ce que le R² ? »**
La part de variance de la cible expliquée par le modèle. C'est un rapport : 1 − (erreur du modèle ÷
erreur d'un modèle qui prédirait la moyenne). À 0, le modèle ne vaut pas mieux que la moyenne ; en
dessous de 0, il fait pire.

**« Pourquoi RMSE et MAE, puisque les deux mesurent une erreur ? »**
La MAE traite toutes les erreurs proportionnellement, le RMSE écrase les petites et amplifie les
grandes. Leur rapport — 3,3 ici contre 1,25 attendu — révèle à lui seul la présence de valeurs
extrêmes.

**« Un R² de 0,64, est-ce bon ? »**
La question n'a pas de réponse dans l'absolu : le R² dépend de l'hétérogénéité de la population. Ce
qui est interprétable, c'est l'écart avec la référence — prédire la médiane donne −0,10 — et l'écart
entre les deux échelles, 0,64 en euros contre 0,90 en logarithme.

**« Pourquoi ne pas avoir optimisé le RMSE ? »**
Parce qu'il aurait conduit à n'optimiser que les comptes à forte valeur. L'apprentissage se fait sur
la cible transformée en logarithme, ce qui traite une erreur de 40 % comme également grave à tous les
niveaux de valeur — l'objectif métier.
