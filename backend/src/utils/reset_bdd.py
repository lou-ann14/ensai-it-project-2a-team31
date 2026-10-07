import os
from pathlib import Path

import dotenv
from src.utils.db_connexion import DBConnexion
from src.utils.singleton import Singleton


class Reset_bdd(metaclass=Singleton):
    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent.parent.parent

    def Demarrer(self, test_dao=False):
        init_chemin_bdd = self.base_path / "backend" / "data" / "init_bdd.sql"

        dotenv.load_dotenv()

        schema = os.environ["POSTGRES_SCHEMA"]
        create_schema = (
            f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"
        )

        try:
            with open(init_chemin_bdd, encoding="utf-8") as init_fichier_bdd:
                init_bdd_as_string = init_fichier_bdd.read()
        except FileNotFoundError as e:
            raise f"Erreur de chemin : impossible de trouver le fichier {e.filename}"

            
        with DBConnexion().connexion.cursor() as cursor:
            cursor.execute(create_schema)
            cursor.execute(init_bdd_as_string)
        
        return True
