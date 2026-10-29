
DROP TABLE IF EXISTS gares CASCADE;
CREATE TABLE gares(
    id_gare SERIAL PRIMARY KEY,
    nom VARCHAR(256),
    ville VARCHAR(256)
);

CREATE TABLE utilisateurs(
    id SERIAL PRIMARY KEY,
    nom_utilisateur VARCHAR(256),
    mdp VARCHAR(256),
    grade VARCHAR(256),
    date_inscription DATE
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
    places_restantes VARCHAR(256)
);

CREATE TABLE trajets(
    id_trajet SERIAL PRIMARY KEY,
    id_ligne INT REFERENCES lignes(id_ligne),
    id_train INT REFERENCES trains(id_train),
    heure_depart TIMESTAMP,
    heure_arrivee TIMESTAMP,
    temps_trajet TIMESTAMP
);

CREATE TABLE reservations(
    id_reservation SERIAL PRIMARY KEY,
    id_trajet INT REFERENCES trajets(id_trajet),
    places_restantes INTEGER,
    prix FLOAT,
    tarif FLOAT
);

