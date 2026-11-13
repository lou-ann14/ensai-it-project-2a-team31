
DROP TABLE IF EXISTS gares CASCADE;
CREATE TABLE gares(
    id_gare SERIAL PRIMARY KEY,
    id_sncf VARCHAR(64) UNIQUE,
    nom VARCHAR(256),
    ville VARCHAR(256)
);

CREATE TABLE utilisateurs(
    id SERIAL PRIMARY KEY,
    nom_utilisateur VARCHAR(256) NOT NULL UNIQUE,  -- deux comptes ne peuvent pas avoir le même nom
    mdp VARCHAR(256) NOT NULL,
    grade VARCHAR(256) NOT NULL,
    date_inscription DATE DEFAULT CURRENT_DATE,     -- renseignée aussi pour les comptes de test
    token_acces VARCHAR(256)
);

CREATE TABLE lignes(
    id_ligne SERIAL PRIMARY KEY,
    id_gare_depart INT REFERENCES gares(id_gare),
    id_gare_arrivee INT REFERENCES gares(id_gare),
    id_collaborateur INT REFERENCES utilisateurs(id)
);

CREATE TABLE trains(
    id_train SERIAL PRIMARY KEY,
    type_train VARCHAR(256),
    places_premieres INTEGER,
    places_secondes INTEGER,
    num_train INTEGER UNIQUE
);

CREATE TABLE trajets(
    id_trajet SERIAL PRIMARY KEY,
    id_ligne INT REFERENCES lignes(id_ligne),
    id_train INT REFERENCES trains(id_train),
    heure_depart TIMESTAMP,
    heure_arrivee TIMESTAMP,
    temps_trajet INT,
    tarif_base FLOAT
);

CREATE TABLE reservations(
    id_reservation SERIAL PRIMARY KEY,
    id_client INT REFERENCES utilisateurs(id),
    id_trajet INT REFERENCES trajets(id_trajet),
    -- places restantes : calculées à la volée (capacité du train - réservations), pas stockées
    place VARCHAR(10),
    classe INTEGER,
    prix FLOAT,
    UNIQUE (id_trajet, classe, place)
);

