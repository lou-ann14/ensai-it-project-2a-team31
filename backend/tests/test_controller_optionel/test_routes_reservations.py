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


def test_trouver_client_collaborateur_autorise():
    """Hiérarchie des grades : un collaborateur a aussi les droits d'un client"""
    assert controller.trouver_client(COLLABORATEUR) is COLLABORATEUR


def test_trouver_client_grade_inconnu():
    with pytest.raises(controller.HTTPException) as erreur:
        controller.trouver_client(Utilisateur("x", "pirate", "INCONNU", id=9))
    assert erreur.value.status_code == 403


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


@pytest.mark.parametrize("grade, id_utilisateur", [("COLLABORATEUR", 2), ("ADMIN", 5)])
def test_reserver_avec_un_grade_superieur(connecte, grade, id_utilisateur):
    """Un collaborateur ou un administrateur peut réserver, en son propre nom"""
    http, services = connecte(Utilisateur("x", "u", grade, token_acces="jeton", id=id_utilisateur))
    services["reservation"].creer.side_effect = ValueError("stop")  # on s'arrête après l'appel

    http.post("/utilisateur/reservations", json={"id_trajet": 10, "place": "12", "classe": 2})

    assert services["reservation"].creer.call_args.args[0].id == id_utilisateur


# Tests GET /reservations


def test_historique_du_client_connecte(connecte):
    """L'historique est celui du client du token, même si un autre id_client est passé"""
    http, services = connecte(CLIENT)
    services["reservation"].historique_par_client.return_value = []

    reponse = http.get("/utilisateur/reservations", params={"id_client": 999})

    assert reponse.status_code == 200
    assert reponse.json() == []
    services["reservation"].historique_par_client.assert_called_once_with(1)


def test_historique_collaborateur(connecte):
    """Un collaborateur consulte ses propres réservations"""
    http, services = connecte(COLLABORATEUR)
    services["reservation"].historique_par_client.return_value = []

    reponse = http.get("/utilisateur/reservations")

    assert reponse.status_code == 200
    services["reservation"].historique_par_client.assert_called_once_with(2)


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


# Tests GET /trains/{num_train} (le 404 est décidé par le contrôleur, plus par le service)


def test_trouver_train_inexistant(connecte):
    http, _ = connecte(CLIENT)
    with patch("src.Classes.controller.utilisateur_controller.TrainService") as train_service:
        train_service.return_value.trouver_train_par_num.return_value = None
        reponse = http.get("/utilisateur/trains/9999")

    assert reponse.status_code == 404
    assert "9999" in reponse.json()["detail"]



# Tests GET /trajets/{id}/places et réservation sans numéro de place


def test_places_libres_route(connecte):
    from src.Classes.classes_objets.gare import Gare
    from src.Classes.classes_objets.ligne import Ligne
    from src.Classes.classes_objets.train import Train
    from src.Classes.classes_objets.trajet import Trajet

    http, services = connecte(CLIENT)
    depart = datetime.now() + timedelta(days=2)
    ligne = Ligne(Gare("A", "A", "s:1", 1), Gare("B", "B", "s:2", 2), id_ligne=1)
    trajet = Trajet(depart, depart + timedelta(hours=1), ligne, Train("TER", 2, 3, 857, id_train=1), 20.0, id_trajet=10)
    services["trajet"].trouver_par_id.return_value = trajet
    services["trajet"].places_libres.return_value = {1: [2], 2: [1, 3]}

    reponse = http.get("/utilisateur/trajets/10/places")

    assert reponse.status_code == 200
    assert reponse.json() == {
        "id_trajet": 10, "capacite_premiere": 2, "capacite_seconde": 3,
        "libres_premiere": [2], "libres_seconde": [1, 3],
    }


def test_places_libres_trajet_inexistant(connecte):
    http, services = connecte(CLIENT)
    services["trajet"].trouver_par_id.return_value = None

    assert http.get("/utilisateur/trajets/99/places").status_code == 404


def test_places_libres_trajet_sans_train(connecte):
    http, services = connecte(CLIENT)
    services["trajet"].places_libres.side_effect = ValueError("Aucun train n'est associé à ce trajet.")

    assert http.get("/utilisateur/trajets/10/places").status_code == 400


def test_places_libres_sans_token():
    app = FastAPI()
    app.include_router(controller.router, prefix="/utilisateur")

    assert TestClient(app).get("/utilisateur/trajets/10/places").status_code == 401


def test_reserver_sans_numero_de_place(connecte):
    """La place est optionnelle : sans elle, None est transmis au service (attribution automatique)"""
    http, services = connecte(CLIENT)
    services["reservation"].creer.side_effect = ValueError("stop")

    reponse = http.post("/utilisateur/reservations", json={"id_trajet": 10, "classe": 2})

    assert reponse.status_code == 400  # « stop » : le service a bien été appelé
    assert services["reservation"].creer.call_args.args[2] is None
