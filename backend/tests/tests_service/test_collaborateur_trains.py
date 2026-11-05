from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import HTTPException
from src.Classes.classes_objets.train import Train
from src.Classes.classes_service.utilisateurs_service.collaborateur_service import CollaborateurService
from src.Classes.controller import administrateur_controller, collaborateur_controller
from src.schema.train_schema import TrainBaseModel

# La base et l'API SNCF sont simulées : aucun appel réel n'est fait.

SERVICE = "src.Classes.classes_service.utilisateurs_service.collaborateur_service"
TRAIN = TrainBaseModel(type_train="TGV", places_premieres=120, places_secondes=280, num_train=8541)
COLLAB = MagicMock(grade="COLLABORATEUR")  # remplace l'utilisateur fourni par verif_token
CLIENT = MagicMock(grade="CLIENT")


def _chemins(controller, methode):
    return {route.path for route in controller.router.routes if methode in route.methods}


def test_routes_deplacees_chez_le_collaborateur():
    assert {"/trains", "/gares/importer"} <= _chemins(collaborateur_controller, "POST")
    assert "/trains/{num_train}" in _chemins(collaborateur_controller, "PUT")


def test_routes_retirees_de_l_administrateur():
    chemins = {route.path for route in administrateur_controller.router.routes}
    assert not {"/trains", "/trains/{num_train}", "/gares/importer"} & chemins


# ------------------------------------------------------------------ service


def test_service_importer_gares():
    with patch(f"{SERVICE}.GareService") as gare_service:
        gare_service.return_value.importer.return_value = ["Rennes"]
        assert CollaborateurService().importer_gares("Rennes") == ["Rennes"]
    gare_service.return_value.importer.assert_called_once_with("Rennes")


def test_service_creer_train():
    with patch(f"{SERVICE}.TrainService") as train_service:
        CollaborateurService().creer_train("TGV", 100, 300, 8541)
    train_service.return_value.creer.assert_called_once_with("TGV", 100, 300, 8541)


def test_service_modifier_capacite_renvoie_le_train_modifie():
    with patch(f"{SERVICE}.TrainService") as train_service:
        train_service.return_value.trouver_train_par_num.return_value = Train("TGV", 100, 300, 8541, id_train=1)
        train_service.return_value.modifier_capacite.return_value = True

        train = CollaborateurService().modifier_capacite(8541, 120, 280)

    train_service.return_value.modifier_capacite.assert_called_once_with(8541, 120, 280)
    assert (train.places_premieres, train.places_secondes, train.id_train) == (120, 280, 1)


def test_service_modifier_capacite_non_executee():
    with patch(f"{SERVICE}.TrainService") as train_service:
        train_service.return_value.modifier_capacite.return_value = False
        assert CollaborateurService().modifier_capacite(8541, 120, 280) is None


# --------------------------------------------------------------- controller


def test_route_importer_gares_texte_trop_court():
    service = MagicMock()
    service.importer_gares.side_effect = ValueError("trop court")
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.importer_gares("a", service, COLLAB)
    assert erreur.value.status_code == 400


def test_route_importer_gares_api_indisponible():
    service = MagicMock()
    service.importer_gares.side_effect = requests.ConnectionError()
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.importer_gares("Rennes", service, COLLAB)
    assert erreur.value.status_code == 502


def test_route_creer_train_numero_existant():
    service = MagicMock()
    service.creer_train.side_effect = ValueError("existe déjà")
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.creer_train(TRAIN, service, COLLAB)
    assert erreur.value.status_code == 400


def test_route_modifier_capacite_ok():
    service = MagicMock()
    service.modifier_capacite.return_value = "le train"
    assert collaborateur_controller.modifier_capacite(8541, TRAIN, service, COLLAB) == "le train"
    service.modifier_capacite.assert_called_once_with(8541, 120, 280)


def test_route_modifier_capacite_invalide():
    service = MagicMock()
    service.modifier_capacite.side_effect = ValueError("capacité incorrecte")
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.modifier_capacite(8541, TRAIN, service, COLLAB)
    assert erreur.value.status_code == 400


def test_route_modifier_capacite_non_executee():
    service = MagicMock()
    service.modifier_capacite.return_value = None
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.modifier_capacite(8541, TRAIN, service, COLLAB)
    assert erreur.value.status_code == 500


@pytest.mark.parametrize(
    "appel",
    [
        lambda service: collaborateur_controller.importer_gares("Rennes", service, CLIENT),
        lambda service: collaborateur_controller.creer_train(TRAIN, service, CLIENT),
        lambda service: collaborateur_controller.modifier_capacite(8541, TRAIN, service, CLIENT),
    ],
)
def test_routes_refusees_sans_le_grade_collaborateur(appel):
    service = MagicMock()
    with pytest.raises(HTTPException) as erreur:
        appel(service)
    assert erreur.value.status_code == 401
    assert service.mock_calls == []
