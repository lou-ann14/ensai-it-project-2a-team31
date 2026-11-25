from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

# main configure les logs et lit le .env à l'import : on neutralise ces effets de bord
with (
    patch("src.utils.log_utils.initialize_logs"),
    patch("src.utils.env_var.load_environment_variables"),
    patch("src.utils.env_var.display_values"),
):
    import main


def test_reset_refuse_pour_un_non_admin():
    """Un compte non ADMIN reçoit une 403 et la base n'est PAS réinitialisée"""
    with patch("main.Reset_bdd") as reset, pytest.raises(HTTPException) as erreur:
        main.reset_database(token=MagicMock(grade="CLIENT"))

    assert erreur.value.status_code == 403
    reset.return_value.demarrer.assert_not_called()


def test_reset_ok_pour_un_admin():
    """Un admin peut réinitialiser la base"""
    with patch("main.Reset_bdd") as reset:
        reset.return_value.demarrer.return_value = True
        reponse = main.reset_database(token=MagicMock(grade="ADMIN"))

    reset.return_value.demarrer.assert_called_once()
    assert "SUCCES" in reponse["message"]


def test_reset_charge_les_fichiers_dans_l_ordre():
    """Le schéma est recréé, puis les tables, les comptes de test et les données de démonstration"""
    # GIVEN
    data = Path(main.__file__).resolve().parent / "data"
    fichiers = ["init_bdd.sql", "admin.sql", "donnees_demo.sql"]

    # WHEN
    with (
        patch("src.utils.reset_bdd.DBConnexion") as connexion,
        patch("src.utils.reset_bdd.dotenv.load_dotenv"),
        patch.dict("os.environ", {"POSTGRES_SCHEMA": "schema_test"}),
    ):
        assert main.Reset_bdd().demarrer() is True

    # THEN
    cursor = connexion().connexion.__enter__().cursor().__enter__()
    requetes = [appel.args[0] for appel in cursor.execute.call_args_list]
    assert requetes[0] == "DROP SCHEMA IF EXISTS schema_test CASCADE; CREATE SCHEMA schema_test;"
    assert requetes[1:] == [(data / nom).read_text(encoding="utf-8") for nom in fichiers]
