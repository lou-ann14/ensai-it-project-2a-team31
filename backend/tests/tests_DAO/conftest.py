import os

import dotenv
import pytest

# On charge le .env, puis on force un schéma de TEST : les tests ne touchent jamais
# au schéma de développement (celui de POSTGRES_SCHEMA dans le .env).
dotenv.load_dotenv()
os.environ["POSTGRES_SCHEMA"] = "projet_test"

from src.utils.db_connexion import DBConnexion  # noqa: E402
from src.utils.reset_bdd import Reset_bdd  # noqa: E402


@pytest.fixture(autouse=True)
def bdd_propre():
    """Avant chaque test : recrée le schéma de test avec les données de test_bdd.sql."""
    # Sécurité : on vérifie qu'on est bien connecté au schéma de test avant de le réinitialiser
    with DBConnexion().connexion as connexion, connexion.cursor() as cursor:
        cursor.execute("SHOW search_path")
        assert cursor.fetchone()["search_path"] == "projet_test"

    Reset_bdd().demarrer()