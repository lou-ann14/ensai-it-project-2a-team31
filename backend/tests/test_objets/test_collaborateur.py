import pytest
from src.Classes.classes_objets.utilisateurs.collaborateur import Collaborateur


class TestCollaborateur:
    @pytest.mark.parametrize(
        "id, nom_utilisateur, resultat_attendu",
        [(22, "jaimelestrains", "Collaborateur : jaimelestrains (#22)")]
    )
    def test_str_collaborateur(self, id, nom_utilisateur, resultat_attendu):
        assert str(Collaborateur("1234", nom_utilisateur, id=id)) == resultat_attendu
