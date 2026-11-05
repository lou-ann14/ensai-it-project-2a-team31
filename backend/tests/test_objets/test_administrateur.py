import pytest
from src.Classes.classes_objets.utilisateurs.administrateur import Administrateur


class TestAdministrateur:
    @pytest.mark.parametrize(
        "id, nom_utilisateur, resultat_attendu",
        [(22, "jaimelestrains", "Administrateur : jaimelestrains (#22)")]
    )
    def test_str_administrateur(self, id, nom_utilisateur, resultat_attendu):
        assert str(Administrateur("1234", nom_utilisateur, id=id)) == resultat_attendu
