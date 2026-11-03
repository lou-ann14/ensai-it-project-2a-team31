import pytest
from src.Classes.classes_objets.utilisateurs.client import Client


class TestClient:
    @pytest.mark.parametrize(
        "id, nom_utilisateur, resultat_attendu",
        [(22, "jaimelestrains", "Client : jaimelestrains 22")]
    )
    def test_str_client(id, nom_utilisateur, resultat_attendu):
        assert Client.__str__() == resultat_attendu
