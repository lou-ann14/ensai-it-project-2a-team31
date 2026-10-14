import pytest
from src.Classes.classes_objets.utilisateurs.administrateur import Administrateur


class TestAdministrateur:
    @pytest.mark.parametrize(
        "id, nom_utilisateur, resultat_attendu",
        [(22, "jaimelestrains", "Administrateur : jaimelestrains 22")]
    )
    def test_str_administrateur(id, nom_utilisateur, resultat_attendu):
        assert Administrateur.__str__() == resultat_attendu
