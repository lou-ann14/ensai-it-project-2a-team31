from unittest.mock import MagicMock, patch

from src.Classes.classes_DAO.gare_DAO import GareDAO
from src.Classes.classes_objets.gare import Gare


# données préenregistrées (équivalent d'une bdd)
gare_matabiau = {"id_gare": 1, "nom": "Matabiau", "ville": "Toulouse"}
gare_massy = {"id_gare": 2, "nom": "MassyTGV", "ville": "Massy"}
gare_montparnasse = {"id_gare": 3, "nom": "Montparnasse", "ville": "Paris"}
gare_de_lyon = {"id_gare": 4, "nom": "Gare de Lyon", "ville": "Paris"}
gare_part_dieu = {"id_gare": 5, "nom": "Part-Dieu", "ville": "Lyon"}
gare_saint_charles = {"id_gare": 6, "nom": "Saint-Charles", "ville": "Marseille"}
gare_rennes = {"id_gare": 7, "nom": "Gare de Rennes", "ville": "Rennes"}

gares_bdd = [
    gare_matabiau,
    gare_massy,
    gare_montparnasse,
    gare_de_lyon,
    gare_part_dieu,
    gare_saint_charles,
    gare_rennes,
]


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion") #ce qui permet de remplacer la connexion a la bdd
def test_rechercher_plusieurs_gares(mock_db):
    """La BDD renvoie 2 gares parisiennes : on obtient 2 objets Gare"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__() #on connecte le cursor a la "fausse" bdd 
    cursor.fetchall.return_value = [gare_de_lyon, gare_montparnasse] 
    gares_trouvees = GareDAO().rechercher(nom=None, ville="Paris")

    assert len(gares_trouvees) == 2  
    assert gares_trouvees[0].nom == "Gare de Lyon"
    assert gares_trouvees[1].id_gare == 3


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_rechercher_aucune_gare(mock_db):
    """La BDD ne renvoie aucune gare"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = []
    gares_trouvees = GareDAO().rechercher(nom=None, ville="Bruz")

    assert gares_trouvees == []


@patch
def test_rechercher_prefixe_nom_insensible_casse():
    pass


def test_rechercher_par_ville():
    pass


def test_rechercher_nom_et_ville():
    pass


def test_rechercher_tri_par_nom():
    pass


def test_trouver_par_id_ok():
    pass


def test_trouver_par_id_introuvable():
    pass
