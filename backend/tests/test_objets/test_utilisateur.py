import re

import pytest
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur


class TestUtilisateur:
    @pytest.mark.parametrize(
        "params, erreur, message_erreur",
        [
            (
                {"id": "22"},
                TypeError,
                "L'identifiant doit être un entier."
            ),
            (
                {"mdp": 22},
                TypeError,
                "Le mot de passe doit être une chaîne de caractères."
            ),
            (
                {"nom_utilisateur": 42},
                TypeError,
                "Le nom d'utilisateur doit être une chaîne de caractères."
            ),
            (
                {"grade": 2},
                TypeError,
                "Le grade doit être une chaîne de caractères"
            )
        ]
    )
    def test_init_utilisateur(self, params, erreur, message_erreur):
        dico = {
            "id": 22,
            "mdp": "1234",
            "nom_utilisateur": "jaimelestrains",
            "grade": "Client"}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Utilisateur(**dico)

    @pytest.mark.parametrize(
        "id, mdp, nom_utilisateur, grade, resultat_attendu",
        [(22, "1234", "jaimelestrains", "Client", "L'utilisateur jaimelestrains 22 est un Client")]
    )
    def test_str_utilisateurs(self, id, mdp, nom_utilisateur, grade, resultat_attendu):
        assert str(Utilisateur()) == resultat_attendu
