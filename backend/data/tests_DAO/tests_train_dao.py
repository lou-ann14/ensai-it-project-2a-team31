from src.Classes.classes_DAO.train_DAO import TrainDAO
from src.Classes.classes_objets.train import Train


def test_trouver_par_id_ok():
    """Retrouve le train présent dans test_bdd.sql"""
    # WHEN
    train = TrainDAO().trouver_par_id(1)

    # THEN
    assert train is not None
    assert train.id_train == 1
    assert train.type_train == "TGV"
    assert train.places_initiales == [100, 300]


def test_trouver_par_id_inexistant():
    """Un id inconnu renvoie None"""
    # WHEN
    train = TrainDAO().trouver_par_id(999)

    # THEN
    assert train is None


def test_creer_ok():
    """Crée un train : son id est renseigné et on peut le relire"""
    # GIVEN
    nouveau = Train(None, "Ouigo", [0, 500])

    # WHEN
    cree = TrainDAO().creer(nouveau)

    # THEN
    assert cree.id_train is not None
    relu = TrainDAO().trouver_par_id(cree.id_train)
    assert relu.type_train == "Ouigo"
    assert relu.places_initiales == [0, 500]