-- Données de démonstration, chargées après init_bdd.sql (tables) et admin.sql (comptes de test).
-- Les gares et les durées viennent de l'API SNCF.
-- Les dates sont calculées à partir du jour de l'initialisation : il y a toujours des trajets à venir.

INSERT INTO gares(id_sncf, nom, ville) VALUES
('stop_area:SNC:FR::LMU:7bdfb4d0-cb0a-11e8-8bfa-f784c1c7c611:', 'Rennes', 'Rennes'),
('stop_area:SNC:FR::LMU:9841ca00-cb0a-11e8-8bfa-f784c1c7c611:', 'Nantes', 'Nantes'),
('stop_area:SNC:FR::LMU:95203eb0-cb0a-11e8-8bfa-f784c1c7c611:', 'Paris Montparnasse Hall 1 - 2', 'Paris'),
('stop_area:SNC:FR::LMU:730a5a90-cb0a-11e8-8bfa-f784c1c7c611:', 'Bordeaux Saint-Jean', 'Bordeaux'),
('stop_area:SNC:FR::LMU:8ef85130-cb0a-11e8-8bfa-f784c1c7c611:', 'Le Mans', 'Le Mans');

-- Rennes -> Le Mans n'a pas de trajet (exemple de recherche sans résultat)
INSERT INTO lignes(id_gare_depart, id_gare_arrivee, id_collaborateur)
SELECT depart.id_gare, arrivee.id_gare, collaborateur.id
  FROM (VALUES
        (1, 'Rennes', 'Nantes'),
        (2, 'Nantes', 'Rennes'),
        (3, 'Rennes', 'Paris Montparnasse Hall 1 - 2'),
        (4, 'Paris Montparnasse Hall 1 - 2', 'Rennes'),
        (5, 'Nantes', 'Paris Montparnasse Hall 1 - 2'),
        (6, 'Paris Montparnasse Hall 1 - 2', 'Bordeaux Saint-Jean'),
        (7, 'Rennes', 'Le Mans')
       ) AS demo(rang, gare_depart, gare_arrivee)
  JOIN gares depart ON depart.nom = demo.gare_depart
  JOIN gares arrivee ON arrivee.nom = demo.gare_arrivee
  JOIN utilisateurs collaborateur ON collaborateur.nom_utilisateur = 'collaborateur'
 ORDER BY demo.rang;

-- Le train 5720 est tout petit pour montrer un trajet presque complet ; le train 5730 n'est pas utilisé
INSERT INTO trains(type_train, places_premieres, places_secondes, num_train) VALUES
('TGV', 100, 300, 8501),
('TGV', 120, 350, 8502),
('TER', 20, 80, 5710),
('TER', 2, 4, 5720),
('TER', 20, 80, 5730);

-- jours : décalage par rapport à aujourd'hui (négatif = trajet déjà parti) ; duree : en minutes
INSERT INTO trajets(id_ligne, id_train, heure_depart, heure_arrivee, temps_trajet, tarif_base)
SELECT ligne.id_ligne,
       train.id_train,
       CURRENT_DATE + demo.jours + demo.heure,
       CURRENT_DATE + demo.jours + demo.heure + demo.duree * INTERVAL '1 minute',
       demo.duree,
       demo.tarif
  FROM (VALUES
        ('Rennes', 'Nantes', 5710, -10, TIME '08:30', 77, 20),
        ('Rennes', 'Paris Montparnasse Hall 1 - 2', 8501, -5, TIME '07:30', 95, 46),
        ('Rennes', 'Nantes', 5710, 3, TIME '08:30', 77, 20),
        ('Nantes', 'Rennes', 5710, 3, TIME '17:30', 76, 20),
        ('Rennes', 'Nantes', 5720, 4, TIME '12:15', 77, 16),
        ('Nantes', 'Rennes', 5720, 4, TIME '18:00', 76, 16),
        ('Rennes', 'Paris Montparnasse Hall 1 - 2', 8501, 5, TIME '07:30', 95, 46),
        ('Paris Montparnasse Hall 1 - 2', 'Rennes', 8501, 5, TIME '18:30', 102, 52),
        ('Nantes', 'Paris Montparnasse Hall 1 - 2', 8502, 6, TIME '09:00', 138, 48),
        ('Paris Montparnasse Hall 1 - 2', 'Bordeaux Saint-Jean', 8502, 7, TIME '10:00', 137, 54),
        ('Rennes', 'Nantes', 5710, 14, TIME '08:30', 77, 18),
        ('Rennes', 'Paris Montparnasse Hall 1 - 2', 8501, 20, TIME '07:30', 95, 38)
       ) AS demo(gare_depart, gare_arrivee, num_train, jours, heure, duree, tarif)
  JOIN gares depart ON depart.nom = demo.gare_depart
  JOIN gares arrivee ON arrivee.nom = demo.gare_arrivee
  JOIN lignes ligne ON ligne.id_gare_depart = depart.id_gare AND ligne.id_gare_arrivee = arrivee.id_gare
  JOIN trains train ON train.num_train = demo.num_train
 ORDER BY demo.jours, demo.heure;

-- Compte « client » : deux voyages passés et deux à venir.
-- Train 5720 dans 4 jours à 12h15 : complet en 1re classe, une seule place libre (la 4) en 2de.
-- Prix comme dans tarification.py : 1re classe = tarif de base x 1,5
INSERT INTO reservations(id_client, id_trajet, place, classe, prix)
SELECT client.id,
       trajet.id_trajet,
       demo.place,
       demo.classe,
       CASE WHEN demo.classe = 1 THEN trajet.tarif_base * 1.5 ELSE trajet.tarif_base END
  FROM (VALUES
        (1, 'client', 5710, -10, TIME '08:30', '12', 2),
        (2, 'client', 8501, -5, TIME '07:30', '5', 1),
        (3, 'client', 5720, 4, TIME '12:15', '1', 2),
        (4, 'client', 8501, 5, TIME '07:30', '45', 2),
        (5, 'collaborateur', 5720, 4, TIME '12:15', '1', 1),
        (6, 'collaborateur', 5720, 4, TIME '12:15', '2', 2),
        (7, 'admin', 5720, 4, TIME '12:15', '2', 1),
        (8, 'admin', 5720, 4, TIME '12:15', '3', 2)
       ) AS demo(rang, nom_utilisateur, num_train, jours, heure, place, classe)
  JOIN utilisateurs client ON client.nom_utilisateur = demo.nom_utilisateur
  JOIN trains train ON train.num_train = demo.num_train
  JOIN trajets trajet ON trajet.id_train = train.id_train
                     AND trajet.heure_depart = CURRENT_DATE + demo.jours + demo.heure
 ORDER BY demo.rang;
