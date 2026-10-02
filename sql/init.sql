-- Entrepôt du dispositif : scores historisés, actions CSM, indicateurs.
-- Trois tables, qui correspondent aux trois circuits de §11.1.

-- 1. Table de scores : une ligne par compte et par cycle (§11.1).
--    Elle porte la version du modèle et le plancher appliqué : un score doit
--    pouvoir être remonté jusqu'à l'artefact qui l'a produit (§13.3).
CREATE TABLE IF NOT EXISTS scores (
    cycle              date        NOT NULL,
    client_id          text        NOT NULL,
    probabilite_churn  numeric(6,4) NOT NULL CHECK (probabilite_churn BETWEEN 0 AND 1),
    valeur_estimee_eur numeric(14,2) NOT NULL,
    risque_de_perte_eur  numeric(14,2) NOT NULL,
    priorite           integer,
    alerte             boolean     NOT NULL,
    groupe_temoin      boolean     NOT NULL DEFAULT false,
    facteurs_principaux text,
    modele_version     text        NOT NULL,
    plancher_risque    numeric(4,2) NOT NULL,
    PRIMARY KEY (cycle, client_id)
);

-- 2. Actions engagées par les CSM : sans elles, les labels du prochain
--    ré-entraînement sont contaminés par l'intervention (§4.1, §13.2).
CREATE TABLE IF NOT EXISTS actions_csm (
    cycle       date NOT NULL,
    client_id   text NOT NULL,
    date_action timestamptz NOT NULL DEFAULT now(),
    type_action text NOT NULL,
    issue       text,
    PRIMARY KEY (cycle, client_id, date_action)
);

-- 3. Indicateurs de surveillance, un enregistrement par cycle (§13.1).
CREATE TABLE IF NOT EXISTS surveillance (
    cycle      date NOT NULL,
    indicateur text NOT NULL,
    variable   text,
    valeur     numeric NOT NULL,
    statut     text,
    PRIMARY KEY (cycle, indicateur, variable)
);

-- 4. Journal des exécutions : détecte l'échec ET la non-exécution (§11.4).
--    Un batch mensuel qui ne tourne pas ne produit aucun signal : c'est
--    l'absence de ligne pour le cycle courant qui déclenche l'alerte.
CREATE TABLE IF NOT EXISTS executions (
    horodatage     timestamptz NOT NULL,
    statut         text        NOT NULL CHECK (statut IN ('succes', 'echec')),
    modele_version text        NOT NULL,
    comptes        integer     NOT NULL DEFAULT 0,
    alertes        integer     NOT NULL DEFAULT 0,
    duree_s        numeric,
    message        text,
    machine        text,
    PRIMARY KEY (horodatage, machine)
);

CREATE INDEX IF NOT EXISTS scores_alerte_idx ON scores (cycle, alerte);
CREATE INDEX IF NOT EXISTS scores_client_idx ON scores (client_id);
