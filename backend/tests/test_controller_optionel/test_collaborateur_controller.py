from datetime import datetime
from unittest.mock import MagicMock

import pytest
import requests
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from src.Classes.controller import administrateur_controller, collaborateur_controller
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.schema.collaborateur_schema import TrajetCreationModel, TrajetModificationModel
from src.schema.train_schema import TrainBaseModel
from src.utils.securite import verif_token

# Tests des routes du collaborateur : le service est remplacé par un MagicMock,
# on vérifie seulement que le contrôleur renvoie les bons codes HTTP.

DEPART = datetime(2027, 6, 1, 8, 0)
TRAIN = TrainBaseModel(type_train="TGV", places_premieres=120, places_secondes=280, num_train=8541)
COLLAB = MagicMock(grade="COLLABORATEUR")  # remplace l'utilisateur fourni par verif_token
CLIENT = MagicMock(grade="CLIENT")
RENNES = Gare("Rennes", "Rennes", "stop_area:SNCF:87471003", id_gare=1)
NANTES = Gare("Nantes", "Nantes", "stop_area:SNCF:87481002", id_gare=2)
TRAJET = TrajetModificationModel(id_ligne=1, id_train=1, heure_depart=DEPART, tarif_base=40)


def service_gares():
    """Simule GareService.rechercher : les routes de lignes reçoivent des noms de gares."""
    service = MagicMock()
    service.rechercher.side_effect = lambda nom, ville: {"Rennes": [RENNES], "Nantes": [NANTES]}.get(nom, [])
    return service


# --------------------------------------------------------------- routes existantes

def _chemins(controller, methode):
    return {route.path for route in controller.router.routes if methode in route.methods}


def test_routes_deplacees_chez_le_collaborateur():
    """Les routes des trains et de l'import des gares sont dans le contrôleur collaborateur"""
    assert {"/trains", "/gares/importer"} <= _chemins(collaborateur_controller, "POST")
    assert "/trains/{num_train}" in _chemins(collaborateur_controller, "PUT")


def test_routes_retirees_de_l_administrateur():
    """Ces routes ne sont plus dans le contrôleur administrateur"""
    chemins = {route.path for route in administrateur_controller.router.routes}
    assert not {"/trains", "/trains/{num_train}", "/gares/importer"} & chemins


# --------------------------------------------------------------- lignes et trajets


@pytest.mark.parametrize(
    "appel, methode, resultat",
    [
        (lambda s: collaborateur_controller.modifier_ligne(9, "Rennes", "Nantes", s, service_gares(), COLLAB), "modifier_ligne", None),
        (lambda s: collaborateur_controller.supprimer_ligne(9, s, COLLAB), "supprimer_ligne", False),
        (lambda s: collaborateur_controller.modifier_trajet(9, TRAJET, s, COLLAB), "modifier_trajet", None),
        (lambda s: collaborateur_controller.supprimer_trajet(9, s, COLLAB), "supprimer_trajet", False),
    ],
)
def test_route_introuvable_renvoie_404(appel, methode, resultat):
    """Ligne, trajet ou train introuvable : 404"""
    service = MagicMock()
    getattr(service, methode).return_value = resultat
    with pytest.raises(HTTPException) as erreur:
        appel(service)
    assert erreur.value.status_code == 404


def test_route_supprimer_refus_renvoie_400():
    """Suppression refusée (trajet avec des réservations) : 400"""
    service = MagicMock()
    service.supprimer_trajet.side_effect = ValueError("Impossible de supprimer un trajet qui a des réservations.")
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.supprimer_trajet(1, service, COLLAB)
    assert erreur.value.status_code == 400


def test_route_modifier_trajet_api_indisponible_renvoie_502():
    """API SNCF injoignable pendant la modification d'un trajet : 502"""
    service = MagicMock()
    service.modifier_trajet.side_effect = requests.ConnectionError()
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.modifier_trajet(1, TRAJET, service, COLLAB)
    assert erreur.value.status_code == 502


def test_route_modifier_ligne_transmet_les_id_des_gares():
    """Les noms des gares sont transformés en id avant d'appeler le service"""
    service = MagicMock()

    collaborateur_controller.modifier_ligne(9, "Rennes", "Nantes", service, service_gares(), COLLAB)

    service.modifier_ligne.assert_called_once_with(9, 1, 2)


@pytest.mark.parametrize(
    "appel",
    [
        lambda s: collaborateur_controller.modifier_ligne(9, "Rennes", "Nantes", s, service_gares(), CLIENT),
        lambda s: collaborateur_controller.supprimer_ligne(9, s, CLIENT),
        lambda s: collaborateur_controller.modifier_trajet(9, TRAJET, s, CLIENT),
        lambda s: collaborateur_controller.supprimer_trajet(9, s, CLIENT),
    ],
)
def test_route_refusee_sans_le_grade_collaborateur(appel):
    """Compte client : 403, et le service n'est jamais appelé"""
    service = MagicMock()
    with pytest.raises(HTTPException) as erreur:
        appel(service)
    assert erreur.value.status_code == 403
    assert service.mock_calls == []


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
    """Texte de recherche trop court : 400"""
    service = MagicMock()
    service.importer_gares.side_effect = ValueError("trop court")
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.importer_gares("a", service, COLLAB)
    assert erreur.value.status_code == 400


def test_route_importer_gares_api_indisponible():
    """API SNCF injoignable pendant l'import des gares : 502"""
    service = MagicMock()
    service.importer_gares.side_effect = requests.ConnectionError()
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.importer_gares("Rennes", service, COLLAB)
    assert erreur.value.status_code == 502


def test_route_creer_train_numero_existant():
    """Numéro de train déjà utilisé : 400"""
    service = MagicMock()
    service.creer_train.side_effect = ValueError("existe déjà")
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.creer_train(TRAIN, service, COLLAB)
    assert erreur.value.status_code == 400


def test_route_modifier_capacite_ok():
    """Nouvelle capacité transmise au service, le train modifié est renvoyé"""
    service = MagicMock()
    service.modifier_capacite.return_value = "le train"
    assert collaborateur_controller.modifier_capacite(8541, TRAIN, service, COLLAB) == "le train"
    service.modifier_capacite.assert_called_once_with(8541, 120, 280)


def test_route_modifier_capacite_invalide():
    """Capacité refusée par le service : 400"""
    service = MagicMock()
    service.modifier_capacite.side_effect = ValueError("capacité incorrecte")
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.modifier_capacite(8541, TRAIN, service, COLLAB)
    assert erreur.value.status_code == 400


def test_route_modifier_capacite_train_inexistant():
    """Le service renvoie None quand le train n'existe pas : le contrôleur répond 404"""
    service = MagicMock()
    service.modifier_capacite.return_value = None
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.modifier_capacite(8541, TRAIN, service, COLLAB)
    assert erreur.value.status_code == 404


@pytest.mark.parametrize(
    "appel",
    [
        lambda service: collaborateur_controller.importer_gares("Rennes", service, CLIENT),
        lambda service: collaborateur_controller.creer_train(TRAIN, service, CLIENT),
        lambda service: collaborateur_controller.modifier_capacite(8541, TRAIN, service, CLIENT),
    ],
)
def test_routes_refusees_sans_le_grade_collaborateur(appel):
    """Toutes les routes collaborateur répondent 403 à un client, sans appeler le service"""
    service = MagicMock()
    with pytest.raises(HTTPException) as erreur:
        appel(service)
    assert erreur.value.status_code == 403
    assert service.mock_calls == []


# --------------------------------------------------------------- listes


LIGNE = Ligne(RENNES, NANTES, id_ligne=3)
TER = Train("TER", 20, 80, 857, id_train=4)


@pytest.fixture
def http():
    """Renvoie une fonction qui crée un TestClient connecté avec l'utilisateur donné (None : pas connecté)"""
    service = MagicMock()

    def _http(utilisateur):
        app = FastAPI()
        app.include_router(collaborateur_controller.router)
        app.dependency_overrides[collaborateur_controller.get_collaborateur_service] = lambda: service
        if utilisateur is not None:
            app.dependency_overrides[verif_token] = lambda: utilisateur
        return TestClient(app), service

    return _http


def test_lister_lignes(http):
    """Les lignes sont renvoyées avec leurs deux gares"""
    client, service = http(COLLAB)
    service.lister_lignes.return_value = [LIGNE]

    reponse = client.get("/lignes")

    assert reponse.status_code == 200
    assert reponse.json()[0]["id_ligne"] == 3
    assert reponse.json()[0]["gare_depart"]["nom"] == "Rennes"
    assert reponse.json()[0]["gare_arrivee"]["nom"] == "Nantes"


def test_lister_trains(http):
    """Les trains sont renvoyés avec leur id"""
    client, service = http(COLLAB)
    service.lister_trains.return_value = [TER]

    reponse = client.get("/trains")

    assert reponse.status_code == 200
    assert reponse.json() == [
        {"type_train": "TER", "places_premieres": 20, "places_secondes": 80, "num_train": 857, "id_train": 4}
    ]


def test_lister_trajets(http):
    """Les trajets sont renvoyés avec leur ligne, même sans train"""
    client, service = http(COLLAB)
    service.lister_trajets.return_value = [
        Trajet(DEPART, DEPART, LIGNE, TER, 20.0, id_trajet=7),
        Trajet(DEPART, DEPART, LIGNE, None, 20.0, id_trajet=8),
    ]

    reponse = client.get("/trajets")

    assert reponse.status_code == 200
    assert [trajet["id_trajet"] for trajet in reponse.json()] == [7, 8]
    assert reponse.json()[0]["ligne"]["id_ligne"] == 3
    assert [trajet["num_train"] for trajet in reponse.json()] == [857, None]


@pytest.mark.parametrize("chemin", ["/lignes", "/trains", "/trajets"])
def test_lister_vide(http, chemin):
    """Rien en base : liste vide"""
    client, service = http(COLLAB)
    getattr(service, f"lister_{chemin[1:]}").return_value = []

    reponse = client.get(chemin)

    assert reponse.status_code == 200
    assert reponse.json() == []


@pytest.mark.parametrize("chemin", ["/lignes", "/trains", "/trajets"])
def test_lister_refuse_pour_un_client(http, chemin):
    """Compte client : 403, et le service n'est jamais appelé"""
    client, service = http(CLIENT)

    assert client.get(chemin).status_code == 403
    assert service.mock_calls == []


@pytest.mark.parametrize("chemin", ["/lignes", "/trains", "/trajets"])
def test_lister_sans_token(http, chemin):
    """Pas de token : 401"""
    client, service = http(None)

    assert client.get(chemin).status_code == 401
    assert service.mock_calls == []
