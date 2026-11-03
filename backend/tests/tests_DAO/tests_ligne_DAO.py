from unittest.mock import MagicMock, patch

import pytest
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from src.Classes.classes_DAO.ligne_DAO import LigneDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne

# données préenregistrées (équivalent d'une bdd)

# gares : objets Gare, car rechercher prend des Gare en paramètres
gare_matabiau = Gare(1, "Matabiau", "Toulouse")
gare_massy = Gare(2, "MassyTGV", "Massy")
gare_montparnasse = Gare(3, "Montparnasse", "Paris")
gare_de_lyon = Gare(4, "Gare de Lyon", "Paris")
gare_part_dieu = Gare(5, "Part-Dieu", "Lyon")
gare_saint_charles = Gare(6, "Saint-Charles", "Marseille")
gare_rennes = Gare(7, "Gare de Rennes", "Rennes")

# lignes : dicts, car c'est ce que renvoie le curseur
ligne_toulouse_paris = {"id_ligne": 1, "id_gare_depart": 1, "id_gare_arrivee": 3}
ligne_paris_rennes = {"id_ligne": 2, "id_gare_depart": 3, "id_gare_arrivee": 7}
ligne_paris_lyon = {"id_ligne": 3, "id_gare_depart": 4, "id_gare_arrivee": 5}
ligne_lyon_marseille = {"id_ligne": 4, "id_gare_depart": 5, "id_gare_arrivee": 6}
ligne_massy_toulouse = {"id_ligne": 5, "id_gare_depart": 2, "id_gare_arrivee": 1}

lignes_bdd = [
    ligne_toulouse_paris,
    ligne_paris_rennes,
    ligne_paris_lyon,
    ligne_lyon_marseille,
    ligne_massy_toulouse,
  ]


@patch("src.Classes.classes_DAO.ligne_DAO.DBConnexion")
def test_creer_ok(mock_db):
    """Création Matabiau -> Montparnasse : le DAO envoie les bons ids et renvoie True"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = {"id_ligne": 1} # la nouvelle ligne a pour idd = 1
    ligne_cree = LigneDAO().creer(gare_matabiau, gare_montparnasse)
    requete, parametres = cursor.execute.call_args.args

    assert "INSERT INTO lignes" in requete
    assert parametres["id_gare_depart"] == 1
    assert parametres["id_gare_arrivee"] == 3
    assert ligne_cree is True


@patch("src.Classes.classes_DAO.ligne_DAO.DBConnexion")
def test_creer_gare_inexistante(mock_db):
    """La BDD refuse une gare inexistante : l'erreur remonte"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.execute.side_effect = ForeignKeyViolation  # execute lève l'erreur au lieu de s'exécuter
    gare_inexistante = Gare(99, "Inconnue", "Nulle part")

    with pytest.raises(ForeignKeyViolation):
        LigneDAO().creer(gare_matabiau, gare_inexistante)


@patch("src.Classes.classes_DAO.ligne_DAO.DBConnexion")
def test_creer_doublon(mock_db):
    """La BDD refuse une ligne déjà existante : l'erreur remonte"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.execute.side_effect = UniqueViolation

    with pytest.raises(UniqueViolation):
        LigneDAO().creer(gare_matabiau, gare_montparnasse)


@patch("src.Classes.classes_DAO.ligne_DAO.DBConnexion")
def test_rechercher_ok(mock_db):
    """Une ligne relie Matabiau à Montparnasse : on obtient cette Ligne"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = ligne_toulouse_paris
    ligne_trouvee = LigneDAO().rechercher(gare_matabiau, gare_montparnasse)
    requete, parametres = cursor.execute.call_args.args

    assert parametres["id_gare_depart"] == 1 
    assert parametres["id_gare_arrivee"] == 3
    assert isinstance(ligne_trouvee, Ligne)
    assert ligne_trouvee.id_ligne == 1
    assert ligne_trouvee.id_gare_depart == 1
    assert ligne_trouvee.id_gare_arrivee == 3


@patch("src.Classes.classes_DAO.ligne_DAO.DBConnexion")
def test_rechercher_introuvable(mock_db):
    """Aucune ligne ne relie Matabiau à Saint-Charles : on obtient None"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = None
    ligne_trouvee = LigneDAO().rechercher(gare_matabiau, gare_saint_charles)

    assert ligne_trouvee is None


@patch("src.Classes.classes_DAO.ligne_DAO.DBConnexion")
def test_rechercher_sens_inverse(mock_db):
    """Montparnasse puis Matabiau : le DAO envoie les gares dans le bon ordre et ne trouve rien"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = None
    ligne_trouvee = LigneDAO().rechercher(gare_montparnasse, gare_matabiau)
    requete, parametres = cursor.execute.call_args.args

    assert parametres["id_gare_depart"] == 3  # départ et arrivée ne sont pas inversés
    assert parametres["id_gare_arrivee"] == 1
    assert ligne_trouvee is None


@patch("src.Classes.classes_DAO.ligne_DAO.DBConnexion")
def test_trouver_par_id_ok(mock_db):
    """L'id 4 existe : on obtient la ligne Part-Dieu -> Saint-Charles"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = ligne_lyon_marseille
    ligne_trouvee = LigneDAO().trouver_par_id(4)
    requete, parametres = cursor.execute.call_args.args

    assert parametres["id_ligne"] == 4
    assert isinstance(ligne_trouvee, Ligne)
    assert ligne_trouvee.id_gare_depart == 5
    assert ligne_trouvee.id_gare_arrivee == 6


@patch("src.Classes.classes_DAO.ligne_DAO.DBConnexion")
def test_trouver_par_id_introuvable(mock_db):
    """L'id 99 n'existe pas : on obtient None"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = None
    ligne_trouvee = LigneDAO().trouver_par_id(99)

    assert ligne_trouvee is None
