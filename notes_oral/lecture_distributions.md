# Lire le tableau des distributions (§6.2) — fiche de préparation orale

Fiche de rappel sur le tableau « Asymétrie et étendue des distributions » et sur le dénombrement
des points extrêmes. Objectif : pouvoir expliquer **ce que chaque colonne mesure**, **ce qu'elle
montre ici**, et **ce qu'on en fait**.

---

## 1. Les colonnes, une par une

### `count` — effectif non manquant

Nombre de valeurs réellement présentes, les manquants étant ignorés. Ce n'est donc pas le nombre de
lignes : c'est le nombre de lignes **exploitables pour cette colonne**.

> **Lecture ici.** 5 000 comptes après dédoublonnage, mais `delai_reponse_support_h` n'en compte que
> 4 500, `csat` 4 600, `heures_usage_30j` 4 700. L'écart est exactement le taux de manquants relevé
> en §5.3.

**Piège à éviter à l'oral :** chaque statistique du tableau est calculée sur *son* `count`, pas sur
un socle commun. Comparer deux colonnes revient donc à comparer deux sous-populations légèrement
différentes.

### `mean` — moyenne arithmétique

Somme des valeurs divisée par leur nombre. Elle utilise toute l'information, mais **chaque valeur y
pèse à proportion de sa taille** : une valeur mille fois plus grande tire la moyenne mille fois plus
fort. Elle n'est donc pas robuste.

### `50%` — médiane (2ᵉ quartile)

Valeur qui coupe l'échantillon en deux moitiés de même effectif : la moitié des comptes est en
dessous, la moitié au-dessus. Elle ne dépend que de l'**ordre** des valeurs, pas de leur amplitude —
multiplier la plus grande valeur par 100 ne la déplace pas. Elle est donc **robuste**.

### Le couple `mean` / `50%` : le diagnostic le plus rapide du tableau

C'est la comparaison la plus parlante à l'oral, parce qu'elle ne demande aucune formule :

| Relation | Interprétation |
|---|---|
| moyenne ≈ médiane | distribution à peu près symétrique |
| moyenne **>** médiane | queue étirée vers la **droite** — une minorité de très grandes valeurs |
| moyenne **<** médiane | queue étirée vers la gauche |

> **Lecture ici.** `valeur_vie_client_eur` : moyenne 74 995 € contre médiane 11 204 € — la moyenne
> vaut **6,7 fois** la médiane. La « valeur vie moyenne » d'un client de ce portefeuille n'est
> représentative d'aucun client réel : elle décrit une poignée de très gros comptes.
>
> Même constat sur `utilisateurs_actifs` (34,7 contre 9) et `revenu_mensuel_recurrent_eur`
> (3 543 € contre 682 €).

**Formule utilisable en soutenance :** « sur ces variables, la moyenne décrit le portefeuille, la
médiane décrit le client typique — et ce n'est pas le même objet. »

### `min` et `max` — bornes observées

Valeurs extrêmes constatées. Elles servent à deux choses : mesurer l'**étendue** de l'échelle, et
faire un **contrôle de plausibilité métier** (une valeur négative sur un compteur, un pourcentage
au-dessus de 100, une durée impossible signaleraient une erreur de saisie ou de parsing).

> **Lecture ici.** Aucune valeur aberrante au sens d'une erreur : les minimums sont à 0 sur les
> compteurs, `taux_adoption_pct` reste dans [0 ; 100], `csat` dans [1 ; 5]. En revanche l'étendue est
> énorme — `valeur_vie_client_eur` va de 300 € à 2 000 000 €, soit un rapport de 1 à 6 667.

### `asymetrie` — coefficient d'asymétrie (*skewness*)

Mesure standardisée du déséquilibre de la distribution autour de sa moyenne : moment d'ordre 3
rapporté au cube de l'écart-type.

$$\gamma_1 \;=\; \mathbb{E}\!\left[\left(\frac{X - \mu}{\sigma}\right)^{3}\right]$$

Ce qu'il faut retenir du cube : les écarts à la moyenne sont élevés à la puissance 3, **en conservant
leur signe**. Les grands écarts pèsent donc démesurément, et les écarts positifs ne se compensent pas
avec les négatifs. Le coefficient est sans unité, donc comparable d'une variable à l'autre — c'est
tout son intérêt ici.

| Valeur | Lecture |
|---|---|
| ≈ 0 | distribution symétrique |
| entre 0,5 et 1 | asymétrie modérée |
| **> 1** | asymétrie forte |
| **> 3** | queue très lourde, quelques valeurs gouvernent la statistique |
| < 0 | queue à gauche (valeurs basses étirées) |

> **Lecture ici.** Cinq variables dépassent 3 : `valeur_vie_client_eur` (5,57),
> `utilisateurs_actifs` (4,73), `revenu_mensuel_recurrent_eur` (4,60),
> `derniere_connexion_jours` (4,54), `sieges_souscrits` (3,57).
>
> Trois variables sont **légèrement négatives** : `taux_adoption_pct` (−0,05, quasi symétrique),
> `csat` (−0,27) et `sante_compte_fin_periode` (−0,55) — normal pour des variables bornées par
> construction, qui ne peuvent pas avoir de queue longue.

### `rapport_max_p75` — maximum rapporté au 3ᵉ quartile

Indicateur ajouté au tableau, non standard mais directement interprétable : **combien de fois le plus
gros individu dépasse le seuil sous lequel se trouvent 75 % des comptes.**

Il complète l'asymétrie en répondant à une question différente. L'asymétrie dit *que* la queue est
lourde ; ce rapport dit *jusqu'où* elle va, dans l'unité de la variable.

> **Lecture ici.** `valeur_vie_client_eur` : 42,7 — le plus gros compte vaut plus de **40 fois** le
> seuil des 25 % supérieurs. `derniere_connexion_jours` : 40,0 — 75 % des comptes se sont connectés
> il y a 5 jours ou moins, et le plus inactif est à 200 jours.
>
> À l'inverse, `csat` (1,2), `anciennete_mois` (2,2), `fonctionnalites_total` (1,5) et
> `taux_adoption_pct` (1,5) sont resserrées : leur échelle est bornée, il n'y a pas de queue.

---

## 2. Le dénombrement des points extrêmes (règle 1,5 × IQR)

### La règle

L'**écart interquartile** IQR = Q3 − Q1 mesure l'étalement du « ventre » de la distribution, les
50 % centraux. Est déclaré extrême tout point hors de l'intervalle :

$$[\,Q_1 - 1{,}5 \times \text{IQR}\;;\;\; Q_3 + 1{,}5 \times \text{IQR}\,]$$

C'est la règle de Tukey, celle qui trace les moustaches de la boîte à moustaches : les points
au-delà sont affichés individuellement.

### Ce que la règle suppose — et pourquoi c'est décisif ici

Le facteur 1,5 n'est pas universel : il est calibré pour qu'une distribution **approximativement
normale** ne produise qu'environ **0,7 %** de points hors bornes. Quand une variable est fortement
asymétrique, la règle ne détecte plus des anomalies : elle **détecte l'asymétrie elle-même**.

> **Lecture ici.** `derniere_connexion_jours` affiche 799 points extrêmes, soit **15,98 %** de
> l'échantillon. Une anomalie qui concerne un compte sur six n'est pas une anomalie : c'est la forme
> normale de la variable. Même chose pour `sieges_souscrits` (15,76 %), `valeur_vie_client_eur`
> (14,30 %), `revenu_mensuel_recurrent_eur` (14,04 %).

**Phrase à retenir pour l'oral :** *un taux de points extrêmes très supérieur à 1 % ne dit pas que
les données sont sales ; il dit que l'hypothèse de normalité sous-jacente à la règle ne tient pas.*

### Extrême ≠ aberrant

Trois mots à ne pas confondre en soutenance :

| Terme | Définition | Traitement |
|---|---|---|
| **Point extrême** (*outlier*) | Valeur éloignée du reste de la distribution | À comprendre, pas forcément à corriger |
| **Valeur aberrante** | Valeur impossible ou incohérente (âge négatif, taux > 100 %) | À corriger ou à supprimer |
| **Erreur de saisie** | Valeur plausible mais fausse | Indétectable sans source externe |

> **Lecture ici.** Les points extrêmes relevés sont **tous métier-plausibles** : un compte à
> 898 sièges est un grand compte, pas une erreur ; 200 jours sans connexion décrit un compte
> abandonné — c'est même précisément le profil que le modèle doit repérer. **Aucune suppression
> n'est justifiée.** Retirer ces lignes reviendrait à retirer les comptes les plus intéressants du
> problème.

---

## 3. Encadré — qu'est-ce qu'une relation monotone ?

Le mot revient trois fois dans le notebook (Spearman en §6.2, `plan` en §6.3, invariance des arbres
en §8) : il vaut la peine d'être défini proprement.

### Définition

Une relation entre deux variables est **monotone** si elle va **toujours dans le même sens** :
quand X augmente, Y augmente toujours (monotone **croissante**), ou bien Y diminue toujours
(monotone **décroissante**). Ce qui est interdit, c'est le **changement de sens** — monter puis
redescendre.

La force de la relation n'entre pas en jeu, seulement sa direction : une relation peut être monotone
et très irrégulière, tant qu'elle ne se retourne jamais.

> **Linéaire ⊂ monotone.** Toute relation linéaire est monotone, mais l'inverse est faux. Une courbe
> qui monte de plus en plus vite, ou de moins en moins vite, reste parfaitement monotone. C'est
> exactement l'écart entre Pearson (qui exige la ligne droite) et Spearman (qui se contente du sens).

### Trois exemples tirés du jeu de données

| Relation | Monotone ? | Lecture |
|---|---|---|
| `derniere_connexion_jours` → churn | **Oui**, croissante | Plus le compte est inactif depuis longtemps, plus il résilie. Jamais l'inverse |
| `plan` → churn | **Oui**, décroissante | 37,5 % en Starter, 26,7 % en Pro, 23,2 % en Business, 20,0 % en Enterprise (§6.3) : le taux baisse à chaque palier, sans exception |
| `tickets_support_90j` → churn | **Non** (probablement en U) | Zéro ticket peut signaler un compte désengagé qui ne se plaint même plus ; beaucoup de tickets signalent un compte en difficulté. Le risque est élevé **aux deux extrémités** et faible au milieu |

Le cas de `plan` est le plus utile à citer : c'est la monotonie constatée qui justifie d'envisager un
**encodage ordinal** (Starter < Pro < Business < Enterprise) plutôt qu'un *one-hot*. On dit alors au
modèle que ces modalités sont ordonnées, information qu'un *one-hot* détruirait.

### Pourquoi la notion est centrale ici

**1. Elle fonde le choix de Spearman.** Le coefficient de Spearman est un Pearson calculé sur les
**rangs** et non sur les valeurs. Il vaut ±1 dès que la relation est parfaitement monotone, même très
courbée. Comme il ne regarde que l'ordre, l'amplitude des points extrêmes disparaît — d'où sa
robustesse aux asymétries de 5,6 relevées plus haut.

**2. Elle explique l'invariance des arbres de décision.** Un arbre ne teste que des conditions du type
« variable ≤ seuil » : il n'utilise donc que l'**ordre** des valeurs. Toute transformation monotone
(logarithme, racine, mise à l'échelle) préserve cet ordre et produit **exactement le même arbre**.
C'est la raison technique pour laquelle une transformation log est inutile côté arbres, alors qu'elle
est nécessaire côté modèles linéaires.

**3. Elle délimite ce que l'analyse peut manquer — le point à connaître.** Un coefficient de Spearman
proche de 0 ne signifie **pas** « aucun lien ». Il signifie « aucun lien **monotone** ». Une relation
en U, comme celle soupçonnée sur `tickets_support_90j`, se compense entre ses deux moitiés et sort à
zéro. C'est précisément pourquoi l'EDA ne s'arrête pas aux corrélations : les boîtes à moustaches par
classe (§6.2) et les taux par modalité (§6.3) montrent la **forme** de la relation, là où un
coefficient unique la résume — parfois à tort.

> **Réponse type si le jury demande :** « une relation monotone va toujours dans le même sens, sans
> jamais se retourner ; elle peut être courbe, ce n'est pas la même chose que linéaire. Je m'appuie
> dessus pour choisir Spearman et pour justifier qu'aucune transformation d'échelle n'est nécessaire
> côté arbres. Sa limite est qu'elle ne voit pas les relations en U, que je vérifie graphiquement. »

---

> **Fiches liées :** [detection_leurres.md](detection_leurres.md) — khi², V de Cramér, puissance et
> correction de Holm (§6.4) · [auc_univariee.md](auc_univariee.md) — AUC univariée et diagnostic de
> fuite (§6.5) · [log_odds.md](log_odds.md) (régression logistique) · [validation_croisee.md](validation_croisee.md) (plis et CV) · [derive_psi.md](derive_psi.md) (dérive, PSI) · [metriques_regression.md](metriques_regression.md) (R², MAE, RMSE) · [metriques_classification.md](metriques_classification.md) (précision, rappel, F1).

---

## 4. Ce que tout cela commande pour la suite

C'est la partie que le jury attend : un constat sans conséquence ne vaut rien.

| Constat | Conséquence retenue |
|---|---|
| Asymétries > 3 et queues lourdes | **Spearman** plutôt que Pearson pour les corrélations (§6.2) : relation monotone, insensible aux points extrêmes |
| Moyenne non représentative | Les seuils et repères métier se lisent en **médiane et quantiles**, jamais en moyenne |
| Points extrêmes légitimes | **Conservés.** Pas de winsorisation ni d'écrêtage : ils portent le signal de churn |
| Échelles très hétérogènes (de 1–5 à 0–2 000 000) | Les modèles **linéaires** exigent une mise à l'échelle robuste (ou une transformation log) ; les modèles **à base d'arbres** y sont insensibles, puisqu'ils ne travaillent que sur l'ordre des valeurs (§8.2) |
| Queue lourde sur la cible de régression `valeur_vie_client_eur` | Le **RMSE** sera dominé par quelques très gros comptes : il est lu **avec le MAE**, insensible à l'amplitude des erreurs extrêmes (§12.4) |
| Manquants inégalement répartis (`count`) | Stratégie d'imputation justifiée en §7.2, appuyée sur le test de manquance non informative (§6.3) |

---

## 5. Questions probables du jury — réponses courtes

**« Pourquoi n'avez-vous pas supprimé les valeurs extrêmes ? »**
Parce qu'elles sont plausibles métier et porteuses de signal. Un compte à 200 jours sans connexion
est exactement ce que le modèle doit détecter. La règle 1,5 × IQR en signale jusqu'à 16 % sur
certaines colonnes : elle mesure ici l'asymétrie de la distribution, pas des anomalies.

**« Pourquoi Spearman et pas Pearson ? »**
Pearson mesure une relation **linéaire** et chaque point y pèse par son amplitude : avec des
asymétries jusqu'à 5,6, une poignée de comptes dicterait le coefficient. Spearman travaille sur les
**rangs** : il détecte toute relation monotone et résiste aux queues lourdes.

**« Avez-vous transformé les variables asymétriques (log) ? »**
Non — le modèle retenu est à base d'arbres, invariant par transformation monotone : une transformation
log ne changerait aucun découpage. Elle serait en revanche nécessaire pour une régression linéaire, et
c'est ce qui est fait côté modèles linéaires comparés en §8.

**« Que signifie une asymétrie négative ? »**
Une queue étirée vers les valeurs basses. Ici elle est faible et concerne des variables **bornées**
(`csat` 1–5, `sante_compte_fin_periode` 0–100) : une borne supérieure empêche mécaniquement toute
queue à droite.

**« Pourquoi avoir ajouté `rapport_max_p75` alors que vous aviez déjà l'asymétrie ? »**
Les deux ne répondent pas à la même question. L'asymétrie est une mesure sans unité, qui dit si la
queue est lourde. Le rapport max/Q3 s'exprime dans l'échelle de la variable et dit jusqu'où elle va —
« le plus gros compte vaut 40 fois le seuil du dernier quartile » se comprend sans formation
statistique, ce qui est précisément l'usage attendu par les équipes CSM.
