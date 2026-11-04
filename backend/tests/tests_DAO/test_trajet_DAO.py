from datetime import datetime
from unittest.mock import patch

import pytest
from psycopg2.errors import ForeignKeyViolation
from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet

# données préenregistrées (équivalent d'une bdd)

# gares, lignes et trains : objets, car creer / modifier / rechercher prennent des objets
gare_matabiau = Gare(nom="Matabiau", ville="Toulouse", id_sncf="stop_area:SNCF:1", id_gare=1)
gare_montparnasse = Gare(nom="Montparnasse", ville="Paris", id_sncf="stop_area:SNCF:3", id_gare=3)
gare_rennes = Gare(nom="Gare de Rennes", ville="Rennes", id_sncf="stop_area:SNCF:7", id_gare=7)

ligne_toulouse_paris = Ligne(gare_depart=gare_matabiau, gare_arrivee=gare_montparnasse, id_ligne=1)
ligne_paris_rennes = Ligne(gare_depart=gare_montparnasse, gare_arrivee=gare_rennes, id_ligne=2)

train_tgv = Train(type_train="TGV", places_premieres=200, places_secondes=400, num_train=8541, id_train=1)

# trajets : dicts, car c'est ce que renvoie le curseur après la requête SELECT_TRAJET
# (le trajet, sa ligne, ses deux gares et son train sur une seule ligne)
trajet_toulouse_paris_matin = {
    "id_trajet": 10,
    "heure_depart": datetime(2026, 1, 15, 8, 0),
    "heure_arrivee": datetime(2026, 1, 15, 12, 30),
    "tarif_base": 45.0,
    "temps_trajet": 270,
    "id_ligne": 1,
    "id_gare_depart": 1,
    "nom_gare_depart": "Matabiau",
    "ville_gare_depart": "Toulouse",
    "id_sncf_gare_depart": "stop_area:SNCF:1",
    "id_gare_arrivee": 3,
    "nom_gare_arrivee": "Montparnasse",
    "ville_gare_arrivee": "Paris",
    "id_sncf_gare_arrivee": "stop_area:SNCF:3",
    "id_train": 1,
    "type_train": "TGV",
    "places_premieres": 200,
    "places_secondes": 400,
    "num_train": 8541,
}
trajet_toulouse_paris_soir = {
    **trajet_toulouse_paris_matin,  # même ligne et même train que le trajet du matin
    "id_trajet": 11,
    "heure_depart": datetime(2026, 1, 15, 18, 0),
    "heure_arrivee": datetime(2026, 1, 15, 22, 30),
}
# trajet sans train : le LEFT JOIN renvoie None pour toutes les colonnes du train
trajet_paris_rennes_sans_train = {
    "id_trajet": 12,
    "heure_depart": datetime(2026, 1, 16, 9, 0),
    "heure_arrivee": datetime(2026, 1, 16, 10, 30),
    "tarif_base": 30.0,
    "temps_trajet": 90,
    "id_ligne": 2,
    "id_gare_depart": 3,
    "nom_gare_depart": "Montparnasse",
    "ville_gare_depart": "Paris",
    "id_sncf_gare_depart": "stop_area:SNCF:3",
    "id_gare_arrivee": 7,
    "nom_gare_arrivee": "Gare de Rennes",
    "ville_gare_arrivee": "Rennes",
    "id_sncf_gare_arrivee": "stop_area:SNCF:7",
    "id_train": None,
    "type_train": None,
    "places_premieres": None,
    "places_secondes": None,
    "num_train": None,
}

trajets_bdd = [trajet_toulouse_paris_matin, trajet_toulouse_paris_soir, trajet_paris_rennes_sans_train]


def creer_nouveau_trajet():
    """Renvoie un nouveau trajet (pas encore d'id_trajet) à insérer avec creer.

    Une fonction plutôt qu'une variable : creer modifie l'objet (il lui donne un id),
    chaque test a donc besoin de son propre trajet.
    """
    return Trajet(
        heure_depart=datetime(2026, 2, 1, 7, 0),
        heure_arrivee=datetime(2026, 2, 1, 11, 30),
        ligne=ligne_toulouse_paris,
        train=train_tgv,
        tarif_base=50.0,
        temps_trajet=270,
    )


# Tests creer


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_creer_ok(mock_db):
    """Création d'un trajet : le DAO renvoie le trajet avec son nouvel id"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = {"id_trajet": 13}  # le nouveau trajet a pour id 13
    trajet = creer_nouveau_trajet()
    trajet_cree = TrajetDAO().creer(trajet)

    assert trajet_cree is trajet  # le DAO renvoie le même objet, complété
    assert trajet_cree.id_trajet == 13


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_creer_parametres_envoyes(mock_db):
    """Le DAO envoie un INSERT avec les ids de la ligne et du train, et les infos du trajet"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = {"id_trajet": 13}
    TrajetDAO().creer(creer_nouveau_trajet())
    requete, parametres = cursor.execute.call_args.args  # ce que le DAO a exécuté

    assert "INSERT INTO trajets" in requete
    assert parametres == {
        "id_ligne": 1,
        "id_train": 1,
        "heure_depart": datetime(2026, 2, 1, 7, 0),
        "heure_arrivee": datetime(2026, 2, 1, 11, 30),
        "tarif_base": 50.0,
        "temps_trajet": 270,
    }


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_creer_ligne_inexistante(mock_db):
    """Si la ligne ou le train n'existe pas, la BDD lève une ForeignKeyViolation que le DAO laisse remonter"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.execute.side_effect = ForeignKeyViolation()  # la BDD refuse l'insertion

    with pytest.raises(ForeignKeyViolation):
        TrajetDAO().creer(creer_nouveau_trajet())


# Tests modifier


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_modifier_ok(mock_db):
    """Modification d'un trajet existant : 1 ligne modifiée, le DAO renvoie True"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.rowcount = 1  # la BDD a modifié 1 trajet
    trajet = creer_nouveau_trajet()
    trajet.id_trajet = 10  # on modifie le trajet 10
    modification = TrajetDAO().modifier(trajet)
    requete, parametres = cursor.execute.call_args.args

    assert "UPDATE trajets" in requete
    assert parametres["id_trajet"] == 10  # le bon trajet est modifié
    assert parametres["tarif_base"] == 50.0  # avec les nouvelles valeurs
    assert modification is True


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_modifier_inexistant(mock_db):
    """Modification d'un trajet qui n'existe pas : 0 ligne modifiée, le DAO renvoie False"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.rowcount = 0  # aucun trajet modifié
    trajet = creer_nouveau_trajet()
    trajet.id_trajet = 99

    assert TrajetDAO().modifier(trajet) is False


# Tests supprimer


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_supprimer_ok(mock_db):
    """Suppression du trajet du matin : 1 trajet supprimé, le DAO renvoie True"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.rowcount = 1  # la BDD a supprimé 1 trajet
    id_trajet = trajet_toulouse_paris_matin["id_trajet"]
    suppression = TrajetDAO().supprimer(id_trajet)
    requete, parametres = cursor.execute.call_args.args

    assert "DELETE FROM trajets" in requete
    assert parametres["id_trajet"] == id_trajet
    assert suppression is True


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_supprimer_inexistant(mock_db):
    """Suppression d'un trajet qui n'existe pas : 0 trajet supprimé, le DAO renvoie False"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.rowcount = 0  # aucun trajet supprimé

    assert TrajetDAO().supprimer(99) is False


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_supprimer_avec_reservations(mock_db):
    """Le trajet a encore des réservations : la BDD refuse et le DAO laisse remonter l'erreur"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.execute.side_effect = ForeignKeyViolation()

    with pytest.raises(ForeignKeyViolation):
        TrajetDAO().supprimer(10)


# Tests rechercher


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_rechercher_plusieurs(mock_db):
    """2 trajets Toulouse -> Paris le 15 janvier : on obtient 2 objets Trajet, dans l'ordre"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = [trajet_toulouse_paris_matin, trajet_toulouse_paris_soir]
    trajets = TrajetDAO().rechercher(gare_matabiau, gare_montparnasse, datetime(2026, 1, 15))

    assert len(trajets) == 2
    assert all(isinstance(t, Trajet) for t in trajets)
    assert trajets[0].id_trajet == 10  # le matin avant le soir
    assert trajets[1].id_trajet == 11


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_rechercher_aucun(mock_db):
    """Aucun trajet ce jour-là : le DAO renvoie une liste vide"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = []
    trajets = TrajetDAO().rechercher(gare_matabiau, gare_rennes, datetime(2026, 1, 15))

    assert trajets == []  # une liste vide, et pas None


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_rechercher_parametres(mock_db):
    """Le DAO envoie les ids des gares et la date, et trie par heure de départ"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = []
    date = datetime(2026, 1, 15)
    TrajetDAO().rechercher(gare_matabiau, gare_montparnasse, date)
    requete, parametres = cursor.execute.call_args.args

    assert "ORDER BY t.heure_depart" in requete
    assert parametres == {"id_gare_depart": 1, "id_gare_arrivee": 3, "date": date}


# Tests trouver_par_id


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_trouver_par_id_ok(mock_db):
    """Le trajet 10 existe : on obtient un Trajet complet (Ligne, Gares et Train)"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = trajet_toulouse_paris_matin
    trajet = TrajetDAO().trouver_par_id(10)
    requete, parametres = cursor.execute.call_args.args

    assert parametres["id_trajet"] == 10
    # les infos du trajet
    assert trajet.id_trajet == 10
    assert trajet.tarif_base == 45.0
    assert trajet.temps_trajet == 270
    # la ligne et ses deux gares ont été reconstruites
    assert trajet.ligne.id_ligne == 1
    assert trajet.ligne.gare_depart.nom == "Matabiau"
    assert trajet.ligne.gare_arrivee.nom == "Montparnasse"
    # le train a été reconstruit
    assert trajet.train.id_train == 1
    assert trajet.train.num_train == 8541


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_trouver_par_id_sans_train(mock_db):
    """Le trajet 12 n'a pas encore de train : son train vaut None"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = trajet_paris_rennes_sans_train
    trajet = TrajetDAO().trouver_par_id(12)

    assert trajet.id_trajet == 12
    assert trajet.ligne.gare_arrivee.nom == "Gare de Rennes"
    assert trajet.train is None


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_trouver_par_id_introuvable(mock_db):
    """L'id 99 n'existe pas : on obtient None"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = None  # fetchone renvoie None quand la requête ne trouve rien

    assert TrajetDAO().trouver_par_id(99) is None
