import os

import psycopg2
from psycopg2.extras import RealDictCursor
from src.utils.singleton import Singleton


class DBConnexion(metaclass=Singleton):
    """Gère la connexion à la base de données en implémentant le pattern Singelton.

    Cette classe assure qu'une seule connection à la base de données PostgreSQL
    soit ouverte lors de l'utilisation de l'application.

    Attributes:
        connection (psycopg2.extensions.connection): The active database
             connection instance.
    """
    def __init__(self):
        """Initialise la connection à la base de données à l'aide des données d'environnement.
        Raises:
            KeyError: Si une variable POSTGRES_* est manquante.
            psycopg2.Error: Si la connection à la bdd échoue.
        """

        self.__connexion = psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            database=os.environ["POSTGRES_DATABASE"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            options=f"-c search_path={os.environ['POSTGRES_SCHEMA']}",
            cursor_factory=RealDictCursor,
        )

    @property
    def connexion(self):
        """Donne accès à la connexion avec la base de données.
        Returns:
            La connexion établie avec la base de données
        """
        return self.__connexion
