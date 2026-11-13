from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.Classes.controller import utilisateur_controller as controller
from src.utils.securite import verif_token

# Les routes sont appelées en HTTP (TestClient) : on vérifie ainsi que le client
# est bien celui du token (dépendance trouver_client), et non un id envoyé dans la requête.
# verif_token et les services sont simulés : ni la base ni l'API SNCF ne sont appelées.

CLIENT = Utilisateur("x", "client", "CLIENT", token_acces="jeton", id=1)
COLLABORATEUR = Utilisateur("x", "collab", "COLLABORATEUR", token_acces="jeton", id=2)
RESERVATION_SERVICE = "src.Classes.classes_service.reservations_service.ReservationDAO"


@pytest.fixture
def connecte():
    """Renvoie une fonction qui crée un TestClient connecté avec l'utilisateur donné."""
    services = {"reservation": MagicMock(), "trajet": MagicMock()}

    def _client(utilisateur):
        app = FastAPI()
        app.include_router(controller.router, prefix="/utilisateur")
        app.dependency_overrides[verif_token] = lambda: utilisateur
        app.dependency_overrides[controller.get_reservation_service] = lambda: services["reservation"]
        app.dependency_overrides[controller.get_trajet_service] = lambda: services["trajet"]
        return TestClient(app), services

    return _client


# Tests trouver_client


def test_trouver_client_ok():
    client = controller.trouver_client(CLIENT)
    assert client.id == 1
    assert client.grade == "CLIENT"


def test_trouver_client_compte_non_client():
    with pytest.raises(controller.HTTPException) as erreur:
        controller.trouver_client(COLLABORATEUR)
    assert erreur.value.status_code == 400


# Tests POST /reservations


def test_reserver_utilise_le_client_du_token(connecte):
    """Même si la requête contient un autre id_client, c'est le client du token qui réserve"""
    http, services = connecte(CLIENT)
    services["reservation"].creer.side_effect = ValueError("stop")  # on s'arrête après l'appel

    reponse = http.post(
        "/utilisateur/reservations",
        json={"id_client": 999, "id_trajet": 10, "place": "12A", "classe": 2},
    )

    assert reponse.status_code == 400
    client_utilise = services["reservation"].creer.call_args.args[0]
    assert client_utilise.id == 1


def test_reserver_trajet_inexistant(connecte):
    http, services = connecte(CLIENT)
    services["trajet"].trouver_par_id.return_value = None

    reponse = http.post("/utilisateur/reservations", json={"id_trajet": 10, "place": "12A", "classe": 2})

    assert reponse.status_code == 404
    services["reservation"].creer.assert_not_called()


def test_reserver_compte_non_client(connecte):
    http, services = connecte(COLLABORATEUR)

    reponse = http.post("/utilisateur/reservations", json={"id_trajet": 10, "place": "12A", "classe": 2})

    assert reponse.status_code == 400
    services["reservation"].creer.assert_not_called()


# Tests GET /reservations


def test_historique_du_client_connecte(connecte):
    """L'historique est celui du client du token, même si un autre id_client est passé"""
    http, services = connecte(CLIENT)
    services["reservation"].historique_par_client.return_value = []

    reponse = http.get("/utilisateur/reservations", params={"id_client": 999})

    assert reponse.status_code == 200
    assert reponse.json() == []
    services["reservation"].historique_par_client.assert_called_once_with(1)


def test_historique_compte_non_client(connecte):
    http, services = connecte(COLLABORATEUR)

    reponse = http.get("/utilisateur/reservations")

    assert reponse.status_code == 400
    services["reservation"].historique_par_client.assert_not_called()


# Tests DELETE /reservations/{id}


def test_annuler_ok(connecte):
    http, services = connecte(CLIENT)
    services["reservation"].annuler.return_value = True

    reponse = http.delete("/utilisateur/reservations/7")

    assert reponse.status_code == 200
    assert reponse.json() == {"message": "Annulation de la réservation réussie"}
    services["reservation"].annuler.assert_called_once_with(7, 1)


def test_annuler_reservation_inexistante(connecte):
    http, services = connecte(CLIENT)
    services["reservation"].annuler.return_value = False

    reponse = http.delete("/utilisateur/reservations/99")

    assert reponse.status_code == 404


def test_annuler_reservation_d_un_autre_client(connecte):
    """Bout en bout jusqu'au vrai ReservationService : seul le DAO est simulé"""
    http, services = connecte(CLIENT)
    from src.Classes.classes_service.reservations_service import ReservationService

    services["reservation"] = ReservationService()
    reservation = MagicMock()
    reservation.client.id = 2  # la réservation appartient au client #2
    reservation.trajet.heure_depart = datetime.now() + timedelta(days=3)

    with patch(RESERVATION_SERVICE) as dao:
        dao.return_value.trouver_par_id.return_value = reservation
        reponse = http.delete("/utilisateur/reservations/7")

    assert reponse.status_code == 400
    assert "autre client" in reponse.json()["detail"]
    dao.return_value.annuler.assert_not_called()
