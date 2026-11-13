import asyncio
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
    with patch("main.Reset_bdd") as reset:
        with pytest.raises(HTTPException) as erreur:
            asyncio.run(main.reset_database(token=MagicMock(grade="CLIENT")))

    assert erreur.value.status_code == 403
    reset.return_value.demarrer.assert_not_called()


def test_reset_ok_pour_un_admin():
    with patch("main.Reset_bdd") as reset:
        reset.return_value.demarrer.return_value = True
        reponse = asyncio.run(main.reset_database(token=MagicMock(grade="ADMIN")))

    reset.return_value.demarrer.assert_called_once()
    assert "SUCCES" in reponse["message"]
