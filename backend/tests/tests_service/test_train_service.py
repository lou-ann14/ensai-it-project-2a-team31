from unittest.mock import patch

import pytest
from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from src.Classes.classes_objets.train import Train
from src.Classes.classes_service.train_service import TrainService

# La base est simulée : TrainDAO et ReservationDAO sont remplacés par des MagicMock.


@pytest.fixture
def reservation_dao():
    """Par défaut, aucune réservation à venir : aucune capacité minimale"""
    with patch("src.Classes.classes_service.train_service.ReservationDAO") as dao_reservation:
        dao_reservation.return_value.capacite_minimale_par_train.return_value = {}
        yield dao_reservation.return_value


@pytest.fixture
def dao(reservation_dao):
    with patch("src.Classes.classes_service.train_service.TrainDAO") as train_dao:
        yield train_dao.return_value


def test_creer_ok(dao):
    """Le train créé par le DAO est renvoyé"""
    dao.creer.side_effect = lambda train: train

    train = TrainService().creer("TGV", 100, 300, 8541)

    assert train.num_train == 8541
    assert train.places_premieres == 100
    assert train.places_secondes == 300


def test_creer_numero_deja_pris(dao):
    """Un numéro déjà utilisé donne une erreur claire"""
    dao.creer.side_effect = UniqueViolation()

    with pytest.raises(ValueError, match="existe déjà"):
        TrainService().creer("TGV", 100, 300, 8541)


@pytest.mark.parametrize("capacite", [(-1, 10), (10, -1)])
def test_creer_capacite_invalide(dao, capacite):
    """Les nombres de places doivent être positifs ou nuls"""
    with pytest.raises(ValueError, match="capacité incorrecte"):
        TrainService().creer("TGV", *capacite, 8541)

    dao.creer.assert_not_called()


def test_trouver_train_par_num_ok(dao):
    """Le train trouvé par le DAO est renvoyé"""
    train = Train("TGV", 100, 300, 8541, id_train=1)
    dao.trouver_train_par_num.return_value = train

    assert TrainService().trouver_train_par_num(8541) is train


def test_trouver_train_par_num_inexistant(dao):
    """Un train inconnu donne une erreur 404"""
    dao.trouver_train_par_num.return_value = None

    with pytest.raises(HTTPException) as erreur:
        TrainService().trouver_train_par_num(9999)

    assert erreur.value.status_code == 404


def test_modifier_capacite_ok(dao):
    """La nouvelle capacité est transmise au DAO"""
    dao.trouver_train_par_num.return_value = Train("TGV", 100, 300, 8541, id_train=1)
    dao.modifier_capacite.return_value = True

    assert TrainService().modifier_capacite(8541, 120, 280) is True
    dao.modifier_capacite.assert_called_once_with(8541, capacite_premiere=120, capacite_seconde=280)


def test_modifier_capacite_invalide(dao):
    """Une capacité incorrecte est refusée sans toucher à la base"""
    with pytest.raises(ValueError, match="capacité incorrecte"):
        TrainService().modifier_capacite(8541, -1, 2)

    dao.modifier_capacite.assert_not_called()


def test_modifier_capacite_train_inexistant(dao):
    """Un train inconnu donne une erreur 404"""
    dao.trouver_train_par_num.return_value = None

    with pytest.raises(HTTPException) as erreur:
        TrainService().modifier_capacite(9999, 100, 300)

    assert erreur.value.status_code == 404
    dao.modifier_capacite.assert_not_called()


def test_modifier_capacite_reduction_possible(dao, reservation_dao):
    """5 places réservées en 2de (jusqu'à la n°40) : on peut descendre à 40, pas en dessous"""
    dao.trouver_train_par_num.return_value = Train("TGV", 100, 300, 8541, id_train=1)
    dao.modifier_capacite.return_value = True
    reservation_dao.capacite_minimale_par_train.return_value = {2: 40}

    assert TrainService().modifier_capacite(8541, 100, 40) is True
    reservation_dao.capacite_minimale_par_train.assert_called_once_with(1)


@pytest.mark.parametrize(
    "minimum, places_premieres, places_secondes, message",
    [
        ({2: 40}, 100, 39, "39 places en seconde classe"),
        ({1: 12}, 11, 300, "11 places en première classe"),
        ({1: 3, 2: 250}, 100, 0, "0 places en seconde classe"),
    ],
)
def test_modifier_capacite_sous_les_reservations(dao, reservation_dao, minimum, places_premieres, places_secondes, message):
    """La nouvelle capacité est sous ce qui est réservé : ValueError, et la base n'est pas modifiée"""
    dao.trouver_train_par_num.return_value = Train("TGV", 100, 300, 8541, id_train=1)
    reservation_dao.capacite_minimale_par_train.return_value = minimum

    with pytest.raises(ValueError, match=message):
        TrainService().modifier_capacite(8541, places_premieres, places_secondes)
    dao.modifier_capacite.assert_not_called()


def test_modifier_capacite_augmentation_toujours_possible(dao, reservation_dao):
    """Augmenter la capacité ne pose jamais de problème, même avec des réservations"""
    dao.trouver_train_par_num.return_value = Train("TGV", 100, 300, 8541, id_train=1)
    dao.modifier_capacite.return_value = True
    reservation_dao.capacite_minimale_par_train.return_value = {1: 100, 2: 300}

    assert TrainService().modifier_capacite(8541, 150, 400) is True


# Tests supprimer


def test_supprimer_ok(dao):
    """Le train 8541 existe (id 1) : il est supprimé par son id"""
    dao.trouver_id_par_num.return_value = 1
    dao.supprimer.return_value = True

    assert TrainService().supprimer(8541) is True
    dao.trouver_id_par_num.assert_called_once_with(8541)
    dao.supprimer.assert_called_once_with(1)


def test_supprimer_train_inexistant(dao):
    """Le train 9999 n'existe pas : False, sans appeler supprimer"""
    dao.trouver_id_par_num.return_value = None

    assert TrainService().supprimer(9999) is False
    dao.supprimer.assert_not_called()


def test_supprimer_train_utilise_par_des_trajets(dao):
    """La BDD refuse (clé étrangère) : ValueError"""
    dao.trouver_id_par_num.return_value = 1
    dao.supprimer.side_effect = ForeignKeyViolation

    with pytest.raises(ValueError, match="des trajets l'utilisent"):
        TrainService().supprimer(8541)
