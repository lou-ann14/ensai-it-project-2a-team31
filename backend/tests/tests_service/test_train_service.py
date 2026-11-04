from unittest.mock import patch

import pytest
from fastapi import HTTPException
from psycopg2.errors import UniqueViolation
from src.Classes.classes_objets.train import Train
from src.Classes.classes_service.train_service import TrainService

# La base est simulée : TrainDAO est remplacé par un MagicMock.


@pytest.fixture
def dao():
    with patch("src.Classes.classes_service.train_service.TrainDAO") as train_dao:
        yield train_dao.return_value


def test_creer_ok(dao):
    """Le train créé par le DAO est renvoyé"""
    dao.creer.side_effect = lambda train: train

    train = TrainService().creer("TGV", [100, 300], 8541)

    assert train.num_train == 8541
    assert train.places_initiales == [100, 300]


def test_creer_numero_deja_pris(dao):
    """Un numéro déjà utilisé donne une erreur claire"""
    dao.creer.side_effect = UniqueViolation()

    with pytest.raises(ValueError, match="existe déjà"):
        TrainService().creer("TGV", [100, 300], 8541)


@pytest.mark.parametrize("capacite", [[100], [1, 2, 3], [-1, 10], [10, -1]])
def test_creer_capacite_invalide(dao, capacite):
    """Il faut exactement deux nombres de places positifs ou nuls"""
    with pytest.raises(ValueError, match="capacité incorrecte"):
        TrainService().creer("TGV", capacite, 8541)

    dao.creer.assert_not_called()


def test_trouver_train_par_num_ok(dao):
    """Le train trouvé par le DAO est renvoyé"""
    train = Train("TGV", [100, 300], 8541, id_train=1)
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
    dao.trouver_train_par_num.return_value = Train("TGV", [100, 300], 8541, id_train=1)
    dao.modifier_capacite.return_value = True

    assert TrainService().modifier_capacite(8541, [120, 280]) is True
    dao.modifier_capacite.assert_called_once_with(8541, capacite=[120, 280])


def test_modifier_capacite_invalide(dao):
    """Une capacité incorrecte est refusée sans toucher à la base"""
    with pytest.raises(ValueError, match="capacité incorrecte"):
        TrainService().modifier_capacite(8541, [1, 2, 3])

    dao.modifier_capacite.assert_not_called()


def test_modifier_capacite_train_inexistant(dao):
    """Un train inconnu donne une erreur 404"""
    dao.trouver_train_par_num.return_value = None

    with pytest.raises(HTTPException) as erreur:
        TrainService().modifier_capacite(9999, [100, 300])

    assert erreur.value.status_code == 404
    dao.modifier_capacite.assert_not_called()
