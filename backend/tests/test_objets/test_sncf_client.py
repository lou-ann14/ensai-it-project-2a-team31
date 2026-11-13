from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests
from src.utils.sncf_client import SncfClient, SncfConfigurationError

# requests.get est simulé : l'API SNCF n'est jamais appelée réellement.

GET = "src.utils.sncf_client.requests.get"


@pytest.fixture
def token(monkeypatch):
    monkeypatch.setenv("SNCF_API_TOKEN", "jeton-de-test")


def reponse_json(donnees, status=200):
    reponse = MagicMock(status_code=status)
    reponse.json.return_value = donnees
    if status >= 400:
        reponse.raise_for_status.side_effect = requests.HTTPError(response=reponse)
    return reponse


# Configuration


def test_token_manquant(monkeypatch):
    """Sans token, une SncfConfigurationError est levée (et non plus une RuntimeError → erreur 500)"""
    monkeypatch.delenv("SNCF_API_TOKEN", raising=False)

    with pytest.raises(SncfConfigurationError):
        SncfClient()


def test_token_manquant_est_une_erreur_requests(monkeypatch):
    """Les contrôleurs attrapent requests.RequestException pour répondre 502 : le cas est couvert"""
    monkeypatch.delenv("SNCF_API_TOKEN", raising=False)

    with pytest.raises(requests.RequestException):
        SncfClient()


# rechercher_gares


def test_rechercher_gares(token):
    donnees = {"places": [{"stop_area": {
        "id": "stop_area:SNCF:87471003",
        "name": "Rennes",
        "administrative_regions": [{"level": 6, "name": "Ille-et-Vilaine"}, {"level": 8, "name": "Rennes"}],
    }}]}
    with patch(GET, return_value=reponse_json(donnees)) as get:
        gares = SncfClient().rechercher_gares("Renn")

    assert gares == [{"id_sncf": "stop_area:SNCF:87471003", "nom": "Rennes", "ville": "Rennes"}]
    assert get.call_args.kwargs["params"] == {"type[]": "stop_area", "q": "Renn"}
    assert get.call_args.kwargs["auth"] == ("jeton-de-test", "")


def test_rechercher_gares_sans_commune(token):
    donnees = {"places": [{"stop_area": {"id": "x", "name": "Gare inconnue"}}]}
    with patch(GET, return_value=reponse_json(donnees)):
        assert SncfClient().rechercher_gares("Gare")[0]["ville"] is None


# duree_trajet


def test_duree_trajet_le_plus_rapide(token):
    donnees = {"journeys": [{"duration": 5400}, {"duration": 4620}, {"duration": 6000}]}
    with patch(GET, return_value=reponse_json(donnees)) as get:
        duree = SncfClient().duree_trajet("a", "b", datetime(2027, 6, 1, 8, 35))

    assert duree == 4620
    assert get.call_args.kwargs["params"]["datetime"] == "20270601T083500"


def test_duree_trajet_aucun_itineraire(token):
    with patch(GET, return_value=reponse_json({"journeys": []})):
        assert SncfClient().duree_trajet("a", "b") is None


def test_duree_trajet_404(token):
    """L'API répond 404 (pas d'itinéraire) : None, pas d'exception"""
    with patch(GET, return_value=reponse_json({}, status=404)):
        assert SncfClient().duree_trajet("a", "b") is None


def test_duree_trajet_erreur_serveur(token):
    """Une autre erreur HTTP est relancée (le contrôleur répondra 502)"""
    with patch(GET, return_value=reponse_json({}, status=503)):
        with pytest.raises(requests.HTTPError):
            SncfClient().duree_trajet("a", "b")
