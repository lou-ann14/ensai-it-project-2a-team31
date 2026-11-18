from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_objets.utilisateurs.client import Client
from src.Classes.classes_service.reservations_service import ReservationService

# données préenregistrées
client_fan2train = Client("jaimelestrains", "fan2train", id=1)

gare_matabiau = Gare("Matabiau", "Toulouse", "stop_area:SNCF:87611004", 1)
gare_montparnasse = Gare("Montparnasse", "Paris", "stop_area:SNCF:87391003", 3)
ligne_toulouse_paris = Ligne(gare_matabiau, gare_montparnasse, id_ligne=1)
train_tgv = Train("TGV", 100, 300, 8541, id_train=1)


def creer_trajet(depart_dans_jours=7):
    """Trajet Toulouse -> Paris à 40 €, qui part dans depart_dans_jours jours (négatif = déjà parti)"""
    depart = datetime.now() + timedelta(days=depart_dans_jours)
    return Trajet(depart, depart + timedelta(hours=4), ligne_toulouse_paris, train_tgv, 40.0, id_trajet=10)


trajet_futur = creer_trajet()
trajet_passe = creer_trajet(depart_dans_jours=-1)

reservation_future = Reservation(client_fan2train, trajet_futur, "12A", 2, 40.0, id_reservation=1)
reservation_passee = Reservation(client_fan2train, trajet_passe, "12A", 2, 40.0, id_reservation=2)


@pytest.fixture
def dao():
    """Remplace ReservationDAO par un faux DAO : aucune vraie base n'est utilisée"""
    # Le même faux DAO sert aussi à TrajetService, qui compte les places réservées
    with (
        patch("src.Classes.classes_service.reservations_service.ReservationDAO") as reservation_dao,
        patch("src.Classes.classes_service.trajet_service.ReservationDAO", reservation_dao),
    ):
        reservation_dao.return_value.creer.side_effect = lambda reservation: reservation  # renvoie ce qu'on lui donne
        reservation_dao.return_value.compter_par_trajets.return_value = {}  # aucune place réservée
        yield reservation_dao.return_value


# Tests creer


def test_creer_seconde_classe_ok(dao):
    """Seconde classe : le prix est le tarif de base"""
    # WHEN
    res = ReservationService().creer(client_fan2train, trajet_futur, "12", 2)

    # THEN
    dao.creer.assert_called_once()
    assert res.client is client_fan2train
    assert res.trajet is trajet_futur
    assert res.classe == 2
    assert res.prix == 40.0


def test_creer_premiere_classe_ok(dao):
    """Première classe : le prix est multiplié par 1,5"""
    res = ReservationService().creer(client_fan2train, trajet_futur, "3", 1)

    assert res.prix == 60.0


def test_creer_place_nettoyee(dao):
    """Les espaces autour de la place sont retirés"""
    res = ReservationService().creer(client_fan2train, trajet_futur, "  12  ", 2)

    assert res.place == "12"


def test_creer_client_manquant(dao):
    """Pas de client : ValueError"""
    with pytest.raises(ValueError, match="client est obligatoire"):
        ReservationService().creer(None, trajet_futur, "12", 2)
    dao.creer.assert_not_called()


@pytest.mark.parametrize("classe", [0, 3, -1])
def test_creer_classe_invalide(dao, classe):
    """La classe n'est ni 1 ni 2 : ValueError"""
    with pytest.raises(ValueError, match="classe"):
        ReservationService().creer(client_fan2train, trajet_futur, "12A", classe)
    dao.creer.assert_not_called()


@pytest.mark.parametrize("place", [None, "", "   "])
def test_creer_place_manquante(dao, place):
    """Pas de numéro de place : ValueError"""
    with pytest.raises(ValueError, match="place est obligatoire"):
        ReservationService().creer(client_fan2train, trajet_futur, place, 2)
    dao.creer.assert_not_called()


def test_creer_trajet_manquant(dao):
    """Pas de trajet : ValueError"""
    with pytest.raises(ValueError, match="trajet est obligatoire"):
        ReservationService().creer(client_fan2train, None, "12", 2)
    dao.creer.assert_not_called()


def test_creer_trajet_deja_parti(dao):
    """Le trajet est parti hier : ValueError"""
    with pytest.raises(ValueError, match="déjà parti"):
        ReservationService().creer(client_fan2train, trajet_passe, "12", 2)
    dao.creer.assert_not_called()


def test_creer_place_deja_reservee(dao):
    """La BDD refuse (contrainte UNIQUE) : ValueError"""
    # GIVEN
    dao.creer.side_effect = UniqueViolation

    # WHEN / THEN
    with pytest.raises(ValueError, match="déjà réservée"):
        ReservationService().creer(client_fan2train, trajet_futur, "12", 2)


def test_creer_client_inexistant(dao):
    """La BDD refuse le client (clé étrangère) : ValueError"""
    # GIVEN
    dao.creer.side_effect = ForeignKeyViolation

    # WHEN / THEN
    with pytest.raises(ValueError, match="n'existe pas"):
        ReservationService().creer(client_fan2train, trajet_futur, "12", 2)


# Tests places (surréservation et numéro de place)


def test_creer_place_normalisee(dao):
    """« 007 » et « 7 » désignent la même place : elle est enregistrée sous la forme « 7 »"""
    res = ReservationService().creer(client_fan2train, trajet_futur, "007", 2)

    assert res.place == "7"


@pytest.mark.parametrize("place, classe", [("999Z", 2), ("12A", 2), ("0", 2), ("301", 2), ("101", 1), ("-3", 1)])
def test_creer_place_inexistante(dao, place, classe):
    """Le train TGV a 100 places en 1re et 300 en 2de : une place hors de ces numéros est refusée"""
    with pytest.raises(ValueError, match="numéro entre 1 et"):
        ReservationService().creer(client_fan2train, trajet_futur, place, classe)
    dao.creer.assert_not_called()


def test_creer_derniere_place_ok(dao):
    """Il reste 1 place en 1re classe (99 réservées sur 100) : la réservation passe"""
    dao.compter_par_trajets.return_value = {trajet_futur.id_trajet: {1: 99}}

    res = ReservationService().creer(client_fan2train, trajet_futur, "100", 1)

    assert res.place == "100"
    dao.creer.assert_called_once()


def test_creer_classe_complete(dao):
    """Les 300 places de seconde sont réservées : ValueError « complet », même si la 1re a de la place"""
    dao.compter_par_trajets.return_value = {trajet_futur.id_trajet: {2: 300, 1: 10}}

    with pytest.raises(ValueError, match="complet en seconde classe"):
        ReservationService().creer(client_fan2train, trajet_futur, "12", 2)
    dao.creer.assert_not_called()


def test_creer_trajet_sans_train(dao):
    """Un trajet sans train n'a pas de places : il n'est pas réservable"""
    trajet = creer_trajet()
    trajet.train = None

    with pytest.raises(ValueError, match="Aucun train"):
        ReservationService().creer(client_fan2train, trajet, "12", 2)
    dao.creer.assert_not_called()


# Tests annuler


def test_annuler_ok(dao):
    """Trajet futur : la réservation est annulée"""
    # GIVEN
    dao.trouver_par_id.return_value = reservation_future
    dao.annuler.return_value = True

    # WHEN / THEN
    assert ReservationService().annuler(1, client_fan2train.id) is True
    dao.annuler.assert_called_once_with(1)


def test_annuler_inexistante(dao):
    """La réservation 99 n'existe pas : False, sans appeler annuler"""
    dao.trouver_par_id.return_value = None

    assert ReservationService().annuler(99, client_fan2train.id) is False
    dao.annuler.assert_not_called()


def test_annuler_trajet_deja_parti(dao):
    """Le trajet est parti : ValueError, sans appeler annuler"""
    dao.trouver_par_id.return_value = reservation_passee

    with pytest.raises(ValueError, match="déjà parti"):
        ReservationService().annuler(2, client_fan2train.id)
    dao.annuler.assert_not_called()


def test_annuler_reservation_d_un_autre_client(dao):
    """Un client ne peut pas annuler la réservation d'un autre : ValueError, sans appeler annuler"""
    dao.trouver_par_id.return_value = reservation_future  # appartient au client #1

    with pytest.raises(ValueError, match="autre client"):
        ReservationService().annuler(1, id_client=2)
    dao.annuler.assert_not_called()


# Tests historique_par_client


def test_historique_par_client_ok(dao):
    """Le service renvoie les réservations trouvées par le DAO"""
    # GIVEN
    dao.trouver_par_client.return_value = [reservation_future, reservation_passee]

    # WHEN
    res = ReservationService().historique_par_client(1)

    # THEN
    dao.trouver_par_client.assert_called_once_with(1)
    assert res == [reservation_future, reservation_passee]


def test_historique_par_client_aucune(dao):
    """Aucune réservation : liste vide"""
    dao.trouver_par_client.return_value = []

    assert ReservationService().historique_par_client(1) == []


def test_historique_client_manquant(dao):
    """Pas d'id client : ValueError"""
    with pytest.raises(ValueError, match="client est obligatoire"):
        ReservationService().historique_par_client(None)
    dao.trouver_par_client.assert_not_called()
