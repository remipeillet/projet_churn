# Le log-odds (logit) — fiche de préparation orale

Définition et usage de l'échelle sur laquelle travaille la régression logistique. Utile pour §8
(choix du modèle), §9.3 (seuil de décision) et §12.2 (lecture explicable des facteurs).

Fiches liées : [lecture_distributions.md](lecture_distributions.md) (§6.2) ·
[detection_leurres.md](detection_leurres.md) (§6.4) · [auc_univariee.md](auc_univariee.md) (§6.5) · [validation_croisee.md](validation_croisee.md) (plis et CV) · [derive_psi.md](derive_psi.md) (dérive, PSI) · [metriques_regression.md](metriques_regression.md) (R², MAE, RMSE) · [metriques_classification.md](metriques_classification.md) (précision, rappel, F1).

---

## 1. Définition

### La cote (*odds*) d'abord

Une probabilité se convertit en **cote** : le rapport entre « l'événement arrive » et « il n'arrive
pas ».

$$\text{cote} = \frac{p}{1-p}$$

> **Sur ce jeu.** Prévalence du churn = 28,0 % → cote = 0,28 / 0,72 = **0,389**. Lecture : pour
> 1 compte qui résilie, environ 2,6 qui restent. C'est le langage du pari.

### Le log-odds

Le **log-odds**, ou **logit**, est le logarithme naturel de la cote :

$$\text{logit}(p) \;=\; \ln\!\left(\frac{p}{1-p}\right)$$

Sa réciproque est la **fonction logistique** (sigmoïde), qui ramène ]−∞ ; +∞[ dans [0 ; 1] :

$$p \;=\; \frac{1}{1 + e^{-z}} \qquad \text{avec } z = \text{logit}(p)$$

### Repères à mémoriser

| p | cote | log-odds |
|---|---|---|
| 0,01 | 0,01 | −4,60 |
| 0,10 | 0,11 | −2,20 |
| **0,28** (prévalence du jeu) | 0,39 | **−0,94** |
| 0,50 | 1,00 | **0,00** |
| 0,72 | 2,57 | +0,94 |
| 0,99 | 99 | +4,60 |

L'échelle est **symétrique autour de 0**, qui correspond à p = 0,5 : 0,28 et 0,72 donnent ±0,94.

---

## 2. Pourquoi cette transformation

Trois problèmes réglés d'un coup — c'est la réponse à donner si le jury demande « pourquoi ne pas
modéliser la probabilité directement ? ».

| Problème | Sur l'échelle des probabilités | Sur l'échelle log-odds |
|---|---|---|
| **Bornes** | p ∈ [0 ; 1] : une somme pondérée de variables déborderait | ]−∞ ; +∞[ : un modèle **linéaire** est possible sans contrainte |
| **Symétrie** | « deux fois plus probable » = 2, « deux fois moins » = 0,5 — deux nombres dissemblables | +0,69 et −0,69 : même distance de part et d'autre du neutre |
| **Composition** | les effets se multiplient | les effets **s'additionnent** : ×3 sur la cote = +ln 3 ≈ +1,1 |

---

## 3. Ce que la régression logistique en fait

Le modèle ne prédit pas une probabilité directement : il pose une relation **linéaire sur le
log-odds**, puis retransforme par la sigmoïde.

$$\ln\!\left(\frac{p}{1-p}\right) = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \dots$$

D'où le nom du modèle : la **régression** est linéaire, c'est la **fonction logistique** qui fait le
retour vers la probabilité.

### Interprétation des coefficients (utile en §12.2)

Chaque βⱼ est un effet **sur le log-odds**. Donc `exp(βⱼ)` est un **rapport de cotes** (*odds ratio*),
directement interprétable.

> **Exemple.** Si `derniere_connexion_jours` sortait avec β = 0,02 : dix jours d'inactivité
> supplémentaires multiplient la **cote** de churn par exp(0,02 × 10) = **1,22**, soit +22 %.

**Deux pièges à éviter en soutenance :**

1. **Un rapport de cotes n'est pas un rapport de probabilités.** Passer de 28 % à 33 % multiplie la
   probabilité par 1,18 mais la cote par 1,26 — et l'écart se creuse vers les extrêmes.
2. **L'effet est constant en log-odds, pas en probabilité.** Dix jours d'inactivité de plus n'ont pas
   le même impact absolu sur un compte à 5 % de risque que sur un compte à 50 % : la sigmoïde est
   plate aux extrémités et raide au milieu.

---

## 4. Trois conséquences pour ce projet

**Le seuil de décision (§9.3).** Un seuil de 0,5 en probabilité est un seuil de **0** en log-odds.
Abaisser le seuil pour privilégier le rappel — le faux négatif coûtant plus cher que le faux positif
(§4.2) — revient, dans l'espace log-odds, à **ajouter une constante à l'intercept**. Le travail se fait
en probabilité, plus lisible pour les CSM, mais c'est la même opération.

**La calibration.** L'AUC ne dépend que de l'**ordre** des scores : elle est indifférente à la justesse
des probabilités. Pour pouvoir dire à un CSM « ce compte a 70 % de risque » et que ce soit vrai, il
faut une **calibration** — et les méthodes usuelles (*Platt scaling*) opèrent précisément par
régression logistique sur les log-odds.

**Le rééquilibrage des classes.** Pondérer ou rééchantillonner décale l'intercept d'une quantité connue
en log-odds : les probabilités sorties ne sont alors plus celles de la population réelle et doivent
être corrigées avant toute lecture métier. Une raison de plus, avec un déséquilibre modéré (28 %,
ratio 2,57 : 1 — cf. §6.1), de **ne pas rééquilibrer sans nécessité**.

---

## 5. Réponse type si le jury demande

> Le log-odds est le logarithme du rapport entre la probabilité qu'un événement arrive et celle qu'il
> n'arrive pas. Il transforme une probabilité bornée dans [0, 1] en une quantité non bornée et
> symétrique autour de zéro, ce qui permet d'écrire un modèle linéaire sans risque de sortir de
> l'intervalle des probabilités. C'est l'échelle sur laquelle travaille la régression logistique :
> ses coefficients s'y additionnent, et leur exponentielle se lit comme un rapport de cotes.
