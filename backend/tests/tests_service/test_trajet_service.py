from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_service.trajet_service import TrajetService, train_depuis_id

# Données communes aux tests

ligne_test = Ligne(
    gare_depart=Gare("Rennes", "Rennes", "stop_area:SNCF:87471003", id_gare=1),
    gare_arrivee=Gare("Nantes", "Nantes", "stop_area:SNCF:87481002", id_gare=2),
    id_ligne=1,
)

train_test = Train(
    type_train="TGV",
    places_premieres=100,
    places_secondes=200,
    num_train=8541,
    id_train=1,
)

heure_depart = datetime(2026, 1, 15, 10, 0)
heure_arrivee = datetime(2026, 1, 15, 11, 0)
tarif_base = 30.0

trajet_test = Trajet(
    id_trajet=10,
    ligne=ligne_test,
    train=train_test,
    heure_depart=heure_depart,
    heure_arrivee=heure_arrivee,
    tarif_base=tarif_base,
)

# tests _verifier_donnees


def test_verifier_donnees_ok():
    """Données valides : ne lève rien"""
    # WHEN
    res = TrajetService()._verifier_donnees(
        ligne_test.id_ligne,
        train_test.id_train,
        heure_depart,
        heure_arrivee,
        tarif_base
        )

    # THEN
    assert res is None


def test_verifier_donnees_ligne_manquante():
    """id_ligne est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(
            None,
            train_test.id_train,
            heure_depart,
            heure_arrivee,
            tarif_base
            )


def test_verifier_donnees_train_manquant():
    """id_train est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(
            ligne_test.id_ligne,
            None,
            heure_depart,
            heure_arrivee,
            tarif_base
            )


def test_verifier_donnees_heures_pas_datetime():
    """Les heures ne sont pas des datetime : TypeError"""
    with pytest.raises(TypeError):
        TrajetService()._verifier_donnees(
            ligne_test.id_ligne,
            train_test.id_train,
            "10h",
            "11h",
            tarif_base
            )


def test_verifier_donnees_arrivee_avant_depart():
    """L'arrivée est avant le départ : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(
            ligne_test.id_ligne,
            train_test.id_train,
            heure_arrivee,
            heure_depart,
            tarif_base
            )


def test_verifier_donnees_tarif_negatif():
    """Le tarif est négatif : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(
            ligne_test.id_ligne,
            train_test.id_train,
            heure_depart,
            heure_arrivee,
            -5.0
            )


def test_verifier_donnees_tarif_manquant():
    """Le tarif est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(
            ligne_test.id_ligne,
            train_test.id_train,
            heure_depart,
            heure_arrivee,
            None
            )

# TODO rajouter tests verifier ligne et trajet similaire

# tests creer


def test_creer_ok():
    """Crée un trajet avec succès"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock()
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=False)
    service.trajet_dao.creer = MagicMock(return_value=trajet_test)

    # WHEN
    trajet = service.creer(
        ligne_test,
        train_test,
        heure_depart,
        heure_arrivee,
        tarif_base
        )

    # THEN
    assert trajet.id_ligne == ligne_test.id_ligne


def test_creer_fail():
    """Ne parvient pas à créer de trajet car TrajetDAO().creer retourne None"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock()
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=False)
    service.trajet_dao.creer = MagicMock(return_value=None)

    # WHEN
    trajet = service.creer(
        ligne_test,
        train_test,
        heure_depart,
        heure_arrivee,
        tarif_base
        )

    # THEN
    assert trajet is None


def test_creer_donnees_invalides():
    """Les données sont invalides : l'erreur est propagée"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock(side_effect=ValueError)

    # WHEN / THEN
    with pytest.raises(ValueError):
        service.creer(
            ligne_test,
            train_test,
            heure_depart,
            heure_arrivee,
            tarif_base
            )

# TODO test creer: ligne inexistante, trajet déjà existant, train inexistant


# tests du calcul du temps de trajet avec l'API SNCF (anciennement test_trajet_temps.py)
# L'API SNCF et la base sont simulées : aucun appel réel n'est fait.

DEPART = datetime(2027, 6, 1, 8, 0)
ID_RENNES = "stop_area:SNCF:87471003"
ID_NANTES = "stop_area:SNCF:87481002"


def faire_ligne(id_sncf_depart=ID_RENNES, id_sncf_arrivee=ID_NANTES):
    return Ligne(
        Gare("Rennes", "Rennes", id_sncf_depart, id_gare=1),
        Gare("Nantes", "Nantes", id_sncf_arrivee, id_gare=2),
        id_ligne=1,
    )


@pytest.fixture
def mocks():
    """Remplace la base et l'API SNCF, pour une ligne valide et sans trajet existant"""
    with (
        patch("src.Classes.classes_service.trajet_service.TrajetDAO") as trajet_dao,
        patch("src.Classes.classes_service.trajet_service.LigneDAO") as ligne_dao,
        patch("src.Classes.classes_service.trajet_service.SncfClient") as sncf,
    ):
        ligne_dao.return_value.trouver_par_id.return_value = faire_ligne()
        trajet_dao.return_value.rechercher.return_value = []
        trajet_dao.return_value.creer.side_effect = lambda trajet: trajet
        yield MagicMock(dao=trajet_dao.return_value, ligne=ligne_dao.return_value, api=sncf.return_value)


def test_creer_calcule_arrivee_et_temps(mocks):
    """1 h 21 d'après l'API : l'arrivée et le temps de trajet sont renseignés"""
    mocks.api.duree_trajet.return_value = 4860

    trajet = TrajetService().creer(1, 1, DEPART, 40.0)

    assert trajet.heure_arrivee == datetime(2027, 6, 1, 9, 21)
    assert trajet.temps_trajet == 81
    mocks.api.duree_trajet.assert_called_once_with(ID_RENNES, ID_NANTES, DEPART)
    mocks.dao.creer.assert_called_once()


def test_creer_date_trop_lointaine_utilise_les_horaires_actuels(mocks):
    """L'API ne connaît pas la date demandée : on redemande la durée sans date"""
    mocks.api.duree_trajet.side_effect = [None, 4620]

    trajet = TrajetService().creer(1, 1, DEPART, 40.0)

    assert trajet.temps_trajet == 77
    assert mocks.api.duree_trajet.call_args_list[1].args == (ID_RENNES, ID_NANTES)


def test_creer_aucun_itineraire(mocks):
    """L'API ne trouve rien, même sans date : le trajet n'est pas créé"""
    mocks.api.duree_trajet.return_value = None

    with pytest.raises(ValueError, match="aucun itinéraire"):
        TrajetService().creer(1, 1, DEPART, 40.0)

    mocks.dao.creer.assert_not_called()


def test_creer_gare_sans_id_sncf(mocks):
    """Une gare qui ne vient pas de l'API : on ne peut pas calculer le temps de trajet"""
    mocks.ligne.trouver_par_id.return_value = faire_ligne(id_sncf_depart=None)

    with pytest.raises(ValueError, match="API SNCF"):
        TrajetService().creer(1, 1, DEPART, 40.0)

    mocks.api.duree_trajet.assert_not_called()
    mocks.dao.creer.assert_not_called()


def test_creer_api_indisponible(mocks):
    """Une panne de l'API remonte, et le trajet n'est pas créé"""
    mocks.api.duree_trajet.side_effect = requests.ConnectionError()

    with pytest.raises(requests.RequestException):
        TrajetService().creer(1, 1, DEPART, 40.0)

    mocks.dao.creer.assert_not_called()


def test_creer_donnee_invalide_sans_appeler_api(mocks):
    """Un tarif négatif est refusé sans consommer de requête API"""
    with pytest.raises(ValueError, match="tarif"):
        TrajetService().creer(1, 1, DEPART, -1)

    mocks.api.duree_trajet.assert_not_called()


def test_creer_doublon_sans_appeler_api(mocks):
    """Un trajet déjà existant à cette heure est refusé sans consommer de requête API"""
    mocks.dao.rechercher.return_value = [MagicMock(heure_depart=DEPART, id_trajet=5)]

    with pytest.raises(ValueError, match="existe déjà"):
        TrajetService().creer(1, 1, DEPART, 40.0)

    mocks.api.duree_trajet.assert_not_called()


def test_modifier_recalcule_arrivee_et_temps(mocks):
    """Modifier l'heure de départ met à jour l'arrivée et le temps de trajet"""
    mocks.dao.trouver_par_id.return_value = MagicMock()
    mocks.dao.modifier.return_value = True
    mocks.api.duree_trajet.return_value = 3600
    trajet = Trajet(DEPART, DEPART, faire_ligne(), Train("TGV", 100, 300, 8541, id_train=1), 40.0)

    assert TrajetService().modifier(1, trajet) is True

    assert trajet.heure_arrivee == datetime(2027, 6, 1, 9, 0)
    assert trajet.temps_trajet == 60
    assert trajet.id_trajet == 1


# tests train_depuis_id et creer (anciennement test_gare_et_train_trajet.py)

SERVICE_TRAJET = "src.Classes.classes_service.trajet_service"
DEPART_RENNES_NANTES = datetime(2026, 11, 18, 8, 35)
LIGNE_RENNES_NANTES = Ligne(
    Gare("Rennes", "Rennes", "stop_area:SNCF:87471003", 1),
    Gare("Nantes", "Nantes", "stop_area:SNCF:87481002", 5),
    id_ligne=1,
)


@pytest.fixture
def service_trajet():
    with patch(f"{SERVICE_TRAJET}.TrajetDAO") as trajet_dao, patch(f"{SERVICE_TRAJET}.LigneDAO") as ligne_dao, patch(
        f"{SERVICE_TRAJET}.SncfClient"
    ) as sncf:
        ligne_dao.return_value.trouver_par_id.return_value = LIGNE_RENNES_NANTES
        trajet_dao.return_value.rechercher.return_value = []
        trajet_dao.return_value.creer.side_effect = lambda trajet: trajet
        sncf.return_value.duree_trajet.return_value = 4620
        yield TrajetService()


def test_train_depuis_id():
    assert train_depuis_id(3).id_train == 3


@pytest.mark.parametrize("tarif", [40, 40.0])
def test_creer_trajet_garde_l_id_du_train(service_trajet, tarif):
    """Un tarif entier est accepté : Trajet exige un float."""
    trajet = service_trajet.creer(1, 3, DEPART_RENNES_NANTES, tarif)

    assert trajet.train.id_train == 3
    assert trajet.tarif_base == 40.0
    assert trajet.temps_trajet == 77
