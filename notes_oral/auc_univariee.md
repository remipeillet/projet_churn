# L'AUC univariée (§6.5) — fiche de préparation orale

Fiche de rappel sur l'outil central du diagnostic de fuite : ce que mesure une AUC, ce que signifie
« univariée », pourquoi c'est un détecteur de fuite et non une preuve.

Fiches liées : [lecture_distributions.md](lecture_distributions.md) (§6.2) ·
[detection_leurres.md](detection_leurres.md) (§6.4) · [log_odds.md](log_odds.md) · [validation_croisee.md](validation_croisee.md) (plis et CV) · [derive_psi.md](derive_psi.md) (dérive, PSI) · [metriques_regression.md](metriques_regression.md) (R², MAE, RMSE) · [metriques_classification.md](metriques_classification.md) (précision, rappel, F1).

---

## 1. Rappel : ce qu'est une AUC

### La courbe ROC d'abord

Un modèle de classification produit un **score continu** (ici une probabilité de churn). Pour en faire
une décision, il faut un **seuil**. Chaque seuil possible donne un couple :

- **Taux de vrais positifs** (rappel, *TPR*) = churners correctement signalés / total des churners ;
- **Taux de faux positifs** (*FPR*) = comptes sains signalés à tort / total des comptes sains.

La **courbe ROC** trace TPR en fonction de FPR **pour tous les seuils**. Elle décrit donc le
comportement du score entier, indépendamment du seuil que l'on choisira plus tard.

### L'AUC

L'**AUC** (*Area Under the Curve*) est l'aire sous cette courbe — un nombre entre 0 et 1 qui résume la
courbe entière.

| AUC | Lecture |
|---|---|
| 0,5 | aucun pouvoir discriminant — équivalent à tirer à pile ou face |
| 0,7 – 0,8 | discrimination correcte |
| 0,8 – 0,9 | bonne discrimination |
| > 0,95 | **suspect** sur un problème métier réel |
| 1,0 | séparation parfaite |

### L'interprétation à citer en soutenance

C'est la formulation la plus parlante, et elle évite de parler d'aire sous une courbe :

> **L'AUC est la probabilité qu'un compte résilié tiré au hasard reçoive un score plus élevé qu'un
> compte conservé tiré au hasard.**

Une AUC de 0,89 signifie donc : dans 89 % des paires (un churner, un non-churner), le modèle classe
bien les deux dans le bon ordre. Mathématiquement, c'est la statistique U de Mann-Whitney normalisée.

### Deux propriétés qui comptent ici

**1. L'AUC ne dépend que de l'ordre des scores.** Elle est invariante par toute transformation
**monotone** (cf. fiche §6.2) : appliquer un log au score ne la change pas. C'est ce qui permet de
l'appliquer à une variable brute, sans mise à l'échelle ni calibration.

**2. L'AUC est insensible au déséquilibre des classes.** Elle se calcule par paires (un positif contre
un négatif), donc la prévalence de 28 % n'entre pas en jeu — contrairement à l'exactitude, ou à la
précision. C'est sa force, mais aussi sa limite : elle ne dit rien du **volume** de faux positifs que
l'on devra traiter à un seuil donné. C'est précisément pour cela que le notebook la complète par la
**PR-AUC** en §12.1.

---

## 2. Ce que « univariée » ajoute

L'AUC univariée consiste à **prendre la variable brute comme s'il s'agissait du score d'un modèle**,
et à mesurer sa capacité à séparer les deux classes. Aucun apprentissage, aucun entraînement, aucun
hyperparamètre : la colonne elle-même sert de prédiction.

Trois conséquences :

- **Aucun risque de sur-apprentissage** — il n'y a rien à apprendre, donc pas besoin de validation
  croisée pour cette mesure.
- **Coût nul**, ce qui permet de balayer les dix-sept variables numériques d'un coup.
- **Mesure du pouvoir discriminant *marginal*** : ce que la variable sait **à elle seule**, sans
  l'aide des autres.

### L'orientation : `max(auc, 1 − auc)`

Une variable peut discriminer **en sens inverse** : plus `nb_integrations` est élevé, moins le compte
résilie, ce qui donne une AUC brute inférieure à 0,5. Or une AUC de 0,25 est exactement aussi
informative qu'une AUC de 0,75 — il suffit d'inverser le signe.

Pour un diagnostic de fuite, seule compte la **capacité à discriminer**, pas le sens. Le notebook
retient donc `max(auc, 1 − auc)` et reporte le sens dans une colonne à part :

| Sens | Signification |
|---|---|
| **protecteur** | plus la valeur est haute, moins le compte résilie (`nb_integrations`, `csat`) |
| **aggravant** | plus la valeur est haute, plus le compte résilie (`derniere_connexion_jours`, `tickets_support_90j`) |

### Précaution de lecture : les manquants

L'AUC de chaque variable est calculée **sur ses seules lignes renseignées** (`n_renseignes` dans le
tableau). `delai_reponse_support_h` est donc évaluée sur 4 500 comptes et `connexions_30j` sur 5 000 :
les valeurs ne portent pas exactement sur la même population. L'écart est trop faible ici pour changer
le classement, mais c'est le genre de nuance qu'un jury apprécie de voir anticipée.

---

## 3. Pourquoi c'est un détecteur de fuite

### Le raisonnement

Une variable disponible **avant** la décision ne peut être qu'un indicateur **imparfait** du futur :
certains comptes en difficulté se redressent, certains comptes sains partent pour des raisons exogènes
— rachat, coupe budgétaire, changement de direction. Une AUC univariée très élevée signifie donc que
la variable ne *prédit* pas l'issue : elle la **connaît**.

### Ce qu'on regarde exactement

**Le niveau absolu**, contre un seuil de suspicion fixé à **0,85** dans le notebook.

**Et surtout la discontinuité du classement.** Dans un jeu sain, les pouvoirs prédictifs s'échelonnent
progressivement. Une variable qui décroche de ses voisines ne se comporte pas comme un prédicteur
parmi d'autres, mais comme une **reformulation de la réponse**.

> **Lecture ici.** `sante_compte_fin_periode` atteint **0,9986**. La deuxième du classement,
> `nb_integrations`, plafonne à **0,7587** — un écart de **0,24 point**, alors que les quinze autres
> variables se répartissent continûment entre 0,53 et 0,76. C'est cette **rupture** qui est le signal
> d'alarme, plus encore que la valeur elle-même.

### Ce que l'AUC univariée ne prouve pas

Rien, à elle seule. Un excellent indicateur avancé **légitime** produirait lui aussi une AUC élevée.
C'est un **symptôme**, pas un diagnostic. Le notebook croise donc trois éléments :

| Élément | Question | Résultat ici |
|---|---|---|
| **Symptôme statistique** | la variable discrimine-t-elle anormalement bien, seule ? | AUC 0,9986 ; un seuil unique (≤ 32) se trompe sur **1,44 %** des comptes |
| **Preuve sémantique** | que dit le dictionnaire sur le **moment de la mesure** ? | « score calculé **en fin de période** » — donc postérieur à la décision |
| **Test de reconstructibilité** | la variable est-elle un simple résumé des autres ? | R² = 0,689 depuis les 14 variables légitimes → **31 % de variance inexpliquée** |

**Le troisième test est le plus subtil, et c'est celui à maîtriser.** Si le score n'était qu'un agrégat
des variables disponibles, il ne pourrait pas discriminer *mieux* qu'un modèle construit sur ces
variables. Or il atteint 0,9986 là où l'ensemble des variables légitimes plafonne à 0,890. La seule
information capable d'expliquer cet écart est **l'issue elle-même**.

> **Une fuite est une affirmation temporelle, pas statistique.** Dire qu'une variable « fuit », c'est
> dire qu'elle est mesurée **après** la décision que l'on prétend prédire. La statistique ne fait que
> mettre sur la piste ; c'est le dictionnaire de données qui tranche.

---

## 4. Le coût de l'exclusion, et pourquoi il faut l'assumer

| Scénario | Régression logistique | Gradient boosting |
|---|---|---|
| Variables légitimes seules | 0,8900 | 0,8753 |
| + `sante_compte_fin_periode` | **0,9996** | **0,9991** |

Exclure la variable coûte **11 points d'AUC**. Ce n'est pas une contre-performance : c'est la
performance réellement atteignable avec l'information réellement disponible **avant** la décision. Le
modèle à 0,9996 est le meilleur du monde sur un jeu de test et **incapable de produire un seul score en
production**, puisque la variable dont il dépend n'existe pas encore au moment où le CSM doit agir.

**AUC ≈ 0,890 devient la référence honnête du notebook** : tout résultat sensiblement supérieur dans
les sections suivantes doit déclencher une nouvelle recherche de fuite.

---

## 5. Le cas `commentaire_csm` — marginal ≠ incrémental

`commentaire_csm` présente une étendue de 98,6 points entre modalités (deux modalités à 100 % et 96,6 %
de churn). Pourtant, l'ajouter au modèle fait passer l'AUC de 0,8900 à **0,8884** — une variation
**inférieure à l'écart-type entre plis** (± 0,011).

C'est l'illustration la plus nette d'une distinction à maîtriser :

| Notion | Question | Mesure |
|---|---|---|
| Pouvoir **marginal** | que sait la variable **seule** ? | AUC univariée, V de Cramér |
| Pouvoir **incrémental** | qu'ajoute-t-elle **aux autres** ? | écart d'AUC du modèle, avec et sans |

Le CSM écrit « faible adoption des sièges » précisément quand les métriques d'adoption sont basses :
son information est **déjà contenue** dans les variables d'usage. Elle est redondante, non
incrémentale. Et les deux modalités quasi séparantes ne couvrent que 60 comptes, soit 1,2 % de
l'échantillon — trop peu pour déplacer une AUC globale.

**Conséquence sur l'argumentaire :** l'exclusion est maintenue mais sa justification change de nature.
Elle ne coûte aucune performance mesurable, donc les motifs **éthique** (§4.1) et **d'horodatage
absent** suffisent. C'est la situation la plus confortable pour décider — aucun arbitrage entre
performance et responsabilité.

---

## 6. Questions probables du jury — réponses courtes

**« Qu'est-ce qu'une AUC, en une phrase ? »**
La probabilité qu'un compte résilié tiré au hasard reçoive un score plus élevé qu'un compte conservé
tiré au hasard. 0,5 = hasard, 1 = séparation parfaite.

**« Pourquoi une AUC élevée vous a-t-elle alerté plutôt que réjoui ? »**
Parce qu'aucun indicateur avancé authentique ne sépare aussi bien : un vrai signal précoce est
nécessairement imparfait, des comptes sains partent pour des raisons exogènes. Une AUC de 0,9986 avec
un décrochage de 0,24 point sur la deuxième variable ne décrit pas une prédiction, mais la
connaissance du résultat.

**« Une AUC élevée prouve-t-elle la fuite ? »**
Non, c'est un symptôme. La preuve est temporelle : le dictionnaire indique « calculé en fin de
période ». Le test de reconstructibilité vient confirmer que ce pouvoir ne peut pas venir des variables
disponibles — 31 % de sa variance reste inexpliquée par les quatorze variables légitimes.

**« Pourquoi ne pas garder la variable, puisqu'elle performe ? »**
Parce qu'elle n'existe pas au moment où l'on doit décider. Un modèle qui l'exige ne peut produire aucun
score en production : il répondrait quand il est déjà trop tard pour agir.

**« Pourquoi l'AUC plutôt que l'exactitude pour ce diagnostic ? »**
L'exactitude dépend du seuil et de la prévalence : à 28 % de churn, prédire « aucun churn » donne déjà
72 %. L'AUC est indépendante du seuil et insensible au déséquilibre, donc directement comparable d'une
variable à l'autre.

**« Pourquoi orienter l'AUC par `max(auc, 1 − auc)` ? »**
Parce qu'une AUC de 0,25 discrimine exactement autant qu'une AUC de 0,75, en sens inverse. Pour un
diagnostic de fuite, seule la capacité à séparer compte ; le sens est reporté dans une colonne
« protecteur / aggravant ».

**« Quelle est la limite de cette analyse ? »**
Elle est univariée, donc marginale : une variable sans pouvoir seul peut en avoir un en interaction, et
inversement une variable redondante peut sembler forte seule — c'est le cas de `commentaire_csm`.
Le contrôle complémentaire est l'écart d'AUC du modèle avec et sans la variable, puis l'importance par
permutation en §12.2.
