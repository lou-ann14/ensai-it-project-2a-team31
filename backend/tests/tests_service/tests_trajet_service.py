from datetime import datetime
from unittest.mock import MagicMock

import pytest
from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_service.trajet_service import TrajetService

# from psycopg2.errors import ForeignKeyViolation
# from src.Classes.classes_DAO.ligne_DAO import LigneDAO

id_ligne, id_train, tarif_base = 1, 1, 30.0
heure_depart = datetime(2026, 1, 15, 10, 0)
heure_arrivee = datetime(2026, 1, 15, 11, 0)

trajet_test = Trajet(
    id_ligne=id_ligne,
    id_train=id_train,
    heure_depart=heure_depart,
    heure_arrivee=heure_arrivee,
    tarif_base=tarif_base,
)

ligne_test = MagicMock(id_gare_depart=1, id_gare_arrivee=2)


# tests _verifier_donnees

def test_verifier_donnees_ok():
    """Données valides : ne lève rien"""
    # WHEN
    res = TrajetService()._verifier_donnees(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base)

    # THEN
    assert res is None


def test_verifier_donnees_ligne_manquante():
    """id_ligne est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(None, id_train, heure_depart, heure_arrivee, tarif_base)


def test_verifier_donnees_train_manquant():
    """id_train est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(id_ligne, None, heure_depart, heure_arrivee, tarif_base)


def test_verifier_donnees_heures_pas_datetime():
    """Les heures ne sont pas des datetime : TypeError"""
    with pytest.raises(TypeError):
        TrajetService()._verifier_donnees(id_ligne, id_train, "10h", "11h", tarif_base)


def test_verifier_donnees_arrivee_avant_depart():
    """L'arrivée est avant le départ : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(id_ligne, id_train, heure_arrivee, heure_depart, tarif_base)


def test_verifier_donnees_tarif_negatif():
    """Le tarif est négatif : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(id_ligne, id_train, heure_depart, heure_arrivee, -5.0)


def test_verifier_donnees_tarif_manquant():
    """Le tarif est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(id_ligne, id_train, heure_depart, heure_arrivee, None)

# TODO rajouter tests verifier ligne et trajet similaire

# tests creer


def test_creer_ok():
    """Crée un trajet avec succès"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock()
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=False)
    TrajetDAO().creer = MagicMock(return_value=trajet_test)

    # WHEN
    trajet = service.creer(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base)

    # THEN
    assert trajet.id_ligne == id_ligne


def test_creer_fail():
    """Ne parvient pas à créer de trajet car TrajetDAO().creer retourne None"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock()
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=False)
    TrajetDAO().creer = MagicMock(return_value=None)

    # WHEN
    trajet = service.creer(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base)

    # THEN
    assert trajet is None


def test_creer_donnees_invalides():
    """Les données sont invalides : l'erreur est propagée"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock(side_effect=ValueError)

    # WHEN / THEN
    with pytest.raises(ValueError):
        service.creer(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base)

# TODO test creer: ligne inexistante, trajet déjà existant, train inexistant
