from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from src.Classes.classes_objets.utilisateurs.client import Client
from src.Classes.classes_service.reservations_service import ReservationService
from src.Classes.classes_service.utilisateurs_service.client_service import ClientService

# La base est simulée : ReservationDAO est remplacé par un MagicMock.

CLIENT = Client("x", "client", id=1)
AUTRE_CLIENT = Client("x", "autre", id=2)


def faire_reservation(client=CLIENT, depart_dans_jours=7):
    depart = datetime.now() + timedelta(days=depart_dans_jours)
    return MagicMock(client=client, trajet=MagicMock(heure_depart=depart))


@pytest.fixture
def dao():
    """Le même faux DAO pour les deux services"""
    with (
        patch("src.Classes.classes_service.reservations_service.ReservationDAO") as dao_reservation,
        patch("src.Classes.classes_service.utilisateurs_service.client_service.ReservationDAO", dao_reservation),
    ):
        dao_reservation.return_value.annuler.return_value = True
        yield dao_reservation.return_value


# ------------------------------------------------------- ReservationService


def test_annuler_ok(dao):
    dao.trouver_par_id.return_value = faire_reservation()

    assert ReservationService().annuler(1) is True
    dao.annuler.assert_called_once_with(1)


def test_annuler_inexistante(dao):
    dao.trouver_par_id.return_value = None

    assert ReservationService().annuler(99) is False
    dao.annuler.assert_not_called()


def test_annuler_trajet_deja_parti(dao):
    dao.trouver_par_id.return_value = faire_reservation(depart_dans_jours=-1)

    with pytest.raises(ValueError, match="déjà parti"):
        ReservationService().annuler(1)
    dao.annuler.assert_not_called()


# ------------------------------------------------------------ ClientService


def test_client_annule_sa_reservation(dao):
    dao.trouver_par_id.return_value = faire_reservation()

    assert ClientService().annuler_reservation(CLIENT, 1) is True
    dao.annuler.assert_called_once_with(1)


def test_client_reservation_inexistante(dao):
    dao.trouver_par_id.return_value = None

    assert ClientService().annuler_reservation(CLIENT, 99) is False


def test_client_ne_peut_pas_annuler_la_reservation_d_un_autre(dao):
    dao.trouver_par_id.return_value = faire_reservation(client=AUTRE_CLIENT)

    with pytest.raises(ValueError, match="autre client"):
        ClientService().annuler_reservation(CLIENT, 1)
    dao.annuler.assert_not_called()
