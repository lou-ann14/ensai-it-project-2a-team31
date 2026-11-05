from unittest.mock import MagicMock, patch

import pytest
from psycopg2.errors import ForeignKeyViolation
from src.Classes.classes_DAO.reservation_DAO import ReservationDAO
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_objets.utilisateurs.client import Client
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur

# données préenregistrées (équivalent d'une bdd)

# identifiants des clients et des trajets utilisés dans les réservations
id_client_fan2train = 1
id_client_groupeprojetinfo = 2
id_client_sans_reservation = 3

id_trajet_toulouse_paris = 10
id_trajet_paris_rennes = 11
id_trajet_paris_lyon = 12

# réservations : dicts, car c'est ce que renvoie le curseur
reservation_fan2train_toulouse_paris = {
    "id_reservation": 1,
    "id_client": 1,
    "id_trajet": 10,
    "place": "12A",
    "classe": 2,
    "prix": 45.0,
}
reservation_fan2train_paris_rennes = {
    "id_reservation": 2,
    "id_client": 1,
    "id_trajet": 11,
    "place": "3B",
    "classe": 1,
    "prix": 80.0,
}
reservation_groupeprojetinfo_toulouse_paris = {
    "id_reservation": 3,
    "id_client": 2,
    "id_trajet": 10,
    "place": "12B",
    "classe": 2,
    "prix": 45.0,
}
reservation_groupeprojetinfo_paris_lyon = {
    "id_reservation": 4,
    "id_client": 2,
    "id_trajet": 12,
    "place": "7C",
    "classe": 2,
    "prix": 30.5,
}

reservations_bdd = [
    reservation_fan2train_toulouse_paris,
    reservation_fan2train_paris_rennes,
    reservation_groupeprojetinfo_toulouse_paris,
    reservation_groupeprojetinfo_paris_lyon,
]

# réservations d'un client donné (ce que renverrait trouver_par_client)
reservations_fan2train = [reservation_fan2train_toulouse_paris, reservation_fan2train_paris_rennes]
reservations_groupeprojetinfo = [
    reservation_groupeprojetinfo_toulouse_paris,
    reservation_groupeprojetinfo_paris_lyon
    ]

# ce que renverraient les autres DAO (simulés) quand on reconstruit une réservation
# utilisateur : ce que renvoie UtilisateurDAO().trouver_par_id(1)
utilisateur_fan2train = Utilisateur(
    mdp="jaimelestrains", nom_utilisateur="fan2train", grade="CLIENT", id=id_client_fan2train
)
# trajet : MagicMock, pas besoin d'un vrai Trajet (avec Ligne, Train et Gares) pour ces tests
# spec=Trajet : Reservation vérifie que le trajet est de type Trajet, et le faux trajet passe ce contrôle
trajet_toulouse_paris = MagicMock(spec=Trajet, id_trajet=id_trajet_toulouse_paris)
trajet_paris_rennes = MagicMock(spec=Trajet, id_trajet=id_trajet_paris_rennes)


def creer_nouvelle_reservation():
    """Renvoie une nouvelle réservation (pas encore d'id_reservation) à insérer avec creer.

    Une fonction plutôt qu'une variable : creer modifie l'objet (il lui donne un id),
    chaque test a donc besoin de sa propre réservation.
    """
    client = Client(id=id_client_sans_reservation, mdp="hainedestrains", nom_utilisateur="vraifan2train")
    trajet = MagicMock(spec=Trajet, id_trajet=id_trajet_paris_lyon) #Le trajet est un MagicMock / creer n'utilise que trajet.id_trajet
    return Reservation(
        id_reservation=None,
        client=client,
        trajet=trajet,
        place="A14",
        classe=1,
        prix=150.5,
    )


@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_creer_ok(mock_db):
    """Création d'une réservation : le DAO renvoie la réservation avec son nouvel id"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = {"id_reservation": 5}  # la nouvelle réservation a pour id 5
    reservation_cree = ReservationDAO().creer(creer_nouvelle_reservation())

    assert reservation_cree.id_reservation == 5
    assert reservation_cree.place == "A14"
    assert reservation_cree.client.id == id_client_sans_reservation


@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_creer_parametres_envoyes(mock_db):
    """Le DAO envoie un INSERT avec les ids du client et du trajet, et les infos de la réservation"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = {"id_reservation": 5}
    ReservationDAO().creer(creer_nouvelle_reservation())
    requete, parametres = cursor.execute.call_args.args  # ce que le DAO a exécuté

    assert "INSERT INTO reservations" in requete
    assert parametres["id_client"] == id_client_sans_reservation
    assert parametres["id_trajet"] == id_trajet_paris_lyon
    assert parametres["place"] == "A14"
    assert parametres["classe"] == 1
    assert parametres["prix"] == 150.5


@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_creer_trajet_inexistant(mock_db):
    """Si le trajet n'existe pas, la BDD lève une ForeignKeyViolation que le DAO laisse remonter"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.execute.side_effect = ForeignKeyViolation()  # la BDD refuse l'insertion

    with pytest.raises(ForeignKeyViolation):
        ReservationDAO().creer(creer_nouvelle_reservation())


@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_annuler_ok(mock_db):
    """Annulation d'une réservation existante : 1 ligne supprimée, le DAO renvoie True"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.rowcount = 1  # la BDD a supprimé 1 ligne
    id_reservation = reservation_fan2train_toulouse_paris["id_reservation"]
    annulation = ReservationDAO().annuler(id_reservation)
    requete, parametres = cursor.execute.call_args.args

    assert "DELETE FROM reservations" in requete
    assert parametres["id_reservation"] == id_reservation
    assert annulation is True


@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_annuler_inexistante(mock_db):
    """Annulation d'une réservation qui n'existe pas : 0 ligne supprimée, le DAO renvoie False"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.rowcount = 0  # aucune ligne supprimée
    annulation = ReservationDAO().annuler(99)

    assert annulation is False


# trouver_par_id appelle UtilisateurDAO et TrajetDAO (via _construire_reservation)
# donc on les remplace aussi par des faux, sinon ils essaieraient de se connecter à la vraie BDD
@patch("src.Classes.classes_DAO.reservation_DAO.TrajetDAO")
@patch("src.Classes.classes_DAO.reservation_DAO.UtilisateurDAO")
@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_trouver_par_id_existe(mock_db, mock_utilisateur_dao, mock_trajet_dao):
    """La réservation 1 existe : le DAO renvoie une Reservation complète (Client + Trajet)"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__() 
    cursor.fetchone.return_value = reservation_fan2train_toulouse_paris  # la fausse BDD trouve la réservation 1
    mock_utilisateur_dao().trouver_par_id.return_value = utilisateur_fan2train  # le faux UtilisateurDAO renvoie fan2train
    mock_trajet_dao().trouver_par_id.return_value = trajet_toulouse_paris  # le faux TrajetDAO renvoie le trajet 10
    reservation = ReservationDAO().trouver_par_id(1)

    assert reservation.id_reservation == 1
    assert reservation.place == "12A"
    assert reservation.classe == 2
    assert reservation.prix == 45.0
    # le DAO a transformé l'Utilisateur renvoyé par UtilisateurDAO en Client
    assert isinstance(reservation.client, Client)
    assert reservation.client.id == id_client_fan2train
    assert reservation.client.nom_utilisateur == "fan2train"
    # "is" : on vérifie que c'est exactement l'objet renvoyé par TrajetDAO, pas une copie
    assert reservation.trajet is trajet_toulouse_paris


# pas besoin de simuler UtilisateurDAO et TrajetDAO ici : la BDD ne trouve rien,
# donc construire_reservation n'est jamais appelée
@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_trouver_par_id_parametre(mock_db):
    """Le DAO envoie bien l'id de la réservation recherchée à la requête"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = None  # peu importe le résultat, on regarde seulement ce qui a été envoyé
    ReservationDAO().trouver_par_id(4)
    requete, parametres = cursor.execute.call_args.args

    assert "FROM reservations" in requete
    assert parametres["id_reservation"] == 4


@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_trouver_par_id_inexistante(mock_db):
    """La réservation 99 n'existe pas : le DAO renvoie None"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = None
    reservation = ReservationDAO().trouver_par_id(99)

    assert reservation is None


# trouver_par_client appelle aussi UtilisateurDAO et TrajetDAO pour chaque réservation trouvée :
# on les remplace par des faux, comme pour trouver_par_id
@patch("src.Classes.classes_DAO.reservation_DAO.TrajetDAO")
@patch("src.Classes.classes_DAO.reservation_DAO.UtilisateurDAO")
@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_trouver_par_client_plusieurs(mock_db, mock_utilisateur_dao, mock_trajet_dao):
    """fan2train a 2 réservations : le DAO renvoie 2 Reservation complètes, dans l'ordre"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = reservations_fan2train
    mock_utilisateur_dao().trouver_par_id.return_value = utilisateur_fan2train
    # side_effect avec une liste : 1er appel -> 1er élément, 2e appel -> 2e élément (car chaque réservation a son propre trajet)
    mock_trajet_dao().trouver_par_id.side_effect = [trajet_toulouse_paris, trajet_paris_rennes]
    reservations = ReservationDAO().trouver_par_client(id_client_fan2train)

    assert len(reservations) == 2
    # l'ordre est conservé (la requête fait ORDER BY id_reservation)
    assert reservations[0].id_reservation == 1
    assert reservations[1].id_reservation == 2
    # chaque réservation a reçu le bon trajet
    assert reservations[0].trajet is trajet_toulouse_paris
    assert reservations[1].trajet is trajet_paris_rennes
    # les deux appartiennent bien au client fan2train, transformé en Client
    assert all(isinstance(r.client, Client) for r in reservations)
    assert all(r.client.id == id_client_fan2train for r in reservations)


@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_trouver_par_client_aucune(mock_db):
    """Le client 3 n'a aucune réservation : le DAO renvoie une liste vide"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = []
    reservations = ReservationDAO().trouver_par_client(id_client_sans_reservation)

    assert reservations == []


@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_trouver_par_client_parametre(mock_db):
    """Le DAO envoie bien l'id du client à la requête, et trie les réservations"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = []  #peu importe le résultat, on regarde seulement ce qui a été envoyé
    ReservationDAO().trouver_par_client(id_client_groupeprojetinfo)
    requete, parametres = cursor.execute.call_args.args

    assert "FROM reservations" in requete
    assert "ORDER BY id_reservation" in requete
    assert parametres["id_client"] == id_client_groupeprojetinfo


@patch("src.Classes.classes_DAO.reservation_DAO.TrajetDAO")
@patch("src.Classes.classes_DAO.reservation_DAO.UtilisateurDAO")
@patch("src.Classes.classes_DAO.reservation_DAO.DBConnexion")
def test_trouver_par_client_ignore_trajet_inexistant(mock_db, mock_utilisateur_dao, mock_trajet_dao):
    """Si le trajet d'une réservation n'existe plus, cette réservation est ignorée (pas de plantage)"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchall.return_value = reservations_fan2train
    mock_utilisateur_dao().trouver_par_id.return_value = utilisateur_fan2train
    # le 1er trajet existe, le 2e est introuvable (None)
    mock_trajet_dao().trouver_par_id.side_effect = [trajet_toulouse_paris, None]
    reservations = ReservationDAO().trouver_par_client(id_client_fan2train)
    assert len(reservations) == 1  # seule la réservation complète est gardée
    assert reservations[0].id_reservation == 1


# _construire_reservation ne parle pas à la BDD, elle reçoit une ligne déjà lue
# et appelle UtilisateurDAO et TrajetDAO / on simule seulement ces deux DAO, pas DBConnexion
@patch("src.Classes.classes_DAO.reservation_DAO.TrajetDAO")
@patch("src.Classes.classes_DAO.reservation_DAO.UtilisateurDAO")
def test_construire_reservation_ok(mock_utilisateur_dao, mock_trajet_dao):
    """À partir d'une ligne de la table reservations, on obtient une Reservation complète"""
    mock_utilisateur_dao().trouver_par_id.return_value = utilisateur_fan2train
    mock_trajet_dao().trouver_par_id.return_value = trajet_toulouse_paris
    reservation = ReservationDAO()._construire_reservation(reservation_fan2train_toulouse_paris)

    assert reservation.id_reservation == 1
    assert reservation.place == "12A"
    assert reservation.classe == 2
    assert reservation.prix == 45.0
    # l'Utilisateur a été transformé en Client, avec le même id et le même nom
    assert isinstance(reservation.client, Client)
    assert reservation.client.id == id_client_fan2train
    assert reservation.client.nom_utilisateur == "fan2train"
    assert reservation.trajet is trajet_toulouse_paris
    # en dessous, pour vérifier que le DAO demande par erreur trouver_par_id(ligne["id_trajet"])
    # à UtilisateurDAO. Le faux DAO renverrait quand même utilisateur_fan2train,
    # puisqu'on lui a dit de toujours le renvoyer, et le test passerait
    mock_utilisateur_dao().trouver_par_id.assert_called_with(id_client_fan2train)
    mock_trajet_dao().trouver_par_id.assert_called_with(id_trajet_toulouse_paris)


@patch("src.Classes.classes_DAO.reservation_DAO.TrajetDAO")
@patch("src.Classes.classes_DAO.reservation_DAO.UtilisateurDAO")
def test_construire_reservation_client_inexistant(mock_utilisateur_dao, mock_trajet_dao):
    """Le client de la réservation n'existe plus : on renvoie None au lieu de planter"""
    mock_utilisateur_dao().trouver_par_id.return_value = None  # client introuvable
    mock_trajet_dao().trouver_par_id.return_value = trajet_toulouse_paris
    reservation = ReservationDAO()._construire_reservation(reservation_fan2train_toulouse_paris)

    assert reservation is None


@patch("src.Classes.classes_DAO.reservation_DAO.TrajetDAO")
@patch("src.Classes.classes_DAO.reservation_DAO.UtilisateurDAO")
def test_construire_reservation_trajet_inexistant(mock_utilisateur_dao, mock_trajet_dao):
    """Le trajet de la réservation n'existe plus : on renvoie None au lieu de planter"""
    mock_utilisateur_dao().trouver_par_id.return_value = utilisateur_fan2train
    mock_trajet_dao().trouver_par_id.return_value = None  # trajet introuvable
    reservation = ReservationDAO()._construire_reservation(reservation_fan2train_toulouse_paris)

    assert reservation is None
