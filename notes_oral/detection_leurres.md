# Établir qu'une variable n'a aucun effet (§6.4) — fiche de préparation orale

Fiche de rappel sur les mesures utilisées pour statuer sur les variables catégorielles : khi²,
V de Cramér, V minimal détectable, correction de Holm. Objectif : pouvoir dire **ce que chaque
mesure établit**, **ce qu'elle ne peut pas établir**, et **pourquoi il en faut trois et non une**.

Fiches liées : [lecture_distributions.md](lecture_distributions.md) (§6.2) ·
[auc_univariee.md](auc_univariee.md) (§6.5) · [log_odds.md](log_odds.md) (régression logistique) · [metriques_classification.md](metriques_classification.md) (précision, rappel, F1).

---

## 0. Le problème à résoudre en une phrase

Quatre variables n'ont, *a priori*, aucun lien métier plausible avec la résiliation — mais ce n'est
qu'une hypothèse tirée du dictionnaire de données, pas un acquis. Pour les écarter, il faut prouver une
**absence d'effet**, ce qui est logiquement bien plus difficile que de prouver une présence : c'est toute
la difficulté de cette section.

> **Vocabulaire.** Le livrable ne parle jamais de « leurres ». Le mot supposerait qu'on sache d'avance
> que certaines colonnes sont inutiles ; dans un vrai projet, c'est précisément ce que l'analyse doit
> établir. On dit donc « variable sans effet mesurable » et, une fois la démonstration faite,
> « absence d'effet établie ».

---

## 1. Le test du khi² d'indépendance

### Principe

On croise la variable catégorielle avec la cible dans un **tableau de contingence** (par exemple
4 plans × 2 classes de churn). Le test compare :

- les effectifs **observés** dans chaque case ;
- les effectifs **attendus** si les deux variables étaient totalement indépendantes, c'est-à-dire si
  chaque modalité churnait exactement au taux global de 28,0 %.

$$\chi^2 \;=\; \sum_{\text{cases}} \frac{(\text{observé} - \text{attendu})^2}{\text{attendu}}$$

Plus les observations s'écartent de ce que produirait l'indépendance, plus le khi² est grand.

### Degrés de liberté (`ddl`)

Nombre d'écarts que le tableau peut faire varier librement : `(nb lignes − 1) × (nb colonnes − 1)`.
Pour `plan` (4 modalités × 2 classes) : 3. Pour `secteur` (7 × 2) : 6.

C'est le paramètre qui règle la sévérité du test : **plus il y a de degrés de liberté, plus le khi²
doit être grand pour être jugé significatif**, parce qu'un tableau plus grand offre mécaniquement plus
d'occasions de s'écarter par hasard.

### La p-value — et ce qu'elle ne dit pas

La p-value répond à : *« si la variable n'avait réellement aucun lien avec le churn, quelle serait la
probabilité d'observer un écart au moins aussi grand que celui-ci, par le seul hasard de
l'échantillonnage ? »*

Trois erreurs de lecture classiques, que le jury peut tester :

| Formulation fausse | Correction |
|---|---|
| « p = 0,045 : il y a 4,5 % de chances que la variable n'ait pas d'effet » | La p-value est une probabilité **sur les données**, pas sur l'hypothèse |
| « p > 0,05 : la variable n'a pas d'effet » | Une p-value élevée n'établit **rien** — c'est une absence de preuve |
| « p très petite : l'effet est important » | Elle mesure la **détectabilité**, pas l'ampleur |

### La limite décisive : l'effet de la taille d'échantillon

Le khi² croît proportionnellement à *n*. Avec 5 000 lignes, **un effet dérisoire devient
« statistiquement significatif »** ; avec 50 lignes, un effet massif peut passer inaperçu. Une p-value
seule ne permet donc de conclure ni à la présence, ni à l'absence d'un signal exploitable.

> **À retenir :** significatif ≠ important. C'est la raison d'être de la mesure suivante.

---

## 2. Le V de Cramér — l'ampleur de la dépendance

### Définition

$$V \;=\; \sqrt{\frac{\chi^2}{n \times \min(l-1,\; c-1)}}$$

On divise le khi² par la taille de l'échantillon (ce qui **neutralise l'effet de *n***) et par les
degrés de liberté de la plus petite dimension (ce qui rend comparables des tableaux de tailles
différentes). Le résultat est une **taille d'effet** comprise entre 0 et 1 :

- **0** = indépendance parfaite ;
- **1** = association parfaite (connaître la modalité donne la classe).

### Repères d'interprétation

Pour un tableau **2 × k** — ce qui est notre cas, la cible étant binaire — le V de Cramér coïncide
avec le ***w* de Cohen**, dont les repères usuels sont :

| V | Ampleur |
|---|---|
| ≈ 0,1 | effet faible |
| ≈ 0,3 | effet moyen |
| ≈ 0,5 | effet fort |

> **Lecture ici.** `plan` atteint V = 0,138 — un effet faible au sens de Cohen, mais bien réel et de
> loin le plus fort des huit. `groupe_experimentation` tombe à V = 0,004, soit trente fois moins.
> Aucune catégorielle ne porte à elle seule un signal massif : c'est cohérent avec le message de
> l'énoncé, « aucune variable ne donne seule la réponse ».

### Ce qu'il ne dit toujours pas

Un V de 0,018 est-il « nul » ou « petit mais réel » ? Le V ne permet pas de trancher : il n'indique
pas si la valeur observée est **distinguable de zéro** sur cet échantillon. D'où la troisième mesure.

---

## 3. Le V minimal détectable — la mesure qui autorise à conclure à l'absence

### La question posée

*« Compte tenu de mon échantillon, quel est le plus petit effet que j'aurais eu 80 % de chances de
détecter ? »*

C'est une analyse de **puissance statistique**. La puissance est la probabilité de détecter un effet
qui existe réellement ; la convention usuelle est de 80 %, au seuil α = 5 %.

### Le raisonnement

Sous l'hypothèse d'un effet réel de taille V, le khi² ne suit plus une loi du khi² centrée mais une
loi **non centrale**, de paramètre de non-centralité :

$$\lambda \;=\; n \times V^2$$

On cherche alors, **par dichotomie**, la valeur de V pour laquelle la probabilité de dépasser le seuil
critique atteint 80 %. C'est ce que fait la fonction `v_minimal_detectable` du notebook.

### Pourquoi c'est le pivot du raisonnement

Cela permet de passer d'une **absence de preuve** à une **preuve d'absence** :

> Si un effet de taille détectable existait, je l'aurais vu. Je ne l'ai pas vu, **et mon échantillon
> avait la résolution nécessaire pour le voir** : je peux donc conclure qu'il n'y en a pas — pas
> seulement que je n'en ai pas trouvé.

Sans cette mesure, déclarer « cette variable n'a aucun effet » sur une p-value élevée serait un **raisonnement
invalide**. C'est le point méthodologique le plus fort de la section.

### Lecture des trois situations

| Situation | Conclusion | Variables concernées |
|---|---|---|
| V **nettement au-dessus** du seuil détectable | Dépendance établie | `plan` (0,138 vs 0,047), `taille_entreprise` (0,068 vs 0,047) |
| V **nettement en dessous** (facteur ≥ 1,5) | **Absence d'effet établie** — preuve d'absence | `code_datacenter` (0,018 vs 0,047), `couleur_theme_interface` (0,015 vs 0,049), `groupe_experimentation` (0,004 vs 0,044) |
| V **au niveau** du seuil | Non concluant — zone grise, à dire tel quel | `secteur` (0,052 vs 0,054), `jour_souscription` (0,045 vs 0,052), `pays` (0,031 vs 0,052) |

> **`groupe_experimentation` sert de témoin négatif.** Un bucket A/B est par construction une
> affectation aléatoire : il ne *peut pas* prédire le churn. Le fait que la méthode le classe au tout
> dernier rang (V = 0,004, soit 12 fois sous son seuil) **valide la méthode elle-même** : elle ne
> fabrique pas de faux signaux. C'est un argument à sortir si le jury doute du protocole.

---

## 4. La correction de Holm-Bonferroni — le risque des tests multiples

### Le problème

Huit variables testées chacune au seuil de 5 % : la probabilité de crier au signal **au moins une
fois** par pur hasard n'est pas 5 %, mais

$$1 - (1 - 0{,}05)^{8} \;=\; 33{,}7\ \%$$

Soit une chance sur trois de présenter au jury un faux positif comme un résultat acquis.

### Les deux corrections

- **Bonferroni** : on compare chaque p-value au seuil α/m (ici 0,05/8 = 0,00625). Simple, mais très
  conservateur — on perd des vrais signaux.
- **Holm-Bonferroni** (retenu) : on ordonne les p-values croissantes et on applique un seuil
  **progressivement moins sévère** — la plus petite est confrontée à α/m, la suivante à α/(m−1), etc.
  Il contrôle le même risque global tout en étant **uniformément plus puissant** que Bonferroni.

### Le cas `secteur` — l'exemple à citer

| | p brute | p après Holm |
|---|---|---|
| `secteur` | **0,045** | **0,271** |

Un candidat pressé aurait lu 0,045 < 0,05 et conclu « le secteur d'activité influence significativement
le churn ». Après correction, la dépendance n'est **pas établie**. Sans correction, ce faux positif
aurait été présenté comme un acquis — et aurait pu orienter tout le discours métier.

---

## 5. Test global contre test par modalité : deux questions différentes

Apparente contradiction dans le notebook : le test global ne conclut pas sur `secteur`, mais la
modalité `Finance` ressort bel et bien. Les deux ne posent pas la même question :

| Test | Question | Famille de correction | Résultat |
|---|---|---|---|
| **Khi² global** | « la répartition du churn diffère-t-elle **entre les sept secteurs** ? » | les 8 variables testées | p Holm = 0,271 → non établi |
| **Binomial par modalité** | « **CE** secteur s'écarte-t-il du taux global de 28,0 % ? » | les 7 secteurs | `Finance` : p Holm = **0,030** → établi |

**L'explication est mécanique** : le khi² global répartit sa puissance sur 6 degrés de liberté — il
cherche un écart *quelconque* entre sept secteurs. Un signal concentré sur **une seule** modalité y est
dilué. Le test binomial ciblé ne dépense qu'un degré de liberté et retrouve le signal.

> **Formulation défendable en soutenance :** pas « le secteur influence le churn », mais « les clients
> du secteur Finance résilient moins (23,4 % contre 28,0 %) ; les six autres secteurs ne se
> distinguent pas ». C'est exactement ce que les données autorisent à dire.

---

## 6. La limite assumée de toute la section

Ces tests mesurent une dépendance **marginale** : chaque variable est confrontée seule à la cible. Une
variable sans effet marginal pourrait théoriquement en avoir un **en interaction** avec une autre — par
exemple un datacenter qui dégraderait l'expérience d'un seul segment de clients.

Le contrôle correspondant est l'**importance par permutation** sur le modèle entraîné (§12.2) : si
l'une de ces variables y ressortait, il faudrait revenir sur la décision.

Une exception notable : pour `groupe_experimentation`, l'argument est **logique et non statistique**.
Une affectation aléatoire ne peut porter aucune information sur un événement futur, en interaction ou
non. C'est la seule des huit dont l'exclusion ne dépend d'aucune mesure.

---

## 7. Questions probables du jury — réponses courtes

**« Pourquoi trois mesures alors que le khi² suffisait ? »**
Parce qu'elles répondent à trois questions distinctes : la p-value dit si une dépendance est
*détectable*, le V de Cramér dit quelle en est l'*ampleur*, le V minimal détectable dit si mon
échantillon avait la *résolution* nécessaire pour trancher. Seule la troisième autorise à conclure à
une absence d'effet.

**« Comment pouvez-vous affirmer qu'une variable n'a aucun effet ? »**
Je ne l'affirme que pour trois d'entre elles, et sur un raisonnement de puissance : leur effet mesuré
est 3 à 12 fois inférieur au plus petit effet que l'échantillon permettrait de détecter à 80 % de
puissance. Pour `secteur` et `jour_souscription`, je ne l'affirme pas : je dis qu'aucune dépendance
n'est établie, ce qui n'est pas la même chose.

**« Un V de 0,138, c'est faible — pourquoi garder `plan` ? »**
Parce que la question n'est pas « cette variable suffit-elle ? » mais « apporte-t-elle une information
que les autres n'ont pas ? ». L'énoncé rappelle qu'aucune variable ne donne seule la réponse : la
performance vient de la combinaison. `plan` est en outre monotone (37,5 % → 20,0 % du Starter à
l'Enterprise), ce qui est métier-interprétable.

**« Pourquoi corriger pour tests multiples ? »**
Huit tests indépendants à 5 % donnent 33,7 % de risque d'au moins un faux positif. Sans correction,
`secteur` (p = 0,045) aurait été présenté comme un signal établi alors qu'il ne l'est pas.

**« Pourquoi Holm plutôt que Bonferroni ? »**
Même contrôle du risque global, mais seuil progressivement moins sévère : Holm est uniformément plus
puissant, donc il perd moins de vrais signaux. Aucune raison de choisir la version la plus
conservatrice.

**« Pourquoi retirer ces variables, puisqu'un arbre les ignorerait ? »**
Trois raisons : le sur-apprentissage (après *one-hot*, ces variables ajoutent 19 colonnes de bruit, où
un arbre trouvera toujours des coupures qui séparent le bruit d'entraînement) ; l'interprétabilité
(« couleur du thème » dans un classement d'importance décrédibilise l'outil auprès des CSM) ; et le
coût d'exploitation (chaque variable conservée est une dépendance amont à maintenir et surveiller en
production).
