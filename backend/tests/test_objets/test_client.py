import pytest
from src.Classes.classes_objets.utilisateurs.client import Client


class TestClient:
    @pytest.mark.parametrize(
        "id, nom_utilisateur, resultat_attendu",
        [(22, "jaimelestrains", "Client : jaimelestrains (#22)")]
    )
    def test_str_client(self, id, nom_utilisateur, resultat_attendu):
        assert str(Client("1234", nom_utilisateur, id=id)) == resultat_attendu
