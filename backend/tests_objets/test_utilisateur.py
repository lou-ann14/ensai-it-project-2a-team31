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
                {"role": 2},
                TypeError,
                "Le role doit être une chaîne de caractères"
            )
        ]
    )
    def test_init_utilisateur(params, erreur, message_erreur):
        dico = {
            22,
            "1234",
            "jaimelestrains",
            "Client"}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Utilisateur(**dico)

    @pytest.mark.parametrize(
        "id, mdp, nom_utilisateur, role, resultat_attendu",
        [(22, "1234", "jaimelestrains", "Client", "L'utilisateur jaimelestrains 22 est un Client")]
    )
    def test_str_utilisateurs(id, mdp, nom_utilisateur, role, resultat_attendu):
        assert Utilisateur.__str__() == resultat_attendu
