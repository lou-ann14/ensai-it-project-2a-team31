INSERT INTO gares(nom, ville) VALUES
('marche', 'stp'),
('Paris Montparnasse', 'Paris'),
('Rennes', 'Rennes');

INSERT INTO lignes(id_gare_depart, id_gare_arrivee) VALUES
(2, 3);

INSERT INTO trains(type_train, places_premiere, places_seconde) VALUES
('TGV', 100, 300);

INSERT INTO trajets(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base) VALUES
(1, 1, '2026-12-01 10:00', '2026-12-01 12:00', 45.0);

[tool.pytest.ini_options]
python_files = ["tests_*.py"]
pythonpath = ["."]
