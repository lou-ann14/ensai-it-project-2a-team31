from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_service.trajet_service import TrajetService

tarif_base = 30.0
heure_depart = datetime(2026, 1, 15, 10, 0)
heure_arrivee = datetime(2026, 1, 15, 11, 0)

ligne_test = Ligne(1, Gare(1, "Montparnasse", "Paris"), Gare(2, "Rennes", "Rennes"))
train_test = Train(1, "TGV", [300, 500])

trajet_test = Trajet(
    id_trajet=None,
    heure_depart=heure_depart,
    heure_arrivee=heure_arrivee,
    ligne=ligne_test,
    train=train_test,
    tarif_base=tarif_base,
)


# tests _verifier_donnees


def test_verifier_donnees_ok():
    """Données valides : ne lève rien"""
    # WHEN
    res = TrajetService()._verifier_donnees(ligne_test, train_test, heure_depart, heure_arrivee, tarif_base)

    # THEN
    assert res is None


def test_verifier_donnees_ligne_manquante():
    """ligne est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(None, train_test, heure_depart, heure_arrivee, tarif_base)


def test_verifier_donnees_train_manquant():
    """train est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(ligne_test, None, heure_depart, heure_arrivee, tarif_base)


def test_verifier_donnees_heures_pas_datetime():
    """Les heures ne sont pas des datetime : TypeError"""
    with pytest.raises(TypeError):
        TrajetService()._verifier_donnees(ligne_test, train_test, "10h", "11h", tarif_base)


def test_verifier_donnees_arrivee_avant_depart():
    """L'arrivée est avant le départ : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(ligne_test, train_test, heure_arrivee, heure_depart, tarif_base)


def test_verifier_donnees_tarif_negatif():
    """Le tarif est négatif : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(ligne_test, train_test, heure_depart, heure_arrivee, -5.0)


def test_verifier_donnees_tarif_manquant():
    """Le tarif est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(ligne_test, train_test, heure_depart, heure_arrivee, None)


# TODO rajouter tests verifier ligne et trajet similaire

# tests creer


def test_creer_ok():
    """Crée un trajet avec succès"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock()
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=False)

    # WHEN
    with patch.object(TrajetDAO, "creer", return_value=trajet_test):
        trajet = service.creer(ligne_test, train_test, heure_depart, heure_arrivee, tarif_base)

    # THEN
    assert trajet.ligne.id_ligne == ligne_test.id_ligne
    assert trajet.train.id_train == train_test.id_train


def test_creer_fail():
    """Ne parvient pas à créer de trajet car TrajetDAO().creer retourne None"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock()
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=False)

    # WHEN
    with patch.object(TrajetDAO, "creer", return_value=None):
        trajet = service.creer(ligne_test, train_test, heure_depart, heure_arrivee, tarif_base)

    # THEN
    assert trajet is None


def test_creer_donnees_invalides():
    """Les données sont invalides : l'erreur est propagée"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock(side_effect=ValueError)

    # WHEN / THEN
    with pytest.raises(ValueError):
        service.creer(ligne_test, train_test, heure_depart, heure_arrivee, tarif_base)


# TODO test creer: ligne inexistante, trajet déjà existant, train inexistant