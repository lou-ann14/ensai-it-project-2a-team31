from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.Classes.controller import utilisateur_controller as controller
from src.utils.securite import verif_token

# La route est appelée en HTTP ; verif_token et le service sont simulés (pas de base).

ROUTE = "/utilisateur/mot-de-passe"


@pytest.fixture
def http():
    """Renvoie (client HTTP, faux service) pour l'utilisateur #7 connecté"""
    service = MagicMock()
    app = FastAPI()
    app.include_router(controller.router, prefix="/utilisateur")
    app.dependency_overrides[verif_token] = lambda: Utilisateur("h", "alice", "COLLABORATEUR", id=7)
    app.dependency_overrides[controller.get_utilisateur_service] = lambda: service
    return TestClient(app), service


def test_changer_mot_de_passe_ok(http):
    client, service = http
    service.changer_mdp.return_value = True

    reponse = client.put(ROUTE, json={"ancien_mdp": "ancien", "nouveau_mdp": "nouveau"})

    assert reponse.status_code == 200
    assert reponse.json() == {"message": "Mot de passe modifié avec succès"}
    # l'utilisateur modifié est celui du token, quel que soit son grade
    service.changer_mdp.assert_called_once_with(7, "ancien", "nouveau")


def test_changer_mot_de_passe_ancien_incorrect(http):
    client, service = http
    service.changer_mdp.return_value = False

    reponse = client.put(ROUTE, json={"ancien_mdp": "faux", "nouveau_mdp": "nouveau"})

    assert reponse.status_code == 400
    assert "incorrect" in reponse.json()["detail"]


def test_changer_mot_de_passe_nouveau_vide(http):
    client, service = http
    service.changer_mdp.side_effect = ValueError("Le nouveau mot de passe est obligatoire.")

    reponse = client.put(ROUTE, json={"ancien_mdp": "ancien", "nouveau_mdp": ""})

    assert reponse.status_code == 400
    assert "obligatoire" in reponse.json()["detail"]


def test_changer_mot_de_passe_sans_token():
    app = FastAPI()
    app.include_router(controller.router, prefix="/utilisateur")

    reponse = TestClient(app).put(ROUTE, json={"ancien_mdp": "a", "nouveau_mdp": "b"})

    assert reponse.status_code == 401
