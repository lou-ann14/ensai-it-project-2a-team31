from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import HTTPException
from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_service.trajet_service import TrajetService
from src.Classes.controller.collaborateur_controller import creer_trajet
from src.schema.collaborateur_schema import TrajetCreationModel

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
    trajet = Trajet(DEPART, DEPART, faire_ligne(), Train("TGV", [100, 300], 8541, id_train=1), 40.0)

    assert TrajetService().modifier(1, trajet) is True

    assert trajet.heure_arrivee == datetime(2027, 6, 1, 9, 0)
    assert trajet.temps_trajet == 60
    assert trajet.id_trajet == 1


@patch("src.Classes.classes_DAO.trajet_DAO.DBConnexion")
def test_dao_enregistre_temps_trajet(mock_db):
    """Le DAO envoie bien le temps de trajet à la base"""
    cursor = mock_db().connexion.__enter__().cursor().__enter__()
    cursor.fetchone.return_value = {"id_trajet": 1}
    trajet = Trajet(
        DEPART, datetime(2027, 6, 1, 9, 21), faire_ligne(), Train("TGV", [100, 300], 8541, id_train=1), 40.0, temps_trajet=81
    )

    TrajetDAO().creer(trajet)

    requete, parametres = cursor.execute.call_args.args
    assert "temps_trajet" in requete
    assert parametres["temps_trajet"] == 81


def test_route_api_indisponible_renvoie_502():
    """Si l'API SNCF est en panne, la route répond 502"""
    service = MagicMock()
    service.creer_trajet.side_effect = requests.ConnectionError()
    donnees = TrajetCreationModel(id_ligne=1, id_train=1, heure_depart=DEPART, tarif_base=40.0)

    with pytest.raises(HTTPException) as erreur:
        creer_trajet(donnees, service)

    assert erreur.value.status_code == 502
