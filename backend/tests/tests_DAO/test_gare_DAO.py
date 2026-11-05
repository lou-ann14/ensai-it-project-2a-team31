from unittest.mock import MagicMock, patch

from src.Classes.classes_DAO.gare_DAO import GareDAO
from src.Classes.classes_objets.gare import Gare

# données préenregistrées (équivalent d'une bdd)
gare_matabiau = {"id_gare": 1, "nom": "Matabiau", "ville": "Toulouse", "id_sncf": "stop_area:SNCF:1"}
gare_massy = {"id_gare": 2, "nom": "MassyTGV", "ville": "Massy", "id_sncf": "stop_area:SNCF:2"}
gare_montparnasse = {"id_gare": 3, "nom": "Montparnasse", "ville": "Paris", "id_sncf": "stop_area:SNCF:3"}
gare_de_lyon = {"id_gare": 4, "nom": "Gare de Lyon", "ville": "Paris", "id_sncf": "stop_area:SNCF:4"}
gare_part_dieu = {"id_gare": 5, "nom": "Part-Dieu", "ville": "Lyon", "id_sncf": "stop_area:SNCF:5"}
gare_saint_charles = {"id_gare": 6, "nom": "Saint-Charles", "ville": "Marseille", "id_sncf": "stop_area:SNCF:6"}
gare_rennes = {"id_gare": 7, "nom": "Gare de Rennes", "ville": "Rennes", "id_sncf": "stop_area:SNCF:7"}

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


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_rechercher_prefixe_nom_insensible_casse(mock_db):
    """La recherche 'mat' envoie le préfixe 'mat%' avec un ILIKE"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = [gare_matabiau]
    gares_trouvees = GareDAO().rechercher(nom="mat", ville=None)
    requete, parametres = cursor.execute.call_args.args  # il regarde ce que le DAO a éxécuté
    
    assert "ILIKE" in requete
    assert parametres["nom"] == "mat%"
    assert gares_trouvees[0].nom == "Matabiau"


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_rechercher_par_ville(mock_db):
    """La recherche 'Paris' envoie 'Paris%' pour la ville et rien pour le nom"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = [gare_de_lyon, gare_montparnasse]
    gares_trouvees = GareDAO().rechercher(nom=None, ville="Paris")
    requete, parametres = cursor.execute.call_args.args

    assert parametres["ville"] == "Paris%"
    assert parametres["nom"] is None
    assert [gare.nom for gare in gares_trouvees] == ["Gare de Lyon", "Montparnasse"]


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_rechercher_nom_et_ville(mock_db):
    """Nom et ville renseignés : les deux préfixes sont envoyés avec un AND"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = [gare_montparnasse]
    gares_trouvees = GareDAO().rechercher(nom="Mont", ville="Paris")
    requete, parametres = cursor.execute.call_args.args

    assert "AND" in requete
    assert parametres["nom"] == "Mont%"
    assert parametres["ville"] == "Paris%"
    assert gares_trouvees[0].nom == "Montparnasse"


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_rechercher_tri_par_nom(mock_db):
    """La requête demande un tri par nom"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = gares_bdd
    GareDAO().rechercher(nom=None, ville=None)
    requete, parametres = cursor.execute.call_args.args

    assert "ORDER BY nom" in requete


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_trouver_par_id_ok(mock_db):
    """L'id 1 existe donc on obtient la gare Matabiau"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = gare_matabiau
    gare_trouvee = GareDAO().trouver_par_id(1)
    requete, parametres = cursor.execute.call_args.args

    assert parametres["id_gare"] == 1
    assert isinstance(gare_trouvee, Gare)
    assert gare_trouvee.nom == "Matabiau"
    assert gare_trouvee.ville == "Toulouse"


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_trouver_par_id_introuvable(mock_db):
    """L'id 99 n'existe pas : on obtient None"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = None
    gare_trouvee = GareDAO().trouver_par_id(99)

    assert gare_trouvee is None


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_supprimer_ok(mock_db):
    """Suppression de la gare de Rennes : 1 gare supprimée, le DAO renvoie True"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.rowcount = 1  # la BDD a supprimé 1 gare
    id_gare = gare_rennes["id_gare"]
    suppression = GareDAO().supprimer(id_gare)
    requete, parametres = cursor.execute.call_args.args  # ce que le DAO a exécuté

    assert "DELETE FROM gares" in requete
    assert parametres["id_gare"] == id_gare
    assert suppression is True


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_supprimer_inexistante(mock_db):
    """Suppression d'une gare qui n'existe pas : 0 gare supprimée, le DAO renvoie False"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.rowcount = 0  # aucune gare supprimée
    suppression = GareDAO().supprimer(99)

    assert suppression is False


# Tests creer_ou_mettre_a_jour


def creer_nouvelle_gare():
    """Renvoie une nouvelle gare venant de l'API, pas encore enregistrée (pas d'id_gare).
    Fonction et pas variable : le DAO modifie la gare en lui donnant un id."""
    return Gare("Gare de Rennes", "Rennes", "stop_area:SNCF:7")


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_creer_ou_mettre_a_jour_ok(mock_db):
    """La BDD renvoie l'id 7 : la gare renvoyée a cet id"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = {"id_gare": 7}
    gare = creer_nouvelle_gare()

    gare_enregistree = GareDAO().creer_ou_mettre_a_jour(gare)

    assert gare_enregistree is gare  # c'est la même gare, complétée
    assert gare_enregistree.id_gare == 7


@patch("src.Classes.classes_DAO.gare_DAO.DBConnexion")
def test_creer_ou_mettre_a_jour_parametres(mock_db):
    """Le DAO envoie nom, ville et id_sncf, et met à jour la gare si l'id_sncf existe déjà"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = {"id_gare": 7}

    GareDAO().creer_ou_mettre_a_jour(creer_nouvelle_gare())
    requete, parametres = cursor.execute.call_args.args

    assert "INSERT INTO gares" in requete
    assert "ON CONFLICT (id_sncf) DO UPDATE" in requete  # pas de doublon pour une gare déjà importée
    assert parametres == {"nom": "Gare de Rennes", "ville": "Rennes", "id_sncf": "stop_area:SNCF:7"}
