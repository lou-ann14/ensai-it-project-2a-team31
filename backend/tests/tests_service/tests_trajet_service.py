from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_service.trajet_service import TrajetService


def test_creer_ok():
    # GIVEN
    id_ligne, id_train, tarif_base = 1, 1, 30.0
    heure_depart = datetime.now()
    heure_arrivee = heure_depart + timedelta(hours=1)

    trajet_attendu = Trajet(
        id_ligne=id_ligne,
        id_train=id_train,
        heure_depart=heure_depart,
        heure_arrivee=heure_arrivee,
        tarif_base=tarif_base,
    )

    TrajetDAO().creer = MagicMock(return_value=trajet_attendu)

    # WHEN
    trajet = TrajetService().creer(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base)

    # THEN
    assert trajet.id_ligne == id_ligne


def test_creer_fail():
    "Ne parvient pas à créer de trajet car TrajetDAO().creer retourne False"
    # GIVEN
    id_ligne, id_train, tarif_base = 1, 1, 30.0
    heure_depart = datetime.now()
    heure_arrivee = heure_depart + timedelta(hours=1)
    TrajetDAO().creer = MagicMock(return_value=None)

    # WHEN
    trajet = TrajetService().creer(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base)

    # THEN
    assert trajet is None
