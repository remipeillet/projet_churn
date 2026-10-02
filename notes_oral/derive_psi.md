# Dérive des variables et dérive du score (§13.1) — fiche de préparation orale

Ce qu'on surveille après la mise en production, avec quel instrument, et pourquoi les deux dérives ne
disent pas la même chose.

Fiches liées : [lecture_distributions.md](lecture_distributions.md) (§6.2) ·
[auc_univariee.md](auc_univariee.md) (§6.5) · [validation_croisee.md](validation_croisee.md) ·
[log_odds.md](log_odds.md) · [metriques_classification.md](metriques_classification.md) (précision, rappel, F1).

---

## 1. Le problème : un modèle se périme sans prévenir

Un modèle appris sur les données d'hier suppose que le monde de demain leur ressemble. Quand cette
hypothèse cesse d'être vraie, **rien ne casse** : le modèle continue à produire des scores, simplement
de moins en moins justes. Aucune exception, aucun message d'erreur.

D'où la nécessité de **capteurs** : des indicateurs calculables à chaque cycle, sans attendre de
connaître les vraies issues.

| Type de dérive | Nom technique | Ce qui change | Quand on le voit |
|---|---|---|---|
| **Dérive des variables** | *data drift* / *covariate shift* | La distribution des **entrées** X | Immédiatement, au cycle suivant |
| **Dérive du score** | *prediction drift* | La distribution des **sorties** ŷ | Immédiatement |
| **Dérive du concept** | *concept drift* | La **relation** entre X et y | Seulement après l'échéance des comptes |

Les deux premières se mesurent **sans labels**, ce qui les rend utilisables tout de suite. La
troisième — la seule qui mesure vraiment la dégradation — exige d'attendre plusieurs mois.

---

## 2. La dérive des variables

### Définition

La distribution d'une variable d'entrée s'écarte de celle sur laquelle le modèle a été entraîné.

> **Exemples plausibles sur ce projet.** Une refonte de l'application fait chuter `connexions_30j`
> pour tout le monde ; une campagne d'acquisition amène des comptes plus petits, décalant
> `sieges_souscrits` ; un changement d'outil de support modifie la façon dont
> `tickets_support_90j` est comptabilisé.

Le modèle, lui, applique toujours les mêmes coefficients : il extrapole en dehors du domaine où il a
appris, et sa fiabilité n'y est plus garantie.

### L'instrument : le PSI (*Population Stability Index*)

Il compare deux distributions de la même variable — une **référence** (le jeu d'entraînement) et un
**cycle courant** :

$$\text{PSI} = \sum_{i=1}^{k} (p^{\text{courant}}_i - p^{\text{réf}}_i) \times \ln\!\left(\frac{p^{\text{courant}}_i}{p^{\text{réf}}_i}\right)$$

**La recette en trois temps :**

1. Découper la variable de référence en **10 classes d'effectifs égaux** (ses déciles).
2. Calculer la **part** des observations dans chaque classe, pour la référence et pour le cycle
   courant.
3. Cumuler, classe par classe, l'écart de part **multiplié par le logarithme de leur rapport**.

### Pourquoi cette forme

Le produit `(écart) × ln(rapport)` a trois propriétés utiles :

- il est **toujours positif** — un déficit dans une classe donne un écart négatif *et* un log négatif,
  dont le produit est positif : les écarts dans les deux sens s'additionnent au lieu de se compenser ;
- il vaut **0** si les deux distributions coïncident exactement ;
- le logarithme le rend **sensible aux petites classes** : une classe qui passe de 1 % à 3 % pèse
  autant qu'une classe qui passe de 30 % à 40 %, ce qui est le comportement voulu — les queues de
  distribution sont souvent là où la dérive commence.

C'est mathématiquement une **divergence de Kullback-Leibler symétrisée**, ce qui explique sa forme.

### Les seuils

| PSI | Lecture | Action |
|---|---|---|
| **< 0,10** | Distributions stables | Rien |
| **0,10 – 0,25** | Écart notable | Vigilance, analyse de la cause |
| **> 0,25** | Dérive avérée | Ré-entraînement si confirmé sur **deux cycles** |

Ces seuils sont **conventionnels** (usage issu du *credit scoring*), pas démontrés. Ils servent de
point de départ et doivent être recalibrés après quelques cycles réels.

> **Sur ce projet.** Tous les PSI mesurés valent moins de 0,02 — mais entre jeu d'entraînement et jeu
> de test, qui sont deux tirages aléatoires du **même** jeu de données. Cette exécution **calibre
> l'instrument** et montre à quoi ressemble l'absence de dérive ; elle ne mesure aucune dérive réelle,
> le jeu ne portant aucun repère temporel (§3.3).

---

## 3. La dérive du score

### Définition

La distribution des **probabilités prédites** se déplace, indépendamment de ce qui l'a causée.

On la mesure avec le même PSI, appliqué cette fois au vecteur des scores, et on la complète par un
indicateur directement opérationnel : **la part du portefeuille alertée** au seuil retenu.

### Pourquoi la suivre en plus des variables

Elle est **plus synthétique** : dix variables peuvent bouger un peu chacune sans que le score bouge,
ou une seule variable importante peut suffire à le déplacer. Le score agrège ces effets avec les poids
du modèle.

Elle est aussi **directement actionnable**. Le seuil de 0,55 a été calibré pour alerter 20 % du
portefeuille (§9.3). Si la part alertée dérive vers 30 %, les CSM reçoivent 50 % de travail
supplémentaire du jour au lendemain, que la performance ait baissé ou non. C'est un incident
d'exploitation avant d'être un problème de modèle.

> **Règle de diagnostic.** Une part alertée hors de la fourchette 15–25 % appelle d'abord à
> **vérifier le seuil**, pas à toucher au modèle. Le seuil est une variable de configuration (§9.3) ;
> le réajuster à capacité constante est immédiat et réversible.

### Le piège à connaître

**Une dérive du score n'est pas une baisse de performance.** Si le portefeuille se dégrade réellement —
plus de comptes inactifs, donc plus de churn à venir —, le score doit monter : le modèle fait
exactement son travail. Inversement, un score parfaitement stable peut masquer une dégradation si la
relation entre variables et churn a changé (*concept drift*).

Les dérives de X et de ŷ sont donc des **capteurs d'alerte**, jamais des verdicts. Seule la
performance mesurée sur le **groupe témoin échu** tranche.

---

## 4. L'articulation des trois signaux

```
Cycle N        dérive des variables (PSI)   → immédiat, sans labels
   │           dérive du score (PSI, part alertée) → immédiat, sans labels
   │
   ▼
Cycle N+3      performance sur le groupe témoin (PR-AUC) → tardif, avec labels
```

Les deux premiers signaux **alertent** ; le troisième **décide**. C'est ce qui justifie l'ordre des
déclencheurs de ré-entraînement en §13.2 : une dérive doit être confirmée sur deux cycles avant
d'agir, mais un recul de PR-AUC sur le témoin déclenche directement.

---

## 5. Questions probables du jury — réponses courtes

**« Qu'est-ce que le PSI, en une phrase ? »**
Un indice qui compare la distribution d'une variable aujourd'hui à celle sur laquelle le modèle a été
entraîné : on découpe la référence en déciles et on cumule les écarts de proportion, pondérés par le
logarithme de leur rapport. 0 = distributions identiques ; au-delà de 0,25, la dérive est avérée.

**« Pourquoi surveiller les entrées alors que seule la performance compte ? »**
Parce que la performance exige des labels, et qu'un label n'existe qu'après l'échéance du compte —
plusieurs mois plus tard. Les dérives de X et du score sont les seuls signaux disponibles
immédiatement.

**« Une dérive détectée signifie-t-elle qu'il faut ré-entraîner ? »**
Non. Elle signifie qu'il faut comprendre pourquoi. Une extraction défaillante se corrige à la source ;
une évolution réelle du portefeuille, confirmée sur deux cycles, justifie un ré-entraînement.

**« Pourquoi 0,10 et 0,25 ? »**
Ce sont des repères d'usage, hérités du *credit scoring*, pas des seuils démontrés. Je les annonce
comme conventions à recalibrer après quelques cycles réels.

**« Votre PSI vaut 0,02 : le modèle est donc stable ? »**
Cette mesure compare l'entraînement au test, deux tirages aléatoires du même jeu. Elle vérifie que
l'instrument fonctionne et donne le niveau de bruit attendu en l'absence de dérive. Aucune dérive
temporelle n'est mesurable avant la mise en production, faute de repère de date dans les données.
