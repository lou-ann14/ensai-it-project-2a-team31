from datetime import datetime
from unittest.mock import MagicMock

import pytest
import requests
from fastapi import HTTPException
from src.Classes.controller import administrateur_controller, collaborateur_controller
from src.schema.collaborateur_schema import LigneModificationModel, TrajetCreationModel, TrajetModificationModel
from src.schema.train_schema import TrainBaseModel

# Tests des routes du collaborateur : le service est remplacé par un MagicMock,
# on vérifie seulement que le contrôleur renvoie les bons codes HTTP.

DEPART = datetime(2027, 6, 1, 8, 0)
TRAIN = TrainBaseModel(type_train="TGV", places_premieres=120, places_secondes=280, num_train=8541)
COLLAB = MagicMock(grade="COLLABORATEUR")  # remplace l'utilisateur fourni par verif_token
CLIENT = MagicMock(grade="CLIENT")


# --------------------------------------------------------------- routes existantes

def _chemins(controller, methode):
    return {route.path for route in controller.router.routes if methode in route.methods}


def test_routes_deplacees_chez_le_collaborateur():
    assert {"/trains", "/gares/importer"} <= _chemins(collaborateur_controller, "POST")
    assert "/trains/{num_train}" in _chemins(collaborateur_controller, "PUT")


def test_routes_retirees_de_l_administrateur():
    chemins = {route.path for route in administrateur_controller.router.routes}
    assert not {"/trains", "/trains/{num_train}", "/gares/importer"} & chemins


# --------------------------------------------------------------- lignes et trajets


@pytest.mark.parametrize(
    "appel, methode, resultat",
    [
        (lambda s: collaborateur_controller.modifier_ligne(9, LigneModificationModel(gare_depart_id=1, gare_arrivee_id=2), s), "modifier_ligne", None),
        (lambda s: collaborateur_controller.supprimer_ligne(9, s), "supprimer_ligne", False),
        (
            lambda s: collaborateur_controller.modifier_trajet(9, TrajetModificationModel(id_ligne=1, id_train=1, heure_depart=DEPART, tarif_base=40), s),
            "modifier_trajet",
            None,
        ),
        (lambda s: collaborateur_controller.supprimer_trajet(9, s), "supprimer_trajet", False),
    ],
)
def test_route_introuvable_renvoie_404(appel, methode, resultat):
    service = MagicMock()
    getattr(service, methode).return_value = resultat
    with pytest.raises(HTTPException) as erreur:
        appel(service)
    assert erreur.value.status_code == 404


def test_route_supprimer_refus_renvoie_400():
    service = MagicMock()
    service.supprimer_trajet.side_effect = ValueError("Impossible de supprimer un trajet qui a des réservations.")
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.supprimer_trajet(1, service)
    assert erreur.value.status_code == 400


def test_route_modifier_trajet_api_indisponible_renvoie_502():
    service = MagicMock()
    service.modifier_trajet.side_effect = requests.ConnectionError()
    donnees = TrajetModificationModel(id_ligne=1, id_train=1, heure_depart=DEPART, tarif_base=40)
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.modifier_trajet(1, donnees, service)
    assert erreur.value.status_code == 502


def test_route_creer_trajet_api_indisponible_renvoie_502():
    """Si l'API SNCF est en panne, la route répond 502"""
    service = MagicMock()
    service.creer_trajet.side_effect = requests.ConnectionError()
    donnees = TrajetCreationModel(id_ligne=1, id_train=1, heure_depart=DEPART, tarif_base=40.0)

    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.creer_trajet(donnees, service, COLLAB)

    assert erreur.value.status_code == 502


# --------------------------------------------------------------- gares et trains


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
