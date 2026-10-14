import pytest
from src.Classes.classes_objets.utilisateurs.collaborateur import Collaborateur


class TestCollaborateur:
    @pytest.mark.parametrize(
        "id, nom_utilisateur, resultat_attendu",
        [(22, "jaimelestrains", "Collaborateur : jaimelestrains 22")]
    )
    def test_str_collaborateur(id, nom_utilisateur, resultat_attendu):
        assert Collaborateur.__str__() == resultat_attendu
